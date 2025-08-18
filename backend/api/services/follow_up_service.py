"""
Follow-Up Service
Automatisches Nachfassen bei Leads für 30% mehr Umsatz (laut Video)
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta, timezone
from sqlmodel import select, and_
from api.core.database import get_session_context
from api.models.lead import Lead, FollowUp, LeadActivity, LeadStatus
from api.services.twilio_service import TwilioService
from api.services.voice_pipeline import VoicePipelineService

logger = logging.getLogger(__name__)


class FollowUpService:
    """
    Service für automatisches Follow-Up Management:
    - Zeitbasierte Follow-Ups (3, 7, 14, 30 Tage)
    - Intelligente Priorisierung
    - Automatische Anruf-Planung
    - 30% mehr Umsatz durch systematisches Follow-Up
    """
    
    # Standard Follow-Up Schedule (in Tagen nach erstem Kontakt)
    DEFAULT_SCHEDULE = [3, 7, 14, 30]
    
    # Follow-Up Templates nach Typ
    FOLLOW_UP_SCRIPTS = {
        'after_offer': {
            'day_3': "Guten Tag {name}, Sie haben vor 3 Tagen unser Angebot erhalten. Ich wollte nachfragen, ob Sie noch Fragen dazu haben?",
            'day_7': "Hallo {name}, ich hoffe es geht Ihnen gut. Haben Sie schon Zeit gehabt, unser Angebot durchzusehen? Gibt es etwas, was ich Ihnen erläutern kann?",
            'day_14': "Guten Tag {name}, vor zwei Wochen haben wir Ihnen unser Angebot zugesendet. Besteht weiterhin Interesse? Ich würde gerne wissen, wie wir Ihnen weiterhelfen können.",
            'day_30': "Hallo {name}, es ist nun ein Monat vergangen seit unserem Angebot. Falls sich Ihre Prioritäten geändert haben, würde ich das gerne wissen. Haben Sie noch Interesse?"
        },
        'after_demo': {
            'day_3': "Hallo {name}, wie hat Ihnen unsere Demo gefallen? Gibt es noch offene Fragen, die ich klären kann?",
            'day_7': "Guten Tag {name}, haben Sie intern schon über unsere Lösung sprechen können? Wie ist das Feedback?",
            'day_14': "Hallo {name}, ich wollte nachfassen bezüglich unserer Demo. Wie können wir Sie bei Ihrer Entscheidung unterstützen?",
            'day_30': "Guten Tag {name}, ist das Projekt noch aktuell? Wir würden uns freuen, Sie unterstützen zu können."
        },
        'reactivation': {
            'inactive_30': "Hallo {name}, wir haben länger nichts voneinander gehört. Hat sich bei Ihrem Projekt etwas getan?",
            'inactive_60': "Guten Tag {name}, vor einiger Zeit hatten wir über {topic} gesprochen. Ist das Thema noch relevant für Sie?",
            'inactive_90': "Hallo {name}, es ist schon eine Weile her. Ich wollte nachfragen, ob sich Ihre Anforderungen geändert haben und ob wir Ihnen helfen können?"
        }
    }
    
    def __init__(self):
        self.twilio_service = TwilioService()
        self.voice_pipeline = VoicePipelineService()
    
    async def schedule_follow_ups(
        self,
        lead_id: int,
        follow_up_type: str = 'after_offer',
        custom_schedule: Optional[List[int]] = None
    ) -> List[FollowUp]:
        """
        Plant Follow-Ups für einen Lead
        
        Args:
            lead_id: Lead ID
            follow_up_type: Typ des Follow-Ups (after_offer, after_demo, etc.)
            custom_schedule: Optionaler Custom Schedule (Tage)
            
        Returns:
            Liste der geplanten Follow-Ups
        """
        schedule = custom_schedule or self.DEFAULT_SCHEDULE
        created_follow_ups = []
        
        async with get_session_context() as session:
            # Lead laden
            stmt = select(Lead).where(Lead.id == lead_id)
            result = await session.exec(stmt)
            lead = result.one()
            
            # Basis-Datum (heute)
            base_date = datetime.now(timezone.utc)
            
            for index, days in enumerate(schedule, 1):
                # Follow-Up Datum berechnen
                follow_up_date = base_date + timedelta(days=days)
                
                # Priorität basierend auf Lead Score
                if lead.lead_score >= 8:
                    priority = 'urgent'
                elif lead.lead_score >= 5:
                    priority = 'high'
                else:
                    priority = 'medium'
                
                # Follow-Up erstellen
                follow_up = FollowUp(
                    lead_id=lead_id,
                    scheduled_date=follow_up_date,
                    follow_up_number=index,
                    script_type=f"{follow_up_type}_day_{days}",
                    priority=priority,
                    status='pending'
                )
                
                session.add(follow_up)
                created_follow_ups.append(follow_up)
                
                logger.info(f"Follow-Up #{index} geplant für Lead {lead_id} am {follow_up_date.date()}")
            
            # Lead Status aktualisieren
            lead.next_follow_up = created_follow_ups[0].scheduled_date if created_follow_ups else None
            lead.status = LeadStatus.NURTURING
            session.add(lead)
            
            # Activity Log
            activity = LeadActivity(
                lead_id=lead_id,
                activity_type='follow_up_scheduled',
                description=f'{len(created_follow_ups)} Follow-Ups geplant',
                metadata={
                    'type': follow_up_type,
                    'schedule': schedule,
                    'first_date': str(created_follow_ups[0].scheduled_date) if created_follow_ups else None
                }
            )
            session.add(activity)
            
            await session.commit()
            
            return created_follow_ups
    
    async def get_todays_follow_ups(
        self,
        organization_id: int
    ) -> List[FollowUp]:
        """
        Holt alle Follow-Ups für heute
        """
        async with get_session_context() as session:
            today = datetime.now(timezone.utc).date()
            tomorrow = today + timedelta(days=1)
            
            stmt = select(FollowUp).join(Lead).where(
                and_(
                    Lead.organization_id == organization_id,
                    FollowUp.scheduled_date >= today,
                    FollowUp.scheduled_date < tomorrow,
                    FollowUp.status == 'pending'
                )
            ).order_by(FollowUp.priority.desc(), FollowUp.scheduled_date)
            
            result = await session.exec(stmt)
            return result.all()
    
    async def process_follow_up(
        self,
        follow_up_id: int,
        use_voice_agent: bool = True
    ) -> Dict:
        """
        Führt ein Follow-Up durch
        
        Args:
            follow_up_id: Follow-Up ID
            use_voice_agent: Ob Voice Agent verwendet werden soll
            
        Returns:
            Ergebnis des Follow-Ups
        """
        async with get_session_context() as session:
            # Follow-Up laden
            stmt = select(FollowUp).where(FollowUp.id == follow_up_id)
            result = await session.exec(stmt)
            follow_up = result.one()
            
            # Lead laden
            stmt = select(Lead).where(Lead.id == follow_up.lead_id)
            result = await session.exec(stmt)
            lead = result.one()
            
            result_data = {
                'success': False,
                'method': 'voice' if use_voice_agent else 'manual',
                'outcome': None,
                'next_action': None
            }
            
            try:
                if use_voice_agent and lead.phone:
                    # Voice Agent Anruf initiieren
                    script = self._get_follow_up_script(follow_up.script_type, lead)
                    
                    # Anruf durchführen
                    call_result = await self.twilio_service.make_outbound_call(
                        to_number=lead.phone,
                        from_number=None,  # Verwendet Standard-Nummer
                        initial_message=script
                    )
                    
                    if call_result.get('success'):
                        result_data['success'] = True
                        result_data['outcome'] = 'called'
                        result_data['call_sid'] = call_result.get('call_sid')
                        
                        # Follow-Up als completed markieren
                        follow_up.status = 'completed'
                        follow_up.completed_date = datetime.now(timezone.utc)
                        follow_up.outcome = 'successful_call'
                        
                        # Lead Update
                        lead.last_contact_date = datetime.now(timezone.utc)
                        lead.follow_up_count += 1
                        
                        # Nächstes Follow-Up planen wenn nötig
                        if follow_up.follow_up_number < len(self.DEFAULT_SCHEDULE):
                            next_days = self.DEFAULT_SCHEDULE[follow_up.follow_up_number]
                            next_date = datetime.now(timezone.utc) + timedelta(days=next_days)
                            lead.next_follow_up = next_date
                            result_data['next_action'] = f"Nächstes Follow-Up in {next_days} Tagen"
                    else:
                        # Anruf fehlgeschlagen
                        follow_up.outcome = 'call_failed'
                        result_data['outcome'] = 'failed'
                        
                        # Neuen Versuch für morgen planen
                        follow_up.scheduled_date = datetime.now(timezone.utc) + timedelta(days=1)
                        result_data['next_action'] = "Erneuter Versuch morgen"
                else:
                    # Manuelles Follow-Up oder keine Telefonnummer
                    follow_up.status = 'pending_manual'
                    result_data['outcome'] = 'manual_required'
                    result_data['next_action'] = "Manueller Kontakt erforderlich"
                
                # Activity Log
                activity = LeadActivity(
                    lead_id=lead.id,
                    activity_type='follow_up',
                    description=f'Follow-Up #{follow_up.follow_up_number} durchgeführt',
                    metadata=result_data
                )
                session.add(activity)
                
                # Speichern
                session.add(follow_up)
                session.add(lead)
                await session.commit()
                
                logger.info(f"Follow-Up {follow_up_id} verarbeitet: {result_data['outcome']}")
                
            except Exception as e:
                logger.error(f"Fehler bei Follow-Up {follow_up_id}: {str(e)}")
                result_data['error'] = str(e)
                
                # Follow-Up als fehlgeschlagen markieren
                follow_up.status = 'failed'
                follow_up.notes = f"Fehler: {str(e)}"
                session.add(follow_up)
                await session.commit()
            
            return result_data
    
    def _get_follow_up_script(self, script_type: str, lead: Lead) -> str:
        """
        Holt das passende Follow-Up Script und personalisiert es
        """
        # Script-Typ aufteilen (z.B. "after_offer_day_7")
        parts = script_type.split('_')
        
        if len(parts) >= 3:
            follow_up_type = '_'.join(parts[:-2])  # z.B. "after_offer"
            day_key = '_'.join(parts[-2:])  # z.B. "day_7"
            
            if follow_up_type in self.FOLLOW_UP_SCRIPTS:
                if day_key in self.FOLLOW_UP_SCRIPTS[follow_up_type]:
                    script = self.FOLLOW_UP_SCRIPTS[follow_up_type][day_key]
                    
                    # Personalisierung
                    name = f"{lead.first_name} {lead.last_name}".strip() or "Herr/Frau"
                    script = script.format(
                        name=name,
                        topic=lead.enrichment_data.get('topic', 'unser Angebot')
                    )
                    
                    return script
        
        # Fallback Script
        return f"Guten Tag, ich rufe bezüglich unseres letzten Gesprächs an. Haben Sie noch Interesse an unserem Angebot?"
    
    async def process_all_due_follow_ups(
        self,
        organization_id: int,
        limit: int = 50
    ) -> Dict[str, int]:
        """
        Verarbeitet alle fälligen Follow-Ups einer Organisation
        """
        follow_ups = await self.get_todays_follow_ups(organization_id)
        
        stats = {
            'total': len(follow_ups),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'manual': 0
        }
        
        # Limitierung anwenden
        follow_ups = follow_ups[:limit]
        
        for follow_up in follow_ups:
            try:
                result = await self.process_follow_up(follow_up.id)
                stats['processed'] += 1
                
                if result['success']:
                    stats['successful'] += 1
                elif result['outcome'] == 'manual_required':
                    stats['manual'] += 1
                else:
                    stats['failed'] += 1
                    
            except Exception as e:
                logger.error(f"Fehler bei Follow-Up Verarbeitung: {str(e)}")
                stats['failed'] += 1
        
        logger.info(f"Follow-Up Verarbeitung abgeschlossen: {stats}")
        
        return stats
    
    async def cancel_follow_ups(
        self,
        lead_id: int,
        reason: str = "Lead converted"
    ) -> int:
        """
        Bricht alle ausstehenden Follow-Ups für einen Lead ab
        (z.B. wenn Lead konvertiert wurde)
        """
        async with get_session_context() as session:
            stmt = select(FollowUp).where(
                and_(
                    FollowUp.lead_id == lead_id,
                    FollowUp.status == 'pending'
                )
            )
            result = await session.exec(stmt)
            follow_ups = result.all()
            
            cancelled_count = 0
            
            for follow_up in follow_ups:
                follow_up.status = 'cancelled'
                follow_up.notes = reason
                session.add(follow_up)
                cancelled_count += 1
            
            if cancelled_count > 0:
                # Activity Log
                activity = LeadActivity(
                    lead_id=lead_id,
                    activity_type='follow_ups_cancelled',
                    description=f'{cancelled_count} Follow-Ups abgebrochen',
                    metadata={'reason': reason}
                )
                session.add(activity)
                
                await session.commit()
                
                logger.info(f"{cancelled_count} Follow-Ups für Lead {lead_id} abgebrochen")
            
            return cancelled_count
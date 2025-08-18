"""
Lead Reaktivierung Service
Automatische Reaktivierung von inaktiven/kalten Leads
"Fehler sind egal bei alten Leads" - niedriges Risiko!
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from sqlmodel import select, and_, or_
from api.core.database import get_session_context
from api.models.lead import Lead, LeadActivity, LeadStatus, FollowUp
from api.services.twilio_service import TwilioService
from api.services.lead_scoring_service import LeadScoringService

logger = logging.getLogger(__name__)


class LeadReactivationService:
    """
    Service für automatische Lead-Reaktivierung nach dem Video-Konzept:
    - Kontaktiert inaktive Leads nach 30/60/90 Tagen
    - Niedriges Risiko, da Leads bereits "kalt" sind
    - Reaktiviert Umsatzpotenzial aus bestehendem Lead-Bestand
    - Personalisierte Ansprache basierend auf Historie
    """
    
    # Reaktivierungs-Intervalle in Tagen
    REACTIVATION_INTERVALS = [30, 60, 90, 180]
    
    # Reaktivierungs-Scripts nach Inaktivitätsdauer
    REACTIVATION_SCRIPTS = {
        30: {
            'greeting': "Guten Tag {name}, hier ist {agent_name} von {company}.",
            'opener': "Wir hatten vor etwa einem Monat über {topic} gesprochen. Ich wollte nachfragen, ob sich bei Ihnen etwas getan hat?",
            'value_prop': "Wir haben inzwischen einige neue Features, die für Sie interessant sein könnten.",
            'close': "Hätten Sie diese Woche Zeit für ein kurzes Gespräch?"
        },
        60: {
            'greeting': "Hallo {name}, schön Sie wieder zu erreichen.",
            'opener': "Es ist schon zwei Monate her seit unserem letzten Gespräch über {topic}. Hat sich Ihre Situation verändert?",
            'value_prop': "Viele unserer Kunden haben in den letzten Wochen großartige Ergebnisse erzielt.",
            'close': "Wäre es sinnvoll, nochmal darüber zu sprechen?"
        },
        90: {
            'greeting': "Guten Tag {name}, hier ist {agent_name} von {company}.",
            'opener': "Vor drei Monaten hatten wir über {topic} gesprochen. Ist das Thema noch relevant für Sie?",
            'value_prop': "Wir haben seitdem unser Angebot deutlich verbessert und der Preis ist aktuell sehr attraktiv.",
            'close': "Soll ich Ihnen die neuen Konditionen zusenden?"
        },
        180: {
            'greeting': "Hallo {name}, es ist eine Weile her.",
            'opener': "Vor einem halben Jahr hatten wir Kontakt bezüglich {topic}. Ich wollte fragen, ob sich Ihre Prioritäten geändert haben?",
            'value_prop': "Wir haben komplett neue Lösungen entwickelt, die perfekt zu Ihren damaligen Anforderungen passen würden.",
            'close': "Haben Sie Interesse an einem unverbindlichen Update-Gespräch?"
        }
    }
    
    def __init__(self):
        self.twilio_service = TwilioService()
        self.scoring_service = LeadScoringService()
    
    async def identify_inactive_leads(
        self,
        organization_id: int,
        days_inactive: int = 30
    ) -> List[Lead]:
        """
        Identifiziert inaktive Leads für Reaktivierung
        
        Args:
            organization_id: Organisation ID
            days_inactive: Tage seit letztem Kontakt
            
        Returns:
            Liste von inaktiven Leads
        """
        async with get_session_context() as session:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_inactive)
            
            # Query für inaktive Leads
            stmt = select(Lead).where(
                and_(
                    Lead.organization_id == organization_id,
                    Lead.status != LeadStatus.CONVERTED,
                    Lead.status != LeadStatus.LOST,
                    or_(
                        Lead.last_contact_date < cutoff_date,
                        Lead.last_contact_date.is_(None)
                    )
                )
            )
            
            # Priorisierung nach Lead Score (höhere Scores zuerst)
            stmt = stmt.order_by(Lead.lead_score.desc())
            
            result = await session.exec(stmt)
            leads = result.all()
            
            # Filtere Leads, die bereits eine geplante Reaktivierung haben
            filtered_leads = []
            for lead in leads:
                if not await self._has_pending_reactivation(lead.id):
                    filtered_leads.append(lead)
            
            logger.info(f"Gefunden: {len(filtered_leads)} inaktive Leads (>{days_inactive} Tage)")
            
            return filtered_leads
    
    async def _has_pending_reactivation(self, lead_id: int) -> bool:
        """Prüft ob bereits eine Reaktivierung geplant ist"""
        async with get_session_context() as session:
            stmt = select(FollowUp).where(
                and_(
                    FollowUp.lead_id == lead_id,
                    FollowUp.status == 'pending',
                    FollowUp.script_type.like('reactivation%')
                )
            )
            result = await session.exec(stmt)
            return result.first() is not None
    
    async def schedule_reactivation(
        self,
        lead: Lead,
        priority: str = 'medium'
    ) -> FollowUp:
        """
        Plant eine Reaktivierungs-Anruf für einen Lead
        
        Args:
            lead: Lead Objekt
            priority: Priorität (low/medium/high/urgent)
            
        Returns:
            Erstelltes FollowUp Objekt
        """
        async with get_session_context() as session:
            # Berechne Inaktivitätsdauer
            days_inactive = lead.calculate_days_since_contact() or 999
            
            # Wähle passendes Script-Intervall
            script_interval = 30
            for interval in self.REACTIVATION_INTERVALS:
                if days_inactive >= interval:
                    script_interval = interval
            
            # Priorität basierend auf Lead Score anpassen
            if lead.lead_score >= 7:
                priority = 'high'
            elif lead.lead_score <= 3:
                priority = 'low'
            
            # Follow-Up für Reaktivierung erstellen
            follow_up = FollowUp(
                lead_id=lead.id,
                scheduled_date=datetime.now(timezone.utc),
                follow_up_number=0,  # Reaktivierung zählt nicht als reguläres Follow-Up
                script_type=f'reactivation_{script_interval}',
                priority=priority,
                status='pending',
                notes=f'Automatische Reaktivierung nach {days_inactive} Tagen Inaktivität'
            )
            
            session.add(follow_up)
            
            # Activity Log
            activity = LeadActivity(
                lead_id=lead.id,
                activity_type='reactivation_scheduled',
                description=f'Reaktivierung geplant nach {days_inactive} Tagen',
                metadata={
                    'days_inactive': days_inactive,
                    'lead_score': lead.lead_score,
                    'priority': priority
                }
            )
            session.add(activity)
            
            await session.commit()
            await session.refresh(follow_up)
            
            logger.info(f"Reaktivierung geplant für Lead {lead.id} (Score: {lead.lead_score})")
            
            return follow_up
    
    async def execute_reactivation(
        self,
        follow_up_id: int
    ) -> Dict:
        """
        Führt einen Reaktivierungs-Anruf durch
        
        Args:
            follow_up_id: Follow-Up ID
            
        Returns:
            Ergebnis des Anrufs
        """
        async with get_session_context() as session:
            # Follow-Up und Lead laden
            stmt = select(FollowUp).where(FollowUp.id == follow_up_id)
            result = await session.exec(stmt)
            follow_up = result.one()
            
            stmt = select(Lead).where(Lead.id == follow_up.lead_id)
            result = await session.exec(stmt)
            lead = result.one()
            
            result_data = {
                'success': False,
                'lead_id': lead.id,
                'outcome': None,
                'new_score': None
            }
            
            try:
                # Script generieren
                script = self._generate_reactivation_script(lead, follow_up.script_type)
                
                # Anruf durchführen
                logger.info(f"Starte Reaktivierungs-Anruf für Lead {lead.id}")
                
                call_result = await self.twilio_service.make_outbound_call(
                    to_number=lead.phone,
                    from_number=None,
                    initial_message=script
                )
                
                if call_result.get('success'):
                    result_data['success'] = True
                    result_data['outcome'] = 'contacted'
                    result_data['call_sid'] = call_result.get('call_sid')
                    
                    # Lead aktualisieren
                    lead.last_contact_date = datetime.now(timezone.utc)
                    lead.status = LeadStatus.CONTACTED
                    
                    # Follow-Up als erledigt markieren
                    follow_up.status = 'completed'
                    follow_up.completed_date = datetime.now(timezone.utc)
                    follow_up.outcome = 'successful_reactivation'
                    
                    # Score neu berechnen (Reaktivierung gibt Bonus-Punkte)
                    call_data = {
                        'duration': call_result.get('duration', 0),
                        'transcript': call_result.get('transcript', ''),
                        'is_reactivation': True
                    }
                    
                    new_score, reasons = await self.scoring_service.calculate_score(
                        call_data, lead
                    )
                    
                    # Bonus für erfolgreiche Reaktivierung
                    new_score = min(10, new_score + 1)
                    reasons.append("✨ Erfolgreich reaktiviert")
                    
                    lead.lead_score = new_score
                    lead.score_reasons = reasons
                    result_data['new_score'] = new_score
                    
                    logger.info(f"Lead {lead.id} erfolgreich reaktiviert! Neuer Score: {new_score}")
                    
                else:
                    # Anruf fehlgeschlagen
                    result_data['outcome'] = 'no_answer'
                    follow_up.outcome = 'no_answer'
                    
                    # Bei mehreren Fehlversuchen Lead als "lost" markieren
                    if lead.follow_up_count >= 5:
                        lead.status = LeadStatus.LOST
                        lead.lost_reason = "Mehrfach nicht erreichbar"
                
                # Activity Log
                activity = LeadActivity(
                    lead_id=lead.id,
                    activity_type='reactivation_attempt',
                    description=f'Reaktivierungsversuch: {result_data["outcome"]}',
                    metadata=result_data
                )
                session.add(activity)
                
                # Speichern
                session.add(lead)
                session.add(follow_up)
                await session.commit()
                
            except Exception as e:
                logger.error(f"Fehler bei Reaktivierung {follow_up_id}: {str(e)}")
                result_data['error'] = str(e)
                result_data['outcome'] = 'error'
            
            return result_data
    
    def _generate_reactivation_script(self, lead: Lead, script_type: str) -> str:
        """
        Generiert personalisiertes Reaktivierungs-Script
        """
        # Extrahiere Intervall aus Script-Typ (z.B. "reactivation_30")
        interval = 30
        if '_' in script_type:
            try:
                interval = int(script_type.split('_')[1])
            except:
                pass
        
        # Wähle Template
        template = self.REACTIVATION_SCRIPTS.get(
            interval,
            self.REACTIVATION_SCRIPTS[30]
        )
        
        # Personalisierung
        name = f"{lead.first_name} {lead.last_name}".strip() or "Herr/Frau"
        company = "VocalIQ"
        agent_name = "Ihr KI-Assistent"
        topic = lead.enrichment_data.get('initial_topic', 'unsere Lösung')
        
        # Script zusammenbauen
        script_parts = []
        
        # Greeting
        script_parts.append(
            template['greeting'].format(
                name=name,
                agent_name=agent_name,
                company=company
            )
        )
        
        # Opener
        script_parts.append(
            template['opener'].format(
                topic=topic
            )
        )
        
        # Value Proposition (nur bei höherem Lead Score)
        if lead.lead_score >= 5:
            script_parts.append(template['value_prop'])
        
        # Close
        script_parts.append(template['close'])
        
        return " ".join(script_parts)
    
    async def bulk_schedule_reactivations(
        self,
        organization_id: int,
        max_leads: int = 50
    ) -> Dict[str, int]:
        """
        Plant Reaktivierungen für alle qualifizierten inaktiven Leads
        """
        stats = {
            '30_days': 0,
            '60_days': 0,
            '90_days': 0,
            '180_days': 0,
            'total': 0
        }
        
        for interval in self.REACTIVATION_INTERVALS:
            # Finde inaktive Leads für dieses Intervall
            leads = await self.identify_inactive_leads(organization_id, interval)
            
            # Limitierung pro Intervall
            interval_limit = max_leads // len(self.REACTIVATION_INTERVALS)
            leads = leads[:interval_limit]
            
            for lead in leads:
                try:
                    await self.schedule_reactivation(lead)
                    stats[f'{interval}_days'] += 1
                    stats['total'] += 1
                    
                except Exception as e:
                    logger.error(f"Fehler bei Reaktivierungs-Planung für Lead {lead.id}: {str(e)}")
        
        logger.info(f"Reaktivierungen geplant: {stats}")
        
        return stats
    
    async def get_reactivation_metrics(
        self,
        organization_id: int,
        days: int = 30
    ) -> Dict:
        """
        Holt Metriken über Reaktivierungs-Erfolg
        """
        async with get_session_context() as session:
            since_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Erfolgreiche Reaktivierungen
            stmt = select(LeadActivity).join(Lead).where(
                and_(
                    Lead.organization_id == organization_id,
                    LeadActivity.activity_type == 'reactivation_attempt',
                    LeadActivity.created_at >= since_date
                )
            )
            result = await session.exec(stmt)
            activities = result.all()
            
            metrics = {
                'total_attempts': len(activities),
                'successful': 0,
                'no_answer': 0,
                'converted': 0,
                'revenue_reactivated': 0.0
            }
            
            for activity in activities:
                metadata = activity.metadata or {}
                
                if metadata.get('outcome') == 'contacted':
                    metrics['successful'] += 1
                    
                    # Prüfe ob Lead konvertiert wurde
                    stmt = select(Lead).where(Lead.id == activity.lead_id)
                    result = await session.exec(stmt)
                    lead = result.one()
                    
                    if lead.converted:
                        metrics['converted'] += 1
                        metrics['revenue_reactivated'] += lead.conversion_value or 0
                        
                elif metadata.get('outcome') == 'no_answer':
                    metrics['no_answer'] += 1
            
            # Erfolgsrate berechnen
            if metrics['total_attempts'] > 0:
                metrics['success_rate'] = (metrics['successful'] / metrics['total_attempts']) * 100
                metrics['conversion_rate'] = (metrics['converted'] / metrics['total_attempts']) * 100
            else:
                metrics['success_rate'] = 0
                metrics['conversion_rate'] = 0
            
            logger.info(f"Reaktivierungs-Metriken: {metrics}")
            
            return metrics
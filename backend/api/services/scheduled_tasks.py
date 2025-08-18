""" 
Scheduled Tasks Service
Automatisierte Aufgaben für Follow-Ups und Lead Reaktivierung
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import select, and_

from api.core.database import get_session_context
from api.models.lead import Lead, FollowUp, LeadStatus
from api.models.database import Organization
from api.services.follow_up_service import FollowUpService
from api.services.lead_reactivation_service import LeadReactivationService
from api.services.lead_scoring_service import LeadScoringService
from api.core.subscription import SubscriptionService, SubscriptionPlan, Feature

logger = logging.getLogger(__name__)


class ScheduledTasksService:
    """
    Service für automatisierte Aufgaben:
    - Tägliche Follow-Up Ausführung
    - Wöchentliche Lead Reaktivierung
    - Monatliche Score-Aktualisierung
    - Automatische Report-Generierung
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Europe/Berlin")
        self.follow_up_service = FollowUpService()
        self.reactivation_service = LeadReactivationService()
        self.scoring_service = LeadScoringService()
        
    def start(self):
        """Startet alle geplanten Aufgaben"""
        
        # Tägliche Follow-Ups (9:00 Uhr)
        self.scheduler.add_job(
            self._execute_daily_follow_ups,
            CronTrigger(hour=9, minute=0),
            id="daily_follow_ups",
            name="Tägliche Follow-Up Anrufe",
            replace_existing=True
        )
        
        # Wöchentliche Lead Reaktivierung (Montags 10:00 Uhr)
        self.scheduler.add_job(
            self._execute_weekly_reactivations,
            CronTrigger(day_of_week='mon', hour=10, minute=0),
            id="weekly_reactivations",
            name="Wöchentliche Lead Reaktivierung",
            replace_existing=True
        )
        
        # Tägliche Score-Aktualisierung (2:00 Uhr nachts)
        self.scheduler.add_job(
            self._update_lead_scores,
            CronTrigger(hour=2, minute=0),
            id="daily_score_update",
            name="Tägliche Lead Score Aktualisierung",
            replace_existing=True
        )
        
        # Stündliche Pending Follow-Up Prüfung
        self.scheduler.add_job(
            self._check_pending_follow_ups,
            CronTrigger(minute=0),  # Jede volle Stunde
            id="hourly_follow_up_check",
            name="Stündliche Follow-Up Prüfung",
            replace_existing=True
        )
        
        # Wöchentlicher Performance Report (Freitags 17:00 Uhr)
        self.scheduler.add_job(
            self._generate_weekly_report,
            CronTrigger(day_of_week='fri', hour=17, minute=0),
            id="weekly_report",
            name="Wöchentlicher Performance Report",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduled Tasks Service gestartet")
    
    def stop(self):
        """Stoppt alle geplanten Aufgaben"""
        self.scheduler.shutdown()
        logger.info("Scheduled Tasks Service gestoppt")
    
    async def _execute_daily_follow_ups(self):
        """
        Führt tägliche Follow-Ups aus
        Nur für Organisationen mit AUTO_FOLLOW_UP Feature
        """
        logger.info("Starte tägliche Follow-Up Ausführung")
        
        async with get_session_context() as session:
            # Alle Organisationen mit Enterprise Plan
            stmt = select(Organization).where(
                Organization.subscription_plan.in_([
                    SubscriptionPlan.ENTERPRISE,
                    SubscriptionPlan.CUSTOM
                ])
            )
            result = await session.exec(stmt)
            organizations = result.all()
            
            total_executed = 0
            
            for org in organizations:
                # Prüfe ob Feature verfügbar
                if not SubscriptionService.has_feature(
                    org.subscription_plan,
                    Feature.AUTO_FOLLOW_UP
                ):
                    continue
                
                # Hole alle fälligen Follow-Ups für heute
                today = datetime.now(timezone.utc).date()
                
                stmt = select(FollowUp).join(Lead).where(
                    and_(
                        Lead.organization_id == org.id,
                        FollowUp.status == 'pending',
                        FollowUp.scheduled_date >= today,
                        FollowUp.scheduled_date < today + timedelta(days=1)
                    )
                )
                result = await session.exec(stmt)
                follow_ups = result.all()
                
                for follow_up in follow_ups:
                    try:
                        # Follow-Up ausführen
                        result = await self.follow_up_service.execute_follow_up(
                            follow_up.id
                        )
                        
                        if result.get('success'):
                            total_executed += 1
                            logger.info(
                                f"Follow-Up {follow_up.id} erfolgreich ausgeführt"
                            )
                        
                    except Exception as e:
                        logger.error(
                            f"Fehler bei Follow-Up {follow_up.id}: {str(e)}"
                        )
            
            logger.info(f"Tägliche Follow-Ups abgeschlossen: {total_executed} ausgeführt")
    
    async def _execute_weekly_reactivations(self):
        """
        Führt wöchentliche Lead Reaktivierungen aus
        Nur für Organisationen mit LEAD_REACTIVATION Feature
        """
        logger.info("Starte wöchentliche Lead Reaktivierung")
        
        async with get_session_context() as session:
            # Alle Organisationen mit Enterprise Plan
            stmt = select(Organization).where(
                Organization.subscription_plan.in_([
                    SubscriptionPlan.ENTERPRISE,
                    SubscriptionPlan.CUSTOM
                ])
            )
            result = await session.exec(stmt)
            organizations = result.all()
            
            total_scheduled = 0
            
            for org in organizations:
                # Prüfe ob Feature verfügbar
                if not SubscriptionService.has_feature(
                    org.subscription_plan,
                    Feature.LEAD_REACTIVATION
                ):
                    continue
                
                # Plane Reaktivierungen für diese Organisation
                stats = await self.reactivation_service.bulk_schedule_reactivations(
                    organization_id=org.id,
                    max_leads=20  # Max 20 pro Woche pro Organisation
                )
                
                total_scheduled += stats['total']
                
                logger.info(
                    f"Organisation {org.id}: {stats['total']} Reaktivierungen geplant"
                )
            
            logger.info(
                f"Wöchentliche Reaktivierung abgeschlossen: {total_scheduled} geplant"
            )
    
    async def _update_lead_scores(self):
        """
        Aktualisiert Lead Scores basierend auf Inaktivität
        Reduziert Score für inaktive Leads
        """
        logger.info("Starte tägliche Lead Score Aktualisierung")
        
        async with get_session_context() as session:
            # Leads die länger als 14 Tage inaktiv sind
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=14)
            
            stmt = select(Lead).where(
                and_(
                    Lead.status != LeadStatus.CONVERTED,
                    Lead.status != LeadStatus.LOST,
                    Lead.last_contact_date < cutoff_date,
                    Lead.lead_score > 1  # Nicht unter 1 fallen
                )
            )
            result = await session.exec(stmt)
            leads = result.all()
            
            updated_count = 0
            
            for lead in leads:
                # Score um 1 Punkt reduzieren pro 14 Tage Inaktivität
                days_inactive = (datetime.now(timezone.utc) - lead.last_contact_date).days
                score_reduction = min(days_inactive // 14, 3)  # Max 3 Punkte Reduktion
                
                new_score = max(1, lead.lead_score - score_reduction)
                
                if new_score != lead.lead_score:
                    lead.lead_score = new_score
                    lead.score_reasons.append(
                        f"📉 Score reduziert wegen {days_inactive} Tagen Inaktivität"
                    )
                    
                    # Update Score Category
                    if new_score >= 8:
                        lead.score_category = 'hot'
                    elif new_score >= 5:
                        lead.score_category = 'warm'
                    else:
                        lead.score_category = 'cold'
                    
                    session.add(lead)
                    updated_count += 1
            
            await session.commit()
            
            logger.info(
                f"Lead Score Update abgeschlossen: {updated_count} Leads aktualisiert"
            )
    
    async def _check_pending_follow_ups(self):
        """
        Prüft stündlich auf überfällige Follow-Ups
        Sendet Benachrichtigungen an Nutzer
        """
        logger.info("Prüfe auf überfällige Follow-Ups")
        
        async with get_session_context() as session:
            # Überfällige Follow-Ups (mehr als 1 Stunde)
            overdue_time = datetime.now(timezone.utc) - timedelta(hours=1)
            
            stmt = select(FollowUp).where(
                and_(
                    FollowUp.status == 'pending',
                    FollowUp.scheduled_date < overdue_time,
                    FollowUp.priority.in_(['high', 'urgent'])
                )
            )
            result = await session.exec(stmt)
            overdue = result.all()
            
            if overdue:
                logger.warning(f"Gefunden: {len(overdue)} überfällige Follow-Ups")
                
                # Hier würden Benachrichtigungen versendet werden
                for follow_up in overdue:
                    # TODO: Send notification to user
                    logger.warning(
                        f"Überfälliges Follow-Up {follow_up.id} "
                        f"(geplant: {follow_up.scheduled_date})"
                    )
    
    async def _generate_weekly_report(self):
        """
        Generiert wöchentlichen Performance Report
        """
        logger.info("Generiere wöchentlichen Performance Report")
        
        async with get_session_context() as session:
            # Alle Organisationen
            stmt = select(Organization)
            result = await session.exec(stmt)
            organizations = result.all()
            
            for org in organizations:
                try:
                    # Sammle Metriken der letzten Woche
                    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
                    
                    # Neue Leads diese Woche
                    stmt = select(Lead).where(
                        and_(
                            Lead.organization_id == org.id,
                            Lead.created_at >= week_ago
                        )
                    )
                    result = await session.exec(stmt)
                    new_leads = len(result.all())
                    
                    # Konvertierte Leads diese Woche
                    stmt = select(Lead).where(
                        and_(
                            Lead.organization_id == org.id,
                            Lead.status == LeadStatus.CONVERTED,
                            Lead.conversion_date >= week_ago
                        )
                    )
                    result = await session.exec(stmt)
                    converted_leads = len(result.all())
                    
                    # Follow-Up Erfolgsrate
                    follow_up_metrics = await self.follow_up_service.get_follow_up_metrics(
                        organization_id=org.id,
                        days=7
                    )
                    
                    # Reaktivierungs-Erfolg
                    reactivation_metrics = await self.reactivation_service.get_reactivation_metrics(
                        organization_id=org.id,
                        days=7
                    )
                    
                    report = {
                        'organization_id': org.id,
                        'organization_name': org.name,
                        'week': week_ago.strftime('%Y-%W'),
                        'new_leads': new_leads,
                        'converted_leads': converted_leads,
                        'follow_up_success_rate': follow_up_metrics.get('success_rate', 0),
                        'reactivation_success_rate': reactivation_metrics.get('success_rate', 0),
                        'revenue_generated': follow_up_metrics.get('revenue_generated', 0) + 
                                           reactivation_metrics.get('revenue_reactivated', 0),
                        'generated_at': datetime.now(timezone.utc)
                    }
                    
                    # TODO: Report speichern oder per E-Mail versenden
                    logger.info(f"Report für {org.name}: {report}")
                    
                except Exception as e:
                    logger.error(f"Fehler bei Report für Organisation {org.id}: {str(e)}")
            
            logger.info("Wöchentliche Reports generiert")
    
    def get_job_status(self) -> List[Dict]:
        """
        Gibt Status aller geplanten Jobs zurück
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'pending': job.pending
            })
        return jobs
    
    async def trigger_job(self, job_id: str) -> bool:
        """
        Triggert einen Job manuell
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.func()
                logger.info(f"Job {job_id} manuell getriggert")
                return True
            else:
                logger.warning(f"Job {job_id} nicht gefunden")
                return False
        except Exception as e:
            logger.error(f"Fehler beim Triggern von Job {job_id}: {str(e)}")
            return False


# Globale Instanz
scheduled_tasks = ScheduledTasksService()


def start_scheduled_tasks():
    """Startet den Scheduled Tasks Service"""
    scheduled_tasks.start()


def stop_scheduled_tasks():
    """Stoppt den Scheduled Tasks Service"""
    scheduled_tasks.stop()
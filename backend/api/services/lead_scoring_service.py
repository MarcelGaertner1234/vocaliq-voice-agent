"""
Lead Scoring Service
Automatisches Scoring von Leads basierend auf Verhalten und Interaktionen
"""
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta, timezone
import re
from sqlmodel import select
from api.core.database import get_session_context
from api.models.lead import Lead, LeadActivity, LeadScore
from api.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class LeadScoringService:
    """
    Service für automatisches Lead Scoring nach dem Video-Konzept:
    - 1-10 Punkte Scoring
    - Automatische Kategorisierung (Hot/Warm/Cold)
    - Scoring basierend auf Gesprächsdauer, Keywords, Sentiment
    """
    
    def __init__(self):
        self.openai_service = OpenAIService()
        
        # Positive Keywords die auf Kaufinteresse hindeuten
        self.positive_keywords = [
            'kaufen', 'interessiert', 'budget', 'termin', 'angebot',
            'preis', 'kosten', 'wann', 'sofort', 'dringend',
            'buchen', 'reservieren', 'vereinbaren'
        ]
        
        # Negative Keywords die auf geringes Interesse hindeuten
        self.negative_keywords = [
            'kein interesse', 'zu teuer', 'später', 'vielleicht',
            'überlegen', 'nicht sicher', 'keine zeit', 'kein budget'
        ]
        
        # Scoring Weights
        self.scoring_weights = {
            'call_duration': 3,      # Max 3 Punkte für Gesprächsdauer
            'sentiment': 2,           # Max 2 Punkte für positives Sentiment
            'keywords': 2,            # Max 2 Punkte für Keywords
            'engagement': 2,          # Max 2 Punkte für Engagement
            'appointment': 10         # Sofort 10 Punkte bei Terminvereinbarung
        }
    
    async def calculate_score(
        self,
        call_data: Dict,
        lead: Optional[Lead] = None
    ) -> Tuple[int, List[str]]:
        """
        Berechnet den Lead Score basierend auf Anrufdaten
        
        Args:
            call_data: Dictionary mit Anrufinformationen
            lead: Optional existing Lead object
            
        Returns:
            Tuple of (score, reasons)
        """
        score = 5  # Basis-Score
        reasons = []
        
        try:
            # 1. Gesprächsdauer bewerten
            duration_score, duration_reason = self._score_duration(
                call_data.get('duration', 0)
            )
            score += duration_score
            if duration_reason:
                reasons.append(duration_reason)
            
            # 2. Sentiment analysieren
            if call_data.get('transcript'):
                sentiment_score, sentiment_reason = await self._score_sentiment(
                    call_data.get('transcript', '')
                )
                score += sentiment_score
                if sentiment_reason:
                    reasons.append(sentiment_reason)
                
                # 3. Keywords analysieren
                keyword_score, keyword_reason = self._score_keywords(
                    call_data.get('transcript', '')
                )
                score += keyword_score
                if keyword_reason:
                    reasons.append(keyword_reason)
            
            # 4. Engagement bewerten (Anzahl der Interaktionen)
            if lead:
                engagement_score, engagement_reason = await self._score_engagement(lead)
                score += engagement_score
                if engagement_reason:
                    reasons.append(engagement_reason)
            
            # 5. Termin vereinbart? (Override auf 10)
            if call_data.get('appointment_scheduled'):
                score = 10
                reasons = ["✅ Termin vereinbart!"]
            
            # 6. Explizite Absage? (Override auf niedrigen Score)
            if call_data.get('explicit_rejection'):
                score = min(score, 2)
                reasons.append("❌ Explizite Absage")
            
            # Score begrenzen (1-10)
            final_score = max(1, min(10, score))
            
            logger.info(f"Lead Score berechnet: {final_score} - Gründe: {reasons}")
            
            return final_score, reasons
            
        except Exception as e:
            logger.error(f"Fehler bei Score-Berechnung: {str(e)}")
            return 5, ["Fehler bei Berechnung"]
    
    def _score_duration(self, duration_seconds: int) -> Tuple[int, str]:
        """Bewertet die Gesprächsdauer"""
        if duration_seconds < 30:
            return -2, "Sehr kurzes Gespräch (<30s)"
        elif duration_seconds < 60:
            return -1, "Kurzes Gespräch (<1min)"
        elif duration_seconds < 180:
            return 0, ""
        elif duration_seconds < 300:
            return 1, "Gutes Gespräch (3-5min)"
        elif duration_seconds < 600:
            return 2, "Langes Gespräch (5-10min)"
        else:
            return 3, "Sehr langes Gespräch (>10min)"
    
    async def _score_sentiment(self, transcript: str) -> Tuple[int, str]:
        """Analysiert das Sentiment des Gesprächs mit GPT"""
        try:
            prompt = f"""
            Analysiere das Sentiment dieses Gesprächs auf einer Skala:
            - Sehr positiv: Der Kunde ist begeistert und will kaufen
            - Positiv: Der Kunde zeigt Interesse
            - Neutral: Der Kunde ist unentschlossen
            - Negativ: Der Kunde zeigt wenig Interesse
            - Sehr negativ: Der Kunde lehnt ab
            
            Gespräch: {transcript[:1000]}
            
            Antworte NUR mit: sehr_positiv, positiv, neutral, negativ, oder sehr_negativ
            """
            
            response = await self.openai_service.generate_response(
                prompt,
                max_tokens=10,
                temperature=0
            )
            
            sentiment = response.strip().lower()
            
            if 'sehr_positiv' in sentiment:
                return 2, "😊 Sehr positives Sentiment"
            elif 'positiv' in sentiment:
                return 1, "🙂 Positives Sentiment"
            elif 'negativ' in sentiment and 'sehr' in sentiment:
                return -2, "😞 Sehr negatives Sentiment"
            elif 'negativ' in sentiment:
                return -1, "😐 Negatives Sentiment"
            else:
                return 0, ""
                
        except Exception as e:
            logger.error(f"Sentiment-Analyse fehlgeschlagen: {str(e)}")
            return 0, ""
    
    def _score_keywords(self, transcript: str) -> Tuple[int, str]:
        """Bewertet basierend auf Keywords im Gespräch"""
        transcript_lower = transcript.lower()
        
        # Positive Keywords zählen
        positive_count = sum(
            1 for keyword in self.positive_keywords
            if keyword in transcript_lower
        )
        
        # Negative Keywords zählen
        negative_count = sum(
            1 for keyword in self.negative_keywords
            if keyword in transcript_lower
        )
        
        # Score berechnen
        keyword_score = positive_count - negative_count
        
        if keyword_score >= 3:
            return 2, "🎯 Viele Kaufsignale erkannt"
        elif keyword_score >= 1:
            return 1, "✓ Kaufsignale erkannt"
        elif keyword_score <= -2:
            return -2, "⚠️ Negative Signale"
        elif keyword_score < 0:
            return -1, "Wenig Interesse erkannt"
        else:
            return 0, ""
    
    async def _score_engagement(self, lead: Lead) -> Tuple[int, str]:
        """Bewertet das Engagement basierend auf Historie"""
        async with get_session_context() as session:
            # Anzahl der Interaktionen in den letzten 30 Tagen
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            
            stmt = select(LeadActivity).where(
                LeadActivity.lead_id == lead.id,
                LeadActivity.created_at >= thirty_days_ago
            )
            result = await session.exec(stmt)
            activities = result.all()
            
            activity_count = len(activities)
            
            if activity_count >= 5:
                return 2, "🔥 Sehr aktiver Lead"
            elif activity_count >= 3:
                return 1, "📈 Aktiver Lead"
            elif activity_count == 0:
                return -1, "💤 Inaktiver Lead"
            else:
                return 0, ""
    
    async def update_lead_score(
        self,
        lead_id: int,
        score: int,
        reasons: List[str]
    ) -> Lead:
        """Aktualisiert den Score eines Leads in der Datenbank"""
        async with get_session_context() as session:
            # Lead laden
            stmt = select(Lead).where(Lead.id == lead_id)
            result = await session.exec(stmt)
            lead = result.one()
            
            # Score aktualisieren
            lead.lead_score = score
            lead.score_reasons = reasons
            lead.score_updated_at = datetime.now(timezone.utc)
            lead.update_score_category()
            
            # Activity Log erstellen
            activity = LeadActivity(
                lead_id=lead_id,
                activity_type='score_change',
                description=f'Lead Score aktualisiert auf {score}',
                activity_metadata={
                    'old_score': lead.lead_score if hasattr(lead, 'lead_score') else None,
                    'new_score': score,
                    'reasons': reasons
                }
            )
            session.add(activity)
            
            # Speichern
            session.add(lead)
            await session.commit()
            await session.refresh(lead)
            
            logger.info(f"Lead {lead_id} Score aktualisiert: {score} ({lead.score_category})")
            
            return lead
    
    async def get_leads_by_score(
        self,
        organization_id: int,
        score_category: Optional[LeadScore] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None
    ) -> List[Lead]:
        """Holt Leads basierend auf Score-Kriterien"""
        async with get_session_context() as session:
            stmt = select(Lead).where(Lead.organization_id == organization_id)
            
            if score_category:
                stmt = stmt.where(Lead.score_category == score_category)
            
            if min_score:
                stmt = stmt.where(Lead.lead_score >= min_score)
            
            if max_score:
                stmt = stmt.where(Lead.lead_score <= max_score)
            
            # Nach Score sortieren (höchste zuerst)
            stmt = stmt.order_by(Lead.lead_score.desc())
            
            result = await session.exec(stmt)
            return result.all()
    
    async def recalculate_all_scores(self, organization_id: int):
        """Neuberechnung aller Lead Scores einer Organisation"""
        async with get_session_context() as session:
            stmt = select(Lead).where(Lead.organization_id == organization_id)
            result = await session.exec(stmt)
            leads = result.all()
            
            updated_count = 0
            
            for lead in leads:
                try:
                    # Hole letzte Call-Daten für diesen Lead
                    # (Hier würde man die CallLog Tabelle abfragen)
                    
                    # Für Demo: Basis-Neuberechnung
                    days_since_contact = lead.calculate_days_since_contact()
                    
                    if days_since_contact:
                        if days_since_contact > 30:
                            # Alter Lead - Score reduzieren
                            new_score = max(1, lead.lead_score - 1)
                            await self.update_lead_score(
                                lead.id,
                                new_score,
                                ["Score reduziert wegen Inaktivität"]
                            )
                            updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Fehler bei Score-Neuberechnung für Lead {lead.id}: {str(e)}")
            
            logger.info(f"{updated_count} Lead Scores aktualisiert für Organisation {organization_id}")
            
            return updated_count
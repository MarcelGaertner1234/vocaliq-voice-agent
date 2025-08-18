"""
Lead Enrichment Service
Automatische Anreicherung von Lead-Daten aus externen Quellen
"""
import logging
import httpx
import re
from typing import Dict, Optional, Any
from datetime import datetime, timezone
from sqlmodel import select
from api.core.database import get_session_context
from api.models.lead import Lead, LeadActivity
from api.core.config import get_settings

logger = logging.getLogger(__name__)


class LeadEnrichmentService:
    """
    Service für automatisches Lead Enrichment:
    - LinkedIn Profil-Daten
    - Firmendaten (Größe, Branche)
    - Google Places / Maps Daten
    - Social Media Profile
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def enrich_lead(
        self,
        lead_id: int,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hauptfunktion für Lead Enrichment
        
        Args:
            lead_id: Lead ID
            phone: Telefonnummer
            email: E-Mail Adresse
            company_name: Firmenname
            
        Returns:
            Dictionary mit angereicherten Daten
        """
        enrichment_data = {}
        
        try:
            # 1. LinkedIn Enrichment (wenn E-Mail vorhanden)
            if email:
                linkedin_data = await self._enrich_from_linkedin(email)
                if linkedin_data:
                    enrichment_data['linkedin'] = linkedin_data
            
            # 2. Firmendaten Enrichment
            if company_name:
                company_data = await self._enrich_company_data(company_name)
                if company_data:
                    enrichment_data['company'] = company_data
            
            # 3. Google Places Enrichment (basierend auf Telefonnummer)
            if phone:
                places_data = await self._enrich_from_google_places(phone)
                if places_data:
                    enrichment_data['google_places'] = places_data
            
            # 4. Social Media Check
            if email or company_name:
                social_data = await self._check_social_media(email, company_name)
                if social_data:
                    enrichment_data['social_media'] = social_data
            
            # 5. Lead in Datenbank aktualisieren
            if enrichment_data:
                await self._update_lead_enrichment(lead_id, enrichment_data)
            
            logger.info(f"Lead {lead_id} erfolgreich angereichert mit {len(enrichment_data)} Datenquellen")
            
            return enrichment_data
            
        except Exception as e:
            logger.error(f"Fehler beim Lead Enrichment für Lead {lead_id}: {str(e)}")
            return {}
        
    async def _enrich_from_linkedin(self, email: str) -> Optional[Dict]:
        """
        LinkedIn Profil-Daten abrufen
        
        Hinweis: In Produktion würde man hier eine echte LinkedIn API
        oder einen Service wie Clearbit, Hunter.io verwenden
        """
        try:
            # Beispiel-Implementation mit Platzhalter
            # In Produktion: LinkedIn Sales Navigator API oder ähnliches
            
            linkedin_data = {
                'profile_found': False,
                'profile_url': None,
                'position': None,
                'company': None,
                'connections': None,
                'skills': []
            }
            
            # Simuliere API-Call (in Produktion ersetzen)
            # response = await self.http_client.get(
            #     f"https://api.linkedin.com/v2/people/(email:{email})",
            #     headers={"Authorization": f"Bearer {self.settings.LINKEDIN_API_KEY}"}
            # )
            
            # Für Demo: Basis-Pattern-Matching
            domain = email.split('@')[1] if '@' in email else None
            if domain:
                linkedin_data['company'] = domain.replace('.de', '').replace('.com', '').title()
                linkedin_data['profile_found'] = True
            
            return linkedin_data
            
        except Exception as e:
            logger.error(f"LinkedIn Enrichment fehlgeschlagen: {str(e)}")
            return None
    
    async def _enrich_company_data(self, company_name: str) -> Optional[Dict]:
        """
        Firmendaten aus öffentlichen Quellen abrufen
        
        In Deutschland: Bundesanzeiger, Northdata, etc.
        International: Crunchbase, Clearbit, etc.
        """
        try:
            company_data = {
                'name': company_name,
                'size': None,
                'industry': None,
                'founded': None,
                'revenue': None,
                'employees': None,
                'website': None,
                'address': None
            }
            
            # Beispiel: Northdata API (Deutsche Firmendaten)
            # In Produktion würde man hier echte APIs verwenden
            
            # Simuliere Firmengröße basierend auf Namen-Pattern
            if any(word in company_name.lower() for word in ['gmbh', 'ag', 'kg']):
                company_data['legal_form'] = 'GmbH' if 'gmbh' in company_name.lower() else 'AG'
                
            # Branchen-Erkennung (vereinfacht)
            industry_keywords = {
                'hotel': 'Hospitality',
                'restaurant': 'Gastronomy',
                'software': 'Technology',
                'beratung': 'Consulting',
                'handel': 'Retail',
                'bau': 'Construction'
            }
            
            for keyword, industry in industry_keywords.items():
                if keyword in company_name.lower():
                    company_data['industry'] = industry
                    break
            
            # Simuliere Mitarbeiterzahl
            if company_data.get('legal_form') == 'AG':
                company_data['employees'] = '500+'
                company_data['size'] = 'large'
            elif company_data.get('legal_form') == 'GmbH':
                company_data['employees'] = '50-200'
                company_data['size'] = 'medium'
            else:
                company_data['employees'] = '1-50'
                company_data['size'] = 'small'
            
            return company_data
            
        except Exception as e:
            logger.error(f"Company Enrichment fehlgeschlagen: {str(e)}")
            return None
    
    async def _enrich_from_google_places(self, phone: str) -> Optional[Dict]:
        """
        Google Places API für lokale Geschäftsdaten
        """
        try:
            places_data = {
                'found': False,
                'name': None,
                'address': None,
                'rating': None,
                'reviews_count': None,
                'opening_hours': None,
                'website': None,
                'categories': []
            }
            
            # In Produktion: Google Places API
            # api_key = self.settings.GOOGLE_PLACES_API_KEY
            # response = await self.http_client.get(
            #     "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
            #     params={
            #         'input': phone,
            #         'inputtype': 'phonenumber',
            #         'key': api_key
            #     }
            # )
            
            # Für Demo: Basis-Daten
            if phone.startswith('+49'):
                places_data['found'] = True
                places_data['country'] = 'Germany'
                
                # Vorwahl-basierte Stadt-Erkennung
                area_codes = {
                    '89': 'München',
                    '30': 'Berlin',
                    '40': 'Hamburg',
                    '69': 'Frankfurt',
                    '221': 'Köln'
                }
                
                for code, city in area_codes.items():
                    if phone.startswith(f'+49{code}') or phone.startswith(f'0{code}'):
                        places_data['city'] = city
                        break
            
            return places_data
            
        except Exception as e:
            logger.error(f"Google Places Enrichment fehlgeschlagen: {str(e)}")
            return None
    
    async def _check_social_media(
        self,
        email: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Social Media Profile finden (Facebook, Instagram, Twitter/X)
        """
        try:
            social_data = {
                'facebook': None,
                'instagram': None,
                'twitter': None,
                'xing': None,
                'website': None
            }
            
            # Website aus E-Mail Domain extrahieren
            if email and '@' in email:
                domain = email.split('@')[1]
                if not any(provider in domain for provider in ['gmail', 'yahoo', 'outlook', 'gmx', 'web']):
                    social_data['website'] = f"https://{domain}"
            
            # Social Media Handles generieren (vereinfacht)
            if company_name:
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
                social_data['facebook'] = f"facebook.com/{clean_name}"
                social_data['instagram'] = f"@{clean_name}"
                
                # Deutsche Unternehmen oft auf XING
                social_data['xing'] = f"xing.com/companies/{clean_name}"
            
            return social_data
            
        except Exception as e:
            logger.error(f"Social Media Check fehlgeschlagen: {str(e)}")
            return None
    
    async def _update_lead_enrichment(
        self,
        lead_id: int,
        enrichment_data: Dict[str, Any]
    ) -> Lead:
        """
        Aktualisiert Lead mit angereicherten Daten
        """
        async with get_session_context() as session:
            # Lead laden
            stmt = select(Lead).where(Lead.id == lead_id)
            result = await session.exec(stmt)
            lead = result.one()
            
            # Daten extrahieren und Lead aktualisieren
            if 'linkedin' in enrichment_data:
                linkedin = enrichment_data['linkedin']
                if linkedin.get('profile_url'):
                    lead.linkedin_url = linkedin['profile_url']
                if linkedin.get('position'):
                    lead.position = linkedin['position']
            
            if 'company' in enrichment_data:
                company = enrichment_data['company']
                if company.get('size'):
                    lead.company_size = company['size']
                if company.get('industry'):
                    lead.industry = company['industry']
                if company.get('website'):
                    lead.website = company['website']
            
            if 'google_places' in enrichment_data:
                places = enrichment_data['google_places']
                if places.get('city'):
                    lead.enrichment_data['city'] = places['city']
            
            if 'social_media' in enrichment_data:
                social = enrichment_data['social_media']
                if social.get('website') and not lead.website:
                    lead.website = social['website']
                lead.enrichment_data['social_media'] = social
            
            # Zeitstempel aktualisieren
            lead.enrichment_updated_at = datetime.now(timezone.utc)
            lead.enrichment_data.update(enrichment_data)
            
            # Activity Log
            activity = LeadActivity(
                lead_id=lead_id,
                activity_type='enrichment',
                description='Lead-Daten automatisch angereichert',
                metadata={
                    'sources': list(enrichment_data.keys()),
                    'fields_updated': len(enrichment_data)
                }
            )
            session.add(activity)
            
            # Speichern
            session.add(lead)
            await session.commit()
            await session.refresh(lead)
            
            logger.info(f"Lead {lead_id} erfolgreich mit Enrichment-Daten aktualisiert")
            
            return lead
    
    async def bulk_enrich_leads(
        self,
        organization_id: int,
        limit: int = 10
    ) -> int:
        """
        Bulk-Enrichment für nicht angereicherte Leads
        """
        async with get_session_context() as session:
            # Leads ohne Enrichment finden
            stmt = select(Lead).where(
                Lead.organization_id == organization_id,
                Lead.enrichment_updated_at.is_(None)
            ).limit(limit)
            
            result = await session.exec(stmt)
            leads = result.all()
            
            enriched_count = 0
            
            for lead in leads:
                try:
                    await self.enrich_lead(
                        lead_id=lead.id,
                        phone=lead.phone,
                        email=lead.email,
                        company_name=lead.company_name
                    )
                    enriched_count += 1
                    
                except Exception as e:
                    logger.error(f"Bulk Enrichment fehlgeschlagen für Lead {lead.id}: {str(e)}")
            
            logger.info(f"{enriched_count} Leads erfolgreich angereichert für Organisation {organization_id}")
            
            return enriched_count
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
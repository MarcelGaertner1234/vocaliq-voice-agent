"""
Enhanced Voice Pipeline Service
Integriert Lead Scoring, Routing und Follow-Up in die Voice Pipeline
"""
import logging
import asyncio
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timezone
from sqlmodel import select
from api.core.database import get_session_context
from api.models.lead import Lead, LeadActivity, LeadStatus, LeadSource
from api.models.database import CallLog, CallStatus, CallDirection
from api.services.voice_pipeline import VoicePipelineService
from api.services.lead_scoring_service import LeadScoringService
from api.services.lead_enrichment_service import LeadEnrichmentService
from api.services.follow_up_service import FollowUpService
from api.services.openai_service import OpenAIService
from api.config.agent_scripts import (
    ROUTING_KEYWORDS, 
    AGENT_SCRIPTS, 
    INTENT_PATTERNS,
    generate_personalized_script
)

logger = logging.getLogger(__name__)


class EnhancedVoicePipeline(VoicePipelineService):
    """
    Erweiterte Voice Pipeline mit:
    - Intelligentes Routing (Hotel Use-Case)
    - Automatisches Lead Scoring
    - Follow-Up Planung
    - Intent-Erkennung
    - Kunde hat IMMER die Wahl (KI oder Mensch)
    """
    
    def __init__(self):
        super().__init__()
        self.scoring_service = LeadScoringService()
        self.enrichment_service = LeadEnrichmentService()
        self.follow_up_service = FollowUpService()
        self.openai_service = OpenAIService()
        
    async def handle_incoming_call(
        self,
        call_sid: str,
        from_number: str,
        to_number: str,
        organization_id: int
    ) -> Dict:
        """
        Haupteinstiegspunkt für eingehende Anrufe
        """
        logger.info(f"Eingehender Anruf: {from_number} → {to_number}")
        
        # Session initialisieren
        session_id = f"call_{call_sid}"
        await self.initialize_session(session_id, call_sid, from_number)
        
        # Lead suchen oder erstellen
        lead = await self._get_or_create_lead(
            phone=from_number,
            organization_id=organization_id
        )
        
        # Call Log erstellen
        call_log = await self._create_call_log(
            call_sid=call_sid,
            lead_id=lead.id,
            organization_id=organization_id,
            from_number=from_number,
            to_number=to_number
        )
        
        # Initiale Begrüßung (Hotel-Rezeptionist Style)
        greeting_context = {
            'hotel_name': 'Hotel Alpenblick',  # Aus Organisation laden
            'agent_name': 'Ihr digitaler Assistent'
        }
        greeting = generate_personalized_script(
            'hotel_receptionist.initial_greeting',
            greeting_context
        )
        
        # Begrüßung abspielen
        await self._send_tts_response(session_id, greeting)
        
        # Conversation Loop starten
        conversation_result = await self._handle_conversation(
            session_id=session_id,
            lead=lead,
            call_log=call_log
        )
        
        # Nach Anruf: Lead Scoring und Follow-Up
        await self._post_call_processing(
            lead=lead,
            call_log=call_log,
            conversation_result=conversation_result
        )
        
        return {
            'success': True,
            'call_sid': call_sid,
            'lead_id': lead.id,
            'lead_score': lead.lead_score,
            'routing_result': conversation_result.get('routing_result')
        }
    
    async def _handle_conversation(
        self,
        session_id: str,
        lead: Lead,
        call_log: CallLog
    ) -> Dict:
        """
        Hauptkonversationsschleife mit intelligentem Routing
        """
        conversation_result = {
            'transcript': [],
            'routing_result': None,
            'appointment_scheduled': False,
            'duration': 0
        }
        
        session = self.sessions.get(session_id)
        if not session:
            return conversation_result
        
        start_time = datetime.now(timezone.utc)
        
        while session.get('active', True):
            try:
                # Auf Nutzer-Input warten
                user_input = await self._wait_for_user_input(session_id)
                
                if not user_input:
                    continue
                
                conversation_result['transcript'].append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Intent erkennen
                intent, confidence = await self._detect_intent(user_input)
                logger.info(f"Intent erkannt: {intent} (Confidence: {confidence})")
                
                # Routing-Entscheidung
                routing_decision = await self._make_routing_decision(
                    user_input=user_input,
                    intent=intent,
                    lead=lead
                )
                
                if routing_decision['should_transfer']:
                    # Kunde möchte zur Rezeption/Abteilung
                    transfer_message = routing_decision['transfer_message']
                    await self._send_tts_response(session_id, transfer_message)
                    
                    # Transfer durchführen
                    conversation_result['routing_result'] = {
                        'transferred_to': routing_decision['department'],
                        'reason': routing_decision['reason']
                    }
                    
                    # Session beenden
                    session['active'] = False
                    
                elif routing_decision['offer_choice']:
                    # Kunde die Wahl geben: KI oder Mensch
                    choice_context = {
                        'intent': intent,
                        'department': routing_decision['suggested_department']
                    }
                    choice_message = generate_personalized_script(
                        'hotel_receptionist.routing_decision',
                        choice_context
                    )
                    
                    await self._send_tts_response(session_id, choice_message)
                    
                    # Auf Antwort warten
                    choice_response = await self._wait_for_user_input(session_id)
                    
                    if 'verbind' in choice_response.lower() or 'rezeption' in choice_response.lower():
                        # Transfer gewünscht
                        transfer_message = ROUTING_KEYWORDS[routing_decision['suggested_department']]['transfer_message']
                        await self._send_tts_response(session_id, transfer_message)
                        conversation_result['routing_result'] = {'transferred_to': routing_decision['suggested_department']}
                        session['active'] = False
                    else:
                        # KI soll helfen
                        await self._handle_with_ai(
                            session_id=session_id,
                            intent=intent,
                            user_input=user_input,
                            lead=lead,
                            conversation_result=conversation_result
                        )
                else:
                    # Direkt mit KI bearbeiten
                    await self._handle_with_ai(
                        session_id=session_id,
                        intent=intent,
                        user_input=user_input,
                        lead=lead,
                        conversation_result=conversation_result
                    )
                
            except Exception as e:
                logger.error(f"Fehler in Conversation Loop: {str(e)}")
                break
        
        # Gesprächsdauer berechnen
        end_time = datetime.now(timezone.utc)
        conversation_result['duration'] = int((end_time - start_time).total_seconds())
        
        return conversation_result
    
    async def _detect_intent(self, user_input: str) -> Tuple[str, float]:
        """
        Erkennt die Absicht des Anrufers mittels GPT-4
        """
        prompt = f"""
        Analysiere die Absicht dieses Anrufers und kategorisiere sie:
        
        Kategorien:
        - booking (Zimmer buchen, Reservierung)
        - support (Problem, Hilfe benötigt)
        - sales (Kaufinteresse, Preisanfrage)
        - information (Allgemeine Fragen)
        - complaint (Beschwerde)
        - appointment (Termin vereinbaren)
        - hr (Bewerbung, Job)
        - delivery (Lieferung, Bestellung)
        - emergency (Notfall)
        - other (Sonstiges)
        
        Anrufer sagt: "{user_input}"
        
        Antworte im Format: intent|confidence
        Beispiel: booking|0.95
        """
        
        try:
            response = await self.openai_service.generate_response(
                prompt,
                max_tokens=20,
                temperature=0
            )
            
            parts = response.strip().split('|')
            if len(parts) == 2:
                return parts[0], float(parts[1])
            
        except Exception as e:
            logger.error(f"Intent-Erkennung fehlgeschlagen: {str(e)}")
        
        return 'other', 0.5
    
    async def _make_routing_decision(
        self,
        user_input: str,
        intent: str,
        lead: Lead
    ) -> Dict:
        """
        Entscheidet ob und wohin geroutet werden soll
        """
        user_input_lower = user_input.lower()
        
        # Notfall-Check (SOFORT weiterleiten)
        for keyword in ROUTING_KEYWORDS['emergency']['keywords']:
            if keyword in user_input_lower:
                return {
                    'should_transfer': True,
                    'department': 'emergency',
                    'transfer_message': ROUTING_KEYWORDS['emergency']['transfer_message'],
                    'reason': 'Notfall erkannt',
                    'offer_choice': False
                }
        
        # Department-spezifische Keywords prüfen
        for dept, config in ROUTING_KEYWORDS.items():
            if dept == 'emergency':
                continue
                
            for keyword in config['keywords']:
                if keyword in user_input_lower:
                    # Bei normalen Anfragen: Wahl anbieten
                    return {
                        'should_transfer': False,
                        'offer_choice': True,
                        'suggested_department': dept,
                        'department': config['department'],
                        'reason': f'Keyword "{keyword}" erkannt'
                    }
        
        # Intent-basierte Entscheidung
        if intent == 'booking':
            return {
                'should_transfer': False,
                'offer_choice': True,
                'suggested_department': 'reception',
                'department': 'reception',
                'reason': 'Buchungsanfrage'
            }
        
        # Standard: KI kann helfen
        return {
            'should_transfer': False,
            'offer_choice': False,
            'department': None,
            'reason': 'KI kann bearbeiten'
        }
    
    async def _handle_with_ai(
        self,
        session_id: str,
        intent: str,
        user_input: str,
        lead: Lead,
        conversation_result: Dict
    ):
        """
        KI bearbeitet die Anfrage
        """
        # Kontext für GPT-4 aufbauen
        context = {
            'intent': intent,
            'lead_name': f"{lead.first_name} {lead.last_name}".strip(),
            'lead_score': lead.lead_score,
            'conversation_history': conversation_result['transcript'][-5:]  # Letzte 5 Nachrichten
        }
        
        # GPT-4 Response generieren
        ai_response = await self._generate_ai_response(user_input, context)
        
        # Response speichern
        conversation_result['transcript'].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        # TTS und abspielen
        await self._send_tts_response(session_id, ai_response)
        
        # Check für Termin-Vereinbarung
        if 'termin' in ai_response.lower() and 'vereinbart' in ai_response.lower():
            conversation_result['appointment_scheduled'] = True
    
    async def _post_call_processing(
        self,
        lead: Lead,
        call_log: CallLog,
        conversation_result: Dict
    ):
        """
        Nach-Anruf-Verarbeitung: Scoring, Follow-Up, Enrichment
        """
        try:
            # 1. Lead Scoring
            call_data = {
                'duration': conversation_result.get('duration', 0),
                'transcript': ' '.join([
                    msg['content'] 
                    for msg in conversation_result.get('transcript', [])
                ]),
                'appointment_scheduled': conversation_result.get('appointment_scheduled', False)
            }
            
            new_score, score_reasons = await self.scoring_service.calculate_score(
                call_data, lead
            )
            
            await self.scoring_service.update_lead_score(
                lead.id, new_score, score_reasons
            )
            
            logger.info(f"Lead {lead.id} Score aktualisiert: {new_score}")
            
            # 2. Follow-Up planen (wenn Score >= 5)
            if new_score >= 5 and not conversation_result.get('appointment_scheduled'):
                follow_up_type = 'after_demo' if 'demo' in str(conversation_result) else 'after_offer'
                await self.follow_up_service.schedule_follow_ups(
                    lead_id=lead.id,
                    follow_up_type=follow_up_type
                )
                logger.info(f"Follow-Ups geplant für Lead {lead.id}")
            
            # 3. Lead Enrichment (im Hintergrund)
            asyncio.create_task(
                self.enrichment_service.enrich_lead(
                    lead_id=lead.id,
                    phone=lead.phone,
                    email=lead.email,
                    company_name=lead.company_name
                )
            )
            
            # 4. Call Log aktualisieren
            async with get_session_context() as session:
                call_log.duration = conversation_result.get('duration', 0)
                call_log.status = CallStatus.COMPLETED
                call_log.transcript = conversation_result.get('transcript', [])
                call_log.lead_score_after = new_score
                
                session.add(call_log)
                await session.commit()
            
        except Exception as e:
            logger.error(f"Post-Call Processing fehlgeschlagen: {str(e)}")
    
    async def _get_or_create_lead(
        self,
        phone: str,
        organization_id: int
    ) -> Lead:
        """
        Findet oder erstellt einen Lead basierend auf Telefonnummer
        """
        async with get_session_context() as session:
            # Existierenden Lead suchen
            stmt = select(Lead).where(
                Lead.phone == phone,
                Lead.organization_id == organization_id
            )
            result = await session.exec(stmt)
            lead = result.first()
            
            if not lead:
                # Neuen Lead erstellen
                lead = Lead(
                    organization_id=organization_id,
                    phone=phone,
                    source=LeadSource.INBOUND,
                    status=LeadStatus.NEW,
                    lead_score=5,  # Start-Score
                    first_contact_date=datetime.now(timezone.utc)
                )
                session.add(lead)
                await session.commit()
                await session.refresh(lead)
                
                logger.info(f"Neuer Lead erstellt: {lead.id}")
            else:
                # Letzten Kontakt aktualisieren
                lead.last_contact_date = datetime.now(timezone.utc)
                session.add(lead)
                await session.commit()
            
            return lead
    
    async def _create_call_log(
        self,
        call_sid: str,
        lead_id: int,
        organization_id: int,
        from_number: str,
        to_number: str
    ) -> CallLog:
        """
        Erstellt einen Call Log Eintrag
        """
        async with get_session_context() as session:
            call_log = CallLog(
                organization_id=organization_id,
                lead_id=lead_id,
                twilio_call_sid=call_sid,
                from_number=from_number,
                to_number=to_number,
                direction=CallDirection.INBOUND,
                status=CallStatus.IN_PROGRESS,
                started_at=datetime.now(timezone.utc)
            )
            
            session.add(call_log)
            await session.commit()
            await session.refresh(call_log)
            
            return call_log
    
    async def _wait_for_user_input(self, session_id: str, timeout: int = 30) -> Optional[str]:
        """
        Wartet auf Nutzer-Input (Mock für Demo)
        In Produktion: Warte auf Twilio WebSocket Audio → Whisper STT
        """
        # Hier würde normalerweise auf Audio-Input gewartet
        # und mit Whisper transkribiert werden
        await asyncio.sleep(1)  # Simulate processing
        return None  # Placeholder
    
    async def _send_tts_response(self, session_id: str, text: str):
        """
        Sendet TTS Response an Anrufer
        In Produktion: Text → ElevenLabs TTS → Twilio WebSocket
        """
        logger.info(f"TTS Response: {text}")
        # Hier würde TTS generiert und gesendet werden
        pass
    
    async def _generate_ai_response(self, user_input: str, context: Dict) -> str:
        """
        Generiert AI Response mit GPT-4
        """
        prompt = f"""
        Du bist ein intelligenter Hotel-Rezeptionist.
        Intent: {context.get('intent')}
        Lead Score: {context.get('lead_score')}
        
        Kunde sagt: {user_input}
        
        Antworte professionell, freundlich und hilfsbereit.
        Halte die Antwort kurz (max. 2-3 Sätze).
        """
        
        return await self.openai_service.generate_response(
            prompt,
            max_tokens=150,
            temperature=0.7
        )
"""
WebSocket-basierter Voice Chat Endpoint
Ermöglicht Echtzeit-Sprachkonversation mit KI
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Optional
import asyncio
import json
import base64
import io
import logging
from datetime import datetime
import os
import httpx

from api.services.openai_service import openai_service
from api.services.elevenlabs_service import elevenlabs_service
from api.services.elevenlabs_websocket import get_conversation_manager
from api.core.config import get_settings

router = APIRouter(prefix="/voice-chat", tags=["Voice Chat"])
logger = logging.getLogger(__name__)
settings = get_settings()

# Audio Processing
import numpy as np
# pydub wird für WebM zu WAV Konvertierung benötigt
try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None
    logger.warning("pydub not installed - WebM to WAV conversion disabled")

# Silero VAD temporär deaktiviert wegen Performance-Problemen
SILERO_AVAILABLE = False
logger.info("Silero VAD temporarily disabled for performance")

# Silero VAD für bessere Voice Activity Detection (deaktiviert)
# try:
#     import torch
#     import torchaudio
#     torch.set_num_threads(1)  # Optimize for single-threaded performance
#     
#     # Load Silero VAD model
#     model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
#                                   model='silero_vad',
#                                   force_reload=False,
#                                   onnx=False)
#     (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils
#     SILERO_AVAILABLE = True
#     logger.info("Silero VAD loaded successfully")
# except Exception as e:
#     SILERO_AVAILABLE = False
#     logger.warning(f"Silero VAD not available: {e}")

class VoiceChatSession:
    """Manages a single voice chat session"""
    
    # Klassen-weiter Cache für häufige Phrasen
    COMMON_RESPONSES_CACHE = {}
    
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice
        self.language = "de"
        self.is_active = True
        self.audio_buffer = []
        self.conversation_history = []
        self.is_processing = False
        self.client_format = 'webm'
        self.is_speaking = False
        self.last_user_text: Optional[str] = None
        self.last_user_ts: float = 0.0
        self.has_greeted = False  # Flag um doppelte Begrüßungen zu verhindern
        self.failed_transcription_count = 0  # Counter für fehlgeschlagene Transkriptionen
        self.last_speech_end_time = 0  # Für End-of-Turn Detection
        self.speech_start_time = 0  # Für Minimum Speech Duration
        # Unternehmenswissen optional aus Settings + Datei
        self.company_context: str = ''
        # Turn Management
        self.turn_locked: bool = False
        self.asked_clarify: bool = False
        # Backchannel responses
        self.last_backchannel_time: float = 0
        self.backchannel_count: int = 0
        # Debounce / Buffering
        self.debounce_task: Optional[asyncio.Task] = None
        self.total_buffer_bytes: int = 0
        self.debounce_ms: int = 600  # 0.6 Sekunden Pause = End of Turn
        self.min_bytes_trigger: int = 2000  # Mindestens ~2KB Audio
        # Force-Flag: beim Client-Force wird die Verarbeitung unabhängig von Schwellwerten ausgelöst
        self.force_next: bool = False
        # A/B Pilot: ElevenLabs Conversational AI
        env_conv = os.getenv("USE_ELEVEN_CONV_AI", "0").lower() in ("1", "true", "yes")
        hard_off = os.getenv("CONVAI_HARD_OFF", "1").lower() in ("1", "true", "yes")
        self.use_eleven_conv: bool = (env_conv and not hard_off)
        logger.info(f"ConvAI flag: {self.use_eleven_conv} (env={os.getenv('USE_ELEVEN_CONV_AI')})")
        self.eleven_mgr = None
        self._eleven_pump_task: Optional[asyncio.Task] = None
        try:
            with open('/app/sample_kb.txt', 'r', encoding='utf-8') as kb:
                text = kb.read().strip()
                if text:
                    self.company_context = text
        except Exception:
            pass
        # Slot-Filling für Terminbuchung
        self.booking_in_progress: bool = False
        self.slots = {"date": None, "time": None, "name": None, "phone": None}
        
    async def send_status(self, status: str):
        """Send status update to client"""
        await self.websocket.send_json({
            "type": "status",
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _send_backchannel_response(self):
        """Send short confirmation sound while user is speaking"""
        try:
            import random
            backchannels = ["Mhm.", "Ja.", "Verstehe.", "Aha.", "Genau.", "Okay."]
            response = random.choice(backchannels)
            
            logger.info(f"Sending backchannel: {response}")
            
            # Generiere kurzen Audio-Response
            audio_response, audio_url = await self.synthesize_speech(response)
            
            if audio_url:
                # Sende als "backchannel" type damit Frontend es anders behandelt
                await self.websocket.send_json({
                    "type": "backchannel",
                    "url": audio_url,
                    "text": response
                })
        except Exception as e:
            logger.error(f"Backchannel error: {e}")
    
    async def process_audio_chunk(self, audio_data: bytes):
        """Process incoming audio from client"""
        # A/B: ElevenLabs Conversational AI Pfad – sofort weiterleiten und zurückkehren
        if self.use_eleven_conv:
            try:
                if not self.eleven_mgr:
                    await self._ensure_eleven_started()
                await self.eleven_mgr.send_user_audio(audio_data)
            except Exception as e:
                logger.error(f"ElevenLabs send error: {e}")
            return
            
        # Barge-In: Wenn KI spricht und User spricht, KI unterbrechen
        if self.is_speaking:
            logger.info("User interrupting AI speech - implementing barge-in")
            self.is_speaking = False
            self.turn_locked = False
            # Signal an Client senden dass KI aufhört zu sprechen
            await self.send_status("interrupted")
            # Audio-Buffer mit User-Input starten
            self.audio_buffer = [audio_data]
            self.total_buffer_bytes = len(audio_data)
            return
            
        if self.is_processing or self.turn_locked:
            return  # Skip if already processing
        
        # Puffern
        self.audio_buffer.append(audio_data)
        self.total_buffer_bytes += len(audio_data)
        
        # Tracke Sprach-Timing für End-of-Turn Detection
        import time
        current_time = time.time()
        if self.speech_start_time == 0:
            self.speech_start_time = current_time
            logger.info("Speech activity started")
        
        self.last_speech_end_time = current_time
        
        logger.info(f"buffer+= {len(audio_data)} total={self.total_buffer_bytes}")
        
        # Backchannel Response: Bestätigungslaut nur nach längerem Sprechen (5+ Sekunden)
        if (current_time - self.last_backchannel_time > 5.0 and 
            self.total_buffer_bytes > 40000 and  # Mehr Audio erforderlich
            self.backchannel_count < 2 and  # Weniger Backchannels
            not self.is_processing):
            
            self.last_backchannel_time = current_time
            self.backchannel_count += 1
            
            # Sende kurzen Bestätigungslaut asynchron
            asyncio.create_task(self._send_backchannel_response())
        
        # End-of-Turn Detection: Warte 1.5 Sekunden Stille nach Speech
        # bevor Verarbeitung (Best Practice von Twilio/LiveKit)
        if self.debounce_task and not self.debounce_task.done():
            self.debounce_task.cancel()
        
        # Reduzierte Debounce Zeit für schnellere Reaktion
        # Verarbeite schneller um Timeouts zu vermeiden
        self.debounce_ms = 600  # 0.6 Sekunden Pause = End of Turn
        self.min_bytes_trigger = 2000  # Mindestens ~2KB Audio
        
        logger.info(f"Restarting end-of-turn timer: {self.debounce_ms}ms")
        self.debounce_task = asyncio.create_task(self._debounce_process())
        # Harte Obergrenze pro Turn: 3.0s seit speech_start_time
        try:
            import time
            if self.speech_start_time > 0 and (time.time() - self.speech_start_time) >= 3.0:
                logger.info("Hard max-turn reached (>=3s) → forcing process now")
                # Überspringe Mindestbytes, verarbeite jetzt
                self.force_next = True
                if self.debounce_task and not self.debounce_task.done():
                    self.debounce_task.cancel()
                await self.process_buffered_audio()
                # speech_start_time für nächsten Turn zurücksetzen
                self.speech_start_time = 0
                return
        except Exception:
            pass

    async def _debounce_process(self):
        try:
            await asyncio.sleep(self.debounce_ms / 1000.0)
            # Nur verarbeiten, wenn genug Bytes da sind – außer Force ist aktiv
            if (
                self.audio_buffer
                and not self.is_processing
                and not self.turn_locked
                and (self.total_buffer_bytes >= self.min_bytes_trigger or self.force_next)
            ):
                await self.process_buffered_audio()
        except asyncio.CancelledError:
            return
    
    async def process_buffered_audio(self):
        """Process buffered audio: STT -> GPT-4 -> TTS"""
        try:
            logger.info(f"process_buffered_audio start: chunks={len(self.audio_buffer)} total_before={self.total_buffer_bytes}")
            # Status: Processing
            await self.send_status("thinking")
            # Sperre Turn, um Doppelantworten zu verhindern
            self.turn_locked = True
            self.is_processing = True
            
            # Nimm das größte einzelne Chunk (MediaRecorder liefert Container-Blöcke)
            if not self.audio_buffer:
                if not self.force_next:
                    logger.info("audio_buffer empty on enter; returning to listening")
                    await self.send_status("listening")
                    self.turn_locked = False
                    self.is_processing = False
                    self.speech_start_time = 0
                    return
                # Force-Fallback ohne Nutzereingabe: kurze Rückfrage sprechen
                fallback_text = "Ich habe nichts gehört. Können Sie das bitte wiederholen?"
                await self.send_status("speaking")
                self.is_speaking = True
                audio_response, audio_url = await self.synthesize_speech(fallback_text)
                if audio_url:
                    try:
                        await self.websocket.send_json({"type": "tts_url", "url": audio_url})
                    except Exception:
                        pass
                await self.send_status("listening")
                await asyncio.sleep(0.2)
                self.is_speaking = False
                self.turn_locked = False
                self.is_processing = False
                self.force_next = False
                self.speech_start_time = 0
                return
            # Kombiniere gesamte Pufferung für robustere STT
            combined_audio = b''.join(self.audio_buffer)
            self.audio_buffer.clear()
            total = self.total_buffer_bytes
            self.total_buffer_bytes = 0
            logger.info(f"combined_audio bytes={len(combined_audio)} total_prev={total}")
            # Bereits geplanten Debounce beenden
            if self.debounce_task and not self.debounce_task.done():
                self.debounce_task.cancel()
            
            # Zu kleine Chunks ignorieren (vermeidet Fehltrigger)
            if len(combined_audio) < 1_200 and not self.force_next:  # ~1.2 KB
                logger.info("combined below minimum; ignore and return to listening")
                await self.send_status("listening")
                self.turn_locked = False
                self.is_processing = False
                self.speech_start_time = 0
                return
            
            # Verwende Silero VAD für bessere Spracherkennung wenn verfügbar
            contains_speech = False
            if SILERO_AVAILABLE and AudioSegment:
                try:
                    # Konvertiere Audio zu WAV für VAD Analyse
                    audio_segment = AudioSegment.from_file(io.BytesIO(combined_audio), format="webm")
                    wav_buffer = io.BytesIO()
                    audio_segment.set_frame_rate(16000).export(wav_buffer, format="wav")
                    wav_buffer.seek(0)
                    
                    # Lade Audio für Silero VAD
                    wav_tensor, sample_rate = torchaudio.load(wav_buffer)
                    if sample_rate != 16000:
                        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                        wav_tensor = resampler(wav_tensor)
                    
                    # Erkenne Sprach-Timestamps
                    speech_timestamps = get_speech_timestamps(
                        wav_tensor,
                        model,
                        sampling_rate=16000,
                        threshold=0.5,  # Standard threshold
                        min_speech_duration_ms=500,  # Mindestens 500ms Sprache
                        min_silence_duration_ms=300   # 300ms Stille zwischen Segmenten
                    )
                    
                    contains_speech = len(speech_timestamps) > 0
                    if contains_speech:
                        total_speech_ms = sum(ts['end'] - ts['start'] for ts in speech_timestamps) * 1000 / 16000
                        logger.info(f"Silero VAD: Speech detected, duration: {total_speech_ms:.0f}ms")
                        
                        # Prüfe ob genug Sprache vorhanden ist (mindestens 500ms)
                        if total_speech_ms < 500:
                            logger.info(f"Speech too short ({total_speech_ms:.0f}ms), waiting for more")
                            await self.send_status("listening")
                            self.turn_locked = False
                            self.is_processing = False
                            self.speech_start_time = 0
                            return
                    else:
                        logger.info("Silero VAD: No speech detected in audio")
                        await self.send_status("listening")
                        self.turn_locked = False
                        self.is_processing = False
                        self.speech_start_time = 0
                        self.failed_transcription_count = 0  # Reset counter bei Stille
                        return
                        
                except Exception as e:
                    logger.warning(f"Silero VAD check failed: {e}, falling back to basic check")
                    # Fallback auf alte Methode
                    if len(combined_audio) > 100:
                        sample = combined_audio[100:min(1000, len(combined_audio))]
                        unique_bytes = len(set(sample))
                        if unique_bytes < 50 and not self.force_next:
                            logger.info("Basic check: Audio appears to be silence/noise")
                            await self.send_status("listening")
                            self.turn_locked = False
                            self.is_processing = False
                            self.speech_start_time = 0
                            return
            else:
                # Fallback wenn Silero nicht verfügbar
                if len(combined_audio) > 100:
                    sample = combined_audio[100:min(1000, len(combined_audio))]
                    unique_bytes = len(set(sample))
                    logger.info(f"Basic audio check: unique_bytes={unique_bytes}")
                    if unique_bytes < 50 and not self.force_next:
                        logger.info("Basic check: Audio appears to be silence/noise")
                        await self.send_status("listening")
                        self.turn_locked = False
                        self.is_processing = False
                        self.speech_start_time = 0
                        return
            # Bei force_next: nur Schwellwerte umgehen – STT/GPT normal fortsetzen
            if self.force_next:
                logger.info("force_next active: skipping size checks only; continuing with STT/GPT")
            
            # Speech-to-Text mit Whisper – WebM direkt übergeben
            logger.info("calling transcribe_audio…")
            transcription = await self.transcribe_audio(combined_audio)
            logger.info(f"transcription result: {'<empty>' if not transcription else transcription[:80]}")
            
            if not transcription:
                # Erhöhe Counter für fehlgeschlagene Transkriptionen
                self.failed_transcription_count += 1
                logger.info(f"Empty transcription, count: {self.failed_transcription_count}")
                
                # Nur nach 3 fehlgeschlagenen Versuchen nachfragen
                if self.failed_transcription_count >= 3:
                    try:
                        fallback_text = "Entschuldigung, ich konnte Sie nicht verstehen. Können Sie das bitte wiederholen?"
                        await self.send_status("speaking")
                        self.is_speaking = True
                        audio_response, audio_url = await self.synthesize_speech(fallback_text)
                        if audio_url:
                            try:
                                await self.websocket.send_json({"type": "tts_url", "url": audio_url})
                            except Exception:
                                pass
                    except Exception as fb_err:
                        logger.error(f"Fallback TTS send error: {fb_err}")
                    finally:
                        self.failed_transcription_count = 0  # Reset counter nach Nachfrage
                        await self.send_status("listening")
                        await asyncio.sleep(0.2)
                        self.is_speaking = False
                else:
                    # Einfach weiter zuhören ohne Fehlermeldung
                    logger.info("Continuing to listen without error message")
                    await self.send_status("listening")
                
                self.turn_locked = False
                self.is_processing = False
                self.force_next = False
                self.speech_start_time = 0
                return
            
            # De-Dupe & minimale Länge
            text_norm = ''.join(ch for ch in transcription.strip().lower() if ch.isalnum() or ch.isspace())
            # Bei sehr kurzer/unklarer Eingabe auch Counter nutzen
            if len(text_norm) < 8 or len(text_norm.split()) < 2:
                self.failed_transcription_count += 1
                logger.info(f"Text too short: '{text_norm}', count: {self.failed_transcription_count}")
                
                if self.failed_transcription_count >= 3:
                    try:
                        short_fb = "Ich konnte das nicht richtig verstehen. Bitte sprechen Sie etwas deutlicher."
                        await self.send_status("speaking")
                        self.is_speaking = True
                        audio_response, audio_url = await self.synthesize_speech(short_fb)
                        if audio_url:
                            try:
                                await self.websocket.send_json({"type": "tts_url", "url": audio_url})
                            except Exception:
                                pass
                    except Exception as sfb_err:
                        logger.error(f"Short fallback TTS send error: {sfb_err}")
                    finally:
                        self.failed_transcription_count = 0
                        await self.send_status("listening")
                        await asyncio.sleep(0.2)
                else:
                    # Weiter zuhören ohne Fehlermeldung
                    await self.send_status("listening")
                
                self.is_speaking = False
                self.turn_locked = False
                self.is_processing = False
                self.force_next = False
                self.speech_start_time = 0
                return
            
            # Reset counter bei erfolgreicher Transkription
            self.failed_transcription_count = 0
            
            logger.info(f"User said: {text_norm}")
            self.conversation_history.append({"role": "user", "content": text_norm})
            # Intent-/Slot-Logik: Terminbuchung vorrangig deterministisch behandeln
            ai_response: str
            try:
                intent_data = await self.analyze_intent(transcription)
            except Exception as _e:
                intent_data = {"intent": "other", "slots": {}}
            intent_label = (intent_data.get("intent") or "other").lower()
            extracted_slots = intent_data.get("slots") or {}
            # Merge erkannte Slots in den Session-Status
            self._merge_slots(extracted_slots)
            if intent_label == "appointment" or self.booking_in_progress:
                self.booking_in_progress = True
                missing = self._get_missing_slots()
                if missing:
                    ai_response = self._render_booking_prompt(missing)
                else:
                    ai_response = self._render_confirmation()
                    # Nach Bestätigung Slots zurücksetzen
                    self.booking_in_progress = False
                    self.slots = {"date": None, "time": None, "name": None, "phone": None}
            else:
                if os.getenv("ECHO_MODE", "").lower() in ("1", "true", "yes"):
                    ai_response = f"Verstanden: {transcription.strip()}"
                else:
                    ai_response = await self.generate_response(transcription)
            
            # No-Refusal-Filter
            refuse_markers = [
                "kann nicht helfen", "kann ich nicht helfen", "kann dir nicht helfen",
                "kann ich Ihnen nicht helfen", "leider nicht", "tut mir leid, ich kann nicht"
            ]
            if any(m in ai_response.lower() for m in refuse_markers):
                ai_response = "Gerne. Sagen Sie mir kurz: Produkt, Termin, Preis oder Kontakt?"
            
            logger.info(f"AI response: {ai_response}")
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Status: Speaking
            await self.send_status("speaking")
            self.is_speaking = True
            
            # Text-to-Speech
            audio_response, audio_url = await self.synthesize_speech(ai_response)
            
            try:
                if audio_url:
                    logger.info(f"Sending tts_url to client: {audio_url}")
                    try:
                        await self.websocket.send_json({"type": "tts_url", "url": audio_url})
                        logger.info("tts_url sent successfully")
                    except Exception:
                        pass
                # Binary Audio deaktiviert um doppelte Ausgaben zu verhindern
                # Frontend nutzt nur tts_url für Audio-Wiedergabe
                send_binary = os.getenv("SEND_WS_AUDIO", "0").lower() in ("1", "true", "yes")
                if send_binary and audio_response:
                    logger.info(f"Binary audio sending disabled to prevent duplicates")
                    # await self.websocket.send_bytes(audio_response)  # Deaktiviert!
            except Exception as send_err:
                logger.error(f"WebSocket send error: {send_err}")
            
            # Status: Listening again
            await self.send_status("listening")
            # Kurze Verzögerung, bevor wieder aufgenommen wird
            await asyncio.sleep(0.3)
            self.is_speaking = False
            self.turn_locked = False
            # Nach abgeschlossenem Turn Rückfrage-Flag zurücksetzen
            self.asked_clarify = False
            self.is_processing = False
            self.force_next = False
            self.speech_start_time = 0
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            await self.send_status("error")
            self.is_speaking = False
            self.turn_locked = False
            self.is_processing = False
            self.force_next = False
            self.speech_start_time = 0
    
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper"""
        try:
            logger.info(f"transcribe_audio enter: bytes={len(audio_data)} lang={self.language} fmt={getattr(self, 'client_format', 'webm')}")
            # 1) Bevorzugt: Deepgram (falls API-Key vorhanden)
            dg_key = os.getenv("DEEPGRAM_API_KEY")
            if dg_key:
                headers = {
                    "Authorization": f"Token {dg_key}",
                    "Content-Type": "audio/webm",
                }
                params = {
                    "model": "nova-2",
                    "language": self.language or "de",
                    "punctuate": "true",
                    "smart_format": "true",
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    logger.info("posting to Deepgram…")
                    resp = await client.post(
                        "https://api.deepgram.com/v1/listen",
                        params=params,
                        headers=headers,
                        content=audio_data,
                    )
                logger.info(f"deepgram status={resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    # Robust extrahieren
                    try:
                        alt = data["results"]["channels"][0]["alternatives"][0]
                        text = alt.get("transcript", "").strip()
                    except Exception:
                        text = (data.get("results", {})
                                     .get("channels", [{}])[0]
                                     .get("alternatives", [{}])[0]
                                     .get("transcript", "")).strip()
                    if text:
                        logger.info(f"Deepgram transcript: {text}")
                        return text
                else:
                    logger.error(f"Deepgram error {resp.status_code}: {resp.text[:200]}")

            # Use OpenAI Whisper API (Fallback)
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Optional: Konvertierung überspringen und direkt WebM an Whisper senden
            force_webm = os.getenv("WHISPER_FORCE_WEBM", "").lower() in ("1", "true", "yes")
            if force_webm:
                ext = 'webm' if getattr(self, 'client_format', 'webm') not in ('mp4', 'm4a') else 'm4a'
                audio_file = io.BytesIO(audio_data)
                audio_file.name = f"audio.{ext}"
                logger.info("WHISPER_FORCE_WEBM=1 active → sending original container to Whisper")
            else:
                # WebM zu WAV konvertieren für Whisper API
                try:
                    from pydub import AudioSegment
                    import tempfile
                    
                    logger.info("Converting WebM to WAV for Whisper API...")
                    # WebM Audio laden
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
                    
                    # Zu WAV konvertieren
                    wav_buffer = io.BytesIO()
                    audio_segment.export(wav_buffer, format="wav")
                    wav_buffer.seek(0)
                    
                    # WAV an Whisper senden
                    audio_file = wav_buffer
                    audio_file.name = "audio.wav"
                    ext = 'wav'
                    logger.info(f"Converted to WAV, size: {len(wav_buffer.getvalue())} bytes")
                    
                except Exception as conv_err:
                    logger.warning(f"WebM to WAV conversion failed: {conv_err}, using original format")
                    # Fallback: Original Format verwenden
                    ext = 'webm' if getattr(self, 'client_format', 'webm') not in ('mp4', 'm4a') else 'm4a'
                    audio_file = io.BytesIO(audio_data)
                    audio_file.name = f"audio.{ext}"
            
            logger.info(f"calling whisper with ext={ext}…")
            import asyncio
            try:
                # Erhöhter Timeout für große Audio-Dateien
                response = await asyncio.wait_for(
                    client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=self.language,
                        prompt="Dies ist ein Telefongespräch auf Deutsch."  # Hilft Whisper bei der Erkennung
                    ),
                    timeout=30.0  # Erhöht von 7 auf 30 Sekunden
                )
            except asyncio.TimeoutError:
                logger.error("Whisper transcription timeout after 30s")
                return ""
            transcript = response.text
            logger.info(f"Whisper transcript: {transcript}")
            
            # Filter bekannte Whisper-Halluzinationen bei stillem/schlechtem Audio
            hallucination_patterns = [
                "Untertitel der Amara.org-Community",
                "Amara.org",
                "Thank you for watching",
                "Thanks for watching",
                "[Music]",
                "[Musik]",
                "[Applaus]",
                "[Applause]"
            ]
            
            for pattern in hallucination_patterns:
                if pattern.lower() in transcript.lower():
                    logger.warning(f"Whisper hallucination detected: {transcript}")
                    return ""  # Return empty to trigger fallback
            
            return transcript
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            # Zweiter Versuch mit alternativer Endung, falls Container-Mismatch
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                fallback_ext = 'webm' if ext != 'webm' else 'ogg'
                alt = io.BytesIO(audio_data)
                alt.name = f"audio.{fallback_ext}"
                logger.info(f"calling whisper fallback with ext={fallback_ext}…")
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=alt,
                    language=self.language
                )
                transcript = response.text
                logger.info(f"Whisper fallback transcript: {transcript}")
                
                # Filter auch im Fallback
                hallucination_patterns = [
                    "Untertitel der Amara.org-Community",
                    "Amara.org",
                    "Thank you for watching",
                    "Thanks for watching",
                    "[Music]",
                    "[Musik]",
                    "[Applaus]",
                    "[Applause]"
                ]
                
                for pattern in hallucination_patterns:
                    if pattern.lower() in transcript.lower():
                        logger.warning(f"Whisper fallback hallucination detected: {transcript}")
                        return ""
                
                return transcript
            except Exception as e2:
                logger.error(f"Transcription fallback error: {e2}")
            # Fallback for demo
            return ""

    async def analyze_intent(self, user_input: str) -> dict:
        """Analysiere Nutzeranfrage mit GPT und extrahiere Intent + Slots (deutsch).
        Gibt ein Dict der Form {"intent": "appointment|other", "slots": {"date":"YYYY-MM-DD","time":"HH:MM","name":"...","phone":"..."}} zurück.
        """
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            system = (
                "Du bist ein deutscher NLU-Parser für Telefonate."
                " Erkenne Intent und extrahiere Slots. Antworte NUR mit JSON."
                " intent: 'appointment' für Terminwunsch, sonst 'other'."
                " slots: date (YYYY-MM-DD), time (HH:MM, 24h), name, phone (nur Ziffern, ggf. mit +)."
                " Wenn etwas fehlt, lass es leer. Keine Erklärungen."
            )
            prompt = (
                "Text: " + (user_input or "").strip() + "\n"
                "Gib JSON: {\"intent\":..., \"slots\":{\"date\":...,\"time\":...,\"name\":...,\"phone\":...}}"
            )
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=120,
            )
            content = resp.choices[0].message.content or "{}"
            data = json.loads(content)
            if not isinstance(data, dict):
                return {"intent": "other", "slots": {}}
            # Normalize
            slots = data.get("slots") or {}
            if not isinstance(slots, dict):
                slots = {}
            return {"intent": (data.get("intent") or "other").lower(), "slots": slots}
        except Exception:
            return {"intent": "other", "slots": {}}

    def _merge_slots(self, slots: dict):
        if not slots:
            return
        for key in ("date", "time", "name", "phone"):
            val = slots.get(key)
            if isinstance(val, str) and val.strip():
                self.slots[key] = val.strip()

    def _get_missing_slots(self) -> list:
        missing_order = ["date", "time", "name", "phone"]
        return [k for k in missing_order if not self.slots.get(k)]

    def _render_booking_prompt(self, missing: list) -> str:
        nxt = missing[0]
        if nxt == "date":
            return "Für den Termin brauche ich bitte das Datum. Welcher Tag passt Ihnen?"
        if nxt == "time":
            return "Welche Uhrzeit passt Ihnen für den Termin?"
        if nxt == "name":
            return "Wie ist Ihr vollständiger Name?"
        if nxt == "phone":
            return "Damit ich den Termin bestätigen kann: Wie lautet Ihre Telefonnummer?"
        return "Können Sie das bitte kurz präzisieren?"

    def _render_confirmation(self) -> str:
        d = self.slots.get("date")
        t = self.slots.get("time")
        nm = self.slots.get("name")
        ph = self.slots.get("phone")
        base = f"Ich habe Sie am {d} um {t} eingetragen. "
        if not nm or not ph:
            return base + "Bitte nennen Sie mir noch Ihren Namen und Ihre Telefonnummer."
        return base + "Vielen Dank, {name}. Sie erhalten gleich eine Bestätigung per SMS.".replace("{name}", nm)
    
    async def generate_response(self, user_input: str) -> str:
        """Generate AI response using GPT-4"""
        try:
            norm = (user_input or '').strip().lower()
            greetings = ["hallo", "hi", "hey", "guten tag", "servus", "moin"]
            # Bei sehr kurzen/generischen Eingaben: direkte kurze Begrüßung/Angebot statt Rückfrage
            if len(norm) <= 5 or any(norm.startswith(g) for g in greetings):
                return "Hallo! Wobei kann ich helfen – Produkt, Termin, Preis oder Kontakt?"
            
            # Sentiment-Analyse für emotionale Anpassung
            sentiment_indicators = {
                'frustrated': ['nervt', 'ärgert', 'schlecht', 'funktioniert nicht', 'geht nicht', 'scheiße', 'mist'],
                'urgent': ['dringend', 'sofort', 'schnell', 'eilig', 'notfall', 'wichtig'],
                'happy': ['super', 'toll', 'klasse', 'freut', 'danke', 'perfekt', 'wunderbar'],
                'confused': ['verstehe nicht', 'wie', 'was bedeutet', 'erklären', 'unklar', 'keine ahnung']
            }
            
            detected_sentiment = 'neutral'
            for sentiment, keywords in sentiment_indicators.items():
                if any(kw in norm for kw in keywords):
                    detected_sentiment = sentiment
                    break
 
            # System prompt for voice conversation mit emotionaler Anpassung
            emotional_context = {
                'frustrated': "Der Anrufer ist frustriert. Sei besonders verständnisvoll und geduldig. Beginne mit 'Ich verstehe Ihren Ärger...' ",
                'urgent': "Der Anrufer hat es eilig. Komme sofort zum Punkt, keine Floskeln. Sage 'Verstehe, das ist dringend...' ",
                'happy': "Der Anrufer ist gut gelaunt. Sei ebenfalls fröhlich und enthusiastisch. ",
                'confused': "Der Anrufer ist verwirrt. Erkläre besonders klar und einfach. Sage 'Gerne erkläre ich das...' ",
                'neutral': ""
            }
            
            base_prompt = (
                "Du bist ein freundlicher, natürlicher Telefonassistent. "
                "Sprache: Deutsch. "
                f"{emotional_context[detected_sentiment]}"
                "WICHTIG: Sprich wie ein echter Mensch am Telefon - verwende 'ähm', 'also', 'moment' und "
                "Bestätigungslaute wie 'mhm', 'verstehe'. Antworte kurz aber menschlich. "
                "Wenn der Nutzer eine Absicht nennt (z. B. Termin, Angebot, Bestellung, Kontakt, Preis, Öffnungszeiten), liefere sofort den nächsten konkreten Schritt. "
                "Stelle höchstens EINE kurze Rückfrage, nur wenn essenziell. "
                "Bei Terminwunsch: Frage nach Datum/Tag und Uhrzeit (ein Satz, eine Frage). "
                "Wenn genügend Infos vorhanden sind, bestätige und nenne den nächsten Schritt (z. B. Termin vorschlagen oder Bestätigung ankündigen). "
            )
            # Unternehmenswissen injizieren (gekürzt)
            extra_hint = os.getenv("DOMAIN_HINT", "").strip()
            kb_text = (self.company_context or "").strip()
            kb_short = (kb_text[:1200] + "…") if len(kb_text) > 1200 else kb_text
            hint_short = (extra_hint[:600] + "…") if len(extra_hint) > 600 else extra_hint
            knowledge_parts = []
            if kb_short:
                knowledge_parts.append(f"Unternehmenswissen: {kb_short}")
            if hint_short:
                knowledge_parts.append(f"Hinweis: {hint_short}")
            knowledge_prompt = (" \n".join(knowledge_parts) + "\n") if knowledge_parts else ""
            guardrails = (
                "Beantworte Fragen vorrangig zu unternehmensrelevanten Themen (Produkte, Leistungen, Zeiten, Kontakt, Prozesse). "
                "Wenn die Frage unklar ist, stelle maximal eine kurze Rückfrage; wiederhole sie nicht mehrfach. "
                "Vermeide Ablehnungen wie 'kann nicht helfen'; stelle stattdessen eine konkrete Rückfrage (einmal) oder biete nächsten Schritt (Termin/Kontakt) an. "
                "Erfinde keine Fakten. Halte Antworten sehr kurz."
            )
            system_prompt = base_prompt + knowledge_prompt + guardrails
            
            # Use OpenAI GPT-4
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            messages = [
                {"role": "system", "content": system_prompt},
                *self.conversation_history[-20:]  # Last 10 exchanges für besseren Kontext
            ]
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=80,
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"GPT-4 error: {e}")
            # Fallback response
            return "Mir geht es gut, danke! VocalIQ ist eine moderne Plattform für KI-gestützte Telefonie. Wie kann ich Ihnen helfen?"
    
    async def synthesize_speech(self, text: str):
        """Convert text to speech using ElevenLabs. Returns (audio_bytes, audio_url)."""
        try:
            # Cache-Check für häufige Phrasen
            cache_key = f"{self.voice_id}:{text[:100]}"
            if cache_key in VoiceChatSession.COMMON_RESPONSES_CACHE:
                logger.info(f"Cache hit for phrase: {text[:30]}...")
                cached = VoiceChatSession.COMMON_RESPONSES_CACHE[cache_key]
                return cached['audio_bytes'], cached['audio_url']
            
            # Antwort für TTS stark kürzen: erste Satzgrenze oder 25 Wörter
            def _shorten_for_tts(t: str) -> str:
                t = (t or "").strip()
                if not t:
                    return t
                for end in ['.', '!', '?']:
                    idx = t.find(end)
                    if idx != -1 and idx < 180:
                        t = t[:idx+1]
                        break
                words = t.split()
                if len(words) > 25:
                    t = ' '.join(words[:25])
                return t

            text = _shorten_for_tts(text)
            from api.models.schemas import TTSRequest
            
            tts_request = TTSRequest(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_turbo_v2_5",  # Turbo model für 50% niedrigere Latenz
                stability=0.4,  # Etwas weniger stabil für natürlichere Variation
                similarity_boost=0.8,  # Höhere Ähnlichkeit für konsistente Stimme
                style=0.2,  # Leicht expressiver
                optimize_streaming_latency=3  # Optimiert für niedrige Latenz
            )
            
            tts_response = await elevenlabs_service.synthesize_speech(tts_request)
            
            if tts_response.audio_url:
                file_cache_key = tts_response.audio_url.split('/')[-1].replace('.mp3', '')
                audio_bytes = await elevenlabs_service.get_cached_audio_file(file_cache_key)
                logger.info(f"TTS synthesized successfully: url={tts_response.audio_url}, bytes={len(audio_bytes) if audio_bytes else 0}")
                
                # In Memory-Cache speichern für häufige Phrasen
                if len(text) < 100 and len(VoiceChatSession.COMMON_RESPONSES_CACHE) < 50:  # Max 50 Phrasen cachen
                    VoiceChatSession.COMMON_RESPONSES_CACHE[cache_key] = {
                        'audio_bytes': audio_bytes,
                        'audio_url': tts_response.audio_url
                    }
                    logger.info(f"Cached phrase: {text[:30]}... (Cache size: {len(VoiceChatSession.COMMON_RESPONSES_CACHE)})")
                
                return audio_bytes, tts_response.audio_url
            else:
                logger.warning("TTS response has no audio_url")
            
            return None, None
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None, None

    async def delayed_force_process(self, delay_seconds: float = 0.25):
        """Verzögert die erzwungene Verarbeitung, damit letzte MediaRecorder‑Chunks noch ankommen."""
        try:
            await asyncio.sleep(delay_seconds)
            if not self.is_processing and not self.turn_locked:
                logger.info(f"force delay elapsed ({delay_seconds}s), processing now; buffered={len(self.audio_buffer)} chunks bytes_total={self.total_buffer_bytes}")
                await self.process_buffered_audio()
            else:
                logger.info("force delay elapsed but session is busy; skipping")
        except Exception as e:
            logger.error(f"delayed_force_process error: {e}")

    async def force_quick_reply_now(self):
        """Sofortige, kurze TTS-Bestätigung senden, unabhängig vom aktuellen Busy-Status."""
        try:
            quick_text = "Alles klar, ich habe Sie gehört. Wie kann ich helfen – Produkt, Termin, Preis oder Kontakt?"
            await self.send_status("speaking")
            self.is_speaking = True
            audio_response, audio_url = await self.synthesize_speech(quick_text)
            if audio_url:
                try:
                    await self.websocket.send_json({"type": "tts_url", "url": audio_url})
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"force_quick_reply_now error: {e}")
        finally:
            # Nach der kurzen Antwort wieder zuhören und Flags zurücksetzen
            await self.send_status("listening")
            await asyncio.sleep(0.2)
            self.is_speaking = False
            self.turn_locked = False
            self.is_processing = False
            # Buffer leeren, um Altlasten zu vermeiden
            self.audio_buffer.clear()
            self.total_buffer_bytes = 0
            self.force_next = False

    async def force_process_after_idle(self, max_wait_seconds: float = 1.0):
        """Wartet kurz, bis die Session idle ist, und stößt dann die Verarbeitung an (mit force)."""
        try:
            waited = 0.0
            step = 0.05
            while (self.is_processing or self.turn_locked or self.is_speaking) and waited < max_wait_seconds:
                await asyncio.sleep(step)
                waited += step
            logger.info(f"force_process_after_idle: waited={waited:.2f}s busy={self.is_processing or self.turn_locked or self.is_speaking}")
            # Debounce sicher beenden
            if self.debounce_task and not self.debounce_task.done():
                self.debounce_task.cancel()
            # Falls noch kein Audio: trotzdem Fallback senden
            if not self.audio_buffer and self.total_buffer_bytes == 0:
                fallback_text = "Ich habe nichts verstanden. Können Sie das bitte wiederholen?"
                await self.send_status("speaking")
                self.is_speaking = True
                _, audio_url = await self.synthesize_speech(fallback_text)
                if audio_url:
                    try:
                        await self.websocket.send_json({"type": "tts_url", "url": audio_url})
                    except Exception:
                        pass
                await self.send_status("listening")
                await asyncio.sleep(0.2)
                self.is_speaking = False
                self.turn_locked = False
                self.is_processing = False
                self.force_next = False
                self.speech_start_time = 0
                return
            await self.process_buffered_audio()
        except Exception as e:
            logger.error(f"force_process_after_idle error: {e}")

    async def _ensure_eleven_started(self):
        """Starte ElevenLabs Conversational Session und beginne Pump-Loop."""
        if self.eleven_mgr:
            return
        try:
            logger.info("Starting ElevenLabs Conversational AI…")
            await self.send_status("connected")
            self.eleven_mgr = await get_conversation_manager(self.voice_id)
            # Audio-Pump-Loop
            self._eleven_pump_task = asyncio.create_task(self._pump_eleven_audio())
            logger.info("ElevenLabs Conversational AI gestartet")
        except Exception as e:
            logger.error(f"Failed to start ElevenLabs conv session: {e}")

    async def _pump_eleven_audio(self):
        """Zieht AI-Audio aus ElevenLabs und sendet es als Binärdaten an den Client."""
        try:
            while self.is_active and self.use_eleven_conv and self.eleven_mgr:
                try:
                    audio_bytes = await self.eleven_mgr.get_ai_audio()
                except Exception:
                    audio_bytes = None
                if audio_bytes:
                    try:
                        await self.send_status("speaking")
                        self.is_speaking = True
                        await self.websocket.send_bytes(audio_bytes)
                    except Exception as send_err:
                        logger.error(f"WS send bytes error: {send_err}")
                    finally:
                        # kurze Pause, dann wieder Listening zulassen
                        await asyncio.sleep(0.05)
                        await self.send_status("listening")
                        self.is_speaking = False
                else:
                    await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"pump_eleven_audio error: {e}")


# Active sessions
active_sessions: Dict[str, VoiceChatSession] = {}


@router.websocket("/ws/{session_id}")
async def voice_chat_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time voice chat"""
    await websocket.accept()
    
    # Create session
    session = VoiceChatSession(websocket, session_id)
    active_sessions[session_id] = session
    logger.info(f"WebSocket connected: {session_id}")
    
    try:
        # Send initial status
        await session.send_status("connected")
        
        while True:
            # Receive data from client
            data = await websocket.receive()
            
            if "text" in data:
                # JSON message
                message = json.loads(data["text"])
                
                if message.get("type") == "config":
                    # Update configuration
                    session.voice_id = message.get("voice_id", session.voice_id)
                    session.language = message.get("language", session.language)
                    session.client_format = message.get("format", session.client_format)
                    logger.info(f"WS config: voice={session.voice_id} lang={session.language} format={session.client_format}")
                    await session.send_status("listening")

                    # A/B: ElevenLabs Conversational AI ggf. starten
                    if session.use_eleven_conv:
                        await session._ensure_eleven_started()
                    
                elif message.get("type") == "ping":
                    # Keepalive ignorieren
                    pass
                    
                elif message.get("type") == "force":
                    # Force-Processing des aktuell gepufferten Segments
                    session.force_next = True
                    # Debounce abbrechen, damit nicht konkurriert wird
                    if session.debounce_task and not session.debounce_task.done():
                        session.debounce_task.cancel()
                    # Bei Busy kurz warten, sonst direkt kurz verzögern – in beiden Fällen STT/GPT ausführen
                    if session.is_processing or session.turn_locked or session.is_speaking:
                        logger.info("WS force: busy -> waiting up to 1.0s, then process")
                        asyncio.create_task(session.force_process_after_idle(1.0))
                    else:
                        logger.info("WS force: scheduled delayed processing (250ms)")
                        asyncio.create_task(session.delayed_force_process(0.25))
                    
                elif message.get("type") == "end":
                    # End session
                    break
                    
            elif "bytes" in data:
                # Audio data
                try:
                    size = len(data.get("bytes") or b"")
                except Exception:
                    size = -1
                logger.info(f"WS audio chunk: {size} bytes (speaking={session.is_speaking})")
                # Half‑Duplex: während KI spricht, nichts verarbeiten
                if not session.is_speaking:
                    await session.process_audio_chunk(data["bytes"]) 
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up session
        if session_id in active_sessions:
            del active_sessions[session_id]
        # ElevenLabs Session: Pump-Task abbrechen
        try:
            if session._eleven_pump_task and not session._eleven_pump_task.done():
                session._eleven_pump_task.cancel()
        except Exception:
            pass


@router.get("/sessions")
async def get_active_sessions():
    """Get list of active voice chat sessions"""
    return {
        "count": len(active_sessions),
        "sessions": list(active_sessions.keys())
    }


@router.delete("/sessions/{session_id}")
async def end_session(session_id: str):
    """End a specific voice chat session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    await session.websocket.close()
    del active_sessions[session_id]
    
    return {"message": "Session ended"}
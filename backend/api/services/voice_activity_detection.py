"""
Voice Activity Detection (VAD) für natürliche Konversation
Erkennt Sprechpausen und Turn-Taking
"""
import numpy as np
import logging
from typing import Optional, Tuple
from collections import deque
import struct

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """
    VAD für Echtzeit-Spracherkennung
    Basiert auf Energie-Schwellwerten und Zero-Crossing-Rate
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration_ms: int = 30,
        energy_threshold: float = 0.01,
        zcr_threshold: float = 0.1,
        silence_duration_ms: int = 500,
        speech_duration_ms: int = 100
    ):
        """
        Initialisiere VAD
        
        Args:
            sample_rate: Audio-Sample-Rate in Hz
            frame_duration_ms: Frame-Länge in Millisekunden
            energy_threshold: Energie-Schwellwert für Sprache
            zcr_threshold: Zero-Crossing-Rate Schwellwert
            silence_duration_ms: Minimale Stille für Ende der Sprache
            speech_duration_ms: Minimale Sprachdauer für Aktivierung
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        
        # Schwellwerte
        self.energy_threshold = energy_threshold
        self.zcr_threshold = zcr_threshold
        
        # Zeitfenster
        self.silence_frames_required = int(silence_duration_ms / frame_duration_ms)
        self.speech_frames_required = int(speech_duration_ms / frame_duration_ms)
        
        # Zustand
        self.is_speaking = False
        self.silence_frames = 0
        self.speech_frames = 0
        
        # Buffer für gleitende Durchschnitte
        self.energy_buffer = deque(maxlen=10)
        self.zcr_buffer = deque(maxlen=10)
        
        # Adaptive Schwellwerte
        self.noise_energy = 0.001
        self.adaptive_threshold = energy_threshold
        
    def process_frame(self, audio_frame: bytes) -> Tuple[bool, float]:
        """
        Verarbeite einen Audio-Frame
        
        Returns:
            Tuple[bool, float]: (is_speech, confidence)
        """
        # Konvertiere Bytes zu Float-Array
        samples = self._bytes_to_float(audio_frame)
        
        if len(samples) == 0:
            return self.is_speaking, 0.0
        
        # Berechne Audio-Features
        energy = self._calculate_energy(samples)
        zcr = self._calculate_zcr(samples)
        
        # Update Buffer
        self.energy_buffer.append(energy)
        self.zcr_buffer.append(zcr)
        
        # Adaptive Schwellwert-Anpassung
        self._update_adaptive_threshold()
        
        # Sprache-Erkennung
        is_speech = self._detect_speech(energy, zcr)
        
        # State Machine für Turn-Taking
        self._update_state(is_speech)
        
        # Confidence Score
        confidence = self._calculate_confidence(energy, zcr)
        
        return self.is_speaking, confidence
    
    def _bytes_to_float(self, audio_bytes: bytes) -> np.ndarray:
        """Konvertiere Audio-Bytes zu Float-Array"""
        try:
            # Annahme: 16-bit PCM
            samples = struct.unpack(f'{len(audio_bytes)//2}h', audio_bytes)
            # Normalisiere zu [-1, 1]
            return np.array(samples) / 32768.0
        except:
            return np.array([])
    
    def _calculate_energy(self, samples: np.ndarray) -> float:
        """Berechne Frame-Energie (RMS)"""
        return np.sqrt(np.mean(samples ** 2))
    
    def _calculate_zcr(self, samples: np.ndarray) -> float:
        """Berechne Zero-Crossing-Rate"""
        sign_changes = np.diff(np.sign(samples))
        zcr = np.sum(np.abs(sign_changes) > 0) / len(samples)
        return zcr
    
    def _detect_speech(self, energy: float, zcr: float) -> bool:
        """Erkenne ob Frame Sprache enthält"""
        # Energie-basierte Erkennung
        energy_speech = energy > self.adaptive_threshold
        
        # ZCR für Unterscheidung Sprache/Musik/Rauschen
        zcr_speech = self.zcr_threshold < zcr < 0.5
        
        # Kombinierte Entscheidung
        return energy_speech and zcr_speech
    
    def _update_state(self, is_speech: bool):
        """Update State Machine für Turn-Taking"""
        if is_speech:
            self.speech_frames += 1
            self.silence_frames = 0
            
            # Aktiviere Sprache nach genügend Frames
            if self.speech_frames >= self.speech_frames_required:
                if not self.is_speaking:
                    logger.debug("🎤 Sprache erkannt - Start")
                self.is_speaking = True
        else:
            self.silence_frames += 1
            self.speech_frames = 0
            
            # Deaktiviere Sprache nach genügend Stille
            if self.silence_frames >= self.silence_frames_required:
                if self.is_speaking:
                    logger.debug("🔇 Sprechpause erkannt - Ende")
                self.is_speaking = False
    
    def _update_adaptive_threshold(self):
        """Passe Schwellwert an Umgebungsgeräusche an"""
        if len(self.energy_buffer) >= 5:
            # Nutze niedrigste Energie als Rausch-Schätzung
            min_energy = min(self.energy_buffer)
            self.noise_energy = 0.9 * self.noise_energy + 0.1 * min_energy
            
            # Setze Schwellwert relativ zum Rauschen
            self.adaptive_threshold = max(
                self.energy_threshold,
                self.noise_energy * 3.0
            )
    
    def _calculate_confidence(self, energy: float, zcr: float) -> float:
        """Berechne Konfidenz-Score für Sprache"""
        if not self.is_speaking:
            return 0.0
        
        # Energie-Konfidenz
        energy_conf = min(1.0, energy / (self.adaptive_threshold * 3))
        
        # ZCR-Konfidenz (optimal für Sprache: 0.1-0.3)
        zcr_optimal = 0.2
        zcr_conf = 1.0 - min(1.0, abs(zcr - zcr_optimal) / zcr_optimal)
        
        # Kombinierte Konfidenz
        return (energy_conf * 0.7 + zcr_conf * 0.3)
    
    def reset(self):
        """Reset VAD Zustand"""
        self.is_speaking = False
        self.silence_frames = 0
        self.speech_frames = 0
        self.energy_buffer.clear()
        self.zcr_buffer.clear()
        self.noise_energy = 0.001
        self.adaptive_threshold = self.energy_threshold


class TurnTakingManager:
    """
    Verwaltet Turn-Taking in Konversationen
    Erkennt wann der Nutzer fertig gesprochen hat
    """
    
    def __init__(
        self,
        vad: VoiceActivityDetector,
        min_turn_duration_ms: int = 500,
        max_pause_ms: int = 1000,
        interruption_threshold_ms: int = 200
    ):
        """
        Initialisiere Turn-Taking Manager
        
        Args:
            vad: Voice Activity Detector Instanz
            min_turn_duration_ms: Minimale Dauer für gültigen Turn
            max_pause_ms: Maximale Pause bevor Turn endet
            interruption_threshold_ms: Zeit für Unterbrechungs-Erkennung
        """
        self.vad = vad
        self.min_turn_duration_ms = min_turn_duration_ms
        self.max_pause_ms = max_pause_ms
        self.interruption_threshold_ms = interruption_threshold_ms
        
        # Zustand
        self.current_speaker = None  # 'user' oder 'ai'
        self.turn_start_time = None
        self.last_speech_time = None
        self.turn_duration = 0
        
        # Ereignis-Callbacks
        self.on_turn_start = None
        self.on_turn_end = None
        self.on_interruption = None
    
    def process_user_audio(
        self,
        audio_frame: bytes,
        timestamp_ms: int
    ) -> Optional[str]:
        """
        Verarbeite User-Audio und erkenne Turn-Wechsel
        
        Returns:
            Optional[str]: Ereignis ('turn_start', 'turn_end', 'interruption')
        """
        is_speech, confidence = self.vad.process_frame(audio_frame)
        
        event = None
        
        if is_speech:
            # User spricht
            if self.current_speaker != 'user':
                # Neuer Turn oder Unterbrechung
                if self.current_speaker == 'ai':
                    # User unterbricht AI
                    if self.turn_duration < self.interruption_threshold_ms:
                        event = 'interruption'
                        logger.info("⚡ Unterbrechung erkannt")
                
                self.current_speaker = 'user'
                self.turn_start_time = timestamp_ms
                event = event or 'turn_start'
                logger.info("👤 User Turn Start")
            
            self.last_speech_time = timestamp_ms
            self.turn_duration = timestamp_ms - self.turn_start_time
            
        elif self.current_speaker == 'user':
            # User hat aufgehört zu sprechen
            pause_duration = timestamp_ms - self.last_speech_time
            
            if pause_duration > self.max_pause_ms:
                # Turn beendet
                if self.turn_duration >= self.min_turn_duration_ms:
                    event = 'turn_end'
                    logger.info(f"👤 User Turn Ende (Dauer: {self.turn_duration}ms)")
                    self.current_speaker = None
                else:
                    # Zu kurz - ignorieren
                    logger.debug("Turn zu kurz, ignoriert")
                    self.current_speaker = None
        
        return event
    
    def signal_ai_speaking(self, is_speaking: bool):
        """Signalisiere dass AI spricht"""
        if is_speaking:
            self.current_speaker = 'ai'
            self.turn_start_time = 0
            logger.info("🤖 AI Turn Start")
        elif self.current_speaker == 'ai':
            self.current_speaker = None
            logger.info("🤖 AI Turn Ende")
    
    def reset(self):
        """Reset Turn-Taking Zustand"""
        self.current_speaker = None
        self.turn_start_time = None
        self.last_speech_time = None
        self.turn_duration = 0
        self.vad.reset()


# Globale Instanzen
_vad_instance: Optional[VoiceActivityDetector] = None
_turn_manager: Optional[TurnTakingManager] = None

def get_vad() -> VoiceActivityDetector:
    """Hole oder erstelle VAD Instanz"""
    global _vad_instance
    if _vad_instance is None:
        _vad_instance = VoiceActivityDetector()
    return _vad_instance

def get_turn_manager() -> TurnTakingManager:
    """Hole oder erstelle Turn Manager"""
    global _turn_manager
    if _turn_manager is None:
        _turn_manager = TurnTakingManager(get_vad())
    return _turn_manager
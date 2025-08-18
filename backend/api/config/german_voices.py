"""
Deutsche Stimmen-Konfiguration für ElevenLabs
"""

GERMAN_VOICES = {
    "male": [
        {
            "voice_id": "onwK4e9ZLuTAKqWW03F9",  # Daniel
            "name": "Daniel",
            "description": "Erwachsene männliche Stimme, professionell und vertrauenswürdig",
            "age": "middle_aged",
            "accent": "german",
            "gender": "male",
            "use_case": "customer_service"
        },
        {
            "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill
            "name": "Bill",
            "description": "Reife männliche Stimme, ruhig und kompetent",
            "age": "middle_aged", 
            "accent": "german",
            "gender": "male",
            "use_case": "professional"
        },
        {
            "voice_id": "ErXwobaYiN019PkySvjV",  # Antoni
            "name": "Antoni",
            "description": "Junge männliche Stimme, freundlich und energisch",
            "age": "young",
            "accent": "german",
            "gender": "male",
            "use_case": "casual"
        },
        {
            "voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold
            "name": "Arnold",
            "description": "Kraftvolle männliche Stimme, autoritär",
            "age": "middle_aged",
            "accent": "german",
            "gender": "male",
            "use_case": "announcement"
        },
        {
            "voice_id": "2EiwWnXFnvU5JabPnv8n",  # Clyde
            "name": "Clyde",
            "description": "Warme männliche Stimme, verständnisvoll",
            "age": "middle_aged",
            "accent": "german",
            "gender": "male",
            "use_case": "support"
        }
    ],
    "female": [
        {
            "voice_id": "MF3mGyEYCl7XYWbV9V6O",  # Elli
            "name": "Elli",
            "description": "Junge weibliche Stimme, freundlich und enthusiastisch",
            "age": "young",
            "accent": "german",
            "gender": "female",
            "use_case": "customer_service"
        },
        {
            "voice_id": "ThT5KcBeYPX3keUQqHPh",  # Dorothy
            "name": "Dorothy",
            "description": "Reife weibliche Stimme, professionell und beruhigend",
            "age": "middle_aged",
            "accent": "german",
            "gender": "female",
            "use_case": "professional"
        },
        {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "name": "Rachel",
            "description": "Erwachsene weibliche Stimme, klar und deutlich",
            "age": "young",
            "accent": "german",
            "gender": "female",
            "use_case": "narration"
        },
        {
            "voice_id": "jsCqWAovK2LkecY7zXl4",  # Freya
            "name": "Freya",
            "description": "Junge weibliche Stimme, lebhaft und freundlich",
            "age": "young",
            "accent": "german",
            "gender": "female",
            "use_case": "casual"
        },
        {
            "voice_id": "oWAxZDx7w5VEj9dCyTzz",  # Grace
            "name": "Grace",
            "description": "Sanfte weibliche Stimme, einfühlsam",
            "age": "young",
            "accent": "german",
            "gender": "female",
            "use_case": "meditation"
        }
    ]
}

# Empfohlene Stimmen für verschiedene Use Cases
RECOMMENDED_VOICES = {
    "customer_service": ["Daniel", "Elli"],
    "sales": ["Antoni", "Rachel"],
    "support": ["Clyde", "Dorothy"],
    "professional": ["Bill", "ThT5KcBeYPX3keUQqHPh"],
    "casual": ["ErXwobaYiN019PkySvjV", "jsCqWAovK2LkecY7zXl4"]
}

# Voice Settings für optimale Qualität
VOICE_SETTINGS = {
    "stability": 0.5,  # Konsistenz der Stimme
    "similarity_boost": 0.75,  # Ähnlichkeit zur Original-Stimme
    "style": 0.0,  # Stil-Anpassung (0 = neutral)
    "use_speaker_boost": True,  # Verbesserte Sprecherqualität
}

def get_german_voice_by_name(name: str) -> dict:
    """Hole deutsche Stimme nach Name"""
    for gender_voices in GERMAN_VOICES.values():
        for voice in gender_voices:
            if voice["name"].lower() == name.lower():
                return voice
    return None

def get_recommended_voice_for_usecase(use_case: str) -> dict:
    """Hole empfohlene Stimme für einen Use Case"""
    voice_ids = RECOMMENDED_VOICES.get(use_case, [])
    if voice_ids:
        # Erste empfohlene Stimme zurückgeben
        first_id = voice_ids[0]
        for gender_voices in GERMAN_VOICES.values():
            for voice in gender_voices:
                if voice["voice_id"] == first_id or voice["name"] == first_id:
                    return voice
    return None

def get_all_german_voices() -> list:
    """Alle deutschen Stimmen als flache Liste"""
    all_voices = []
    for gender_voices in GERMAN_VOICES.values():
        all_voices.extend(gender_voices)
    return all_voices
"""
Voice Agent Scripts für Hotel und Business Use Cases
Intelligente Routing und personalisierte Gesprächsführung
"""

# Hotel-spezifische Routing Keywords
ROUTING_KEYWORDS = {
    'reception': {
        'keywords': ['rezeption', 'empfang', 'front desk', 'check-in', 'check-out'],
        'department': 'reception',
        'transfer_message': 'Einen Moment bitte, ich verbinde Sie mit der Rezeption.'
    },
    'kitchen': {
        'keywords': ['küche', 'lieferung', 'bestellung', 'lebensmittel', 'getränke', 'lieferant'],
        'department': 'kitchen',
        'transfer_message': 'Ich verbinde Sie direkt mit unserer Küche.'
    },
    'hr': {
        'keywords': ['bewerbung', 'job', 'stelle', 'arbeit', 'personal', 'hr', 'karriere'],
        'department': 'hr',
        'transfer_message': 'Ich leite Sie an unsere Personalabteilung weiter.'
    },
    'accounting': {
        'keywords': ['rechnung', 'zahlung', 'buchhaltung', 'mahnung', 'überweisung'],
        'department': 'accounting',
        'transfer_message': 'Einen Moment, ich verbinde Sie mit der Buchhaltung.'
    },
    'management': {
        'keywords': ['geschäftsführung', 'direktor', 'chef', 'manager', 'beschwerde'],
        'department': 'management',
        'transfer_message': 'Ich verbinde Sie mit der Geschäftsführung.'
    },
    'emergency': {
        'keywords': ['notfall', 'feuer', 'verletzt', 'polizei', 'krankenwagen', 'hilfe', 'dringend'],
        'department': 'emergency',
        'transfer_message': 'NOTFALL ERKANNT - Ich verbinde Sie sofort!'
    }
}

# Hauptscripts für verschiedene Szenarien
AGENT_SCRIPTS = {
    # ============================================
    # HOTEL USE CASE - Intelligenter Rezeptionist
    # ============================================
    'hotel_receptionist': {
        'initial_greeting': """
        Guten Tag und herzlich willkommen im {hotel_name}.
        Mein Name ist {agent_name}, Ihr digitaler Assistent.
        Wie kann ich Ihnen heute helfen?
        """,
        
        'routing_decision': """
        Ich verstehe, Sie möchten {intent}.
        
        Ich kann Ihnen gerne dabei helfen oder Sie direkt mit unserer {department} verbinden.
        Was wäre Ihnen lieber?
        
        Sagen Sie einfach "Sie helfen mir" oder "Bitte verbinden".
        """,
        
        'booking_assistant': """
        Sehr gerne helfe ich Ihnen bei Ihrer Buchung.
        
        Für welchen Zeitraum möchten Sie bei uns übernachten?
        Und wie viele Personen werden Sie sein?
        """,
        
        'booking_confirmation': """
        Perfekt! Ich habe folgende Buchung für Sie vorbereitet:
        - Anreise: {check_in}
        - Abreise: {check_out}
        - Personen: {guests}
        - Zimmertyp: {room_type}
        - Preis pro Nacht: {price}€
        
        Möchten Sie diese Buchung verbindlich bestätigen?
        """,
        
        'transfer_to_human': """
        Natürlich, sehr gerne!
        {transfer_message}
        
        Bitte bleiben Sie kurz in der Leitung.
        Einen schönen Tag wünsche ich Ihnen!
        """,
        
        'no_availability': """
        Es tut mir leid, aber für Ihren gewünschten Zeitraum haben wir leider keine Verfügbarkeiten.
        
        Möchten Sie:
        1. Alternative Termine prüfen?
        2. Auf die Warteliste?
        3. Mit der Rezeption sprechen?
        
        Was wäre Ihnen am liebsten?
        """
    },
    
    # ============================================
    # LEAD SCORING & QUALIFICATION
    # ============================================
    'lead_qualification': {
        'initial': """
        Guten Tag {name}, schön dass ich Sie erreiche.
        
        Ich rufe an bezüglich Ihrer Anfrage zu {product}.
        Haben Sie gerade 2 Minuten Zeit für ein paar kurze Fragen?
        """,
        
        'qualifying_questions': [
            "Was ist Ihre größte Herausforderung bei {topic}?",
            "Welchen Zeitrahmen haben Sie für die Umsetzung im Sinn?",
            "Haben Sie bereits ein Budget eingeplant?",
            "Wer ist noch in die Entscheidung involviert?"
        ],
        
        'high_score_response': """
        Das klingt sehr vielversprechend!
        Basierend auf Ihren Anforderungen kann ich Ihnen definitiv eine passende Lösung anbieten.
        
        Ich würde vorschlagen, dass wir einen Termin vereinbaren, wo wir alles im Detail besprechen.
        Passt Ihnen {suggested_time}?
        """,
        
        'low_score_response': """
        Ich verstehe. Es scheint, als wäre der Zeitpunkt noch nicht optimal.
        
        Darf ich Ihnen trotzdem unsere Informationsunterlagen zusenden?
        Dann können Sie sich in Ruhe damit beschäftigen.
        
        Wann darf ich mich wieder bei Ihnen melden?
        """
    },
    
    # ============================================
    # FOLLOW-UP SCRIPTS
    # ============================================
    'follow_up': {
        'day_3': """
        Guten Tag {name}, hier ist {agent_name} von {company}.
        
        Sie haben vor 3 Tagen unser Angebot erhalten.
        Ich wollte kurz nachfragen, ob Sie schon Zeit hatten, es durchzusehen?
        
        Gibt es Fragen, die ich Ihnen direkt beantworten kann?
        """,
        
        'day_7': """
        Hallo {name}, ich hoffe es geht Ihnen gut.
        
        Letzte Woche haben wir Ihnen unser Angebot zugesendet.
        Konnten Sie es schon intern besprechen?
        
        Ich stehe gerne für Rückfragen zur Verfügung.
        Wann würde es Ihnen passen, nochmal zu sprechen?
        """,
        
        'day_14': """
        Guten Tag {name},
        
        vor zwei Wochen haben wir über {product} gesprochen.
        Ich wollte nachfassen und fragen, wie Ihre Überlegungen aussehen?
        
        Gibt es noch Bedenken, die ich ausräumen kann?
        Oder benötigen Sie zusätzliche Informationen?
        """,
        
        'day_30': """
        Hallo {name},
        
        es ist nun ein Monat vergangen seit unserem Angebot.
        Ich verstehe, dass Prioritäten sich ändern können.
        
        Ist das Projekt noch aktuell für Sie?
        Falls nicht, wäre es hilfreich zu wissen, was sich geändert hat.
        """
    },
    
    # ============================================
    # REAKTIVIERUNG (Alte/Kalte Leads)
    # ============================================
    'reactivation': {
        '30_days': """
        Guten Tag {name}, hier ist {agent_name} von {company}.
        
        Wir hatten vor etwa einem Monat über {topic} gesprochen.
        Ich wollte nachfragen, ob sich bei Ihnen etwas getan hat?
        
        Wir haben inzwischen einige neue Features entwickelt, die perfekt zu Ihren Anforderungen passen würden.
        Hätten Sie diese Woche Zeit für ein kurzes Update-Gespräch?
        """,
        
        '60_days': """
        Hallo {name}, schön Sie wieder zu erreichen.
        
        Es ist schon zwei Monate her seit unserem letzten Gespräch.
        Hat sich Ihre Situation verändert?
        
        Viele unserer Kunden haben in den letzten Wochen großartige Ergebnisse erzielt.
        Ich würde Ihnen gerne zeigen, was jetzt möglich ist.
        
        Wann hätten Sie 15 Minuten Zeit?
        """,
        
        '90_days': """
        Guten Tag {name},
        
        vor drei Monaten hatten wir über {topic} gesprochen.
        Ist das Thema noch relevant für Sie?
        
        Wir haben unser Angebot deutlich verbessert und der Preis ist aktuell sehr attraktiv.
        Außerdem gibt es einen Bonus für Neukunden diesen Monat.
        
        Soll ich Ihnen die neuen Konditionen zusenden?
        """,
        
        '180_days': """
        Hallo {name}, es ist eine Weile her.
        
        Vor einem halben Jahr hatten wir Kontakt bezüglich {topic}.
        Ich wollte fragen, ob sich Ihre Prioritäten geändert haben?
        
        Wir haben komplett neue Lösungen entwickelt.
        Vielleicht ist jetzt der richtige Zeitpunkt gekommen?
        
        Darf ich Ihnen unverbindlich unsere aktuellen Möglichkeiten vorstellen?
        """
    },
    
    # ============================================
    # INTELLIGENTE ANTWORTEN
    # ============================================
    'intelligent_responses': {
        'price_objection': """
        Ich verstehe Ihre Bedenken bezüglich des Preises.
        
        Lassen Sie uns über den Wert sprechen, den Sie erhalten:
        {value_points}
        
        Außerdem bieten wir flexible Zahlungsoptionen an.
        Was wäre für Sie machbar?
        """,
        
        'competitor_mention': """
        {competitor} ist in der Tat eine Option.
        
        Unsere Kunden schätzen besonders:
        - {differentiator_1}
        - {differentiator_2}
        - {differentiator_3}
        
        Wäre es hilfreich, wenn ich Ihnen eine Vergleichsübersicht zusende?
        """,
        
        'not_interested': """
        Das verstehe ich vollkommen.
        
        Darf ich fragen, was der Hauptgrund für Ihr geringes Interesse ist?
        Vielleicht kann ich ein Missverständnis ausräumen.
        
        Falls nicht, respektiere ich natürlich Ihre Entscheidung.
        Wann darf ich mich gegebenenfalls wieder melden?
        """,
        
        'need_time': """
        Natürlich, das ist eine wichtige Entscheidung.
        
        Gibt es spezifische Punkte, die Sie noch klären müssen?
        Ich kann Ihnen gerne zusätzliche Informationen bereitstellen.
        
        Wann wäre ein guter Zeitpunkt für unser nächstes Gespräch?
        """
    },
    
    # ============================================
    # TERMINE & MEETINGS
    # ============================================
    'appointment': {
        'scheduling': """
        Perfekt, lassen Sie uns einen Termin finden.
        
        Ich habe folgende Optionen:
        - {option_1}
        - {option_2}
        - {option_3}
        
        Welcher Termin passt Ihnen am besten?
        Oder möchten Sie einen anderen Zeitpunkt vorschlagen?
        """,
        
        'confirmation': """
        Wunderbar! Ich habe unseren Termin bestätigt:
        
        📅 Datum: {date}
        ⏰ Uhrzeit: {time}
        📍 Ort/Medium: {location}
        👥 Teilnehmer: {participants}
        
        Sie erhalten gleich eine Kalendereinladung per E-Mail.
        Gibt es noch etwas, was Sie für das Meeting benötigen?
        """,
        
        'reminder': """
        Guten Tag {name},
        
        ich möchte Sie an unseren Termin erinnern:
        {appointment_details}
        
        Sind Sie noch verfügbar?
        Benötigen Sie noch Informationen für unser Gespräch?
        """
    },
    
    # ============================================
    # NOTFALL & PRIORITÄT
    # ============================================
    'emergency_handling': {
        'detected': """
        Ich habe einen Notfall erkannt.
        Ich verbinde Sie SOFORT mit der zuständigen Stelle.
        Bitte bleiben Sie in der Leitung!
        """,
        
        'high_priority': """
        Ich verstehe, dass dies dringend ist.
        Lassen Sie mich sofort jemanden für Sie finden.
        Einen Moment bitte.
        """
    }
}

# Intent-Erkennungs-Patterns
INTENT_PATTERNS = {
    'booking': ['buchen', 'reservieren', 'zimmer', 'übernachtung', 'verfügbarkeit'],
    'support': ['problem', 'hilfe', 'funktioniert nicht', 'fehler', 'kaputt'],
    'sales': ['kaufen', 'preis', 'kosten', 'angebot', 'rabatt'],
    'information': ['information', 'frage', 'wissen', 'erkläre', 'was ist'],
    'complaint': ['beschwerde', 'unzufrieden', 'schlecht', 'problem', 'ärger'],
    'appointment': ['termin', 'treffen', 'meeting', 'besprechung', 'zeit']
}

# Dynamische Script-Generierung
def generate_personalized_script(
    script_type: str,
    context: dict
) -> str:
    """
    Generiert personalisierte Scripts basierend auf Kontext
    
    Args:
        script_type: Typ des Scripts (z.B. 'hotel_receptionist.initial_greeting')
        context: Dictionary mit Kontextdaten (name, company, topic, etc.)
    
    Returns:
        Personalisiertes Script
    """
    # Script-Template holen
    parts = script_type.split('.')
    if len(parts) == 2:
        category, script_key = parts
        if category in AGENT_SCRIPTS and script_key in AGENT_SCRIPTS[category]:
            template = AGENT_SCRIPTS[category][script_key]
            
            # Template mit Kontext füllen
            try:
                return template.format(**context)
            except KeyError as e:
                # Fehlende Kontext-Werte mit Defaults ersetzen
                defaults = {
                    'name': 'Kunde',
                    'agent_name': 'Ihr KI-Assistent',
                    'company': 'VocalIQ',
                    'hotel_name': 'Hotel Alpenblick',
                    'topic': 'unser Angebot',
                    'product': 'unsere Lösung'
                }
                context_with_defaults = {**defaults, **context}
                return template.format(**context_with_defaults)
    
    # Fallback
    return "Wie kann ich Ihnen helfen?"
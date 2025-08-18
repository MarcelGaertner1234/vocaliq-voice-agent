"""
Subscription and Feature Management
Preismodelle und Feature-Gates für VocalIQ
"""
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

class SubscriptionPlan(str, Enum):
    """Verfügbare Subscription Plans"""
    FREE = "free"           # Test-Account
    BASIC = "basic"         # 49€/Monat
    PROFESSIONAL = "professional"  # 149€/Monat
    ENTERPRISE = "enterprise"      # 399€/Monat
    CUSTOM = "custom"       # Individuelle Vereinbarung


class Feature(str, Enum):
    """Alle verfügbaren Features"""
    # Basis Features (alle Plans)
    VOICE_AGENT = "voice_agent"
    BASIC_ROUTING = "basic_routing"
    CALL_HISTORY = "call_history"
    KNOWLEDGE_BASE_BASIC = "knowledge_base_basic"
    
    # Professional Features
    LEAD_SCORING = "lead_scoring"
    LEAD_DASHBOARD = "lead_dashboard"
    MANUAL_FOLLOW_UP = "manual_follow_up"
    KNOWLEDGE_BASE_PRO = "knowledge_base_pro"
    BASIC_ANALYTICS = "basic_analytics"
    
    # Enterprise Features
    AUTO_FOLLOW_UP = "auto_follow_up"
    LEAD_REACTIVATION = "lead_reactivation"
    LEAD_ENRICHMENT = "lead_enrichment"
    ROI_ANALYTICS = "roi_analytics"
    BULK_OPERATIONS = "bulk_operations"
    API_ACCESS = "api_access"
    CUSTOM_SCRIPTS = "custom_scripts"
    WHITE_LABEL = "white_label"
    PRIORITY_SUPPORT = "priority_support"


class PlanLimits(BaseModel):
    """Limits für jeden Plan"""
    max_leads: Optional[int] = None
    max_calls_per_month: Optional[int] = None
    max_knowledge_docs: int = 5
    max_users: int = 1
    max_phone_numbers: int = 1
    included_minutes: int = 100
    max_follow_ups_per_month: Optional[int] = None


# Feature-Zuordnung zu Plans
FEATURE_MATRIX: Dict[SubscriptionPlan, List[Feature]] = {
    SubscriptionPlan.FREE: [
        Feature.VOICE_AGENT,
        Feature.BASIC_ROUTING,
        Feature.CALL_HISTORY,
    ],
    
    SubscriptionPlan.BASIC: [
        Feature.VOICE_AGENT,
        Feature.BASIC_ROUTING,
        Feature.CALL_HISTORY,
        Feature.KNOWLEDGE_BASE_BASIC,
    ],
    
    SubscriptionPlan.PROFESSIONAL: [
        Feature.VOICE_AGENT,
        Feature.BASIC_ROUTING,
        Feature.CALL_HISTORY,
        Feature.KNOWLEDGE_BASE_BASIC,
        Feature.LEAD_SCORING,
        Feature.LEAD_DASHBOARD,
        Feature.MANUAL_FOLLOW_UP,
        Feature.KNOWLEDGE_BASE_PRO,
        Feature.BASIC_ANALYTICS,
    ],
    
    SubscriptionPlan.ENTERPRISE: [
        # Alle Features
        Feature.VOICE_AGENT,
        Feature.BASIC_ROUTING,
        Feature.CALL_HISTORY,
        Feature.KNOWLEDGE_BASE_BASIC,
        Feature.LEAD_SCORING,
        Feature.LEAD_DASHBOARD,
        Feature.MANUAL_FOLLOW_UP,
        Feature.KNOWLEDGE_BASE_PRO,
        Feature.BASIC_ANALYTICS,
        Feature.AUTO_FOLLOW_UP,
        Feature.LEAD_REACTIVATION,
        Feature.LEAD_ENRICHMENT,
        Feature.ROI_ANALYTICS,
        Feature.BULK_OPERATIONS,
        Feature.API_ACCESS,
        Feature.CUSTOM_SCRIPTS,
        Feature.WHITE_LABEL,
        Feature.PRIORITY_SUPPORT,
    ],
    
    SubscriptionPlan.CUSTOM: [
        # Individuell konfigurierbar
    ]
}

# Plan Limits
PLAN_LIMITS: Dict[SubscriptionPlan, PlanLimits] = {
    SubscriptionPlan.FREE: PlanLimits(
        max_leads=10,
        max_calls_per_month=50,
        max_knowledge_docs=2,
        max_users=1,
        max_phone_numbers=1,
        included_minutes=30,
        max_follow_ups_per_month=0
    ),
    
    SubscriptionPlan.BASIC: PlanLimits(
        max_leads=100,
        max_calls_per_month=500,
        max_knowledge_docs=5,
        max_users=2,
        max_phone_numbers=1,
        included_minutes=100,
        max_follow_ups_per_month=0
    ),
    
    SubscriptionPlan.PROFESSIONAL: PlanLimits(
        max_leads=500,
        max_calls_per_month=2000,
        max_knowledge_docs=50,
        max_users=5,
        max_phone_numbers=3,
        included_minutes=500,
        max_follow_ups_per_month=100
    ),
    
    SubscriptionPlan.ENTERPRISE: PlanLimits(
        max_leads=None,  # Unlimited
        max_calls_per_month=None,  # Unlimited
        max_knowledge_docs=500,
        max_users=50,
        max_phone_numbers=10,
        included_minutes=2000,
        max_follow_ups_per_month=None  # Unlimited
    ),
    
    SubscriptionPlan.CUSTOM: PlanLimits(
        # Individuell vereinbart
    )
}

# Preise in EUR (monatlich)
PLAN_PRICES: Dict[SubscriptionPlan, float] = {
    SubscriptionPlan.FREE: 0.0,
    SubscriptionPlan.BASIC: 49.0,
    SubscriptionPlan.PROFESSIONAL: 149.0,
    SubscriptionPlan.ENTERPRISE: 399.0,
    SubscriptionPlan.CUSTOM: 0.0  # Individuell
}

# Add-On Preise
ADDON_PRICES = {
    'extra_100_leads': 10.0,
    'extra_500_minutes': 40.0,
    'premium_voices': 20.0,
    'custom_script': 500.0,  # Einmalig
    'white_label': 100.0,
    'extra_phone_number': 15.0,
}

# Usage-Based Preise
USAGE_PRICES = {
    'minute_overage': 0.10,  # Pro Minute nach Kontingent
    'sms_follow_up': 0.15,   # Pro SMS
    'lead_enrichment': 0.50, # Pro Lead
    'api_call': 0.001,       # Pro API Call nach Kontingent
}


class SubscriptionService:
    """Service für Subscription und Feature Management"""
    
    @staticmethod
    def has_feature(plan: SubscriptionPlan, feature: Feature) -> bool:
        """
        Prüft ob ein Plan ein Feature hat
        
        Args:
            plan: Der Subscription Plan
            feature: Das zu prüfende Feature
            
        Returns:
            True wenn Feature verfügbar, sonst False
        """
        if plan == SubscriptionPlan.CUSTOM:
            # Custom Plans müssen individuell geprüft werden
            return True  # Oder aus Datenbank laden
        
        return feature in FEATURE_MATRIX.get(plan, [])
    
    @staticmethod
    def get_plan_features(plan: SubscriptionPlan) -> List[Feature]:
        """
        Gibt alle Features eines Plans zurück
        
        Args:
            plan: Der Subscription Plan
            
        Returns:
            Liste der verfügbaren Features
        """
        return FEATURE_MATRIX.get(plan, [])
    
    @staticmethod
    def get_plan_limits(plan: SubscriptionPlan) -> PlanLimits:
        """
        Gibt die Limits eines Plans zurück
        
        Args:
            plan: Der Subscription Plan
            
        Returns:
            PlanLimits Objekt
        """
        return PLAN_LIMITS.get(plan, PlanLimits())
    
    @staticmethod
    def check_limit(
        plan: SubscriptionPlan,
        limit_type: str,
        current_value: int
    ) -> bool:
        """
        Prüft ob ein Limit erreicht wurde
        
        Args:
            plan: Der Subscription Plan
            limit_type: Art des Limits (z.B. 'max_leads')
            current_value: Aktueller Wert
            
        Returns:
            True wenn noch im Limit, False wenn überschritten
        """
        limits = PLAN_LIMITS.get(plan)
        if not limits:
            return True
        
        limit_value = getattr(limits, limit_type, None)
        if limit_value is None:  # Unlimited
            return True
        
        return current_value < limit_value
    
    @staticmethod
    def get_upgrade_benefits(current_plan: SubscriptionPlan) -> Dict:
        """
        Zeigt die Vorteile eines Upgrades
        
        Args:
            current_plan: Aktueller Plan
            
        Returns:
            Dictionary mit Upgrade-Vorteilen
        """
        benefits = {}
        
        if current_plan == SubscriptionPlan.BASIC:
            benefits['professional'] = {
                'new_features': [
                    'Lead Scoring - Automatische Lead-Bewertung',
                    'Lead Dashboard - Übersicht aller Leads',
                    'Follow-Up Erinnerungen',
                    '50 Knowledge Base Dokumente',
                    'Basic Analytics'
                ],
                'increased_limits': {
                    'leads': '500 statt 100',
                    'calls': '2000 statt 500',
                    'minutes': '500 statt 100'
                },
                'price_difference': PLAN_PRICES[SubscriptionPlan.PROFESSIONAL] - PLAN_PRICES[SubscriptionPlan.BASIC]
            }
            
        elif current_plan == SubscriptionPlan.PROFESSIONAL:
            benefits['enterprise'] = {
                'new_features': [
                    'Automatisches Follow-Up - 30% mehr Umsatz!',
                    'Lead Reaktivierung - Alte Leads wiederbeleben',
                    'Lead Enrichment - LinkedIn & Firmendaten',
                    'ROI Analytics - Conversion Tracking',
                    'API Zugang',
                    'Priority Support'
                ],
                'increased_limits': {
                    'leads': 'Unlimited',
                    'calls': 'Unlimited',
                    'minutes': '2000 included'
                },
                'price_difference': PLAN_PRICES[SubscriptionPlan.ENTERPRISE] - PLAN_PRICES[SubscriptionPlan.PROFESSIONAL]
            }
        
        return benefits
    
    @staticmethod
    def calculate_overage_cost(
        plan: SubscriptionPlan,
        usage: Dict[str, int]
    ) -> float:
        """
        Berechnet Kosten für Übernutzung
        
        Args:
            plan: Der Subscription Plan
            usage: Dictionary mit Nutzungsdaten
            
        Returns:
            Zusatzkosten in EUR
        """
        limits = PLAN_LIMITS.get(plan)
        if not limits:
            return 0.0
        
        overage_cost = 0.0
        
        # Minuten-Übernutzung
        included_minutes = limits.included_minutes
        used_minutes = usage.get('minutes', 0)
        if used_minutes > included_minutes:
            overage_minutes = used_minutes - included_minutes
            overage_cost += overage_minutes * USAGE_PRICES['minute_overage']
        
        # SMS Follow-Ups (nur wenn Feature verfügbar)
        if SubscriptionService.has_feature(plan, Feature.AUTO_FOLLOW_UP):
            sms_count = usage.get('sms_follow_ups', 0)
            overage_cost += sms_count * USAGE_PRICES['sms_follow_up']
        
        # Lead Enrichment (nur Enterprise)
        if SubscriptionService.has_feature(plan, Feature.LEAD_ENRICHMENT):
            enrichment_count = usage.get('lead_enrichments', 0)
            overage_cost += enrichment_count * USAGE_PRICES['lead_enrichment']
        
        return round(overage_cost, 2)
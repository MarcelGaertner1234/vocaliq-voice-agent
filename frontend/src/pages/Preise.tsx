import React, { useState, useEffect } from 'react'
import '../styles/professional.css'

export default function Preise() {
  const [darkMode, setDarkMode] = useState(false)
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)

  useEffect(() => {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true)
    }
  }, [])

  const plans = [
    {
      name: 'Starter',
      description: 'Perfekt für kleine Unternehmen und Startups',
      setupCost: 2500,
      monthlyCost: 499,
      yearlyDiscount: 0.15,
      features: [
        'Bis zu 500 Anrufe/Monat',
        '1 Telefonnummer',
        'Basis KI-Modell',
        'E-Mail Support',
        'Standard Integrationen',
        'Basis Analytics',
        '99.5% Verfügbarkeit',
        'Onboarding Workshop (2h)'
      ],
      limitations: [
        'Keine Custom Voices',
        'Keine API-Zugriff',
        'Keine Mehrsprachigkeit'
      ],
      recommended: false
    },
    {
      name: 'Professional',
      description: 'Ideal für wachsende Unternehmen mit höheren Anforderungen',
      setupCost: 7500,
      monthlyCost: 1499,
      yearlyDiscount: 0.15,
      features: [
        'Bis zu 5.000 Anrufe/Monat',
        '5 Telefonnummern',
        'Advanced KI-Modell (GPT-4)',
        'Priority Support (24h Response)',
        'Alle Integrationen',
        'Advanced Analytics & Reports',
        '99.9% Verfügbarkeit SLA',
        'Onboarding Package (8h)',
        'Custom Voice Training',
        'API-Zugriff',
        '3 Sprachen inklusive',
        'A/B Testing',
        'Call Recording & Transcripts'
      ],
      limitations: [],
      recommended: true
    },
    {
      name: 'Enterprise',
      description: 'Maßgeschneiderte Lösungen für Großunternehmen',
      setupCost: null,
      monthlyCost: null,
      yearlyDiscount: 0,
      features: [
        'Unbegrenzte Anrufe',
        'Unbegrenzte Telefonnummern',
        'Dedizierte KI-Modelle',
        '24/7 Premium Support',
        'Custom Integrationen',
        'Enterprise Analytics',
        '99.99% Verfügbarkeit SLA',
        'Vollständiges Onboarding',
        'Unlimited Custom Voices',
        'Full API Access',
        'Alle Sprachen',
        'On-Premise Option',
        'Dedizierter Account Manager',
        'Custom Compliance & Security',
        'Service Level Agreement'
      ],
      limitations: [],
      recommended: false
    }
  ]

  const implementationSteps = [
    { phase: 'Analyse & Planung', duration: '1-2 Wochen', included: ['Anforderungsanalyse', 'Prozessmapping', 'Systemarchitektur'] },
    { phase: 'Setup & Integration', duration: '2-3 Wochen', included: ['Systemeinrichtung', 'API-Integration', 'Datenmigration'] },
    { phase: 'Training & Testing', duration: '1-2 Wochen', included: ['KI-Training', 'Testläufe', 'Optimierung'] },
    { phase: 'Go-Live & Support', duration: 'Ongoing', included: ['Produktivschaltung', 'Monitoring', 'Support'] }
  ]

  const calculatePrice = (plan: typeof plans[0]) => {
    if (!plan.monthlyCost) return 'Individuell'
    
    const monthlyPrice = plan.monthlyCost
    const yearlyPrice = billingCycle === 'yearly' 
      ? Math.round(monthlyPrice * 12 * (1 - plan.yearlyDiscount))
      : monthlyPrice * 12

    return billingCycle === 'monthly' 
      ? `${monthlyPrice.toLocaleString('de-DE')}€/Monat`
      : `${Math.round(yearlyPrice / 12).toLocaleString('de-DE')}€/Monat`
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-slate-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className={`fixed top-0 left-0 right-0 z-50 ${darkMode ? 'bg-slate-900/95' : 'bg-white/95'} backdrop-blur-md border-b ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <a href="/#/" className="flex items-center gap-3">
                <div className={`h-10 w-10 rounded-lg ${darkMode ? 'bg-gradient-to-br from-slate-600 to-slate-700' : 'bg-gradient-to-br from-slate-700 to-slate-900'}`} />
                <div>
                  <span className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    VocalIQ
                  </span>
                  <span className={`block text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                    Enterprise Voice AI
                  </span>
                </div>
              </a>
            </div>
            <nav className="flex items-center gap-6">
              <a href="/#/" className={`text-sm font-medium ${darkMode ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Zurück zur Startseite
              </a>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2 rounded-lg ${darkMode ? 'bg-slate-800 text-slate-400' : 'bg-gray-100 text-gray-600'} transition-colors`}
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className={`text-5xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
              Transparente Preise für jeden Bedarf
            </h1>
            <p className={`text-xl ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-8 max-w-3xl mx-auto`}>
              Einmalige Implementierungskosten plus überschaubare monatliche Gebühren. 
              Keine versteckten Kosten, volle Kostenkontrolle.
            </p>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4 mb-12">
              <span className={`text-sm font-medium ${billingCycle === 'monthly' ? 'text-teal-600' : darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Monatlich
              </span>
              <button
                onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${billingCycle === 'yearly' ? 'bg-teal-600' : darkMode ? 'bg-slate-700' : 'bg-gray-300'}`}
              >
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'}`} />
              </button>
              <span className={`text-sm font-medium ${billingCycle === 'yearly' ? 'text-teal-600' : darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Jährlich <span className="text-teal-600 font-bold">(15% Rabatt)</span>
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative rounded-2xl p-8 ${
                  plan.recommended
                    ? 'ring-2 ring-teal-600 shadow-xl scale-105'
                    : ''
                } ${
                  darkMode ? 'bg-slate-800/50' : 'bg-white'
                } border ${
                  darkMode ? 'border-slate-700' : 'border-gray-200'
                } hover:shadow-lg transition-all duration-200`}
              >
                {plan.recommended && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="bg-gradient-to-r from-teal-600 to-teal-700 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      EMPFOHLEN
                    </span>
                  </div>
                )}

                <div className="mb-6">
                  <h3 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-2`}>
                    {plan.name}
                  </h3>
                  <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'} text-sm`}>
                    {plan.description}
                  </p>
                </div>

                {/* Implementation Cost */}
                <div className={`mb-4 p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-gray-50'}`}>
                  <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'} mb-1`}>
                    Einmalige Implementierung
                  </p>
                  <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    {plan.setupCost ? `${plan.setupCost.toLocaleString('de-DE')}€` : 'Auf Anfrage'}
                  </p>
                </div>

                {/* Monthly Cost */}
                <div className={`mb-6 p-4 rounded-lg ${darkMode ? 'bg-slate-900/50' : 'bg-gray-50'}`}>
                  <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'} mb-1`}>
                    Laufende Kosten
                  </p>
                  <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    {calculatePrice(plan)}
                  </p>
                  {billingCycle === 'yearly' && plan.yearlyDiscount > 0 && (
                    <p className={`text-sm ${darkMode ? 'text-teal-400' : 'text-teal-600'} mt-1`}>
                      Sie sparen {Math.round(plan.monthlyCost! * 12 * plan.yearlyDiscount).toLocaleString('de-DE')}€/Jahr
                    </p>
                  )}
                </div>

                {/* Features */}
                <div className="mb-6">
                  <h4 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                    Inklusive:
                  </h4>
                  <ul className="space-y-2">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-teal-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Limitations */}
                {plan.limitations.length > 0 && (
                  <div className="mb-6">
                    <ul className="space-y-2">
                      {plan.limitations.map((limitation, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <svg className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          <span className={`text-sm ${darkMode ? 'text-slate-500' : 'text-gray-500'}`}>
                            {limitation}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* CTA Button */}
                <button
                  onClick={() => setSelectedPlan(plan.name)}
                  className={`w-full py-3 rounded-lg font-semibold transition-all duration-200 ${
                    plan.recommended
                      ? 'bg-gradient-to-r from-teal-600 to-teal-700 text-white hover:from-teal-700 hover:to-teal-800'
                      : plan.name === 'Enterprise'
                      ? darkMode
                        ? 'bg-slate-700 text-white hover:bg-slate-600'
                        : 'bg-slate-900 text-white hover:bg-black'
                      : darkMode
                      ? 'bg-slate-700 text-white hover:bg-slate-600'
                      : 'bg-gray-100 text-slate-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.name === 'Enterprise' ? 'Kontakt aufnehmen' : 'Jetzt starten'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Implementation Timeline */}
      <section className={`py-16 ${darkMode ? 'bg-slate-800/30' : 'bg-gray-50'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} text-center mb-12`}>
            Implementierungsprozess
          </h2>
          <div className="grid md:grid-cols-4 gap-6">
            {implementationSteps.map((step, idx) => (
              <div key={idx} className="relative">
                <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-full bg-teal-600 text-white flex items-center justify-center font-bold">
                      {idx + 1}
                    </div>
                    <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      {step.phase}
                    </h3>
                  </div>
                  <p className={`text-sm ${darkMode ? 'text-teal-400' : 'text-teal-600'} mb-3`}>
                    {step.duration}
                  </p>
                  <ul className="space-y-1">
                    {step.included.map((item, itemIdx) => (
                      <li key={itemIdx} className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                        • {item}
                      </li>
                    ))}
                  </ul>
                </div>
                {idx < implementationSteps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2">
                    <svg className="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Cost Benefits */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className={`rounded-2xl p-12 ${darkMode ? 'bg-gradient-to-br from-teal-900/20 to-slate-800/50' : 'bg-gradient-to-br from-teal-50 to-slate-50'}`}>
            <h2 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-8 text-center`}>
              Ihre Kostenersparnis mit VocalIQ
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className={`text-4xl font-bold ${darkMode ? 'text-teal-400' : 'text-teal-600'} mb-2`}>
                  -65%
                </div>
                <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  Personalkosten im Kundenservice
                </p>
              </div>
              <div className="text-center">
                <div className={`text-4xl font-bold ${darkMode ? 'text-teal-400' : 'text-teal-600'} mb-2`}>
                  24/7
                </div>
                <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  Verfügbarkeit ohne Mehrkosten
                </p>
              </div>
              <div className="text-center">
                <div className={`text-4xl font-bold ${darkMode ? 'text-teal-400' : 'text-teal-600'} mb-2`}>
                  ROI &lt; 6
                </div>
                <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  Monate Amortisationszeit
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-16">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <h2 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} text-center mb-12`}>
            Häufige Fragen zu Kosten
          </h2>
          <div className="space-y-6">
            <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-2`}>
                Was ist in den Implementierungskosten enthalten?
              </h3>
              <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Die Implementierungskosten decken die komplette Einrichtung ab: Systemsetup, Integration in Ihre bestehende IT-Infrastruktur, 
                KI-Training mit Ihren Daten, Mitarbeiterschulung und Support während der Einführungsphase.
              </p>
            </div>

            <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-2`}>
                Gibt es versteckte Kosten?
              </h3>
              <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Nein. Alle Kosten sind transparent aufgeführt. Die monatlichen Gebühren beinhalten alle Updates, Support und die vereinbarte Anzahl an Anrufen. 
                Nur bei Überschreitung des Kontingents fallen zusätzliche Kosten an (0,05€ pro zusätzlichem Anruf).
              </p>
            </div>

            <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-2`}>
                Kann ich das Paket später wechseln?
              </h3>
              <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Ja, Sie können jederzeit upgraden. Ein Downgrade ist zum Ende der Vertragslaufzeit möglich. 
                Beim Upgrade zahlen Sie nur die Differenz der Implementierungskosten.
              </p>
            </div>

            <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
              <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-2`}>
                Welche Zahlungsmethoden werden akzeptiert?
              </h3>
              <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Wir akzeptieren Überweisung, SEPA-Lastschrift und für Enterprise-Kunden auch individuelle Zahlungsvereinbarungen. 
                Die Implementierungskosten werden zu 50% bei Vertragsabschluss und 50% bei Go-Live fällig.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className={`py-16 ${darkMode ? 'bg-slate-800/30' : 'bg-gray-50'}`}>
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
          <h2 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
            Bereit für die Zukunft der Kundenkommunikation?
          </h2>
          <p className={`text-xl ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-8`}>
            Lassen Sie uns gemeinsam berechnen, wie viel Sie mit VocalIQ sparen können.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/#/kontakt"
              className="px-8 py-4 rounded-lg font-semibold bg-gradient-to-r from-teal-600 to-teal-700 text-white hover:from-teal-700 hover:to-teal-800 transition-all duration-200"
            >
              Kostenlose Beratung
            </a>
            <button
              className={`px-8 py-4 rounded-lg font-semibold ${darkMode ? 'bg-slate-700 text-white hover:bg-slate-600' : 'bg-white text-slate-900 hover:bg-gray-100'} transition-colors`}
            >
              ROI-Rechner starten
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={`py-12 ${darkMode ? 'bg-slate-900 border-t border-slate-800' : 'bg-white border-t border-gray-200'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-3 mb-4 md:mb-0">
              <div className={`h-8 w-8 rounded-lg ${darkMode ? 'bg-gradient-to-br from-slate-600 to-slate-700' : 'bg-gradient-to-br from-slate-700 to-slate-900'}`} />
              <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                © 2024 VocalIQ GmbH. Alle Rechte vorbehalten.
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a href="/#/datenschutz" className={`text-sm ${darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Datenschutz
              </a>
              <a href="/#/impressum" className={`text-sm ${darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Impressum
              </a>
              <a href="/#/agb" className={`text-sm ${darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                AGB
              </a>
              <a href="/#/kontakt" className={`text-sm ${darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Kontakt
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
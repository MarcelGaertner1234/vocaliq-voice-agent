import React, { useEffect, useState, useRef } from 'react'
import apiClient from '../services/api'
import VoiceChat from '../components/VoiceChat'
import '../styles/professional.css'

export default function Landing() {
  const [voices, setVoices] = useState<Array<{voice_id: string; name: string; preview_url?: string | null}>>([])
  const [loading, setLoading] = useState(false)
  const [sampleText, setSampleText] = useState('Guten Tag! Wie kann ich Ihnen bei Ihrem Anliegen behilflich sein?')
  const [playing, setPlaying] = useState<string | null>(null)
  const [voiceId, setVoiceId] = useState('21m00Tcm4TlvDq8ikWAM')
  const [darkMode, setDarkMode] = useState(false)
  const [showDemo, setShowDemo] = useState(false)
  const [scrollY, setScrollY] = useState(0)
  const [activeTab, setActiveTab] = useState('implementation')
  const [roiCalculator, setRoiCalculator] = useState({
    calls: 1000,
    avgDuration: 5,
    costPerMinute: 0.5
  })

  useEffect(() => {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true)
    }

    const handleScroll = () => {
      setScrollY(window.scrollY)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        let res = await apiClient.get('/voices/all')
        let list = Array.isArray(res.data) && res.data.length ? res.data : []
        if (!list.length) {
          const rec = await apiClient.get('/voices/recommended', { params: { language: 'de' } })
          list = rec.data || []
        }
        setVoices(list)
        if (list.length) setVoiceId(list[0].voice_id)
      } catch {
        setVoices([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const play = async (id: string) => {
    try {
      setPlaying(id)
      const res = await apiClient.post('/voices/tts', { 
        text: sampleText, 
        voice_id: id, 
        stability: 0.5, 
        similarity_boost: 0.75, 
        style: 0.0 
      })
      const url: string | undefined = res.data?.audio_url
      if (url) {
        const a = new Audio(url)
        await a.play()
      }
    } catch {
      // ignore
    } finally {
      setPlaying(null)
    }
  }

  const calculateROI = () => {
    const humanCost = roiCalculator.calls * roiCalculator.avgDuration * roiCalculator.costPerMinute
    const aiCost = roiCalculator.calls * roiCalculator.avgDuration * 0.1 // AI costs 80% less
    const savings = humanCost - aiCost
    return {
      humanCost: humanCost.toFixed(2),
      aiCost: aiCost.toFixed(2),
      savings: savings.toFixed(2),
      percentage: ((savings / humanCost) * 100).toFixed(0)
    }
  }

  const roi = calculateROI()

  const industries = [
    {
      name: 'Gesundheitswesen',
      icon: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z',
      benefits: ['Terminvereinbarung', 'Patientenbetreuung', 'Notfallweiterleitung']
    },
    {
      name: 'E-Commerce',
      icon: 'M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z',
      benefits: ['Bestellannahme', 'Sendungsverfolgung', 'Produktberatung']
    },
    {
      name: 'Finanzdienstleister',
      icon: 'M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z',
      benefits: ['Kontostandsabfrage', 'Betrugserkennung', 'Kreditberatung']
    },
    {
      name: 'Versicherungen',
      icon: 'M12 2l-5.5 9h11z M12 2l-5.5 9h11z M12 2l-5.5 9h11z',
      benefits: ['Schadenmeldung', 'Policenverwaltung', 'Beratungstermine']
    },
    {
      name: 'Telekommunikation',
      icon: 'M3.62 6.4c-.39-.39-.39-1.02 0-1.41s1.02-.39 1.41 0L6.44 6.4c.39.39.39 1.02 0 1.41s-1.02.39-1.41 0L3.62 6.4zM6.4 3.62c.39-.39 1.02-.39 1.41 0s.39 1.02 0 1.41L6.4 6.44c-.39.39-1.02.39-1.41 0s-.39-1.02 0-1.41L6.4 3.62z',
      benefits: ['Störungsmeldung', 'Tarifberatung', 'Vertragsverwaltung']
    },
    {
      name: 'Reisebranche',
      icon: 'M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z',
      benefits: ['Buchungen', 'Stornierungen', 'Reiseberatung']
    }
  ]

  const capabilities = [
    {
      title: 'Intelligente Gesprächsführung',
      description: 'Natürliche Konversation mit Kontext-Verständnis und emotionaler Intelligenz',
      features: ['Multi-Turn Dialoge', 'Sentiment-Analyse', 'Intention-Erkennung']
    },
    {
      title: 'Nahtlose Integration',
      description: 'Verbindung mit allen gängigen CRM und ERP Systemen',
      features: ['REST API', 'Webhooks', 'Real-time Updates']
    },
    {
      title: 'Automatisierung',
      description: 'Vollautomatische Abwicklung von Standardprozessen',
      features: ['Terminbuchung', 'Datenabfrage', 'Ticketerstellung']
    },
    {
      title: 'Compliance & Sicherheit',
      description: 'DSGVO-konform mit höchsten Sicherheitsstandards',
      features: ['Ende-zu-Ende Verschlüsselung', 'Audit Logs', 'ISO 27001']
    }
  ]

  const implementationSteps = [
    {
      phase: 'Tag 1-7',
      title: 'Analyse & Setup',
      tasks: ['Anforderungsanalyse', 'Systemarchitektur', 'Datenimport']
    },
    {
      phase: 'Woche 2-3',
      title: 'Konfiguration',
      tasks: ['Dialogdesign', 'Integration APIs', 'Testszenarien']
    },
    {
      phase: 'Woche 4',
      title: 'Testing',
      tasks: ['Qualitätssicherung', 'Belastungstests', 'Feintuning']
    },
    {
      phase: 'Ab Woche 5',
      title: 'Go-Live',
      tasks: ['Produktivschaltung', 'Monitoring', 'Optimierung']
    }
  ]

  const caseStudies = [
    {
      company: 'MediCare GmbH',
      industry: 'Gesundheitswesen',
      metric: '73%',
      result: 'Reduzierung der Wartezeit',
      quote: 'Die KI-Lösung hat unsere Patientenbetreuung revolutioniert.'
    },
    {
      company: 'TechShop24',
      industry: 'E-Commerce',
      metric: '52%',
      result: 'Kosteneinsparung im Support',
      quote: 'Endlich können wir 24/7 Support bieten ohne Mehrkosten.'
    },
    {
      company: 'SecureBank AG',
      industry: 'Finanzwesen',
      metric: '95%',
      result: 'Kundenzufriedenheit',
      quote: 'Unsere Kunden schätzen die sofortige Verfügbarkeit.'
    }
  ]

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-slate-900' : 'bg-gray-50'}`}>
      {/* Professional Header */}
      <header className={`fixed top-0 left-0 right-0 z-50 ${darkMode ? 'bg-slate-900/95' : 'bg-white/95'} backdrop-blur-md border-b ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className={`h-10 w-10 rounded-lg ${darkMode ? 'bg-gradient-to-br from-slate-600 to-slate-700' : 'bg-gradient-to-br from-slate-700 to-slate-900'}`} />
              <div>
                <span className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  VocalIQ
                </span>
                <span className={`block text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  Enterprise Voice AI
                </span>
              </div>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              <a href="#capabilities" className={`text-sm font-medium ${darkMode ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Funktionen
              </a>
              <a href="#industries" className={`text-sm font-medium ${darkMode ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Branchen
              </a>
              <a href="#implementation" className={`text-sm font-medium ${darkMode ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Implementierung
              </a>
              <a href="#roi" className={`text-sm font-medium ${darkMode ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                ROI
              </a>
              
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2 rounded-lg ${darkMode ? 'bg-slate-800 text-slate-400' : 'bg-gray-100 text-gray-600'} transition-colors`}
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
              
              <a 
                href="/#/dashboard" 
                className={`px-6 py-2 rounded-lg font-medium text-white ${darkMode ? 'bg-teal-600 hover:bg-teal-700' : 'bg-slate-800 hover:bg-slate-900'} transition-colors`}
              >
                Demo anfragen
              </a>
            </nav>
          </div>
        </div>
      </header>

      <main className="pt-16">
        {/* Hero Section */}
        <section className="relative py-20 overflow-hidden">
          <div 
            className="absolute inset-0 -z-10"
            style={{
              background: darkMode 
                ? 'radial-gradient(ellipse at top, rgba(15, 118, 110, 0.1), transparent 50%)' 
                : 'radial-gradient(ellipse at top, rgba(71, 85, 105, 0.05), transparent 50%)'
            }}
          />
          
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className={`text-5xl lg:text-6xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-6`}>
                Intelligente Sprachassistenz
                <span className={`block ${darkMode ? 'text-teal-400' : 'text-slate-700'}`}>
                  für Ihr Unternehmen
                </span>
              </h1>
              <p className={`text-xl ${darkMode ? 'text-slate-300' : 'text-slate-600'} max-w-3xl mx-auto mb-8`}>
                Automatisieren Sie Ihre Kundenkommunikation mit modernster KI-Technologie. 
                24/7 verfügbar, skalierbar und DSGVO-konform.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => setShowDemo(true)}
                  className={`px-8 py-4 rounded-lg font-semibold text-white ${darkMode ? 'bg-teal-600 hover:bg-teal-700' : 'bg-slate-800 hover:bg-slate-900'} transition-colors`}
                >
                  Live Demo starten
                </button>
                <button
                  className={`px-8 py-4 rounded-lg font-semibold ${darkMode ? 'bg-slate-800 text-white hover:bg-slate-700' : 'bg-white text-slate-800 border border-slate-300 hover:bg-gray-50'} transition-colors`}
                >
                  Beratungsgespräch vereinbaren
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="flex items-center justify-center gap-8 mt-12 opacity-60">
                <div className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  Vertraut von führenden Unternehmen
                </div>
                <div className={`text-sm font-semibold ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  DSGVO konform
                </div>
                <div className={`text-sm font-semibold ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                  ISO 27001
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Capabilities Section */}
        <section id="capabilities" className={`py-20 ${darkMode ? 'bg-slate-800/50' : 'bg-white'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Was unser System kann
              </h2>
              <p className={`text-lg ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                Umfassende Funktionen für professionelle Kundenkommunikation
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {capabilities.map((capability, idx) => (
                <div key={idx} className={`p-8 rounded-xl ${darkMode ? 'bg-slate-900/50 border border-slate-700' : 'bg-gray-50 border border-gray-200'}`}>
                  <h3 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                    {capability.title}
                  </h3>
                  <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'} mb-4`}>
                    {capability.description}
                  </p>
                  <ul className="space-y-2">
                    {capability.features.map((feature, fidx) => (
                      <li key={fidx} className={`flex items-center gap-2 ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                        <svg className="w-5 h-5 text-teal-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Industries Section */}
        <section id="industries" className={`py-20 ${darkMode ? 'bg-slate-900' : 'bg-gray-50'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Branchen die wir unterstützen
              </h2>
              <p className={`text-lg ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                Maßgeschneiderte Lösungen für Ihre Branche
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {industries.map((industry, idx) => (
                <div key={idx} className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800 border border-slate-700' : 'bg-white border border-gray-200'} hover:shadow-lg transition-shadow`}>
                  <div className={`w-12 h-12 rounded-lg ${darkMode ? 'bg-teal-900/50' : 'bg-teal-50'} flex items-center justify-center mb-4`}>
                    <svg className="w-6 h-6 text-teal-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d={industry.icon} />
                    </svg>
                  </div>
                  <h3 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                    {industry.name}
                  </h3>
                  <ul className="space-y-2">
                    {industry.benefits.map((benefit, bidx) => (
                      <li key={bidx} className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'} flex items-center gap-2`}>
                        <span className="w-1.5 h-1.5 bg-teal-500 rounded-full" />
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Implementation Section */}
        <section id="implementation" className={`py-20 ${darkMode ? 'bg-slate-800/50' : 'bg-white'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                So setzen wir Ihr Projekt um
              </h2>
              <p className={`text-lg ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                Von der Analyse bis zum Go-Live in nur 4 Wochen
              </p>
            </div>

            <div className="grid md:grid-cols-4 gap-6">
              {implementationSteps.map((step, idx) => (
                <div key={idx} className="relative">
                  {idx < implementationSteps.length - 1 && (
                    <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-teal-500 to-transparent" />
                  )}
                  <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-900 border border-slate-700' : 'bg-gray-50 border border-gray-200'}`}>
                    <div className="text-teal-600 font-bold text-sm mb-2">{step.phase}</div>
                    <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                      {step.title}
                    </h3>
                    <ul className="space-y-1">
                      {step.tasks.map((task, tidx) => (
                        <li key={tidx} className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                          • {task}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ROI Calculator */}
        <section id="roi" className={`py-20 ${darkMode ? 'bg-slate-900' : 'bg-gray-50'}`}>
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                ROI Rechner
              </h2>
              <p className={`text-lg ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                Berechnen Sie Ihre potenzielle Kostenersparnis
              </p>
            </div>

            <div className={`p-8 rounded-xl ${darkMode ? 'bg-slate-800 border border-slate-700' : 'bg-white border border-gray-200'}`}>
              <div className="grid md:grid-cols-3 gap-6 mb-8">
                <div>
                  <label className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                    Anrufe pro Monat
                  </label>
                  <input
                    type="number"
                    value={roiCalculator.calls}
                    onChange={(e) => setRoiCalculator({...roiCalculator, calls: parseInt(e.target.value) || 0})}
                    className={`w-full px-4 py-2 rounded-lg ${darkMode ? 'bg-slate-900 border-slate-600 text-white' : 'bg-gray-50 border-gray-300'} border`}
                  />
                </div>
                <div>
                  <label className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                    Ø Gesprächsdauer (Min)
                  </label>
                  <input
                    type="number"
                    value={roiCalculator.avgDuration}
                    onChange={(e) => setRoiCalculator({...roiCalculator, avgDuration: parseInt(e.target.value) || 0})}
                    className={`w-full px-4 py-2 rounded-lg ${darkMode ? 'bg-slate-900 border-slate-600 text-white' : 'bg-gray-50 border-gray-300'} border`}
                  />
                </div>
                <div>
                  <label className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                    Kosten pro Minute (€)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={roiCalculator.costPerMinute}
                    onChange={(e) => setRoiCalculator({...roiCalculator, costPerMinute: parseFloat(e.target.value) || 0})}
                    className={`w-full px-4 py-2 rounded-lg ${darkMode ? 'bg-slate-900 border-slate-600 text-white' : 'bg-gray-50 border-gray-300'} border`}
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-6">
                <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900' : 'bg-gray-50'}`}>
                  <div className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'} mb-1`}>Aktuelle Kosten</div>
                  <div className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>€{roi.humanCost}</div>
                </div>
                <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-900' : 'bg-gray-50'}`}>
                  <div className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'} mb-1`}>Mit VocalIQ</div>
                  <div className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>€{roi.aiCost}</div>
                </div>
                <div className={`p-4 rounded-lg bg-gradient-to-r from-teal-500/10 to-emerald-500/10 border ${darkMode ? 'border-teal-700' : 'border-teal-200'}`}>
                  <div className={`text-sm ${darkMode ? 'text-teal-400' : 'text-teal-700'} mb-1`}>Ihre Ersparnis</div>
                  <div className="text-2xl font-bold text-teal-600">€{roi.savings} ({roi.percentage}%)</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Case Studies */}
        <section className={`py-20 ${darkMode ? 'bg-slate-800/50' : 'bg-white'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Erfolgsgeschichten
              </h2>
              <p className={`text-lg ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                So profitieren unsere Kunden von VocalIQ
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {caseStudies.map((study, idx) => (
                <div key={idx} className={`p-6 rounded-xl ${darkMode ? 'bg-slate-900 border border-slate-700' : 'bg-gray-50 border border-gray-200'}`}>
                  <div className="mb-4">
                    <div className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'} mb-1`}>{study.industry}</div>
                    <h3 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>{study.company}</h3>
                  </div>
                  <div className="text-center py-6">
                    <div className="text-4xl font-bold text-teal-600 mb-2">{study.metric}</div>
                    <div className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>{study.result}</div>
                  </div>
                  <blockquote className={`italic ${darkMode ? 'text-slate-400' : 'text-slate-600'} border-t ${darkMode ? 'border-slate-700' : 'border-gray-200'} pt-4`}>
                    "{study.quote}"
                  </blockquote>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Voice Selection */}
        <section className={`py-20 ${darkMode ? 'bg-slate-900' : 'bg-gray-50'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Professionelle Stimmen
              </h2>
              <div className="max-w-2xl mx-auto mt-6">
                <input
                  value={sampleText}
                  onChange={e => setSampleText(e.target.value)}
                  placeholder="Testen Sie unsere Stimmen..."
                  className={`w-full px-4 py-3 rounded-lg ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-gray-300'} border`}
                />
              </div>
            </div>

            {loading ? (
              <div className="flex justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {voices.map(v => (
                  <div
                    key={v.voice_id}
                    className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800 border border-slate-700' : 'bg-white border border-gray-200'} ${
                      voiceId === v.voice_id ? 'ring-2 ring-teal-500' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <div className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {v.name}
                        </div>
                        <div className={`text-xs ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
                          {v.voice_id.slice(0, 8)}...
                        </div>
                      </div>
                      {voiceId === v.voice_id && (
                        <span className="text-xs px-2 py-1 rounded bg-teal-500/20 text-teal-600">
                          Aktiv
                        </span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => play(v.voice_id)}
                        disabled={playing === v.voice_id}
                        className={`flex-1 px-3 py-2 rounded text-sm font-medium ${
                          playing === v.voice_id
                            ? 'bg-gray-300 text-gray-500'
                            : `${darkMode ? 'bg-slate-700 text-white hover:bg-slate-600' : 'bg-gray-100 text-slate-700 hover:bg-gray-200'}`
                        } transition-colors`}
                      >
                        {playing === v.voice_id ? 'Spielt...' : 'Abspielen'}
                      </button>
                      <button
                        onClick={() => setVoiceId(v.voice_id)}
                        className={`px-3 py-2 rounded text-sm font-medium ${
                          voiceId === v.voice_id
                            ? 'bg-teal-500 text-white'
                            : `${darkMode ? 'bg-slate-700 text-slate-400' : 'bg-gray-100 text-gray-600'}`
                        } transition-colors`}
                      >
                        {voiceId === v.voice_id ? '✓' : 'Wählen'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Demo Section */}
        <section className={`py-20 ${darkMode ? 'bg-slate-800/50' : 'bg-white'}`}>
          <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Testen Sie es selbst
              </h2>
              <p className={`text-lg ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                Erleben Sie die Zukunft der Kundenkommunikation
              </p>
            </div>

            <div className={`rounded-xl ${darkMode ? 'bg-slate-900 border border-slate-700' : 'bg-gray-50 border border-gray-200'} p-8`}>
              {showDemo ? (
                <VoiceChat voiceId={voiceId} language="de" />
              ) : (
                <div className="text-center py-12">
                  <svg className="w-20 h-20 mx-auto mb-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <h3 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                    Bereit für eine Live-Demo?
                  </h3>
                  <p className={`${darkMode ? 'text-slate-400' : 'text-slate-600'} mb-8 max-w-md mx-auto`}>
                    Testen Sie unsere KI-Sprachassistenz und erleben Sie, wie natürlich
                    und effizient automatisierte Gespräche sein können.
                  </p>
                  <button
                    onClick={() => setShowDemo(true)}
                    className={`px-8 py-4 rounded-lg font-semibold text-white ${darkMode ? 'bg-teal-600 hover:bg-teal-700' : 'bg-slate-800 hover:bg-slate-900'} transition-colors`}
                  >
                    Demo jetzt starten
                  </button>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className={`py-20 ${darkMode ? 'bg-gradient-to-r from-slate-900 to-slate-800' : 'bg-gradient-to-r from-slate-800 to-slate-900'}`}>
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-4xl font-bold text-white mb-4">
              Bereit für den nächsten Schritt?
            </h2>
            <p className="text-xl text-slate-300 mb-8">
              Lassen Sie uns gemeinsam Ihre Kundenkommunikation revolutionieren
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/#/dashboard"
                className="px-8 py-4 rounded-lg font-semibold bg-white text-slate-900 hover:bg-gray-100 transition-colors"
              >
                Kostenlose Beratung
              </a>
              <a
                href="/#/kontakt"
                className="px-8 py-4 rounded-lg font-semibold bg-teal-600 text-white hover:bg-teal-700 transition-colors inline-block text-center"
              >
                Kontakt aufnehmen
              </a>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className={`py-12 ${darkMode ? 'bg-slate-900 border-t border-slate-800' : 'bg-gray-100 border-t border-gray-200'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-3 mb-4 md:mb-0">
              <div className={`h-8 w-8 rounded-lg ${darkMode ? 'bg-gradient-to-br from-slate-600 to-slate-700' : 'bg-gradient-to-br from-slate-700 to-slate-900'}`} />
              <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                © 2024 VocalIQ GmbH. Alle Rechte vorbehalten.
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a href="/#/preise" className={`text-sm ${darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900'} transition-colors`}>
                Preise
              </a>
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
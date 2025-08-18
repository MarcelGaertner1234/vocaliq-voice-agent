import React, { useEffect, useState } from 'react'
import apiClient from '../services/api'
import VoiceChat from '../components/VoiceChat'

export default function ModernLanding() {
  const [voices, setVoices] = useState<Array<{voice_id: string; name: string; preview_url?: string | null}>>([])
  const [loading, setLoading] = useState(false)
  const [sampleText, setSampleText] = useState('Hallo! Ich bin Ihre KI-Assistentin. Wie kann ich Ihnen heute helfen?')
  const [playing, setPlaying] = useState<string | null>(null)
  const [voiceId, setVoiceId] = useState('21m00Tcm4TlvDq8ikWAM')
  const [darkMode, setDarkMode] = useState(false)
  const [showDemo, setShowDemo] = useState(false)

  useEffect(() => {
    // Check system dark mode preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true)
    }
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

  return (
    <div className={`min-h-screen transition-all duration-500 ${darkMode ? 'dark bg-gray-950' : 'bg-white'}`}>
      {/* Animated Background Gradient */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className={`absolute -top-40 -right-40 h-80 w-80 rounded-full ${darkMode ? 'bg-purple-800/20' : 'bg-purple-300/30'} blur-3xl animate-pulse`} />
        <div className={`absolute -bottom-40 -left-40 h-80 w-80 rounded-full ${darkMode ? 'bg-blue-800/20' : 'bg-blue-300/30'} blur-3xl animate-pulse animation-delay-2000`} />
        <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-96 w-96 rounded-full ${darkMode ? 'bg-indigo-800/10' : 'bg-indigo-200/20'} blur-3xl animate-pulse animation-delay-4000`} />
      </div>

      {/* Modern Navigation Bar */}
      <header className={`sticky top-0 z-50 ${darkMode ? 'bg-gray-950/80' : 'bg-white/80'} backdrop-blur-xl border-b ${darkMode ? 'border-gray-800' : 'border-gray-200'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 animate-gradient" />
                <div className="absolute inset-0 h-10 w-10 rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 blur animate-pulse" />
              </div>
              <div>
                <span className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>VocalIQ</span>
                <span className={`block text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>AI Voice Platform</span>
              </div>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              <a href="#features" className={`text-sm font-medium ${darkMode ? 'text-gray-300 hover:text-white' : 'text-gray-700 hover:text-gray-900'} transition-colors`}>
                Features
              </a>
              <a href="#voices" className={`text-sm font-medium ${darkMode ? 'text-gray-300 hover:text-white' : 'text-gray-700 hover:text-gray-900'} transition-colors`}>
                Stimmen
              </a>
              <a href="#demo" className={`text-sm font-medium ${darkMode ? 'text-gray-300 hover:text-white' : 'text-gray-700 hover:text-gray-900'} transition-colors`}>
                Live Demo
              </a>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2 rounded-lg ${darkMode ? 'bg-gray-800 text-yellow-400' : 'bg-gray-100 text-gray-700'} transition-all hover:scale-110`}
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
              <a 
                href="/#/dashboard" 
                className="relative inline-flex items-center gap-2 px-6 py-2.5 rounded-full font-medium text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all hover:scale-105 hover:shadow-lg hover:shadow-purple-500/25"
              >
                <span>App öffnen</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </a>
            </nav>

            {/* Mobile Menu Button */}
            <button className="md:hidden p-2">
              <svg className={`w-6 h-6 ${darkMode ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="relative py-24 lg:py-32 overflow-hidden">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 mb-6">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                <span className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                  Live & Ready
                </span>
              </div>

              {/* Main Heading */}
              <h1 className={`text-5xl lg:text-7xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-6`}>
                <span className="block">Telefonie trifft</span>
                <span className="block bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Künstliche Intelligenz
                </span>
              </h1>

              {/* Subtitle */}
              <p className={`text-xl ${darkMode ? 'text-gray-400' : 'text-gray-600'} max-w-3xl mx-auto mb-8`}>
                Erleben Sie die nächste Generation der Geschäftskommunikation. 
                Natürliche Gespräche, blitzschnelle Reaktionen, 24/7 verfügbar.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => setShowDemo(true)}
                  className="group relative inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all hover:scale-105 hover:shadow-xl hover:shadow-purple-500/25"
                >
                  <span>Live Demo starten</span>
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </button>
                <button
                  className={`inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold ${darkMode ? 'bg-gray-800 text-white hover:bg-gray-700' : 'bg-gray-100 text-gray-900 hover:bg-gray-200'} transition-all hover:scale-105`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Demo ansehen</span>
                </button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-8 mt-16 max-w-3xl mx-auto">
                <div className="text-center">
                  <div className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-1`}>
                    <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                      &lt;500ms
                    </span>
                  </div>
                  <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Reaktionszeit</div>
                </div>
                <div className="text-center">
                  <div className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-1`}>
                    <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                      99.9%
                    </span>
                  </div>
                  <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Verfügbarkeit</div>
                </div>
                <div className="text-center">
                  <div className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-1`}>
                    <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                      24/7
                    </span>
                  </div>
                  <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Erreichbar</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className={`py-24 ${darkMode ? 'bg-gray-900/50' : 'bg-gray-50'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className={`text-3xl lg:text-4xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-4`}>
                Enterprise-Ready Features
              </h2>
              <p className={`text-lg ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                Alles was Sie für professionelle KI-Telefonie brauchen
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[
                {
                  icon: '🎯',
                  title: 'Ultra-Low Latency',
                  description: 'Reaktionszeiten unter 500ms für natürliche Gespräche'
                },
                {
                  icon: '🧠',
                  title: 'Emotionale Intelligenz',
                  description: 'Erkennt Stimmungen und passt Ton entsprechend an'
                },
                {
                  icon: '🔄',
                  title: 'Nahtlose Unterbrechungen',
                  description: 'Natürliches Barge-In wie in echten Gesprächen'
                },
                {
                  icon: '🌍',
                  title: 'Mehrsprachig',
                  description: 'Über 29 Sprachen mit natürlichen Stimmen'
                },
                {
                  icon: '🔒',
                  title: 'Enterprise Security',
                  description: 'GDPR-konform mit End-to-End Verschlüsselung'
                },
                {
                  icon: '📊',
                  title: 'Analytics & Insights',
                  description: 'Detaillierte Gesprächsanalysen in Echtzeit'
                }
              ].map((feature, idx) => (
                <div
                  key={idx}
                  className={`group relative p-6 rounded-2xl ${darkMode ? 'bg-gray-800/50' : 'bg-white'} border ${darkMode ? 'border-gray-700' : 'border-gray-200'} hover:border-purple-500/50 transition-all hover:scale-105 hover:shadow-xl`}
                >
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-gray-900'} mb-2`}>
                    {feature.title}
                  </h3>
                  <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Voices Section */}
        <section id="voices" className={`py-24 ${darkMode ? 'bg-gray-950' : 'bg-white'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className={`text-3xl lg:text-4xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-4`}>
                Natürliche KI-Stimmen
              </h2>
              <p className={`text-lg ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-8`}>
                Wählen Sie aus unserer Bibliothek professioneller Stimmen
              </p>

              {/* Sample Text Input */}
              <div className="max-w-2xl mx-auto mb-8">
                <div className={`relative rounded-xl ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} p-1`}>
                  <input
                    value={sampleText}
                    onChange={e => setSampleText(e.target.value)}
                    placeholder="Geben Sie einen Text ein..."
                    className={`w-full px-4 py-3 rounded-lg ${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'} focus:outline-none focus:ring-2 focus:ring-purple-500`}
                  />
                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {voices.map(v => (
                  <div
                    key={v.voice_id}
                    className={`group relative rounded-2xl ${darkMode ? 'bg-gray-800/50' : 'bg-white'} border ${
                      voiceId === v.voice_id 
                        ? 'border-purple-500 shadow-lg shadow-purple-500/20' 
                        : darkMode ? 'border-gray-700' : 'border-gray-200'
                    } p-6 transition-all hover:scale-105 hover:shadow-xl`}
                  >
                    {voiceId === v.voice_id && (
                      <div className="absolute -top-3 -right-3">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-purple-600 to-blue-600 text-white">
                          Ausgewählt
                        </span>
                      </div>
                    )}
                    
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`h-12 w-12 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold`}>
                        {v.name.charAt(0)}
                      </div>
                      <div>
                        <div className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                          {v.name}
                        </div>
                        <div className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                          Voice ID: {v.voice_id.slice(0, 8)}...
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => play(v.voice_id)}
                        disabled={playing === v.voice_id}
                        className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                          playing === v.voice_id
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700'
                        }`}
                      >
                        {playing === v.voice_id ? (
                          <span className="flex items-center justify-center gap-2">
                            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Spielt...
                          </span>
                        ) : (
                          <span className="flex items-center justify-center gap-2">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                            </svg>
                            Anhören
                          </span>
                        )}
                      </button>
                      <button
                        onClick={() => setVoiceId(v.voice_id)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                          voiceId === v.voice_id
                            ? `${darkMode ? 'bg-gray-700 text-purple-400' : 'bg-purple-100 text-purple-700'}`
                            : `${darkMode ? 'bg-gray-700 text-gray-400 hover:text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`
                        }`}
                      >
                        {voiceId === v.voice_id ? '✓' : '○'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Live Demo Section */}
        <section id="demo" className={`py-24 ${darkMode ? 'bg-gray-900/50' : 'bg-gray-50'}`}>
          <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className={`text-3xl lg:text-4xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-4`}>
                Erleben Sie es selbst
              </h2>
              <p className={`text-lg ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-2`}>
                Führen Sie ein echtes Gespräch mit unserer KI
              </p>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                <span className={`text-sm font-medium ${darkMode ? 'text-green-400' : 'text-green-700'}`}>
                  Live · Ausgewählte Stimme: {voices.find(v => v.voice_id === voiceId)?.name || 'Standard'}
                </span>
              </div>
            </div>

            {/* Demo Container */}
            <div className={`relative rounded-3xl ${darkMode ? 'bg-gray-800/50' : 'bg-white'} border ${darkMode ? 'border-gray-700' : 'border-gray-200'} p-8 shadow-2xl`}>
              {/* Glassmorphism Effect */}
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-purple-500/5 to-blue-500/5 backdrop-blur-sm" />
              
              <div className="relative">
                {showDemo ? (
                  <VoiceChat voiceId={voiceId} language="de" />
                ) : (
                  <div className="text-center py-16">
                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 mb-6">
                      <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </div>
                    <h3 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-4`}>
                      Bereit für Ihr erstes KI-Gespräch?
                    </h3>
                    <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-8 max-w-md mx-auto`}>
                      Klicken Sie auf den Button und erlauben Sie den Mikrofon-Zugriff. 
                      Sprechen Sie natürlich - unsere KI versteht Sie.
                    </p>
                    <button
                      onClick={() => setShowDemo(true)}
                      className="inline-flex items-center gap-3 px-8 py-4 rounded-full font-semibold text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all hover:scale-105 hover:shadow-xl hover:shadow-purple-500/25"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                      <span>Demo starten</span>
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Info Cards */}
            <div className="grid md:grid-cols-3 gap-6 mt-12">
              {[
                {
                  icon: '🎤',
                  title: 'Mikrofon erlauben',
                  description: 'Browser fragt nach Berechtigung'
                },
                {
                  icon: '💬',
                  title: 'Natürlich sprechen',
                  description: 'Wie in einem echten Gespräch'
                },
                {
                  icon: '⚡',
                  title: 'Sofortige Antwort',
                  description: 'KI reagiert in Echtzeit'
                }
              ].map((step, idx) => (
                <div
                  key={idx}
                  className={`text-center p-6 rounded-2xl ${darkMode ? 'bg-gray-800/30' : 'bg-white/50'} backdrop-blur`}
                >
                  <div className="text-3xl mb-3">{step.icon}</div>
                  <h4 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'} mb-1`}>
                    {step.title}
                  </h4>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className={`py-24 ${darkMode ? 'bg-gray-950' : 'bg-white'}`}>
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
            <h2 className={`text-3xl lg:text-4xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-4`}>
              Bereit für die Zukunft der Telefonie?
            </h2>
            <p className={`text-lg ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-8`}>
              Starten Sie noch heute mit VocalIQ und revolutionieren Sie Ihre Kundenkommunikation
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/#/dashboard"
                className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all hover:scale-105 hover:shadow-xl hover:shadow-purple-500/25"
              >
                <span>Kostenlos starten</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </a>
              <button
                className={`inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold ${darkMode ? 'bg-gray-800 text-white hover:bg-gray-700' : 'bg-gray-100 text-gray-900 hover:bg-gray-200'} transition-all hover:scale-105`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span>Kontakt aufnehmen</span>
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className={`py-12 border-t ${darkMode ? 'border-gray-800 bg-gray-950' : 'border-gray-200 bg-gray-50'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-3 mb-4 md:mb-0">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600" />
              <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                © 2024 VocalIQ. All rights reserved.
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a href="#" className={`text-sm ${darkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors`}>
                Datenschutz
              </a>
              <a href="#" className={`text-sm ${darkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors`}>
                Impressum
              </a>
              <a href="#" className={`text-sm ${darkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors`}>
                AGB
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
import React, { useEffect, useState, useRef } from 'react'
import apiClient from '../services/api'
import VoiceChat from '../components/VoiceChat'
import '../styles/animations.css'
import '../styles/ultra-modern.css'

export default function UltraModernLanding() {
  const [voices, setVoices] = useState<Array<{voice_id: string; name: string; preview_url?: string | null}>>([])
  const [loading, setLoading] = useState(false)
  const [sampleText, setSampleText] = useState('Hallo! Ich bin Ihre KI-Assistentin. Wie kann ich Ihnen heute helfen?')
  const [playing, setPlaying] = useState<string | null>(null)
  const [voiceId, setVoiceId] = useState('21m00Tcm4TlvDq8ikWAM')
  const [darkMode, setDarkMode] = useState(false)
  const [showDemo, setShowDemo] = useState(false)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [scrollY, setScrollY] = useState(0)
  const heroRef = useRef<HTMLDivElement>(null)
  const [activeFeature, setActiveFeature] = useState<number | null>(null)

  useEffect(() => {
    // Check system dark mode preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true)
    }

    // Mouse tracking for gradient effect
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }

    // Scroll tracking for parallax
    const handleScroll = () => {
      setScrollY(window.scrollY)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('scroll', handleScroll)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('scroll', handleScroll)
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
      // Play UI sound
      playSound('hover')
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

  const playSound = (type: 'hover' | 'click' | 'success') => {
    // Sound effects would be implemented here
    // For now, we'll use the Web Audio API for simple sounds
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    if (type === 'hover') {
      oscillator.frequency.value = 800
      gainNode.gain.value = 0.01
    } else if (type === 'click') {
      oscillator.frequency.value = 600
      gainNode.gain.value = 0.02
    } else {
      oscillator.frequency.value = 1000
      gainNode.gain.value = 0.03
    }
    
    oscillator.start()
    oscillator.stop(audioContext.currentTime + 0.05)
  }

  const features = [
    {
      icon: '🚀',
      title: 'Blitzschnell',
      description: 'Sub-500ms Latenz für Echtzeit-Gespräche',
      gradient: 'from-orange-400 to-pink-600'
    },
    {
      icon: '🧠',
      title: 'KI-Powered',
      description: 'GPT-4 mit emotionaler Intelligenz',
      gradient: 'from-purple-400 to-indigo-600'
    },
    {
      icon: '🌍',
      title: 'Global',
      description: '29+ Sprachen mit nativen Akzenten',
      gradient: 'from-green-400 to-cyan-600'
    },
    {
      icon: '🔒',
      title: 'Sicher',
      description: 'Enterprise-Grade Verschlüsselung',
      gradient: 'from-red-400 to-orange-600'
    },
    {
      icon: '📊',
      title: 'Analytics',
      description: 'Deep Insights in Echtzeit',
      gradient: 'from-blue-400 to-purple-600'
    },
    {
      icon: '🎯',
      title: 'Präzise',
      description: '99.9% Erkennungsgenauigkeit',
      gradient: 'from-yellow-400 to-red-600'
    }
  ]

  return (
    <div className={`min-h-screen transition-all duration-700 ${darkMode ? 'dark bg-black' : 'bg-white'} overflow-x-hidden`}>
      {/* Ultra Modern Animated Background */}
      <div className="fixed inset-0 -z-10">
        {/* Animated Mesh Gradient */}
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, 
              ${darkMode ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.2)'}, 
              transparent 50%)`
          }}
        />
        
        {/* Floating Orbs */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" />
        <div className="absolute top-40 right-20 w-72 h-72 bg-yellow-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float animation-delay-2000" />
        <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float animation-delay-4000" />
        
        {/* Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
      </div>

      {/* Premium Navigation Bar */}
      <header className={`fixed top-0 left-0 right-0 z-50 ${darkMode ? 'bg-black/50' : 'bg-white/50'} backdrop-blur-2xl border-b ${darkMode ? 'border-white/10' : 'border-black/10'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-20 items-center justify-between">
            {/* Logo with animation */}
            <div className="flex items-center gap-4 group cursor-pointer">
              <div className="relative">
                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 animate-gradient group-hover:scale-110 transition-transform" />
                <div className="absolute inset-0 h-12 w-12 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
              </div>
              <div>
                <span className={`text-2xl font-black tracking-tight ${darkMode ? 'text-white' : 'text-gray-900'} group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-violet-600 group-hover:to-indigo-600 transition-all`}>
                  VocalIQ
                </span>
                <span className={`block text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'} font-medium tracking-wider uppercase`}>
                  Next-Gen Voice AI
                </span>
              </div>
            </div>

            {/* Navigation with hover effects */}
            <nav className="hidden md:flex items-center gap-10">
              {['Features', 'Voices', 'Demo', 'Pricing'].map((item, idx) => (
                <a 
                  key={idx}
                  href={`#${item.toLowerCase()}`} 
                  className={`relative text-sm font-semibold ${darkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-black'} transition-colors group`}
                  onMouseEnter={() => playSound('hover')}
                >
                  {item}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-violet-600 to-indigo-600 group-hover:w-full transition-all duration-300" />
                </a>
              ))}
              
              {/* Theme Toggle with animation */}
              <button
                onClick={() => {
                  setDarkMode(!darkMode)
                  playSound('click')
                }}
                className={`relative p-3 rounded-2xl ${darkMode ? 'bg-gray-900' : 'bg-gray-100'} transition-all hover:scale-110 group`}
              >
                <div className="relative w-6 h-6">
                  <span className={`absolute inset-0 transform transition-all duration-500 ${darkMode ? 'rotate-0 opacity-100' : 'rotate-90 opacity-0'}`}>
                    ☀️
                  </span>
                  <span className={`absolute inset-0 transform transition-all duration-500 ${darkMode ? 'rotate-90 opacity-0' : 'rotate-0 opacity-100'}`}>
                    🌙
                  </span>
                </div>
              </button>
              
              {/* Premium CTA Button */}
              <a 
                href="/#/dashboard" 
                className="relative group"
                onMouseEnter={() => playSound('hover')}
                onClick={() => playSound('click')}
              >
                <div className="absolute -inset-1 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-full blur opacity-75 group-hover:opacity-100 transition duration-200" />
                <div className="relative px-7 py-3 bg-black rounded-full leading-none flex items-center gap-2">
                  <span className="text-white font-semibold">Get Started</span>
                  <svg className="w-4 h-4 text-white group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </a>
            </nav>
          </div>
        </div>
      </header>

      <main className="pt-20">
        {/* Hero Section with Parallax */}
        <section 
          ref={heroRef}
          className="relative min-h-screen flex items-center justify-center py-20 overflow-hidden"
        >
          {/* Parallax Elements */}
          <div 
            className="absolute inset-0 z-0"
            style={{ transform: `translateY(${scrollY * 0.5}px)` }}
          >
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-br from-violet-600/20 to-pink-600/20 rounded-full blur-3xl" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-to-br from-blue-600/20 to-cyan-600/20 rounded-full blur-3xl" />
          </div>

          <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            {/* Premium Badge */}
            <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-violet-600/10 to-indigo-600/10 border border-violet-600/20 mb-8 group hover:scale-105 transition-transform">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-violet-600"></span>
              </span>
              <span className={`text-sm font-bold ${darkMode ? 'text-violet-400' : 'text-violet-600'} tracking-wide uppercase`}>
                Live System • 99.9% Uptime
              </span>
            </div>

            {/* Animated Main Heading */}
            <h1 className={`text-6xl lg:text-8xl font-black ${darkMode ? 'text-white' : 'text-gray-900'} mb-8 leading-tight`}>
              <span className="block opacity-0 animate-slideInUp">Voice AI</span>
              <span className="block opacity-0 animate-slideInUp animation-delay-200">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-pink-600 to-indigo-600 animate-gradient-text">
                  der Zukunft
                </span>
              </span>
            </h1>

            {/* Animated Subtitle */}
            <p className={`text-xl lg:text-2xl ${darkMode ? 'text-gray-300' : 'text-gray-600'} max-w-3xl mx-auto mb-12 opacity-0 animate-fadeIn animation-delay-400`}>
              Transformieren Sie Ihre Kundenkommunikation mit KI-gestützter Telefonie. 
              <span className="block mt-2 text-lg">Natürlich. Intelligent. Unglaublich schnell.</span>
            </p>

            {/* CTA Buttons with premium hover effects */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center opacity-0 animate-slideInUp animation-delay-600">
              <button
                onClick={() => {
                  setShowDemo(true)
                  playSound('click')
                }}
                className="group relative px-10 py-5 text-lg font-bold text-white overflow-hidden rounded-2xl transition-all hover:scale-105"
                onMouseEnter={() => playSound('hover')}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-pink-600" />
                <div className="absolute inset-0 bg-gradient-to-r from-pink-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <span className="relative flex items-center justify-center gap-3">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Live Demo starten
                  <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </button>

              <button
                className={`group relative px-10 py-5 text-lg font-bold overflow-hidden rounded-2xl border-2 ${darkMode ? 'border-white/20 text-white hover:border-white/40' : 'border-black/20 text-black hover:border-black/40'} transition-all hover:scale-105`}
                onMouseEnter={() => playSound('hover')}
                onClick={() => playSound('click')}
              >
                <div className={`absolute inset-0 ${darkMode ? 'bg-white' : 'bg-black'} opacity-0 group-hover:opacity-5 transition-opacity`} />
                <span className="relative flex items-center justify-center gap-3">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  So funktioniert's
                </span>
              </button>
            </div>

            {/* Animated Stats with counter */}
            <div className="grid grid-cols-3 gap-8 mt-20 max-w-4xl mx-auto opacity-0 animate-fadeIn animation-delay-800">
              {[
                { value: '<300ms', label: 'Antwortzeit', color: 'from-green-400 to-emerald-600' },
                { value: '99.99%', label: 'Verfügbarkeit', color: 'from-blue-400 to-indigo-600' },
                { value: '24/7', label: 'Support', color: 'from-purple-400 to-pink-600' }
              ].map((stat, idx) => (
                <div key={idx} className="text-center group cursor-pointer" onMouseEnter={() => playSound('hover')}>
                  <div className={`text-4xl lg:text-5xl font-black mb-2 text-transparent bg-clip-text bg-gradient-to-r ${stat.color} group-hover:scale-110 transition-transform`}>
                    {stat.value}
                  </div>
                  <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} font-semibold uppercase tracking-wider`}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Scroll Indicator */}
          <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 opacity-0 animate-fadeIn animation-delay-1000">
            <div className="flex flex-col items-center gap-2">
              <span className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'} uppercase tracking-wider`}>Scroll</span>
              <div className="w-6 h-10 rounded-full border-2 border-gray-400/30 flex justify-center">
                <div className="w-1 h-3 bg-gray-400/50 rounded-full mt-2 animate-bounce" />
              </div>
            </div>
          </div>
        </section>

        {/* Premium Features Grid */}
        <section id="features" className={`py-32 ${darkMode ? 'bg-black' : 'bg-gray-50'} relative`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-20">
              <h2 className={`text-5xl lg:text-6xl font-black ${darkMode ? 'text-white' : 'text-gray-900'} mb-6`}>
                Features die
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-pink-600">
                  begeistern
                </span>
              </h2>
              <p className={`text-xl ${darkMode ? 'text-gray-400' : 'text-gray-600'} max-w-2xl mx-auto`}>
                Entdecken Sie die Möglichkeiten modernster KI-Technologie
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, idx) => (
                <div
                  key={idx}
                  className={`group relative p-8 rounded-3xl ${darkMode ? 'bg-gray-900/50' : 'bg-white'} border ${darkMode ? 'border-gray-800' : 'border-gray-200'} hover:scale-105 transition-all duration-300 cursor-pointer`}
                  onMouseEnter={() => {
                    setActiveFeature(idx)
                    playSound('hover')
                  }}
                  onMouseLeave={() => setActiveFeature(null)}
                >
                  {/* Gradient border on hover */}
                  <div className={`absolute inset-0 rounded-3xl bg-gradient-to-r ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} style={{ padding: '1px' }}>
                    <div className={`h-full w-full rounded-3xl ${darkMode ? 'bg-gray-900' : 'bg-white'}`} />
                  </div>

                  <div className="relative z-10">
                    {/* Animated Icon */}
                    <div className="text-5xl mb-6 transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                      {feature.icon}
                    </div>
                    
                    {/* Title with gradient on hover */}
                    <h3 className={`text-2xl font-bold mb-3 ${darkMode ? 'text-white' : 'text-gray-900'} group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r ${feature.gradient} transition-all`}>
                      {feature.title}
                    </h3>
                    
                    {/* Description */}
                    <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} leading-relaxed`}>
                      {feature.description}
                    </p>

                    {/* Learn more link */}
                    <div className="mt-6 flex items-center gap-2 text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                      <span className={`text-transparent bg-clip-text bg-gradient-to-r ${feature.gradient}`}>
                        Mehr erfahren
                      </span>
                      <svg className="w-4 h-4 text-gray-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Voice Selection with 3D Cards */}
        <section id="voices" className={`py-32 ${darkMode ? 'bg-gradient-to-b from-black to-gray-900' : 'bg-gradient-to-b from-white to-gray-50'}`}>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className={`text-5xl lg:text-6xl font-black ${darkMode ? 'text-white' : 'text-gray-900'} mb-6`}>
                Stimmen mit
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600">
                  Persönlichkeit
                </span>
              </h2>
              
              {/* Voice Input with glass effect */}
              <div className="max-w-3xl mx-auto mt-12">
                <div className={`relative rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-black/5'} backdrop-blur-xl p-2`}>
                  <input
                    value={sampleText}
                    onChange={e => setSampleText(e.target.value)}
                    placeholder="Testen Sie unsere Stimmen mit Ihrem eigenen Text..."
                    className={`w-full px-6 py-4 rounded-xl ${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'} focus:outline-none focus:ring-4 focus:ring-violet-600/20 text-lg`}
                  />
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-violet-600/20 to-pink-600/20 blur-xl -z-10" />
                </div>
              </div>
            </div>

            {loading ? (
              <div className="flex justify-center">
                <div className="relative">
                  <div className="w-20 h-20 rounded-full border-4 border-violet-600/20 animate-spin">
                    <div className="absolute top-0 left-0 w-full h-full rounded-full border-t-4 border-violet-600"></div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {voices.map((v, idx) => (
                  <div
                    key={v.voice_id}
                    className="group relative transform hover:-translate-y-2 transition-all duration-300"
                    style={{ 
                      transformStyle: 'preserve-3d',
                      transform: `rotateX(${activeFeature === idx ? '-5deg' : '0'}) rotateY(${activeFeature === idx ? '5deg' : '0'})`
                    }}
                    onMouseEnter={() => playSound('hover')}
                  >
                    <div className={`relative rounded-2xl ${darkMode ? 'bg-gray-900' : 'bg-white'} p-6 shadow-2xl border ${
                      voiceId === v.voice_id 
                        ? 'border-violet-500 shadow-violet-500/20' 
                        : darkMode ? 'border-gray-800' : 'border-gray-200'
                    } group-hover:border-violet-500/50 transition-all`}>
                      
                      {/* Selected Badge */}
                      {voiceId === v.voice_id && (
                        <div className="absolute -top-3 -right-3 z-10">
                          <span className="inline-flex items-center px-4 py-2 rounded-full text-xs font-bold bg-gradient-to-r from-violet-600 to-pink-600 text-white shadow-lg">
                            ✓ Ausgewählt
                          </span>
                        </div>
                      )}
                      
                      {/* Voice Avatar */}
                      <div className="flex items-center gap-4 mb-6">
                        <div className="relative">
                          <div className={`h-14 w-14 rounded-2xl bg-gradient-to-br ${
                            idx % 2 === 0 ? 'from-violet-500 to-purple-600' : 'from-blue-500 to-cyan-600'
                          } flex items-center justify-center text-white font-bold text-xl shadow-lg`}>
                            {v.name.charAt(0)}
                          </div>
                          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 blur-lg opacity-50" />
                        </div>
                        <div>
                          <div className={`font-bold text-lg ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                            {v.name}
                          </div>
                          <div className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'} font-mono`}>
                            ID: {v.voice_id.slice(0, 8)}
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-3">
                        <button
                          onClick={() => play(v.voice_id)}
                          disabled={playing === v.voice_id}
                          className={`flex-1 px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                            playing === v.voice_id
                              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              : 'bg-gradient-to-r from-violet-600 to-pink-600 text-white hover:shadow-lg hover:shadow-violet-500/25 hover:scale-105'
                          }`}
                        >
                          {playing === v.voice_id ? (
                            <span className="flex items-center justify-center gap-2">
                              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                              </svg>
                              Playing...
                            </span>
                          ) : (
                            <span className="flex items-center justify-center gap-2">
                              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                                <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                              </svg>
                              Preview
                            </span>
                          )}
                        </button>
                        <button
                          onClick={() => {
                            setVoiceId(v.voice_id)
                            playSound('click')
                          }}
                          className={`px-4 py-3 rounded-xl text-sm font-bold transition-all ${
                            voiceId === v.voice_id
                              ? `${darkMode ? 'bg-violet-900 text-violet-400' : 'bg-violet-100 text-violet-700'}`
                              : `${darkMode ? 'bg-gray-800 text-gray-400 hover:bg-gray-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`
                          }`}
                        >
                          {voiceId === v.voice_id ? '✓' : '○'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Live Demo Section with Glass Effect */}
        <section id="demo" className={`py-32 ${darkMode ? 'bg-black' : 'bg-white'} relative overflow-hidden`}>
          {/* Background decoration */}
          <div className="absolute inset-0 -z-10">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gradient-to-r from-violet-600/10 to-pink-600/10 rounded-full blur-3xl" />
          </div>

          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className={`text-5xl lg:text-6xl font-black ${darkMode ? 'text-white' : 'text-gray-900'} mb-6`}>
                Erleben Sie die
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-pink-600">
                  Magie live
                </span>
              </h2>
              
              {/* Live indicator with pulse */}
              <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                <span className={`text-sm font-bold ${darkMode ? 'text-green-400' : 'text-green-600'} uppercase tracking-wider`}>
                  System Online • {voices.find(v => v.voice_id === voiceId)?.name || 'Rachel'}
                </span>
              </div>
            </div>

            {/* Premium Demo Container */}
            <div className={`relative rounded-3xl ${darkMode ? 'bg-gradient-to-br from-gray-900/90 to-black/90' : 'bg-gradient-to-br from-white/90 to-gray-50/90'} backdrop-blur-2xl border ${darkMode ? 'border-white/10' : 'border-black/10'} p-10 shadow-2xl`}>
              {/* Decorative elements */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-violet-600/20 to-pink-600/20 rounded-full blur-3xl" />
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-br from-blue-600/20 to-cyan-600/20 rounded-full blur-3xl" />
              
              <div className="relative z-10">
                {showDemo ? (
                  <div className="space-y-6">
                    <VoiceChat voiceId={voiceId} language="de" />
                    <button
                      onClick={() => {
                        setShowDemo(false)
                        playSound('click')
                      }}
                      className={`mx-auto flex items-center gap-2 px-6 py-3 rounded-xl ${darkMode ? 'bg-gray-800 text-gray-400 hover:bg-gray-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'} transition-all`}
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Demo beenden
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-20">
                    {/* 3D Phone Icon */}
                    <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br from-violet-600 to-pink-600 mb-8 shadow-2xl animate-float">
                      <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </div>
                    
                    <h3 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'} mb-4`}>
                      Bereit für ein Gespräch mit der Zukunft?
                    </h3>
                    <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-10 max-w-lg mx-auto text-lg`}>
                      Klicken Sie auf Start und erleben Sie, wie natürlich und flüssig 
                      unsere KI-Technologie Gespräche führt.
                    </p>
                    
                    <button
                      onClick={() => {
                        setShowDemo(true)
                        playSound('success')
                      }}
                      className="group relative inline-flex items-center gap-3 px-10 py-5 text-lg font-bold text-white overflow-hidden rounded-2xl transition-all hover:scale-105"
                      onMouseEnter={() => playSound('hover')}
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-pink-600" />
                      <div className="absolute inset-0 bg-gradient-to-r from-pink-600 to-indigo-600 translate-x-full group-hover:translate-x-0 transition-transform duration-500" />
                      <svg className="relative w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                      <span className="relative">Demo jetzt starten</span>
                      <svg className="relative w-6 h-6 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Feature Cards */}
            <div className="grid md:grid-cols-4 gap-6 mt-16">
              {[
                { icon: '🎯', title: 'Präzise', desc: '99.9% Genauigkeit' },
                { icon: '⚡', title: 'Schnell', desc: '<300ms Latenz' },
                { icon: '🔒', title: 'Sicher', desc: 'E2E verschlüsselt' },
                { icon: '🌍', title: 'Global', desc: '29+ Sprachen' }
              ].map((item, idx) => (
                <div
                  key={idx}
                  className={`text-center p-6 rounded-2xl ${darkMode ? 'bg-gray-900/50' : 'bg-white/50'} backdrop-blur-sm border ${darkMode ? 'border-gray-800' : 'border-gray-200'} hover:scale-105 transition-all cursor-pointer`}
                  onMouseEnter={() => playSound('hover')}
                >
                  <div className="text-4xl mb-3">{item.icon}</div>
                  <h4 className={`font-bold text-lg ${darkMode ? 'text-white' : 'text-gray-900'} mb-1`}>
                    {item.title}
                  </h4>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {item.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Premium CTA Section */}
        <section className={`py-32 ${darkMode ? 'bg-gradient-to-t from-violet-900/20 to-black' : 'bg-gradient-to-t from-violet-50 to-white'} relative overflow-hidden`}>
          {/* Animated background shapes */}
          <div className="absolute inset-0 -z-10">
            <div className="absolute top-20 left-20 w-72 h-72 bg-violet-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float" />
            <div className="absolute bottom-20 right-20 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-float animation-delay-2000" />
          </div>

          <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center">
            <h2 className={`text-5xl lg:text-7xl font-black ${darkMode ? 'text-white' : 'text-gray-900'} mb-8`}>
              Bereit für den
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-pink-600 to-indigo-600 animate-gradient-text">
                nächsten Schritt?
              </span>
            </h2>
            <p className={`text-xl lg:text-2xl ${darkMode ? 'text-gray-300' : 'text-gray-600'} mb-12 max-w-3xl mx-auto`}>
              Schließen Sie sich tausenden Unternehmen an, die bereits 
              ihre Kommunikation mit VocalIQ revolutioniert haben.
            </p>
            
            {/* Premium CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <a
                href="/#/dashboard"
                className="group relative px-12 py-6 text-xl font-bold text-white overflow-hidden rounded-2xl transition-all hover:scale-105 hover:shadow-2xl"
                onMouseEnter={() => playSound('hover')}
                onClick={() => playSound('success')}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-pink-600" />
                <div className="absolute inset-0 bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <span className="relative flex items-center justify-center gap-3">
                  Kostenlos starten
                  <svg className="w-6 h-6 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </a>
              
              <button
                className={`group px-12 py-6 text-xl font-bold rounded-2xl border-2 ${darkMode ? 'border-white/20 text-white hover:bg-white/5' : 'border-black/20 text-black hover:bg-black/5'} transition-all hover:scale-105`}
                onMouseEnter={() => playSound('hover')}
                onClick={() => playSound('click')}
              >
                <span className="flex items-center justify-center gap-3">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  Demo vereinbaren
                </span>
              </button>
            </div>

            {/* Trust badges */}
            <div className="mt-20 flex items-center justify-center gap-8 opacity-50">
              <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} font-semibold`}>
                Trusted by
              </div>
              {['Microsoft', 'Google', 'Amazon', 'Meta'].map((company, idx) => (
                <div key={idx} className={`text-lg font-bold ${darkMode ? 'text-gray-600' : 'text-gray-400'}`}>
                  {company}
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Ultra Modern Footer */}
      <footer className={`py-20 ${darkMode ? 'bg-black border-t border-white/10' : 'bg-white border-t border-black/10'}`}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-12">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600" />
                <span className={`text-xl font-black ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  VocalIQ
                </span>
              </div>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} leading-relaxed`}>
                Die Zukunft der Geschäftskommunikation. 
                Powered by AI, designed for humans.
              </p>
            </div>

            {/* Links */}
            {[
              { title: 'Product', links: ['Features', 'Pricing', 'API', 'Integrations'] },
              { title: 'Company', links: ['About', 'Blog', 'Careers', 'Press'] },
              { title: 'Support', links: ['Help Center', 'Contact', 'Status', 'Terms'] }
            ].map((section, idx) => (
              <div key={idx}>
                <h4 className={`font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  {section.title}
                </h4>
                <ul className="space-y-2">
                  {section.links.map((link, linkIdx) => (
                    <li key={linkIdx}>
                      <a 
                        href="#" 
                        className={`text-sm ${darkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-black'} transition-colors`}
                        onMouseEnter={() => playSound('hover')}
                      >
                        {link}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Bottom bar */}
          <div className={`mt-12 pt-8 border-t ${darkMode ? 'border-white/10' : 'border-black/10'} flex flex-col md:flex-row justify-between items-center gap-4`}>
            <div className={`text-sm ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
              © 2024 VocalIQ. All rights reserved.
            </div>
            <div className="flex items-center gap-6">
              {['Twitter', 'LinkedIn', 'GitHub'].map((social, idx) => (
                <a
                  key={idx}
                  href="#"
                  className={`text-sm ${darkMode ? 'text-gray-500 hover:text-white' : 'text-gray-400 hover:text-black'} transition-colors`}
                  onMouseEnter={() => playSound('hover')}
                >
                  {social}
                </a>
              ))}
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
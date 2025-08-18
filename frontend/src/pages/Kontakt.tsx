import React, { useState, useEffect } from 'react'
import '../styles/professional.css'

export default function Kontakt() {
  const [darkMode, setDarkMode] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    email: '',
    phone: '',
    subject: '',
    message: '',
    consent: false
  })

  useEffect(() => {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true)
    }
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      setFormData(prev => ({ ...prev, [name]: (e.target as HTMLInputElement).checked }))
    } else {
      setFormData(prev => ({ ...prev, [name]: value }))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission
    console.log('Form submitted:', formData)
    alert('Vielen Dank für Ihre Nachricht. Wir werden uns innerhalb von 24 Stunden bei Ihnen melden.')
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

      {/* Content */}
      <main className="pt-24 pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Contact Form */}
            <div>
              <h1 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Kontaktieren Sie uns
              </h1>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-8`}>
                Haben Sie Fragen zu unserer Voice-AI-Plattform? Wir sind für Sie da und freuen uns auf Ihre Nachricht.
              </p>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                      Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      required
                      value={formData.name}
                      onChange={handleInputChange}
                      className={`w-full px-4 py-3 rounded-lg ${darkMode ? 'bg-slate-800 text-white border-slate-700' : 'bg-white text-slate-900 border-gray-200'} border focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 transition-colors`}
                    />
                  </div>

                  <div>
                    <label htmlFor="company" className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                      Unternehmen
                    </label>
                    <input
                      type="text"
                      id="company"
                      name="company"
                      value={formData.company}
                      onChange={handleInputChange}
                      className={`w-full px-4 py-3 rounded-lg ${darkMode ? 'bg-slate-800 text-white border-slate-700' : 'bg-white text-slate-900 border-gray-200'} border focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 transition-colors`}
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="email" className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                      E-Mail *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      required
                      value={formData.email}
                      onChange={handleInputChange}
                      className={`w-full px-4 py-3 rounded-lg ${darkMode ? 'bg-slate-800 text-white border-slate-700' : 'bg-white text-slate-900 border-gray-200'} border focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 transition-colors`}
                    />
                  </div>

                  <div>
                    <label htmlFor="phone" className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                      Telefon
                    </label>
                    <input
                      type="tel"
                      id="phone"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className={`w-full px-4 py-3 rounded-lg ${darkMode ? 'bg-slate-800 text-white border-slate-700' : 'bg-white text-slate-900 border-gray-200'} border focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 transition-colors`}
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="subject" className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                    Betreff *
                  </label>
                  <select
                    id="subject"
                    name="subject"
                    required
                    value={formData.subject}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-3 rounded-lg ${darkMode ? 'bg-slate-800 text-white border-slate-700' : 'bg-white text-slate-900 border-gray-200'} border focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 transition-colors`}
                  >
                    <option value="">Bitte wählen</option>
                    <option value="demo">Demo anfragen</option>
                    <option value="sales">Vertriebsanfrage</option>
                    <option value="support">Technischer Support</option>
                    <option value="partnership">Partnerschaft</option>
                    <option value="general">Allgemeine Anfrage</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="message" className={`block text-sm font-medium ${darkMode ? 'text-slate-300' : 'text-slate-700'} mb-2`}>
                    Nachricht *
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={6}
                    value={formData.message}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-3 rounded-lg ${darkMode ? 'bg-slate-800 text-white border-slate-700' : 'bg-white text-slate-900 border-gray-200'} border focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 transition-colors resize-none`}
                    placeholder="Beschreiben Sie Ihr Anliegen..."
                  />
                </div>

                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="consent"
                    name="consent"
                    required
                    checked={formData.consent}
                    onChange={handleInputChange}
                    className="mt-1 h-4 w-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                  />
                  <label htmlFor="consent" className={`ml-3 text-sm ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                    Ich stimme der Verarbeitung meiner Daten gemäß der <a href="/#/datenschutz" className="text-teal-600 hover:text-teal-700 underline">Datenschutzerklärung</a> zu. *
                  </label>
                </div>

                <button
                  type="submit"
                  className={`w-full px-6 py-3 rounded-lg font-semibold ${darkMode ? 'bg-gradient-to-r from-teal-600 to-teal-700 text-white hover:from-teal-700 hover:to-teal-800' : 'bg-gradient-to-r from-slate-700 to-slate-900 text-white hover:from-slate-800 hover:to-black'} transition-all duration-200 transform hover:scale-[1.02]`}
                >
                  Nachricht senden
                </button>
              </form>
            </div>

            {/* Contact Information */}
            <div className="space-y-8">
              <div>
                <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-6`}>
                  Weitere Kontaktmöglichkeiten
                </h2>

                {/* Office Cards */}
                <div className="space-y-6">
                  <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
                    <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                      <svg className="inline-block w-5 h-5 mr-2 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      Hauptsitz Berlin
                    </h3>
                    <div className={`space-y-2 ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                      <p>VocalIQ GmbH</p>
                      <p>Musterstraße 123</p>
                      <p>12345 Berlin</p>
                      <p className="pt-2">
                        <strong>Tel:</strong> +49 (0) 30 123456789<br />
                        <strong>E-Mail:</strong> berlin@vocaliq.de
                      </p>
                    </div>
                  </div>

                  <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
                    <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                      <svg className="inline-block w-5 h-5 mr-2 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Geschäftszeiten
                    </h3>
                    <div className={`space-y-2 ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                      <p><strong>Montag - Freitag:</strong> 9:00 - 18:00 Uhr</p>
                      <p><strong>Samstag:</strong> 10:00 - 14:00 Uhr (Hotline)</p>
                      <p><strong>Sonntag:</strong> Geschlossen</p>
                    </div>
                  </div>

                  <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
                    <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                      <svg className="inline-block w-5 h-5 mr-2 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                      Support & Service
                    </h3>
                    <div className={`space-y-2 ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                      <p><strong>Support-Hotline:</strong> +49 (0) 30 123456700</p>
                      <p><strong>Support-E-Mail:</strong> support@vocaliq.de</p>
                      <p><strong>Notfall-Hotline:</strong> +49 (0) 30 123456799</p>
                      <p className="text-sm">(24/7 für Enterprise-Kunden)</p>
                    </div>
                  </div>

                  <div className={`p-6 rounded-xl ${darkMode ? 'bg-slate-800/50' : 'bg-white'} border ${darkMode ? 'border-slate-700' : 'border-gray-200'}`}>
                    <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                      <svg className="inline-block w-5 h-5 mr-2 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Weitere Abteilungen
                    </h3>
                    <div className={`space-y-2 ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                      <p><strong>Vertrieb:</strong> sales@vocaliq.de</p>
                      <p><strong>Partner:</strong> partner@vocaliq.de</p>
                      <p><strong>Presse:</strong> presse@vocaliq.de</p>
                      <p><strong>Karriere:</strong> karriere@vocaliq.de</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Links */}
              <div className={`p-6 rounded-xl ${darkMode ? 'bg-gradient-to-br from-teal-900/20 to-slate-800/50' : 'bg-gradient-to-br from-teal-50 to-slate-50'} border ${darkMode ? 'border-teal-800/50' : 'border-teal-200'}`}>
                <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                  Schnellzugriff
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  <a href="/#/demo" className={`px-4 py-2 rounded-lg text-center ${darkMode ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-white text-slate-700 hover:bg-gray-50'} transition-colors`}>
                    Demo buchen
                  </a>
                  <a href="/#/preise" className={`px-4 py-2 rounded-lg text-center ${darkMode ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-white text-slate-700 hover:bg-gray-50'} transition-colors`}>
                    Preise
                  </a>
                  <a href="/#/docs" className={`px-4 py-2 rounded-lg text-center ${darkMode ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-white text-slate-700 hover:bg-gray-50'} transition-colors`}>
                    Dokumentation
                  </a>
                  <a href="/#/status" className={`px-4 py-2 rounded-lg text-center ${darkMode ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-white text-slate-700 hover:bg-gray-50'} transition-colors`}>
                    System-Status
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
import React, { useState, useEffect } from 'react'
import '../styles/professional.css'

export default function Datenschutz() {
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true)
    }
  }, [])

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
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <h1 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-8`}>
            Datenschutzerklärung
          </h1>

          <div className={`prose prose-lg ${darkMode ? 'prose-invert' : ''} max-w-none`}>
            <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-6`}>
              Stand: {new Date().toLocaleDateString('de-DE', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                1. Verantwortlicher
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Verantwortlich für die Datenverarbeitung auf dieser Website ist:
              </p>
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-gray-100'} mb-4`}>
                <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  VocalIQ GmbH<br />
                  Musterstraße 123<br />
                  12345 Berlin<br />
                  Deutschland<br />
                  <br />
                  E-Mail: datenschutz@vocaliq.de<br />
                  Telefon: +49 (0) 30 123456789
                </p>
              </div>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                2. Datenerfassung auf unserer Website
              </h2>
              
              <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                2.1 Server-Log-Dateien
              </h3>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten Server-Log-Dateien, 
                die Ihr Browser automatisch an uns übermittelt. Dies sind:
              </p>
              <ul className={`list-disc pl-6 ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <li>Browsertyp und Browserversion</li>
                <li>Verwendetes Betriebssystem</li>
                <li>Referrer URL</li>
                <li>Hostname des zugreifenden Rechners</li>
                <li>Uhrzeit der Serveranfrage</li>
                <li>IP-Adresse</li>
              </ul>

              <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                2.2 Cookies
              </h3>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Unsere Website verwendet Cookies. Das sind kleine Textdateien, die Ihr Webbrowser auf Ihrem Endgerät speichert. 
                Cookies helfen uns dabei, unser Angebot nutzerfreundlicher, effektiver und sicherer zu machen.
              </p>

              <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                2.3 Voice-Daten
              </h3>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Bei Nutzung unserer Voice-AI-Dienste werden folgende Daten verarbeitet:
              </p>
              <ul className={`list-disc pl-6 ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <li>Sprachaufnahmen (werden nach Verarbeitung sofort gelöscht)</li>
                <li>Transkribierte Texte (anonymisiert gespeichert)</li>
                <li>Metadaten zur Qualitätsverbesserung</li>
                <li>Zeitstempel der Interaktionen</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                3. Ihre Rechte
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Sie haben folgende Rechte hinsichtlich Ihrer personenbezogenen Daten:
              </p>
              <ul className={`list-disc pl-6 ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <li><strong>Auskunftsrecht:</strong> Sie können Auskunft über Ihre gespeicherten Daten verlangen</li>
                <li><strong>Berichtigungsrecht:</strong> Sie können die Berichtigung unrichtiger Daten verlangen</li>
                <li><strong>Löschungsrecht:</strong> Sie können die Löschung Ihrer Daten verlangen</li>
                <li><strong>Einschränkungsrecht:</strong> Sie können die Einschränkung der Verarbeitung verlangen</li>
                <li><strong>Widerspruchsrecht:</strong> Sie können der Verarbeitung widersprechen</li>
                <li><strong>Datenübertragbarkeit:</strong> Sie können Ihre Daten in einem übertragbaren Format erhalten</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                4. Datensicherheit
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Wir verwenden innerhalb des Website-Besuchs das verbreitete SSL-Verfahren (Secure Socket Layer) in Verbindung 
                mit der jeweils höchsten Verschlüsselungsstufe, die von Ihrem Browser unterstützt wird. Alle Sprachdaten 
                werden Ende-zu-Ende verschlüsselt übertragen und verarbeitet.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                5. Drittanbieter
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Wir nutzen folgende Drittanbieter-Dienste:
              </p>
              <ul className={`list-disc pl-6 ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <li><strong>OpenAI:</strong> Für Sprachverarbeitung (Daten werden nicht für Training verwendet)</li>
                <li><strong>ElevenLabs:</strong> Für Text-to-Speech Konvertierung</li>
                <li><strong>AWS:</strong> Für sichere Cloud-Infrastruktur (Server in Deutschland)</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                6. Kontakt zum Datenschutzbeauftragten
              </h2>
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-gray-100'}`}>
                <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  Unser Datenschutzbeauftragter:<br />
                  Dr. Max Mustermann<br />
                  E-Mail: dsb@vocaliq.de<br />
                  Telefon: +49 (0) 30 123456790
                </p>
              </div>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                7. Änderungen dieser Datenschutzerklärung
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Wir behalten uns vor, diese Datenschutzerklärung anzupassen, damit sie stets den aktuellen rechtlichen 
                Anforderungen entspricht oder um Änderungen unserer Leistungen in der Datenschutzerklärung umzusetzen. 
                Für Ihren erneuten Besuch gilt dann die neue Datenschutzerklärung.
              </p>
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}
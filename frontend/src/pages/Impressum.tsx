import React, { useState, useEffect } from 'react'
import '../styles/professional.css'

export default function Impressum() {
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
            Impressum
          </h1>

          <div className={`prose prose-lg ${darkMode ? 'prose-invert' : ''} max-w-none`}>
            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Angaben gemäß § 5 TMG
              </h2>
              <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-gray-100'}`}>
                <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                  <strong>VocalIQ GmbH</strong><br />
                  Intelligente Sprachassistenz-Lösungen<br />
                  Musterstraße 123<br />
                  12345 Berlin<br />
                  Deutschland
                </p>
              </div>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Vertreten durch
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Geschäftsführer:<br />
                Marcel Gärtner<br />
                Dr. Sarah Schmidt
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Kontakt
              </h2>
              <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-gray-100'}`}>
                <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  <strong>Telefon:</strong> +49 (0) 30 123456789<br />
                  <strong>Fax:</strong> +49 (0) 30 123456788<br />
                  <strong>E-Mail:</strong> info@vocaliq.de<br />
                  <strong>Website:</strong> www.vocaliq.de
                </p>
              </div>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Registereintrag
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <strong>Eintragung im Handelsregister</strong><br />
                Registergericht: Amtsgericht Berlin-Charlottenburg<br />
                Registernummer: HRB 234567 B
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Umsatzsteuer-ID
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <strong>Umsatzsteuer-Identifikationsnummer gemäß § 27a Umsatzsteuergesetz:</strong><br />
                DE 123 456 789
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Wirtschafts-ID
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <strong>Wirtschafts-Identifikationsnummer gemäß § 139c AO:</strong><br />
                DE 987 654 321
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV
              </h2>
              <div className={`p-6 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-gray-100'}`}>
                <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                  Marcel Gärtner<br />
                  VocalIQ GmbH<br />
                  Musterstraße 123<br />
                  12345 Berlin<br />
                  Deutschland
                </p>
              </div>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Berufsrechtliche Angaben
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <strong>Aufsichtsbehörde:</strong><br />
                Berliner Beauftragte für Datenschutz und Informationsfreiheit<br />
                Friedrichstr. 219<br />
                10969 Berlin
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                EU-Streitschlichtung
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:<br />
                <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer" 
                   className="text-teal-600 hover:text-teal-700 underline">
                  https://ec.europa.eu/consumers/odr/
                </a><br />
                Unsere E-Mail-Adresse finden Sie oben im Impressum.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Verbraucherstreitbeilegung
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer 
                Verbraucherschlichtungsstelle teilzunehmen.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Haftungsausschluss
              </h2>
              
              <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                Haftung für Inhalte
              </h3>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den 
                allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht 
                verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen 
                zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
              </p>

              <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                Haftung für Links
              </h3>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. 
                Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten 
                Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.
              </p>

              <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-900'} mb-3`}>
                Urheberrecht
              </h3>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen 
                Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der 
                Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                Bildnachweise
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Alle verwendeten Bilder und Grafiken sind Eigentum der VocalIQ GmbH oder wurden mit entsprechenden 
                Lizenzen erworben.
              </p>
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}
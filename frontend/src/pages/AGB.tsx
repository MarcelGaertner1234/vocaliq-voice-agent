import React, { useState, useEffect } from 'react'
import '../styles/professional.css'

export default function AGB() {
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
            Allgemeine Geschäftsbedingungen (AGB)
          </h1>

          <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-8`}>
            Stand: {new Date().toLocaleDateString('de-DE', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>

          <div className={`prose prose-lg ${darkMode ? 'prose-invert' : ''} max-w-none`}>
            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 1 Geltungsbereich
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Diese Allgemeinen Geschäftsbedingungen (nachfolgend "AGB") gelten für alle Verträge zwischen der 
                VocalIQ GmbH (nachfolgend "Anbieter") und dem Kunden (nachfolgend "Kunde") über die Nutzung der 
                Voice-AI-Plattform und damit verbundener Dienstleistungen.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Geschäftsbedingungen des Kunden finden keine Anwendung, auch wenn der Anbieter ihrer Geltung im 
                Einzelfall nicht gesondert widerspricht.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 2 Vertragsgegenstand
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Der Anbieter stellt dem Kunden eine cloudbasierte Voice-AI-Plattform zur automatisierten 
                Sprachkommunikation zur Verfügung (Software-as-a-Service).
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Der genaue Funktionsumfang ergibt sich aus der jeweiligen Leistungsbeschreibung und dem 
                gewählten Tarif.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Die Plattform umfasst:
              </p>
              <ul className={`list-disc pl-6 ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <li>Spracherkennung und -verarbeitung</li>
                <li>KI-gestützte Dialogführung</li>
                <li>Text-to-Speech Funktionalität</li>
                <li>Integration in bestehende Systeme</li>
                <li>Analyse und Reporting-Tools</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 3 Vertragsschluss
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Die Darstellung der Produkte auf unserer Website stellt kein rechtlich bindendes Angebot dar, 
                sondern eine Aufforderung zur Bestellung.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Der Vertrag kommt durch die Annahme des Kundenangebots durch den Anbieter zustande. Die Annahme 
                erfolgt durch Zusendung einer Auftragsbestätigung per E-Mail.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Der Anbieter behält sich vor, Bestellungen ohne Angabe von Gründen abzulehnen.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 4 Leistungsumfang und Verfügbarkeit
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Der Anbieter gewährleistet eine Verfügbarkeit der Plattform von 99,5% im Jahresmittel.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Hiervon ausgenommen sind:
              </p>
              <ul className={`list-disc pl-6 ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <li>Geplante Wartungsarbeiten (werden 48h vorher angekündigt)</li>
                <li>Höhere Gewalt</li>
                <li>Störungen außerhalb des Einflussbereichs des Anbieters</li>
                <li>Vom Kunden verursachte Störungen</li>
              </ul>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Der Anbieter ist berechtigt, die Plattform weiterzuentwickeln und Änderungen vorzunehmen, 
                sofern diese den Vertragsgegenstand nicht wesentlich beeinträchtigen.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 5 Preise und Zahlungsbedingungen
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Es gelten die zum Zeitpunkt der Bestellung angegebenen Preise. Alle Preise verstehen sich 
                zuzüglich der gesetzlichen Mehrwertsteuer.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Die Abrechnung erfolgt monatlich im Voraus. Die Zahlung ist innerhalb von 14 Tagen nach 
                Rechnungsstellung fällig.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Bei Zahlungsverzug ist der Anbieter berechtigt, Verzugszinsen in Höhe von 9 Prozentpunkten 
                über dem Basiszinssatz zu verlangen.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 6 Pflichten des Kunden
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Der Kunde verpflichtet sich:
              </p>
              <ul className={`list-disc pl-6 ${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                <li>Die Plattform nur für rechtmäßige Zwecke zu nutzen</li>
                <li>Keine Inhalte zu übertragen, die Rechte Dritter verletzen</li>
                <li>Zugangsdaten vertraulich zu behandeln</li>
                <li>Technische Mindestanforderungen einzuhalten</li>
                <li>Datenschutzbestimmungen einzuhalten</li>
                <li>Keine Manipulationsversuche zu unternehmen</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 7 Nutzungsrechte
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Der Kunde erhält für die Vertragslaufzeit ein nicht ausschließliches, nicht übertragbares 
                Nutzungsrecht an der Plattform.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Eine Unterlizenzierung ist nur mit schriftlicher Zustimmung des Anbieters gestattet.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Alle Rechte an der Plattform und der zugrunde liegenden Software verbleiben beim Anbieter.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 8 Datenschutz und Datensicherheit
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Der Anbieter verpflichtet sich zur Einhaltung der datenschutzrechtlichen Bestimmungen, 
                insbesondere der DSGVO.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Nähere Informationen zur Datenverarbeitung finden sich in der Datenschutzerklärung.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Der Anbieter trifft angemessene technische und organisatorische Maßnahmen zur Datensicherheit.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 9 Gewährleistung
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Der Anbieter gewährleistet, dass die Plattform im Wesentlichen entsprechend der 
                Leistungsbeschreibung funktioniert.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Bei Mängeln wird der Anbieter nach eigener Wahl nacherfüllen oder Ersatz leisten.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Der Kunde hat Mängel unverzüglich schriftlich anzuzeigen.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 10 Haftung
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Der Anbieter haftet unbeschränkt für Vorsatz und grobe Fahrlässigkeit sowie bei Verletzung 
                von Leben, Körper oder Gesundheit.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Bei leichter Fahrlässigkeit haftet der Anbieter nur bei Verletzung wesentlicher 
                Vertragspflichten und begrenzt auf den vorhersehbaren, vertragstypischen Schaden.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Die Haftung für Datenverlust ist auf den typischen Wiederherstellungsaufwand beschränkt.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 11 Vertragslaufzeit und Kündigung
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Der Vertrag wird für die vereinbarte Laufzeit geschlossen.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Die ordentliche Kündigung ist mit einer Frist von 3 Monaten zum Vertragsende möglich.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (4) Kündigungen bedürfen der Textform.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 12 Geheimhaltung
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Die Parteien verpflichten sich, alle im Rahmen der Vertragsbeziehung erlangten vertraulichen 
                Informationen geheim zu halten.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Diese Verpflichtung besteht für einen Zeitraum von 5 Jahren nach Vertragsende fort.
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 13 Höhere Gewalt
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                Keine Partei haftet für die Nichterfüllung ihrer Verpflichtungen, wenn diese auf höhere Gewalt 
                zurückzuführen ist (z.B. Naturkatastrophen, Krieg, Streik, Pandemien).
              </p>
            </section>

            <section className="mb-8">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'} mb-4`}>
                § 14 Schlussbestimmungen
              </h2>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (1) Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (2) Gerichtsstand ist Berlin, sofern der Kunde Kaufmann ist.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (3) Sollten einzelne Bestimmungen unwirksam sein, bleibt die Wirksamkeit der übrigen 
                Bestimmungen unberührt.
              </p>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} mb-4`}>
                (4) Änderungen und Ergänzungen bedürfen der Textform. Dies gilt auch für die Aufhebung dieser 
                Formerfordernis.
              </p>
            </section>

            <div className={`mt-12 p-6 rounded-lg ${darkMode ? 'bg-slate-800' : 'bg-gray-100'}`}>
              <p className={`${darkMode ? 'text-slate-300' : 'text-slate-600'} font-semibold`}>
                VocalIQ GmbH<br />
                Musterstraße 123<br />
                12345 Berlin<br />
                <br />
                E-Mail: agb@vocaliq.de<br />
                Telefon: +49 (0) 30 123456789
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
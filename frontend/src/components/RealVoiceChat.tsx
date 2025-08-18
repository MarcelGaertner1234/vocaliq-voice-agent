import React, { useState, useRef, useEffect } from 'react'

const RealVoiceChat: React.FC = () => {
  const [isCallActive, setIsCallActive] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState('Bereit für Anruf')
  const [transcript, setTranscript] = useState<Array<{speaker: string, text: string}>>([])
  const [error, setError] = useState<string | null>(null)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    // Web Speech API für Speech-to-Text (falls verfügbar)
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'de-DE'
      
      recognitionRef.current.onresult = (event: any) => {
        const last = event.results.length - 1
        const text = event.results[last][0].transcript
        
        if (event.results[last].isFinal) {
          handleUserSpeech(text)
        }
      }
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  const handleUserSpeech = async (text: string) => {
    // Füge User-Text zum Transcript hinzu
    setTranscript(prev => [...prev, { speaker: 'Sie', text }])
    setStatus('KI denkt nach...')
    
    try {
      // Sende an API
      const response = await fetch(`/api/voices/chat?voice_id=21m00Tcm4TlvDq8ikWAM&message=${encodeURIComponent(text)}`, {
        method: 'POST'
      })
      
      const data = await response.json()
      
      // Füge KI-Antwort zum Transcript hinzu
      setTranscript(prev => [...prev, { speaker: 'KI', text: data.reply }])
      
      // Spiele Audio ab wenn vorhanden
      if (data.audio_url) {
        const audio = new Audio(data.audio_url)
        setStatus('KI spricht...')
        
        audio.onended = () => {
          setStatus('Sprechen Sie...')
        }
        
        await audio.play()
      }
    } catch (err) {
      console.error('API Error:', err)
      setError('Verbindungsfehler. Bitte versuchen Sie es erneut.')
    }
  }

  const startCall = async () => {
    try {
      setError(null)
      setIsLoading(true)
      setTranscript([])
      
      // Mikrofon-Zugriff anfordern
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      
      // Starte Speech Recognition
      if (recognitionRef.current) {
        recognitionRef.current.start()
      }
      
      setIsCallActive(true)
      setStatus('Sprechen Sie jetzt...')
      setIsLoading(false)
      
      // Begrüßung
      setTimeout(() => {
        setTranscript([{ speaker: 'KI', text: 'Hallo! Ich bin Ihr VocalIQ Assistent. Wie kann ich Ihnen helfen?' }])
      }, 1000)
      
    } catch (err) {
      console.error('Mikrofon-Fehler:', err)
      setError('Mikrofon-Zugriff verweigert. Bitte erlauben Sie den Zugriff.')
      setIsLoading(false)
    }
  }

  const endCall = () => {
    // Stoppe Speech Recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    
    // Stoppe Mikrofon
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    
    setIsCallActive(false)
    setStatus('Anruf beendet')
    
    // Zeige Zusammenfassung
    setTimeout(() => {
      setStatus('Bereit für neuen Anruf')
    }, 2000)
  }

  // Simpler Fallback für Browser ohne Mikrofon-Support
  const simulateCall = async () => {
    setIsLoading(true)
    setTranscript([])
    setIsCallActive(true)
    
    // Simuliere Gespräch
    const conversation = [
      { speaker: 'KI', text: 'Hallo! Willkommen bei VocalIQ. Wie kann ich Ihnen helfen?', delay: 1000 },
      { speaker: 'Sie', text: 'Was ist VocalIQ?', delay: 3000 },
      { speaker: 'KI', text: 'VocalIQ ist eine KI-Telefonie-Plattform, die natürliche Gespräche mit Kunden ermöglicht.', delay: 5000 },
      { speaker: 'Sie', text: 'Welche Features gibt es?', delay: 8000 },
      { speaker: 'KI', text: 'Wir bieten Echtzeit-Spracherkennung, mehrsprachige Unterstützung und Integration mit Ihrem CRM.', delay: 10000 }
    ]
    
    for (const msg of conversation) {
      setTimeout(() => {
        setTranscript(prev => [...prev, { speaker: msg.speaker, text: msg.text }])
        setStatus(msg.speaker === 'KI' ? 'KI spricht...' : 'Sie sprechen...')
      }, msg.delay)
    }
    
    setIsLoading(false)
    
    setTimeout(() => {
      setStatus('Demo-Gespräch läuft...')
    }, 2000)
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
          <h3 className="text-2xl font-bold mb-2">Voice Demo</h3>
          <p className="text-indigo-100">Führen Sie ein echtes Gespräch mit unserer KI</p>
        </div>

        {/* Status Bar */}
        <div className="bg-gray-50 px-6 py-3 border-b">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Status:</span>
            <span className={`text-sm font-bold ${isCallActive ? 'text-green-600' : 'text-gray-600'}`}>
              {status}
            </span>
          </div>
        </div>

        {/* Transcript Area */}
        <div className="h-64 overflow-y-auto p-6 bg-gray-50">
          {transcript.length === 0 ? (
            <div className="text-center text-gray-400 mt-16">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p>Starten Sie einen Anruf um das Gespräch zu beginnen</p>
            </div>
          ) : (
            <div className="space-y-3">
              {transcript.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.speaker === 'KI' ? 'justify-start' : 'justify-end'}`}>
                  <div className={`max-w-xs px-4 py-2 rounded-lg ${
                    msg.speaker === 'KI' 
                      ? 'bg-white text-gray-800 shadow' 
                      : 'bg-indigo-600 text-white'
                  }`}>
                    <div className="text-xs font-semibold mb-1">{msg.speaker}</div>
                    <div className="text-sm">{msg.text}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mx-6 mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Control Buttons */}
        <div className="p-6 bg-white border-t">
          <div className="flex gap-4 justify-center">
            {!isCallActive ? (
              <>
                <button
                  onClick={startCall}
                  disabled={isLoading}
                  className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-full transition-all transform hover:scale-105 shadow-lg disabled:opacity-50"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                      </svg>
                      Verbinde...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      Mit Mikrofon anrufen
                    </span>
                  )}
                </button>
                
                <button
                  onClick={simulateCall}
                  disabled={isLoading}
                  className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-full transition-all transform hover:scale-105 shadow-lg"
                >
                  <span className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Demo abspielen
                  </span>
                </button>
              </>
            ) : (
              <button
                onClick={endCall}
                className="px-8 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-full transition-all transform hover:scale-105 shadow-lg"
              >
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Anruf beenden
                </span>
              </button>
            )}
          </div>
          
          {/* Info Text */}
          <div className="mt-4 text-center text-xs text-gray-500">
            {isCallActive ? 
              'Das Gespräch läuft. Sprechen Sie natürlich.' : 
              'Wählen Sie "Mit Mikrofon" für echte Sprache oder "Demo" für eine Simulation'
            }
          </div>
        </div>
      </div>

      {/* Feature List */}
      <div className="mt-6 grid grid-cols-4 gap-4 text-center">
        <div className="text-gray-600">
          <div className="text-2xl mb-1">🎤</div>
          <div className="text-xs">Echtzeit-Sprache</div>
        </div>
        <div className="text-gray-600">
          <div className="text-2xl mb-1">🌍</div>
          <div className="text-xs">31 Sprachen</div>
        </div>
        <div className="text-gray-600">
          <div className="text-2xl mb-1">⚡</div>
          <div className="text-xs">Niedrige Latenz</div>
        </div>
        <div className="text-gray-600">
          <div className="text-2xl mb-1">🤖</div>
          <div className="text-xs">GPT-4 Power</div>
        </div>
      </div>
    </div>
  )
}

export default RealVoiceChat
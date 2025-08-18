import React, { useState } from 'react'

const SimplifiedVoiceChat: React.FC = () => {
  const [isCallActive, setIsCallActive] = useState(false)
  const [status, setStatus] = useState('Bereit')
  
  const startCall = () => {
    setIsCallActive(true)
    setStatus('Demo-Modus - In echter Version: Live-Gespräch')
    
    // Simuliere Gespräch
    setTimeout(() => {
      setStatus('KI: Hallo! Ich bin Ihr VocalIQ Assistent.')
    }, 2000)
    
    setTimeout(() => {
      setStatus('Sie: Wie funktioniert VocalIQ?')
    }, 5000)
    
    setTimeout(() => {
      setStatus('KI: VocalIQ verbindet Telefonie mit KI für natürliche Gespräche.')
    }, 8000)
  }
  
  const endCall = () => {
    setIsCallActive(false)
    setStatus('Bereit')
  }

  return (
    <div className="flex flex-col items-center p-8 bg-white rounded-3xl shadow-xl max-w-2xl mx-auto">
      {/* Visualisierung Bereich */}
      <div className="relative w-64 h-64 mb-8">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className={`w-48 h-48 rounded-full ${isCallActive ? 'bg-gradient-to-br from-indigo-400 to-purple-600 animate-pulse' : 'bg-gradient-to-br from-gray-200 to-gray-300'}`}>
            <div className="w-full h-full rounded-full flex items-center justify-center">
              {isCallActive ? (
                <svg className="w-24 h-24 text-white animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                </svg>
              ) : (
                <svg className="w-24 h-24 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Status Anzeige */}
      <div className="mb-6 text-center">
        <p className="text-lg font-medium text-gray-700">{status}</p>
      </div>

      {/* Anruf Button */}
      <button
        onClick={isCallActive ? endCall : startCall}
        className={`
          px-8 py-4 rounded-full font-bold text-white text-lg
          transform transition-all duration-300 hover:scale-105
          ${isCallActive 
            ? 'bg-red-500 hover:bg-red-600 shadow-lg' 
            : 'bg-indigo-600 hover:bg-indigo-700 shadow-xl'}
        `}
      >
        {isCallActive ? 'ANRUF BEENDEN' : 'ANRUF AUSPROBIEREN'}
      </button>

      {/* Features */}
      <div className="mt-8 grid grid-cols-2 gap-4 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>Niedrige Latenz</span>
        </div>
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>Turn-Taking</span>
        </div>
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>31 Sprachen</span>
        </div>
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <span>Telefon-Support</span>
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-8 p-4 bg-indigo-50 rounded-lg text-center">
        <p className="text-sm text-indigo-700 font-medium">
          🎯 Vollversion: WebRTC Audio-Streaming mit GPT-4 & ElevenLabs
        </p>
      </div>
    </div>
  )
}

export default SimplifiedVoiceChat</
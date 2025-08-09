import { useState, useRef, useEffect } from 'react'
import Button from './ui/Button'
import { PlayIcon, PauseIcon, SpeakerWaveIcon } from '@heroicons/react/24/outline'

interface VoicePreviewProps {
  voiceId: string
  className?: string
  size?: 'sm' | 'md'
}

interface VoiceInfo {
  id: string
  name: string
  language: string
  gender: string
  sampleFile: string
  sampleText: string
}

const voiceDatabase: VoiceInfo[] = [
  // German voices
  {
    id: 'Antoni',
    name: 'Antoni',
    language: 'de',
    gender: 'male',
    sampleFile: '/audio/voice-samples/antoni-de.mp3',
    sampleText: 'Hallo, ich bin Ihr virtueller Assistent von VocalIQ. Wie kann ich Ihnen heute helfen?'
  },
  {
    id: 'Elli',
    name: 'Elli', 
    language: 'de',
    gender: 'female',
    sampleFile: '/audio/voice-samples/elli-de.mp3',
    sampleText: 'Hallo, ich bin Ihr virtueller Assistent von VocalIQ. Wie kann ich Ihnen heute helfen?'
  },
  {
    id: 'Callum',
    name: 'Callum',
    language: 'de', 
    gender: 'male',
    sampleFile: '/audio/voice-samples/callum-de.mp3',
    sampleText: 'Hallo, ich bin Ihr virtueller Assistent von VocalIQ. Wie kann ich Ihnen heute helfen?'
  },
  {
    id: 'Charlotte',
    name: 'Charlotte',
    language: 'de',
    gender: 'female', 
    sampleFile: '/audio/voice-samples/charlotte-de.mp3',
    sampleText: 'Hallo, ich bin Ihr virtueller Assistent von VocalIQ. Wie kann ich Ihnen heute helfen?'
  },
  {
    id: 'Liam',
    name: 'Liam',
    language: 'de',
    gender: 'male',
    sampleFile: '/audio/voice-samples/liam-de.mp3', 
    sampleText: 'Hallo, ich bin Ihr virtueller Assistent von VocalIQ. Wie kann ich Ihnen heute helfen?'
  },
  // English voices
  {
    id: 'Rachel',
    name: 'Rachel',
    language: 'en',
    gender: 'female',
    sampleFile: '/audio/voice-samples/rachel-en.mp3',
    sampleText: "Hello, I'm your virtual assistant from VocalIQ. How can I help you today?"
  },
  {
    id: 'Drew',
    name: 'Drew',
    language: 'en',
    gender: 'male',
    sampleFile: '/audio/voice-samples/drew-en.mp3',
    sampleText: "Hello, I'm your virtual assistant from VocalIQ. How can I help you today?"
  },
  {
    id: 'Clyde',
    name: 'Clyde',
    language: 'en',
    gender: 'male',
    sampleFile: '/audio/voice-samples/clyde-en.mp3',
    sampleText: "Hello, I'm your virtual assistant from VocalIQ. How can I help you today?"
  },
  {
    id: 'Paul',
    name: 'Paul',
    language: 'en',
    gender: 'male',
    sampleFile: '/audio/voice-samples/paul-en.mp3',
    sampleText: "Hello, I'm your virtual assistant from VocalIQ. How can I help you today?"
  },
  {
    id: 'Domi',
    name: 'Domi',
    language: 'en',
    gender: 'female',
    sampleFile: '/audio/voice-samples/domi-en.mp3',
    sampleText: "Hello, I'm your virtual assistant from VocalIQ. How can I help you today?"
  },
  {
    id: 'Dave',
    name: 'Dave',
    language: 'en',
    gender: 'male',
    sampleFile: '/audio/voice-samples/dave-en.mp3',
    sampleText: "Hello, I'm your virtual assistant from VocalIQ. How can I help you today?"
  }
]

function VoicePreview({ voiceId, className = '', size = 'sm' }: VoicePreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  const voice = voiceDatabase.find(v => v.id === voiceId)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleEnded = () => setIsPlaying(false)
    const handleError = () => {
      setError('Audio file not available')
      setIsPlaying(false)
      setIsLoading(false)
    }

    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('error', handleError)

    return () => {
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('error', handleError)
    }
  }, [])

  const handlePlayPause = async () => {
    if (!voice || !audioRef.current) return

    try {
      setError(null)

      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        setIsLoading(true)
        await audioRef.current.play()
        setIsPlaying(true)
        setIsLoading(false)
      }
    } catch (error) {
      console.warn('Audio playback failed:', error)
      setError('Playback failed')
      setIsPlaying(false)
      setIsLoading(false)
    }
  }

  if (!voice) {
    return (
      <div className={`inline-flex items-center space-x-1 text-gray-400 ${className}`}>
        <SpeakerWaveIcon className="h-4 w-4" />
        <span className="text-sm">Preview not available</span>
      </div>
    )
  }

  const buttonSize = size === 'md' ? 'sm' : 'xs'
  const iconSize = size === 'md' ? 'h-4 w-4' : 'h-3 w-3'

  return (
    <div className={`inline-flex items-center space-x-2 ${className}`}>
      <Button
        variant="outline"
        size={buttonSize}
        onClick={handlePlayPause}
        disabled={isLoading}
        className="inline-flex items-center"
        title={`Preview ${voice.name} voice`}
      >
        {isLoading ? (
          <div className={`animate-spin rounded-full border-2 border-primary-300 border-t-primary-600 ${iconSize}`} />
        ) : isPlaying ? (
          <PauseIcon className={iconSize} />
        ) : (
          <PlayIcon className={iconSize} />
        )}
        {size === 'md' && (
          <span className="ml-1">
            {isLoading ? 'Loading...' : isPlaying ? 'Playing' : 'Preview'}
          </span>
        )}
      </Button>

      {/* Waveform animation when playing */}
      {isPlaying && (
        <div className="inline-flex items-center space-x-1">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className={`bg-primary-500 rounded-full animate-pulse ${
                size === 'md' ? 'w-1 h-4' : 'w-0.5 h-3'
              }`}
              style={{
                animationDelay: `${i * 0.15}s`,
                animationDuration: '0.6s'
              }}
            />
          ))}
        </div>
      )}

      {error && (
        <span className="text-xs text-error-500">{error}</span>
      )}

      {/* Hidden audio element */}
      <audio 
        ref={audioRef}
        preload="none"
        src={voice.sampleFile}
        onLoadStart={() => setIsLoading(true)}
        onCanPlay={() => setIsLoading(false)}
      />
    </div>
  )
}

export default VoicePreview
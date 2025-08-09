import { useState, useEffect, useRef } from 'react'
import { Card, CardHeader, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { 
  PhoneIcon,
  MicrophoneIcon,
  SpeakerWaveIcon,
  StopIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

type CallStatus = 'idle' | 'connecting' | 'active' | 'ending' | 'ended'

interface TranscriptEntry {
  id: number
  speaker: 'agent' | 'user'
  text: string
  timestamp: string
}

function TestCall() {
  const [callStatus, setCallStatus] = useState<CallStatus>('idle')
  const [duration, setDuration] = useState(0)
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const transcriptEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (callStatus === 'active') {
      intervalRef.current = setInterval(() => {
        setDuration(prev => prev + 1)
        // Simulate audio level changes
        setAudioLevel(Math.random() * 100)
      }, 1000)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      setAudioLevel(0)
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [callStatus])

  useEffect(() => {
    // Auto-scroll transcript
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [transcript])

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const startCall = async () => {
    setCallStatus('connecting')
    setDuration(0)
    setTranscript([])
    
    // Simulate connection delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setCallStatus('active')
    setIsRecording(true)
    
    // Simulate agent greeting
    setTimeout(() => {
      addTranscriptEntry('agent', 'Hello! Thank you for calling. How can I help you today?')
    }, 1000)
    
    // Simulate conversation
    setTimeout(() => {
      addTranscriptEntry('user', 'Hi, I would like to test the voice agent system.')
    }, 3000)
    
    setTimeout(() => {
      addTranscriptEntry('agent', 'Of course! I\'m here to demonstrate the voice agent capabilities. What would you like to know about?')
    }, 5000)
    
    setTimeout(() => {
      addTranscriptEntry('user', 'Can you tell me about your features?')
    }, 8000)
    
    setTimeout(() => {
      addTranscriptEntry('agent', 'Certainly! I can handle various tasks including answering questions from the knowledge base, scheduling appointments, providing business information, and assisting with customer inquiries. I\'m available 24/7 and can speak multiple languages.')
    }, 10000)
  }

  const endCall = async () => {
    setCallStatus('ending')
    setIsRecording(false)
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setCallStatus('ended')
    addTranscriptEntry('agent', 'Thank you for calling. Goodbye!')
  }

  const resetCall = () => {
    setCallStatus('idle')
    setDuration(0)
    setTranscript([])
    setIsRecording(false)
  }

  const addTranscriptEntry = (speaker: 'agent' | 'user', text: string) => {
    const now = new Date()
    const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
    
    setTranscript(prev => [...prev, {
      id: prev.length + 1,
      speaker,
      text,
      timestamp
    }])
  }

  const getStatusColor = () => {
    switch (callStatus) {
      case 'connecting': return 'warning'
      case 'active': return 'success'
      case 'ending': return 'warning'
      case 'ended': return 'default'
      default: return 'default'
    }
  }

  const getStatusText = () => {
    switch (callStatus) {
      case 'connecting': return 'Connecting...'
      case 'active': return 'Call Active'
      case 'ending': return 'Ending Call...'
      case 'ended': return 'Call Ended'
      default: return 'Ready'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Test Voice Agent</h1>
        <Badge variant={getStatusColor()}>{getStatusText()}</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Control Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Call Control</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Call Button */}
            <div className="flex justify-center">
              {callStatus === 'idle' && (
                <button
                  onClick={startCall}
                  className="p-6 bg-green-500 hover:bg-green-600 rounded-full text-white transition-colors"
                >
                  <PhoneIcon className="h-12 w-12" />
                </button>
              )}
              {(callStatus === 'active' || callStatus === 'connecting') && (
                <button
                  onClick={endCall}
                  className="p-6 bg-red-500 hover:bg-red-600 rounded-full text-white transition-colors animate-pulse"
                >
                  <StopIcon className="h-12 w-12" />
                </button>
              )}
              {callStatus === 'ended' && (
                <button
                  onClick={resetCall}
                  className="p-6 bg-blue-500 hover:bg-blue-600 rounded-full text-white transition-colors"
                >
                  <ArrowPathIcon className="h-12 w-12" />
                </button>
              )}
            </div>

            {/* Call Timer */}
            <div className="text-center">
              <p className="text-3xl font-mono font-bold text-gray-900">
                {formatDuration(duration)}
              </p>
              <p className="text-sm text-gray-500">Call Duration</p>
            </div>

            {/* Audio Visualizer */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Audio Level</span>
                {isRecording && (
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-red-500">Recording</span>
                  </div>
                )}
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 transition-all duration-200"
                  style={{ width: `${audioLevel}%` }}
                />
              </div>
            </div>

            {/* Status Indicators */}
            <div className="space-y-2 pt-4 border-t">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <MicrophoneIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Microphone</span>
                </div>
                <Badge variant={isRecording ? 'success' : 'default'}>
                  {isRecording ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <SpeakerWaveIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Speaker</span>
                </div>
                <Badge variant={callStatus === 'active' ? 'success' : 'default'}>
                  {callStatus === 'active' ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>

            {/* Test Options */}
            <div className="space-y-2 pt-4 border-t">
              <p className="text-sm font-medium text-gray-700">Test Scenarios</p>
              <select 
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                disabled={callStatus !== 'idle'}
              >
                <option>General Inquiry</option>
                <option>Make Reservation</option>
                <option>Business Hours</option>
                <option>Technical Support</option>
                <option>Emergency Scenario</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Transcript */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Live Transcript</h3>
              {transcript.length > 0 && (
                <Button variant="outline" size="sm">
                  Export
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-96 overflow-y-auto bg-gray-50 rounded-lg p-4 space-y-3">
              {transcript.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <PhoneIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p>Start a test call to see the transcript</p>
                </div>
              ) : (
                <>
                  {transcript.map((entry) => (
                    <div
                      key={entry.id}
                      className={`flex ${entry.speaker === 'agent' ? 'justify-start' : 'justify-end'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          entry.speaker === 'agent'
                            ? 'bg-white text-gray-900'
                            : 'bg-blue-500 text-white'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className={`text-xs font-medium ${
                            entry.speaker === 'agent' ? 'text-gray-500' : 'text-blue-100'
                          }`}>
                            {entry.speaker === 'agent' ? 'Agent' : 'You'}
                          </span>
                          <span className={`text-xs ${
                            entry.speaker === 'agent' ? 'text-gray-400' : 'text-blue-100'
                          }`}>
                            {entry.timestamp}
                          </span>
                        </div>
                        <p className="text-sm">{entry.text}</p>
                      </div>
                    </div>
                  ))}
                  <div ref={transcriptEndRef} />
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Call Statistics */}
      {callStatus === 'ended' && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Call Summary</h3>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-2xl font-bold text-gray-900">{formatDuration(duration)}</p>
                <p className="text-sm text-gray-500">Total Duration</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{transcript.length}</p>
                <p className="text-sm text-gray-500">Interactions</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600">Positive</p>
                <p className="text-sm text-gray-500">Sentiment</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">98%</p>
                <p className="text-sm text-gray-500">Accuracy</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default TestCall
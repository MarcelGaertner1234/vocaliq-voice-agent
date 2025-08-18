import { useState, useEffect, useRef } from 'react'
import { Card, CardHeader, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { 
  PhoneIcon,
  MicrophoneIcon,
  SpeakerWaveIcon,
  StopIcon,
  ArrowPathIcon,
  FireIcon,
  ChartBarIcon,
  ClockIcon,
  UserGroupIcon
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
  const [selectedScenario, setSelectedScenario] = useState<string>('standard')
  const [leadScore, setLeadScore] = useState(5)
  const [followUpScheduled, setFollowUpScheduled] = useState<string | null>(null)
  const [routingDecision, setRoutingDecision] = useState<string | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const transcriptEndRef = useRef<HTMLDivElement>(null)

  // Demo Scenarios with enhanced descriptions
  const scenarios = [
    {
      id: 'system_explain',
      name: 'System Erklärung',
      description: 'KI erklärt das VocalIQ System',
      icon: PhoneIcon,
      color: 'blue',
      features: ['System Overview', 'Feature Demonstration', 'Benefits']
    },
    {
      id: 'lead_scoring',
      name: 'Lead Scoring Demo',
      description: 'Automatische Lead-Bewertung (1-10)',
      icon: ChartBarIcon,
      color: 'purple',
      features: ['Sentiment Analysis', 'Keyword Detection', 'Score Calculation']
    },
    {
      id: 'follow_up',
      name: '30% mehr Umsatz',
      description: 'Follow-Up System (3/7/14/30 Tage)',
      icon: ClockIcon,
      color: 'green',
      features: ['Automated Scheduling', 'Personalized Scripts', 'Revenue Tracking']
    },
    {
      id: 'reactivation',
      name: 'Lead Reaktivierung',
      description: 'Kalte Leads wiederbeleben (30/60/90/180 Tage)',
      icon: ArrowPathIcon,
      color: 'orange',
      features: ['Cold Lead Detection', 'Special Offers', 'Win-Back Campaigns']
    },
    {
      id: 'hotel_routing',
      name: 'Hotel Use-Case',
      description: 'Kunde wählt: KI-Assistent oder Mensch',
      icon: UserGroupIcon,
      color: 'indigo',
      features: ['Intelligent Routing', 'Customer Choice', 'Department Transfer']
    }
  ]

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
    setLeadScore(5)
    setFollowUpScheduled(null)
    setRoutingDecision(null)
    
    // Simulate connection delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setCallStatus('active')
    setIsRecording(true)
    
    // Different conversation flows based on selected scenario
    if (selectedScenario === 'system_explain') {
      // System explanation flow
      setTimeout(() => {
        addTranscriptEntry('agent', 'Hallo! Willkommen bei VocalIQ. Ich bin Ihre KI-Assistentin und erkläre Ihnen gerne unser System.')
      }, 1000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Hallo, was kann VocalIQ alles?')
      }, 3000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', 'VocalIQ ist eine KI-Maschine für profitables Telefon-Marketing. Wir steigern Ihren Umsatz um 30% durch automatische Lead-Bewertung, intelligente Follow-Ups und systematische Lead-Reaktivierung.')
      }, 5000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Wie funktioniert die Lead-Bewertung?')
      }, 8000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', 'Nach jedem Anruf bewerte ich automatisch den Lead von 1-10 basierend auf Gesprächsdauer, Sentiment und Keywords. Heiße Leads (8-10) bekommen sofortige Priorität!')
        setLeadScore(9)
      }, 10000)
      
    } else if (selectedScenario === 'lead_scoring') {
      // Lead scoring demonstration
      setTimeout(() => {
        addTranscriptEntry('agent', 'Guten Tag! Ich rufe von TechSolutions an. Haben Sie kurz Zeit für unser neues CRM-System?')
      }, 1000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Ja, wir suchen tatsächlich gerade eine neue Lösung!')
      }, 3000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', '🎯 [Lead Score steigt auf 8] Das ist perfekt! Welche Herausforderungen haben Sie mit Ihrem aktuellen System?')
        setLeadScore(8)
      }, 5000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Die Integration mit anderen Tools ist schwierig und die Benutzeroberfläche ist veraltet.')
      }, 8000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', '📈 [Lead Score: 9 - Hohe Kaufbereitschaft erkannt] Diese Probleme löst unser System perfekt. Können wir einen Demo-Termin vereinbaren?')
        setLeadScore(9)
      }, 10000)
      
      setTimeout(() => {
        addTranscriptEntry('system', '✅ Lead automatisch als HOT kategorisiert. Follow-Up in 3 Tagen geplant.')
        setFollowUpScheduled('3 Tage')
      }, 12000)
      
    } else if (selectedScenario === 'follow_up') {
      // 30% mehr Umsatz demonstration
      setTimeout(() => {
        addTranscriptEntry('agent', 'Hallo Herr Schmidt! Vor 7 Tagen hatten wir über unsere Lösung gesprochen. Sie wollten sich intern beraten.')
      }, 1000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Ah ja, richtig. Wir hatten noch keine Zeit für ein Meeting.')
      }, 3000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', 'Kein Problem! Ich habe inzwischen eine Fallstudie von einem ähnlichen Unternehmen wie Ihrem. 45% Effizienzsteigerung in 3 Monaten!')
      }, 5000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Das klingt interessant! Können Sie mir die zusenden?')
      }, 8000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', 'Natürlich! Ich sende sie sofort. Wann wäre ein guter Zeitpunkt für einen kurzen Call nächste Woche?')
        setLeadScore(7)
      }, 10000)
      
      setTimeout(() => {
        addTranscriptEntry('system', '💰 Follow-Up erfolgreich! Nächster Kontakt in 7 Tagen. Umsatzpotenzial: +30%')
        setFollowUpScheduled('7 Tage')
      }, 12000)
      
    } else if (selectedScenario === 'reactivation') {
      // Lead Reactivation demonstration
      setTimeout(() => {
        addTranscriptEntry('agent', 'Guten Tag Frau Müller! Es ist schon 90 Tage her seit unserem letzten Gespräch. Ich wollte fragen, ob sich Ihre Anforderungen geändert haben?')
      }, 1000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Oh, hallo. Ja, wir hatten uns damals dagegen entschieden.')
      }, 3000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', 'Verstehe. Seit damals haben wir unser Angebot stark verbessert. Speziell für Bestandskunden haben wir jetzt 25% Rabatt auf das erste Jahr!')
      }, 5000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Hmm, das macht es schon interessanter. Was hat sich noch geändert?')
      }, 8000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', 'Wir haben jetzt auch die Integration, die Sie damals vermisst haben, plus kostenlosen Premium-Support!')
        setLeadScore(6)
      }, 10000)
      
      setTimeout(() => {
        addTranscriptEntry('system', '🔄 Lead erfolgreich reaktiviert! Status: WARM. Follow-Up in 14 Tagen.')
        setFollowUpScheduled('14 Tage')
      }, 12000)
      
    } else if (selectedScenario === 'hotel_routing') {
      // Hotel routing with customer choice
      setTimeout(() => {
        addTranscriptEntry('agent', 'Guten Tag! Willkommen im Hotel Königshof. Wie kann ich Ihnen helfen?')
      }, 1000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Ich möchte ein Zimmer für nächstes Wochenende buchen.')
      }, 3000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', 'Gerne! Ich kann Ihnen sofort bei der Buchung helfen oder Sie direkt mit unserer Reservierung verbinden. Was wäre Ihnen lieber?')
        setRoutingDecision('pending')
      }, 5000)
      
      setTimeout(() => {
        addTranscriptEntry('user', 'Können Sie mir erst mal die Preise nennen?')
      }, 8000)
      
      setTimeout(() => {
        addTranscriptEntry('agent', 'Natürlich! Für nächstes Wochenende haben wir Doppelzimmer ab 120€ und Suiten ab 180€ pro Nacht. Soll ich prüfen, was verfügbar ist?')
        setRoutingDecision('ai_assistant')
      }, 10000)
      
      setTimeout(() => {
        addTranscriptEntry('system', '🎯 Kunde entschied sich für KI-Assistenten. Lead Score: 7')
        setLeadScore(7)
      }, 12000)
    }
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

            {/* Scenario Selection */}
            <div className="space-y-2 pt-4 border-t">
              <p className="text-sm font-medium text-gray-700">Demo Szenario</p>
              <select 
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                value={selectedScenario}
                onChange={(e) => setSelectedScenario(e.target.value)}
                disabled={callStatus !== 'idle'}
              >
                {scenarios.map(scenario => (
                  <option key={scenario.id} value={scenario.id}>
                    {scenario.name}
                  </option>
                ))}
              </select>
              
              {/* Scenario Description */}
              {callStatus === 'idle' && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  {scenarios.find(s => s.id === selectedScenario) && (
                    <>
                      <p className="text-sm text-gray-600 mb-2">
                        {scenarios.find(s => s.id === selectedScenario)?.description}
                      </p>
                      <div className="space-y-1">
                        {scenarios.find(s => s.id === selectedScenario)?.features.map((feature, idx) => (
                          <div key={idx} className="flex items-center space-x-1">
                            <FireIcon className="h-3 w-3 text-orange-500" />
                            <span className="text-xs text-gray-500">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
            
            {/* Lead Management Indicators */}
            {callStatus === 'active' && (
              <div className="space-y-2 pt-4 border-t">
                <p className="text-sm font-medium text-gray-700">Lead Management</p>
                
                {/* Lead Score */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Lead Score</span>
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      {[...Array(10)].map((_, i) => (
                        <div
                          key={i}
                          className={`h-2 w-2 rounded-full ${
                            i < leadScore
                              ? leadScore >= 8 ? 'bg-green-500' 
                                : leadScore >= 5 ? 'bg-yellow-500' 
                                : 'bg-red-500'
                              : 'bg-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-sm font-bold">{leadScore}/10</span>
                  </div>
                </div>
                
                {/* Follow-Up Status */}
                {followUpScheduled && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Follow-Up</span>
                    <Badge variant="success">{followUpScheduled}</Badge>
                  </div>
                )}
                
                {/* Routing Decision */}
                {routingDecision && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Routing</span>
                    <Badge variant={routingDecision === 'ai_assistant' ? 'info' : 'warning'}>
                      {routingDecision === 'ai_assistant' ? 'KI' : 'Mensch'}
                    </Badge>
                  </div>
                )}
              </div>
            )}
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

      {/* Enhanced Call Statistics with Lead Management */}
      {callStatus === 'ended' && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Anruf-Zusammenfassung</h3>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <p className="text-2xl font-bold text-gray-900">{formatDuration(duration)}</p>
                <p className="text-sm text-gray-500">Gesprächsdauer</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{transcript.length}</p>
                <p className="text-sm text-gray-500">Interaktionen</p>
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <p className="text-2xl font-bold">
                    <span className={`${
                      leadScore >= 8 ? 'text-green-600' : 
                      leadScore >= 5 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {leadScore}/10
                    </span>
                  </p>
                </div>
                <p className="text-sm text-gray-500">Lead Score</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600">Positiv</p>
                <p className="text-sm text-gray-500">Sentiment</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {followUpScheduled || 'Keine'}
                </p>
                <p className="text-sm text-gray-500">Follow-Up</p>
              </div>
            </div>
            
            {/* Lead Management Actions */}
            <div className="mt-6 pt-6 border-t">
              <p className="text-sm font-medium text-gray-700 mb-3">Empfohlene Aktionen</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {leadScore >= 8 && (
                  <Button variant="primary" size="sm" className="w-full">
                    <FireIcon className="h-4 w-4 mr-2" />
                    Sofort kontaktieren
                  </Button>
                )}
                {leadScore >= 5 && leadScore < 8 && (
                  <Button variant="outline" size="sm" className="w-full">
                    <ClockIcon className="h-4 w-4 mr-2" />
                    Follow-Up planen
                  </Button>
                )}
                {leadScore < 5 && (
                  <Button variant="outline" size="sm" className="w-full">
                    <ArrowPathIcon className="h-4 w-4 mr-2" />
                    In 30 Tagen reaktivieren
                  </Button>
                )}
                <Button variant="outline" size="sm" className="w-full">
                  <ChartBarIcon className="h-4 w-4 mr-2" />
                  Lead Details anzeigen
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Scenario Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {scenarios.map(scenario => (
          <Card 
            key={scenario.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedScenario === scenario.id ? 'ring-2 ring-blue-500' : ''
            }`}
            onClick={() => callStatus === 'idle' && setSelectedScenario(scenario.id)}
          >
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg bg-${scenario.color}-100`}>
                  <scenario.icon className={`h-6 w-6 text-${scenario.color}-600`} />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{scenario.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">{scenario.description}</p>
                  <div className="mt-2 space-y-1">
                    {scenario.features.map((feature, idx) => (
                      <div key={idx} className="flex items-center space-x-1">
                        <div className="h-1.5 w-1.5 bg-gray-400 rounded-full" />
                        <span className="text-xs text-gray-500">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default TestCall
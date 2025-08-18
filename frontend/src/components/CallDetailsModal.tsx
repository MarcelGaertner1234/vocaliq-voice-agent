import { Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import Button from './ui/Button'
import Badge from './ui/Badge'
import {
  XMarkIcon,
  PhoneIcon,
  ClockIcon,
  DocumentTextIcon,
  SpeakerWaveIcon,
  ArrowDownTrayIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

interface CallDetails {
  id: number
  phone: string
  customerName: string | null
  direction: 'inbound' | 'outbound'
  status: string
  duration: string
  timestamp: string
  transcript: string
  intent: string | null
  sentiment?: 'positive' | 'neutral' | 'negative'
  audioUrl?: string
  fullTranscript?: Array<{
    speaker: 'agent' | 'customer'
    text: string
    timestamp: string
  }>
}

interface CallDetailsModalProps {
  isOpen: boolean
  onClose: () => void
  call: CallDetails | null
}

function CallDetailsModal({ isOpen, onClose, call }: CallDetailsModalProps) {
  if (!call) return null

  // Mock full transcript
  const fullTranscript = call.fullTranscript || [
    { speaker: 'agent', text: 'Hello! Thank you for calling. How can I help you today?', timestamp: '00:00:01' },
    { speaker: 'customer', text: call.transcript || 'Customer inquiry...', timestamp: '00:00:05' },
    { speaker: 'agent', text: 'I understand. Let me help you with that.', timestamp: '00:00:15' },
    { speaker: 'customer', text: 'That would be great, thank you.', timestamp: '00:00:20' },
    { speaker: 'agent', text: 'I\'ve processed your request. Is there anything else I can help you with?', timestamp: '00:00:30' },
    { speaker: 'customer', text: 'No, that\'s all. Thank you for your help!', timestamp: '00:00:35' },
    { speaker: 'agent', text: 'You\'re welcome! Have a great day!', timestamp: '00:00:40' },
  ]

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive': return 'success'
      case 'negative': return 'error'
      default: return 'default'
    }
  }

  const getIntentColor = (intent: string | null) => {
    if (!intent) return 'default'
    switch (intent) {
      case 'reservation': return 'success'
      case 'cancellation': return 'error'
      case 'inquiry': return 'warning'
      default: return 'default'
    }
  }

  const handleExportTranscript = () => {
    const content = fullTranscript.map(entry => 
      `[${entry.timestamp}] ${entry.speaker.toUpperCase()}: ${entry.text}`
    ).join('\n\n')
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `call_transcript_${call.id}.txt`
    a.click()
  }

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl">
                {/* Header */}
                <div className="bg-gray-50 px-6 py-4 border-b">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <PhoneIcon className="h-6 w-6 text-gray-400" />
                      <Dialog.Title className="text-lg font-semibold text-gray-900">
                        Call Details
                      </Dialog.Title>
                    </div>
                    <button
                      onClick={onClose}
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <XMarkIcon className="h-6 w-6" />
                    </button>
                  </div>
                </div>

                {/* Content */}
                <div className="px-6 py-4">
                  {/* Call Information */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div>
                      <p className="text-sm text-gray-500">Contact</p>
                      <p className="font-medium">{call.customerName || call.phone}</p>
                      {call.customerName && (
                        <p className="text-sm text-gray-500">{call.phone}</p>
                      )}
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Duration</p>
                      <div className="flex items-center mt-1">
                        <ClockIcon className="h-4 w-4 text-gray-400 mr-1" />
                        <span className="font-medium">{call.duration}</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Time</p>
                      <p className="font-medium">{call.timestamp}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Direction</p>
                      <Badge variant={call.direction === 'inbound' ? 'success' : 'default'}>
                        {call.direction}
                      </Badge>
                    </div>
                  </div>

                  {/* Analytics */}
                  <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-500">Intent</p>
                      {call.intent ? (
                        <Badge variant={getIntentColor(call.intent)}>
                          {call.intent}
                        </Badge>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Sentiment</p>
                      <Badge variant={getSentimentColor(call.sentiment || 'neutral')}>
                        {call.sentiment || 'neutral'}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <Badge variant={call.status === 'completed' ? 'success' : 'error'}>
                        {call.status}
                      </Badge>
                    </div>
                  </div>

                  {/* Audio Player */}
                  {call.audioUrl && (
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <SpeakerWaveIcon className="h-5 w-5 text-gray-400" />
                          <span className="text-sm font-medium text-gray-700">Recording</span>
                        </div>
                      </div>
                      <audio controls className="w-full">
                        <source src={call.audioUrl} type="audio/mpeg" />
                        Your browser does not support the audio element.
                      </audio>
                    </div>
                  )}

                  {/* Transcript */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-700">Full Transcript</span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleExportTranscript}
                      >
                        <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                        Export
                      </Button>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto space-y-3">
                      {fullTranscript.map((entry, index) => (
                        <div
                          key={index}
                          className={`flex ${entry.speaker === 'agent' ? 'justify-start' : 'justify-end'}`}
                        >
                          <div
                            className={`max-w-md px-4 py-2 rounded-lg ${
                              entry.speaker === 'agent'
                                ? 'bg-white text-gray-900 border border-gray-200'
                                : 'bg-blue-500 text-white'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className={`text-xs font-medium ${
                                entry.speaker === 'agent' ? 'text-gray-500' : 'text-blue-100'
                              }`}>
                                {entry.speaker === 'agent' ? 'Agent' : 'Customer'}
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
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="bg-gray-50 px-6 py-3 flex justify-between">
                  <Button
                    variant="outline"
                    onClick={() => {
                      // Generate PDF report
                      alert('PDF report generation would be implemented here')
                    }}
                  >
                    <ChartBarIcon className="h-4 w-4 mr-2" />
                    Generate Report
                  </Button>
                  <Button onClick={onClose}>
                    Close
                  </Button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}

export default CallDetailsModal
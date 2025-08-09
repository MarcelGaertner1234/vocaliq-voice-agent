import { useState } from 'react'
import { Card, CardHeader, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'
import { 
  MagnifyingGlassIcon,
  PhoneIcon,
  ClockIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

function CallHistory() {
  const [searchTerm, setSearchTerm] = useState('')

  const calls = [
    {
      id: 1,
      phone: '+49 30 12345678',
      direction: 'inbound',
      status: 'completed',
      duration: '4:23',
      timestamp: '2024-01-15 14:32',
      transcript: 'Customer called to make a reservation for tonight...',
      customerName: 'Max Mustermann',
      intent: 'reservation'
    },
    {
      id: 2,
      phone: '+49 30 87654321',
      direction: 'outbound',
      status: 'failed',
      duration: '0:15',
      timestamp: '2024-01-15 14:24',
      transcript: 'Call failed to connect...',
      customerName: null,
      intent: null
    },
    {
      id: 3,
      phone: '+49 30 11223344',
      direction: 'inbound',
      status: 'completed',
      duration: '2:17',
      timestamp: '2024-01-15 14:18',
      transcript: 'Customer asked about opening hours and menu...',
      customerName: 'Anna Schmidt',
      intent: 'inquiry'
    },
    {
      id: 4,
      phone: '+49 30 99887766',
      direction: 'inbound',
      status: 'completed',
      duration: '6:45',
      timestamp: '2024-01-15 13:55',
      transcript: 'Customer wanted to cancel their reservation...',
      customerName: 'Peter Weber',
      intent: 'cancellation'
    },
  ]

  const filteredCalls = calls.filter(call => 
    call.phone.includes(searchTerm) || 
    call.customerName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    call.intent?.includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'failed': return 'error'
      case 'in-progress': return 'warning'
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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Call History</h1>
        <Button>Export Data</Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by phone, name, or intent..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline">Filter</Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Direction
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Intent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCalls.map((call) => (
                  <tr key={call.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <PhoneIcon className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {call.customerName || call.phone}
                          </div>
                          {call.customerName && (
                            <div className="text-sm text-gray-500">{call.phone}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={call.direction === 'inbound' ? 'success' : 'default'}>
                        {call.direction}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <ClockIcon className="h-4 w-4 text-gray-400 mr-1" />
                        {call.duration}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={getStatusColor(call.status)}>
                        {call.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {call.intent ? (
                        <Badge variant={getIntentColor(call.intent)}>
                          {call.intent}
                        </Badge>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {call.timestamp}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Button variant="outline" size="sm">
                        <DocumentTextIcon className="h-4 w-4 mr-1" />
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default CallHistory
import { useState } from 'react'
import { Card, CardHeader, CardContent } from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import { 
  DocumentTextIcon,
  FunnelIcon
} from '@heroicons/react/24/outline'

// Mock log data
const mockLogs = [
  { id: 1, timestamp: '2025-08-09 21:15:43', level: 'INFO', message: 'User login successful', details: 'admin@vocaliq.de' },
  { id: 2, timestamp: '2025-08-09 21:14:22', level: 'ERROR', message: 'API call failed', details: 'OpenAI rate limit exceeded' },
  { id: 3, timestamp: '2025-08-09 21:13:15', level: 'INFO', message: 'Call completed', details: 'Duration: 3:45, Company: TechCorp' },
  { id: 4, timestamp: '2025-08-09 21:12:08', level: 'WARNING', message: 'High memory usage', details: 'Memory usage at 85%' },
  { id: 5, timestamp: '2025-08-09 21:10:55', level: 'INFO', message: 'Database backup started', details: 'Automatic backup' },
  { id: 6, timestamp: '2025-08-09 21:09:30', level: 'INFO', message: 'New user registered', details: 'user@example.com' },
  { id: 7, timestamp: '2025-08-09 21:08:12', level: 'ERROR', message: 'Twilio webhook failed', details: 'Connection timeout' },
  { id: 8, timestamp: '2025-08-09 21:07:45', level: 'INFO', message: 'API key updated', details: 'ElevenLabs configuration' },
  { id: 9, timestamp: '2025-08-09 21:06:20', level: 'WARNING', message: 'Rate limit approaching', details: '90/100 requests used' },
  { id: 10, timestamp: '2025-08-09 21:05:10', level: 'INFO', message: 'System health check', details: 'All services operational' },
]

const levelColors = {
  INFO: 'default',
  WARNING: 'warning',
  ERROR: 'error'
} as const

function Logs() {
  const [filter, setFilter] = useState<'ALL' | 'INFO' | 'WARNING' | 'ERROR'>('ALL')
  
  const filteredLogs = filter === 'ALL' 
    ? mockLogs 
    : mockLogs.filter(log => log.level === filter)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">System Logs</h1>
        
        {/* Filter Buttons */}
        <div className="flex items-center space-x-2">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <div className="flex space-x-2">
            {(['ALL', 'INFO', 'WARNING', 'ERROR'] as const).map((level) => (
              <button
                key={level}
                onClick={() => setFilter(level)}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  filter === level
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Recent Logs</h3>
            </div>
            <span className="text-sm text-gray-500">
              Showing {filteredLogs.length} entries
            </span>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Message
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-6 py-3 whitespace-nowrap text-xs text-gray-500 font-mono">
                      {log.timestamp}
                    </td>
                    <td className="px-6 py-3 whitespace-nowrap">
                      <Badge variant={levelColors[log.level as keyof typeof levelColors]}>
                        {log.level}
                      </Badge>
                    </td>
                    <td className="px-6 py-3 text-sm text-gray-900">
                      {log.message}
                    </td>
                    <td className="px-6 py-3 text-xs text-gray-500">
                      {log.details}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Log Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {mockLogs.filter(l => l.level === 'INFO').length}
                </p>
                <p className="text-sm text-gray-500">Info Logs</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-yellow-600">
                  {mockLogs.filter(l => l.level === 'WARNING').length}
                </p>
                <p className="text-sm text-gray-500">Warnings</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-red-600">
                  {mockLogs.filter(l => l.level === 'ERROR').length}
                </p>
                <p className="text-sm text-gray-500">Errors</p>
              </div>
              <div className="p-3 bg-red-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Logs
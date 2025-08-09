import { Card, CardHeader, CardContent } from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { 
  PhoneIcon, 
  ClockIcon, 
  CheckCircleIcon,
  ExclamationCircleIcon 
} from '@heroicons/react/24/outline'

function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <PhoneIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Calls Today</p>
                <p className="text-2xl font-bold text-gray-900">47</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg Call Duration</p>
                <p className="text-2xl font-bold text-gray-900">3:42</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Successful Calls</p>
                <p className="text-2xl font-bold text-gray-900">89%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationCircleIcon className="h-8 w-8 text-error-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Failed Calls</p>
                <p className="text-2xl font-bold text-gray-900">5</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">Recent Calls</h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { id: 1, phone: '+49 30 12345678', status: 'completed', duration: '4:23', time: '2 min ago' },
                { id: 2, phone: '+49 30 87654321', status: 'failed', duration: '0:15', time: '8 min ago' },
                { id: 3, phone: '+49 30 11223344', status: 'completed', duration: '2:17', time: '12 min ago' },
                { id: 4, phone: '+49 30 99887766', status: 'completed', duration: '6:45', time: '18 min ago' },
              ].map((call) => (
                <div key={call.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                  <div className="flex items-center">
                    <div className="ml-0">
                      <p className="text-sm font-medium text-gray-900">{call.phone}</p>
                      <p className="text-xs text-gray-500">{call.time}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-sm text-gray-500">{call.duration}</span>
                    <Badge variant={call.status === 'completed' ? 'success' : 'error'}>
                      {call.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium text-gray-900">System Status</h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: 'VoiceAI API', status: 'online', latency: '42ms' },
                { name: 'Twilio Connection', status: 'online', latency: '18ms' },
                { name: 'Database', status: 'online', latency: '8ms' },
                { name: 'Knowledge Base', status: 'online', latency: '120ms' },
              ].map((service) => (
                <div key={service.name} className="flex items-center justify-between py-2">
                  <div className="flex items-center">
                    <div className={`h-2 w-2 rounded-full mr-3 ${
                      service.status === 'online' ? 'bg-success-500' : 'bg-error-500'
                    }`} />
                    <span className="text-sm font-medium text-gray-900">{service.name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">{service.latency}</span>
                    <Badge variant={service.status === 'online' ? 'success' : 'error'}>
                      {service.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard
import { Card, CardHeader, CardContent } from '../../components/ui/Card'
import { 
  PhoneIcon, 
  UsersIcon, 
  CurrencyEuroIcon,
  ClockIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'

const stats = [
  { 
    label: 'Total Calls', 
    value: '12,543', 
    change: '+12%', 
    trend: 'up',
    icon: PhoneIcon,
    color: 'bg-blue-500'
  },
  { 
    label: 'Active Users', 
    value: '347', 
    change: '+8%', 
    trend: 'up',
    icon: UsersIcon,
    color: 'bg-green-500'
  },
  { 
    label: 'Monthly Revenue', 
    value: '€24,780', 
    change: '+23%', 
    trend: 'up',
    icon: CurrencyEuroIcon,
    color: 'bg-purple-500'
  },
  { 
    label: 'Avg Call Duration', 
    value: '4:23', 
    change: '-5%', 
    trend: 'down',
    icon: ClockIcon,
    color: 'bg-orange-500'
  },
]

const recentActivity = [
  { time: '2 min ago', event: 'New call completed', details: 'TechCorp GmbH - 3:45 duration' },
  { time: '15 min ago', event: 'User registered', details: 'peter@example.com - Sales Masters AG' },
  { time: '1 hour ago', event: 'API key updated', details: 'OpenAI configuration changed' },
  { time: '2 hours ago', event: 'Company upgraded', details: 'Support Plus - Starter to Professional' },
  { time: '3 hours ago', event: 'System backup', details: 'Automatic backup completed' },
]

function Analytics() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analytics Overview</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className={`p-3 rounded-lg ${stat.color} bg-opacity-10`}>
                  <stat.icon className={`h-6 w-6 ${stat.color.replace('bg-', 'text-')}`} />
                </div>
                <div className={`flex items-center text-sm font-medium ${
                  stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stat.change}
                  {stat.trend === 'up' ? (
                    <ArrowUpIcon className="h-4 w-4 ml-1" />
                  ) : (
                    <ArrowDownIcon className="h-4 w-4 ml-1" />
                  )}
                </div>
              </div>
              <div className="mt-4">
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-start space-x-3 pb-4 border-b border-gray-100 last:border-0">
                <div className="flex-shrink-0 w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">{activity.event}</p>
                    <span className="text-xs text-gray-500">{activity.time}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{activity.details}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Analytics
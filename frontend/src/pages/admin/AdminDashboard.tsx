import { Card, CardHeader, CardContent } from '../../components/ui/Card'
import { 
  ArrowTopRightOnSquareIcon,
  CpuChipIcon,
  PhoneIcon,
  SpeakerWaveIcon,
  MagnifyingGlassIcon,
  EnvelopeIcon,
  ChartBarIcon,
  CreditCardIcon,
  DocumentTextIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'

// Service Quick Links
const serviceLinks = [
  {
    category: 'AI & Voice Services',
    services: [
      {
        name: 'OpenAI Platform',
        description: 'GPT-4 & Whisper API',
        url: 'https://platform.openai.com/api-keys',
        icon: CpuChipIcon,
        color: 'bg-green-500',
        quickLinks: [
          { label: 'API Keys', url: 'https://platform.openai.com/api-keys' },
          { label: 'Usage', url: 'https://platform.openai.com/usage' },
          { label: 'Billing', url: 'https://platform.openai.com/account/billing' },
          { label: 'Docs', url: 'https://platform.openai.com/docs' }
        ]
      },
      {
        name: 'ElevenLabs',
        description: 'Text-to-Speech',
        url: 'https://elevenlabs.io/app',
        icon: SpeakerWaveIcon,
        color: 'bg-purple-500',
        quickLinks: [
          { label: 'Voice Lab', url: 'https://elevenlabs.io/app/voice-lab' },
          { label: 'API Keys', url: 'https://elevenlabs.io/app/settings/api-keys' },
          { label: 'Usage', url: 'https://elevenlabs.io/app/usage' },
          { label: 'Voices', url: 'https://elevenlabs.io/voice-library' }
        ]
      },
      {
        name: 'Twilio Console',
        description: 'Telephony Services',
        url: 'https://console.twilio.com',
        icon: PhoneIcon,
        color: 'bg-red-500',
        quickLinks: [
          { label: 'Dashboard', url: 'https://console.twilio.com' },
          { label: 'Phone Numbers', url: 'https://console.twilio.com/us1/develop/phone-numbers' },
          { label: 'Logs', url: 'https://console.twilio.com/us1/monitor/logs' },
          { label: 'Billing', url: 'https://console.twilio.com/us1/billing/manage-billing' }
        ]
      }
    ]
  },
  {
    category: 'Database & Infrastructure',
    services: [
      {
        name: 'Weaviate Cloud',
        description: 'Vector Database',
        url: 'https://console.weaviate.cloud',
        icon: MagnifyingGlassIcon,
        color: 'bg-blue-500',
        quickLinks: [
          { label: 'Clusters', url: 'https://console.weaviate.cloud' },
          { label: 'API Keys', url: 'https://console.weaviate.cloud/api-keys' },
          { label: 'Docs', url: 'https://weaviate.io/developers/weaviate' }
        ]
      }
    ]
  },
  {
    category: 'Monitoring & Analytics',
    services: [
      {
        name: 'System Monitoring',
        description: 'Internal Metrics',
        url: '/admin/monitoring',
        icon: ChartBarIcon,
        color: 'bg-indigo-500',
        internal: true
      }
    ]
  }
]

// System Stats (Mock data - replace with real API calls)
const systemStats = [
  { label: 'Active Companies', value: '12', change: '+2', trend: 'up' },
  { label: 'Total Users', value: '247', change: '+18', trend: 'up' },
  { label: 'Calls Today', value: '1,429', change: '+127', trend: 'up' },
  { label: 'System Health', value: '99.9%', change: '0%', trend: 'stable' }
]

function AdminDashboard() {
  const handleServiceClick = (url: string, internal?: boolean) => {
    if (internal) {
      window.location.href = url
    } else {
      window.open(url, '_blank')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">System administration and service management</p>
        </div>
        <div className="flex items-center space-x-2">
          <ShieldCheckIcon className="h-5 w-5 text-red-600" />
          <span className="text-sm font-medium text-gray-700">Admin Access</span>
        </div>
      </div>

      {/* System Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {systemStats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={`text-sm font-medium ${
                  stat.trend === 'up' ? 'text-green-600' : 
                  stat.trend === 'down' ? 'text-red-600' : 
                  'text-gray-500'
                }`}>
                  {stat.change}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Service Quick Links */}
      {serviceLinks.map((category) => (
        <div key={category.category}>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">{category.category}</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {category.services.map((service) => (
              <Card 
                key={service.name}
                className="hover:shadow-lg transition-shadow cursor-pointer"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${service.color} bg-opacity-10`}>
                        <service.icon className={`h-6 w-6 ${service.color.replace('bg-', 'text-')}`} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{service.name}</h3>
                        <p className="text-xs text-gray-500">{service.description}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleServiceClick(service.url, service.internal)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <ArrowTopRightOnSquareIcon className="h-5 w-5" />
                    </button>
                  </div>
                </CardHeader>
                {service.quickLinks && (
                  <CardContent className="pt-0">
                    <div className="grid grid-cols-2 gap-2">
                      {service.quickLinks.map((link) => (
                        <button
                          key={link.label}
                          onClick={() => handleServiceClick(link.url)}
                          className="text-xs text-left px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-md text-gray-700 hover:text-gray-900 transition-colors"
                        >
                          {link.label} →
                        </button>
                      ))}
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        </div>
      ))}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-primary-50 hover:bg-primary-100 rounded-lg text-primary-700 transition-colors">
              <CreditCardIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Check Billing</span>
            </button>
            <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-50 hover:bg-green-100 rounded-lg text-green-700 transition-colors">
              <DocumentTextIcon className="h-5 w-5" />
              <span className="text-sm font-medium">View Logs</span>
            </button>
            <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-purple-700 transition-colors">
              <EnvelopeIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Email Reports</span>
            </button>
            <button className="flex items-center justify-center space-x-2 px-4 py-3 bg-red-50 hover:bg-red-100 rounded-lg text-red-700 transition-colors">
              <ShieldCheckIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Security Audit</span>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default AdminDashboard
import { useState, useEffect } from 'react'
import { Card, CardHeader, CardContent } from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Badge from '../../components/ui/Badge'
import { 
  KeyIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowTopRightOnSquareIcon,
  ClipboardDocumentIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline'
import { settingsApi } from '../../services/api'

interface ApiConfig {
  service: string
  name: string
  icon: string
  color: string
  fields: {
    key: string
    label: string
    value: string
    type: 'text' | 'password'
    required: boolean
  }[]
  links: {
    label: string
    url: string
  }[]
  status?: 'connected' | 'error' | 'not_configured'
}

const apiConfigs: ApiConfig[] = [
  {
    service: 'openai',
    name: 'OpenAI',
    icon: '🤖',
    color: 'green',
    fields: [
      { key: 'OPENAI_API_KEY', label: 'API Key', value: '', type: 'password', required: true },
      { key: 'OPENAI_ORGANIZATION', label: 'Organization ID', value: '', type: 'text', required: false },
      { key: 'OPENAI_MODEL', label: 'Model', value: 'gpt-4-turbo-preview', type: 'text', required: true }
    ],
    links: [
      { label: 'Get API Key', url: 'https://platform.openai.com/api-keys' },
      { label: 'Usage Dashboard', url: 'https://platform.openai.com/usage' },
      { label: 'Documentation', url: 'https://platform.openai.com/docs' }
    ]
  },
  {
    service: 'elevenlabs',
    name: 'ElevenLabs',
    icon: '🎙️',
    color: 'purple',
    fields: [
      { key: 'ELEVENLABS_API_KEY', label: 'API Key', value: '', type: 'password', required: true },
      { key: 'ELEVENLABS_VOICE_ID', label: 'Default Voice ID', value: '', type: 'text', required: true }
    ],
    links: [
      { label: 'Get API Key', url: 'https://elevenlabs.io/app/settings/api-keys' },
      { label: 'Voice Library', url: 'https://elevenlabs.io/voice-library' },
      { label: 'Documentation', url: 'https://docs.elevenlabs.io' }
    ]
  },
  {
    service: 'twilio',
    name: 'Twilio',
    icon: '📞',
    color: 'red',
    fields: [
      { key: 'TWILIO_ACCOUNT_SID', label: 'Account SID', value: '', type: 'text', required: true },
      { key: 'TWILIO_AUTH_TOKEN', label: 'Auth Token', value: '', type: 'password', required: true },
      { key: 'TWILIO_PHONE_NUMBER', label: 'Phone Number', value: '', type: 'text', required: true }
    ],
    links: [
      { label: 'Console', url: 'https://console.twilio.com' },
      { label: 'Phone Numbers', url: 'https://console.twilio.com/us1/develop/phone-numbers' },
      { label: 'Documentation', url: 'https://www.twilio.com/docs' }
    ]
  },
  {
    service: 'weaviate',
    name: 'Weaviate',
    icon: '🔍',
    color: 'blue',
    fields: [
      { key: 'WEAVIATE_URL', label: 'Cluster URL', value: '', type: 'text', required: true },
      { key: 'WEAVIATE_API_KEY', label: 'API Key', value: '', type: 'password', required: false }
    ],
    links: [
      { label: 'Cloud Console', url: 'https://console.weaviate.cloud' },
      { label: 'Documentation', url: 'https://weaviate.io/developers/weaviate' }
    ]
  }
]

function ApiConfiguration() {
  const [configs, setConfigs] = useState(apiConfigs)
  const [showKeys, setShowKeys] = useState<{ [key: string]: boolean }>({})
  const [testing, setTesting] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadConfiguration()
  }, [])

  const loadConfiguration = async () => {
    try {
      const settings = await settingsApi.get()
      // Update configs with loaded values
      // This would map the settings to the config fields
    } catch (error) {
      console.error('Failed to load configuration:', error)
    }
  }

  const handleFieldChange = (serviceIndex: number, fieldIndex: number, value: string) => {
    const newConfigs = [...configs]
    newConfigs[serviceIndex].fields[fieldIndex].value = value
    setConfigs(newConfigs)
  }

  const handleTestConnection = async (service: string) => {
    setTesting(service)
    try {
      const config = configs.find(c => c.service === service)
      if (!config) return

      const credentials = config.fields.reduce((acc, field) => {
        acc[field.key] = field.value
        return acc
      }, {} as Record<string, string>)

      const success = await settingsApi.testConnection(service, credentials)
      
      // Update status
      const newConfigs = [...configs]
      const index = newConfigs.findIndex(c => c.service === service)
      newConfigs[index].status = success ? 'connected' : 'error'
      setConfigs(newConfigs)
    } catch (error) {
      console.error('Test failed:', error)
    } finally {
      setTesting(null)
    }
  }

  const handleSaveAll = async () => {
    setSaving(true)
    try {
      // Save all configurations
      const allSettings = configs.reduce((acc, config) => {
        config.fields.forEach(field => {
          acc[field.key] = field.value
        })
        return acc
      }, {} as Record<string, string>)

      await settingsApi.update(allSettings)
      alert('Configuration saved successfully!')
    } catch (error) {
      alert('Failed to save configuration')
    } finally {
      setSaving(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  const toggleShowKey = (key: string) => {
    setShowKeys(prev => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">API Configuration</h1>
          <p className="text-sm text-gray-500 mt-1">Manage all third-party service integrations</p>
        </div>
        <Button onClick={handleSaveAll} disabled={saving}>
          {saving ? 'Saving...' : 'Save All Changes'}
        </Button>
      </div>

      {/* API Configurations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {configs.map((config, serviceIndex) => (
          <Card key={config.service}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{config.icon}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{config.name}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      {config.status === 'connected' && (
                        <Badge variant="success">
                          <CheckCircleIcon className="h-3 w-3 mr-1" />
                          Connected
                        </Badge>
                      )}
                      {config.status === 'error' && (
                        <Badge variant="error">
                          <XCircleIcon className="h-3 w-3 mr-1" />
                          Error
                        </Badge>
                      )}
                      {config.status === 'not_configured' && (
                        <Badge variant="warning">Not Configured</Badge>
                      )}
                    </div>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleTestConnection(config.service)}
                  disabled={testing === config.service}
                >
                  {testing === config.service ? 'Testing...' : 'Test'}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Fields */}
              {config.fields.map((field, fieldIndex) => (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  <div className="flex space-x-2">
                    <div className="relative flex-1">
                      <input
                        type={field.type === 'password' && !showKeys[field.key] ? 'password' : 'text'}
                        value={field.value}
                        onChange={(e) => handleFieldChange(serviceIndex, fieldIndex, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        placeholder={field.type === 'password' ? '••••••••' : 'Enter value'}
                      />
                      {field.type === 'password' && (
                        <button
                          type="button"
                          onClick={() => toggleShowKey(field.key)}
                          className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
                        >
                          {showKeys[field.key] ? (
                            <EyeSlashIcon className="h-5 w-5" />
                          ) : (
                            <EyeIcon className="h-5 w-5" />
                          )}
                        </button>
                      )}
                    </div>
                    <button
                      onClick={() => copyToClipboard(field.value)}
                      className="p-2 text-gray-400 hover:text-gray-600"
                      title="Copy"
                    >
                      <ClipboardDocumentIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              ))}

              {/* Quick Links */}
              <div className="pt-4 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-500 mb-2">Quick Links</p>
                <div className="flex flex-wrap gap-2">
                  {config.links.map((link) => (
                    <a
                      key={link.label}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1 text-xs px-3 py-1 bg-gray-50 hover:bg-gray-100 rounded-md text-gray-700 hover:text-gray-900 transition-colors"
                    >
                      <span>{link.label}</span>
                      <ArrowTopRightOnSquareIcon className="h-3 w-3" />
                    </a>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Environment Variables Info */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Environment Variables</h3>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-xs text-green-400 font-mono">
{`# Copy these to your .env file
${configs.map(config => 
  config.fields.map(field => 
    `${field.key}="${field.value}"`
  ).join('\n')
).join('\n')}
`}
            </pre>
          </div>
          <div className="mt-4 flex justify-end">
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                const envContent = configs.map(config => 
                  config.fields.map(field => 
                    `${field.key}="${field.value}"`
                  ).join('\n')
                ).join('\n')
                copyToClipboard(envContent)
              }}
            >
              <ClipboardDocumentIcon className="h-4 w-4 mr-2" />
              Copy All
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ApiConfiguration
import { useState, useEffect } from 'react'
import { Card, CardHeader, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'
import { useSettingsStore, type ScheduleSlot } from '../store/settingsStore'
import ScheduleEditor from '../components/ScheduleEditor'
import VoicePreview from '../components/VoicePreview'
import { 
  KeyIcon,
  PhoneIcon,
  SpeakerWaveIcon,
  CogIcon,
  PowerIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

function Settings() {
  const { settings, isLoading, loadSettings, updateSettings, testConnection } = useSettingsStore()
  const [testingService, setTestingService] = useState<string | null>(null)
  const [localSettings, setLocalSettings] = useState(settings)
  
  useEffect(() => {
    loadSettings()
  }, [])
  
  useEffect(() => {
    setLocalSettings(settings)
  }, [settings])

  const handleInputChange = (
    key: string,
    value: string | boolean | Record<string, ScheduleSlot[]>
  ) => {
    setLocalSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSave = async () => {
    await updateSettings(localSettings)
  }

  const handleTestConnection = async (service: string) => {
    setTestingService(service)
    
    let credentials: Record<string, string> = {}
    switch (service) {
      case 'OpenAI':
        credentials = { apiKey: localSettings.openaiApiKey }
        break
      case 'ElevenLabs':
        credentials = { apiKey: localSettings.elevenLabsApiKey }
        break
      case 'Twilio':
        credentials = { 
          accountSid: localSettings.twilioAccountSid,
          authToken: localSettings.twilioAuthToken
        }
        break
    }
    
    const success = await testConnection(service, credentials)
    alert(success ? `${service} connection successful!` : `${service} connection failed!`)
    setTestingService(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      {/* Agent Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <PowerIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Agent Control</h3>
            </div>
            <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              localSettings.agentEnabled 
                ? 'bg-success-100 text-success-700' 
                : 'bg-error-100 text-error-700'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${
                localSettings.agentEnabled ? 'bg-success-500' : 'bg-error-500'
              }`} />
              {localSettings.agentEnabled ? 'ACTIVE' : 'OFFLINE'}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">Voice Agent</label>
              <p className="text-sm text-gray-500">
                {localSettings.agentEnabled 
                  ? 'Agent is active and will handle incoming calls' 
                  : 'Agent is disabled - calls will go to voicemail'
                }
              </p>
            </div>
            <button
              onClick={() => handleInputChange('agentEnabled', !localSettings.agentEnabled)}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                localSettings.agentEnabled ? 'bg-primary-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  localSettings.agentEnabled ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <ClockIcon className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">Timezone:</span>
              <select
                value={localSettings.timezone}
                onChange={(e) => handleInputChange('timezone', e.target.value)}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="Europe/Berlin">Europe/Berlin (CET/CEST)</option>
                <option value="Europe/London">Europe/London (GMT/BST)</option>
                <option value="America/New_York">America/New_York (EST/EDT)</option>
                <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Schedule Editor */}
      <ScheduleEditor 
        schedule={localSettings.schedule} 
        onChange={(schedule) => handleInputChange('schedule', schedule)}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <CogIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">General Settings</h3>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <Input
                value={localSettings.companyName}
                onChange={(e) => handleInputChange('companyName', e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Primary Phone Number
              </label>
              <Input
                value={localSettings.phoneNumber}
                onChange={(e) => handleInputChange('phoneNumber', e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Language
              </label>
              <select
                value={localSettings.language}
                onChange={(e) => handleInputChange('language', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="de-DE">German (Germany)</option>
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="es-ES">Spanish</option>
                <option value="fr-FR">French</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Call Duration (seconds)
              </label>
              <Input
                type="number"
                value={localSettings.maxCallDuration}
                onChange={(e) => handleInputChange('maxCallDuration', e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center">
              <KeyIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">API Keys</h3>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OpenAI API Key
              </label>
              <div className="flex space-x-2">
                <Input
                  type="password"
                  value={localSettings.openaiApiKey}
                  onChange={(e) => handleInputChange('openaiApiKey', e.target.value)}
                  className="flex-1"
                  placeholder="sk-..."
                />
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleTestConnection('OpenAI')}
                  disabled={testingService === 'OpenAI' || !localSettings.openaiApiKey}
                >
                  {testingService === 'OpenAI' ? 'Testing...' : 'Test'}
                </Button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ElevenLabs API Key
              </label>
              <div className="flex space-x-2">
                <Input
                  type="password"
                  value={localSettings.elevenLabsApiKey}
                  onChange={(e) => handleInputChange('elevenLabsApiKey', e.target.value)}
                  className="flex-1"
                  placeholder="el_..."
                />
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleTestConnection('ElevenLabs')}
                  disabled={testingService === 'ElevenLabs' || !localSettings.elevenLabsApiKey}
                >
                  {testingService === 'ElevenLabs' ? 'Testing...' : 'Test'}
                </Button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Twilio Account SID
              </label>
              <Input
                type="password"
                value={localSettings.twilioAccountSid}
                onChange={(e) => handleInputChange('twilioAccountSid', e.target.value)}
                placeholder="AC..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Twilio Auth Token
              </label>
              <div className="flex space-x-2">
                <Input
                  type="password"
                  value={localSettings.twilioAuthToken}
                  onChange={(e) => handleInputChange('twilioAuthToken', e.target.value)}
                  className="flex-1"
                  placeholder="Enter auth token..."
                />
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleTestConnection('Twilio')}
                  disabled={testingService === 'Twilio' || !localSettings.twilioAccountSid || !localSettings.twilioAuthToken}
                >
                  {testingService === 'Twilio' ? 'Testing...' : 'Test'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center">
              <SpeakerWaveIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Voice Settings</h3>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Voice ID
              </label>
              <div className="space-y-3">
                <select
                  value={localSettings.voiceId}
                  onChange={(e) => handleInputChange('voiceId', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <optgroup label="Deutsche Stimmen">
                    <option value="Antoni">Antoni (Deutsch, männlich)</option>
                    <option value="Elli">Elli (Deutsch, weiblich)</option>
                    <option value="Callum">Callum (Deutsch, männlich)</option>
                    <option value="Charlotte">Charlotte (Deutsch, weiblich)</option>
                    <option value="Liam">Liam (Deutsch, männlich)</option>
                  </optgroup>
                  <optgroup label="English Voices">
                    <option value="Rachel">Rachel (English, female)</option>
                    <option value="Drew">Drew (English, male)</option>
                    <option value="Clyde">Clyde (English, male)</option>
                    <option value="Paul">Paul (English, male)</option>
                    <option value="Domi">Domi (English, female)</option>
                    <option value="Dave">Dave (English, male)</option>
                  </optgroup>
                </select>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md border">
                  <div className="flex items-center space-x-3">
                    <SpeakerWaveIcon className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-700">Voice Preview:</span>
                  </div>
                  <VoicePreview voiceId={localSettings.voiceId} size="md" />
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="enableRecording"
                checked={localSettings.enableRecording}
                onChange={(e) => handleInputChange('enableRecording', e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="enableRecording" className="text-sm font-medium text-gray-700">
                Enable Call Recording
              </label>
            </div>

            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="enableNotifications"
                checked={localSettings.enableNotifications}
                onChange={(e) => handleInputChange('enableNotifications', e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="enableNotifications" className="text-sm font-medium text-gray-700">
                Enable Email Notifications
              </label>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center">
              <PhoneIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Connection Status</h3>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { service: 'OpenAI API', status: 'connected', lastCheck: '2 min ago' },
              { service: 'ElevenLabs API', status: 'connected', lastCheck: '5 min ago' },
              { service: 'Twilio', status: 'connected', lastCheck: '1 min ago' },
              { service: 'Database', status: 'connected', lastCheck: '30 sec ago' },
            ].map((connection) => (
              <div key={connection.service} className="flex items-center justify-between py-2">
                <div className="flex items-center">
                  <div className={`h-2 w-2 rounded-full mr-3 ${
                    connection.status === 'connected' ? 'bg-success-500' : 'bg-error-500'
                  }`} />
                  <span className="text-sm font-medium text-gray-900">{connection.service}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">{connection.lastCheck}</span>
                  <Badge variant={connection.status === 'connected' ? 'success' : 'error'}>
                    {connection.status}
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Settings
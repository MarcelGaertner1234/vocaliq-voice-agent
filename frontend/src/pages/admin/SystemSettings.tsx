import { Card, CardHeader, CardContent } from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import { 
  CogIcon,
  ServerIcon,
  ShieldCheckIcon,
  BellIcon
} from '@heroicons/react/24/outline'

const systemInfo = {
  version: '1.0.0',
  environment: 'Development',
  apiVersion: 'v1',
  buildDate: '2025-08-09',
  nodeVersion: 'v18.17.0',
  database: 'PostgreSQL 15',
  cache: 'Redis 7.0'
}

const featureFlags = [
  { name: 'Outbound Calls', key: 'FEATURE_OUTBOUND_CALLS', enabled: true },
  { name: 'Inbound Calls', key: 'FEATURE_INBOUND_CALLS', enabled: true },
  { name: 'Calendar Integration', key: 'FEATURE_CALENDAR_INTEGRATION', enabled: false },
  { name: 'CRM Integration', key: 'FEATURE_CRM_INTEGRATION', enabled: false },
  { name: 'Multi-Tenant', key: 'FEATURE_MULTI_TENANT', enabled: true },
  { name: 'Analytics', key: 'FEATURE_ANALYTICS', enabled: true },
  { name: 'Webhooks', key: 'FEATURE_WEBHOOKS', enabled: true },
]

const securitySettings = [
  { setting: 'JWT Token Expiry', value: '30 minutes' },
  { setting: 'Password Hash Rounds', value: '12' },
  { setting: 'Max Login Attempts', value: '5' },
  { setting: 'Lockout Duration', value: '15 minutes' },
  { setting: 'Rate Limiting', value: 'Enabled (100/min)' },
  { setting: 'CORS', value: 'Enabled' },
]

function SystemSettings() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Information */}
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <ServerIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">System Information</h3>
            </div>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3">
              {Object.entries(systemInfo).map(([key, value]) => (
                <div key={key} className="flex justify-between py-2 border-b border-gray-100 last:border-0">
                  <dt className="text-sm font-medium text-gray-500 capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </dt>
                  <dd className="text-sm text-gray-900 font-medium">{value}</dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>

        {/* Feature Flags */}
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <CogIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Feature Flags</h3>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {featureFlags.map((feature) => (
                <div key={feature.key} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{feature.name}</p>
                    <p className="text-xs text-gray-500">{feature.key}</p>
                  </div>
                  <Badge variant={feature.enabled ? 'success' : 'default'}>
                    {feature.enabled ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Security Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <ShieldCheckIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Security Settings</h3>
            </div>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3">
              {securitySettings.map((item) => (
                <div key={item.setting} className="flex justify-between py-2 border-b border-gray-100 last:border-0">
                  <dt className="text-sm font-medium text-gray-500">{item.setting}</dt>
                  <dd className="text-sm text-gray-900 font-medium">{item.value}</dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>

        {/* Maintenance */}
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <BellIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Maintenance</h3>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Maintenance Mode</span>
                <Badge variant="default">Disabled</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Last Backup</span>
                <span className="text-sm text-gray-900 font-medium">Today, 03:00 AM</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Next Scheduled</span>
                <span className="text-sm text-gray-900 font-medium">Tomorrow, 03:00 AM</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Auto-Update</span>
                <Badge variant="success">Enabled</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SystemSettings
import { useState } from 'react'
import { Card, CardHeader, CardContent } from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import { 
  GlobeAltIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  PlayIcon,
  XMarkIcon,
  CheckIcon
} from '@heroicons/react/24/outline'

type Webhook = {
  id: number
  name: string
  url: string
  events: string[]
  status: 'active' | 'inactive'
  lastTriggered?: string
  successRate: number
  headers?: Record<string, string>
}

const availableEvents = [
  'call.started',
  'call.ended',
  'call.failed',
  'agent.error',
  'transcript.ready',
  'recording.ready',
  'user.created',
  'user.updated',
  'company.updated'
]

const initialWebhooks: Webhook[] = [
  {
    id: 1,
    name: 'CRM Integration',
    url: 'https://crm.example.com/webhook',
    events: ['call.ended', 'transcript.ready'],
    status: 'active',
    lastTriggered: '2 hours ago',
    successRate: 98
  },
  {
    id: 2,
    name: 'Analytics Service',
    url: 'https://analytics.example.com/api/webhook',
    events: ['call.started', 'call.ended', 'call.failed'],
    status: 'active',
    lastTriggered: '15 min ago',
    successRate: 100
  },
  {
    id: 3,
    name: 'Backup System',
    url: 'https://backup.internal/webhook',
    events: ['recording.ready'],
    status: 'inactive',
    successRate: 95
  }
]

function Webhooks() {
  const [webhooks, setWebhooks] = useState(initialWebhooks)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [selectedEvents, setSelectedEvents] = useState<string[]>([])
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    events: [] as string[],
    status: 'active' as Webhook['status']
  })

  const handleAdd = () => {
    setFormData({
      name: '',
      url: '',
      events: [],
      status: 'active'
    })
    setSelectedEvents([])
    setShowAddModal(true)
  }

  const handleEdit = (webhook: Webhook) => {
    setFormData({
      name: webhook.name,
      url: webhook.url,
      events: webhook.events,
      status: webhook.status
    })
    setSelectedEvents(webhook.events)
    setEditingId(webhook.id)
  }

  const handleSave = () => {
    const webhookData = {
      ...formData,
      events: selectedEvents
    }

    if (editingId) {
      setWebhooks(prev => prev.map(w => 
        w.id === editingId 
          ? { ...w, ...webhookData }
          : w
      ))
      setEditingId(null)
    } else {
      const newWebhook: Webhook = {
        id: Math.max(...webhooks.map(w => w.id)) + 1,
        ...webhookData,
        successRate: 0,
        lastTriggered: undefined
      }
      setWebhooks(prev => [...prev, newWebhook])
      setShowAddModal(false)
    }
  }

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this webhook?')) {
      setWebhooks(prev => prev.filter(w => w.id !== id))
    }
  }

  const handleTest = (webhook: Webhook) => {
    alert(`Testing webhook: ${webhook.name}\nSending test payload to: ${webhook.url}`)
  }

  const toggleEvent = (event: string) => {
    setSelectedEvents(prev => 
      prev.includes(event)
        ? prev.filter(e => e !== event)
        : [...prev, event]
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Webhooks</h1>
        <Button onClick={handleAdd} className="flex items-center">
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Webhook
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {webhooks.filter(w => w.status === 'active').length}
                </p>
                <p className="text-sm text-gray-500">Active Webhooks</p>
              </div>
              <GlobeAltIcon className="h-8 w-8 text-blue-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-green-600">
                  {Math.round(webhooks.reduce((acc, w) => acc + w.successRate, 0) / webhooks.length)}%
                </p>
                <p className="text-sm text-gray-500">Avg Success Rate</p>
              </div>
              <CheckIcon className="h-8 w-8 text-green-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-purple-600">
                  {webhooks.reduce((acc, w) => acc + w.events.length, 0)}
                </p>
                <p className="text-sm text-gray-500">Total Events</p>
              </div>
              <PlayIcon className="h-8 w-8 text-purple-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Webhooks Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    URL
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Events
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Success Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Triggered
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {webhooks.map((webhook) => (
                  <tr key={webhook.id} className="hover:bg-gray-50">
                    {editingId === webhook.id ? (
                      <>
                        <td className="px-6 py-4">
                          <Input
                            value={formData.name}
                            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                            className="text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <Input
                            value={formData.url}
                            onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                            className="text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-1">
                            {availableEvents.slice(0, 3).map(event => (
                              <Badge
                                key={event}
                                variant={selectedEvents.includes(event) ? 'primary' : 'default'}
                                className="cursor-pointer text-xs"
                                onClick={() => toggleEvent(event)}
                              >
                                {event.split('.')[1]}
                              </Badge>
                            ))}
                            <span className="text-xs text-gray-500">...</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <select
                            value={formData.status}
                            onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as Webhook['status'] }))}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                          </select>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {webhook.successRate}%
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {webhook.lastTriggered || '-'}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex space-x-2">
                            <button
                              onClick={handleSave}
                              className="text-green-600 hover:text-green-900"
                            >
                              <CheckIcon className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => setEditingId(null)}
                              className="text-gray-400 hover:text-gray-600"
                            >
                              <XMarkIcon className="h-5 w-5" />
                            </button>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <GlobeAltIcon className="h-5 w-5 text-gray-400 mr-2" />
                            <span className="text-sm font-medium text-gray-900">{webhook.name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-gray-600 font-mono text-xs">
                            {webhook.url.length > 40 ? webhook.url.substring(0, 40) + '...' : webhook.url}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-1">
                            {webhook.events.map(event => (
                              <Badge key={event} variant="default" className="text-xs">
                                {event.split('.')[1]}
                              </Badge>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={webhook.status === 'active' ? 'success' : 'default'}>
                            {webhook.status}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className={`text-sm font-medium ${
                              webhook.successRate >= 95 ? 'text-green-600' :
                              webhook.successRate >= 80 ? 'text-yellow-600' :
                              'text-red-600'
                            }`}>
                              {webhook.successRate}%
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {webhook.lastTriggered || 'Never'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleTest(webhook)}
                              className="text-blue-600 hover:text-blue-900"
                              title="Test webhook"
                            >
                              <PlayIcon className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => handleEdit(webhook)}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              <PencilIcon className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => handleDelete(webhook.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              <TrashIcon className="h-5 w-5" />
                            </button>
                          </div>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Add Webhook Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4">Add New Webhook</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., CRM Integration"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <Input
                  value={formData.url}
                  onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                  placeholder="https://your-service.com/webhook"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Events</label>
                <div className="space-y-2 max-h-48 overflow-y-auto border rounded-md p-3">
                  {availableEvents.map(event => (
                    <label key={event} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedEvents.includes(event)}
                        onChange={() => toggleEvent(event)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-700">{event}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as Webhook['status'] }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <Button variant="secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSave} disabled={!formData.name || !formData.url || selectedEvents.length === 0}>
                  Add Webhook
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Webhooks
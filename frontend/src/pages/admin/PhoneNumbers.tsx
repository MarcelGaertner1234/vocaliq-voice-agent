import { useState } from 'react'
import { Card, CardHeader, CardContent } from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import { 
  PhoneIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
  CheckIcon
} from '@heroicons/react/24/outline'

type PhoneNumber = {
  id: number
  number: string
  type: 'twilio' | 'byod' | 'virtual'
  status: 'active' | 'inactive' | 'testing'
  company: string
  purpose: string
  assignedTo?: string
}

// Mock data
const initialPhoneNumbers: PhoneNumber[] = [
  { id: 1, number: '+49 30 12345678', type: 'twilio', status: 'active', company: 'TechCorp GmbH', purpose: 'Main Support' },
  { id: 2, number: '+49 30 87654321', type: 'twilio', status: 'active', company: 'TechCorp GmbH', purpose: 'Sales' },
  { id: 3, number: '+49 170 9876543', type: 'byod', status: 'active', company: 'Sales Masters AG', purpose: 'Customer Service', assignedTo: 'Tom Weber' },
  { id: 4, number: '+49 30 11223344', type: 'virtual', status: 'testing', company: 'Support Plus', purpose: 'Testing' },
  { id: 5, number: '+49 30 55667788', type: 'twilio', status: 'inactive', company: 'Demo Company', purpose: 'General' },
]

const typeColors = {
  twilio: 'primary',
  byod: 'warning',
  virtual: 'default'
} as const

const statusColors = {
  active: 'success',
  inactive: 'default',
  testing: 'warning'
} as const

function PhoneNumbers() {
  const [phoneNumbers, setPhoneNumbers] = useState(initialPhoneNumbers)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    number: '',
    type: 'twilio' as PhoneNumber['type'],
    status: 'active' as PhoneNumber['status'],
    company: '',
    purpose: '',
    assignedTo: ''
  })

  const handleAdd = () => {
    setFormData({
      number: '',
      type: 'twilio',
      status: 'active',
      company: '',
      purpose: '',
      assignedTo: ''
    })
    setShowAddModal(true)
  }

  const handleEdit = (phone: PhoneNumber) => {
    setFormData({
      number: phone.number,
      type: phone.type,
      status: phone.status,
      company: phone.company,
      purpose: phone.purpose,
      assignedTo: phone.assignedTo || ''
    })
    setEditingId(phone.id)
  }

  const handleSave = () => {
    if (editingId) {
      setPhoneNumbers(prev => prev.map(p => 
        p.id === editingId 
          ? { ...p, ...formData }
          : p
      ))
      setEditingId(null)
    } else {
      const newPhone: PhoneNumber = {
        id: Math.max(...phoneNumbers.map(p => p.id)) + 1,
        ...formData,
        assignedTo: formData.assignedTo || undefined
      }
      setPhoneNumbers(prev => [...prev, newPhone])
      setShowAddModal(false)
    }
  }

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this phone number?')) {
      setPhoneNumbers(prev => prev.filter(p => p.id !== id))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Phone Numbers</h1>
        <Button onClick={handleAdd} className="flex items-center">
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Number
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {phoneNumbers.filter(p => p.type === 'twilio').length}
                </p>
                <p className="text-sm text-gray-500">Twilio Numbers</p>
              </div>
              <PhoneIcon className="h-8 w-8 text-blue-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-yellow-600">
                  {phoneNumbers.filter(p => p.type === 'byod').length}
                </p>
                <p className="text-sm text-gray-500">Own Numbers (BYOD)</p>
              </div>
              <PhoneIcon className="h-8 w-8 text-yellow-200" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-green-600">
                  {phoneNumbers.filter(p => p.status === 'active').length}
                </p>
                <p className="text-sm text-gray-500">Active Numbers</p>
              </div>
              <PhoneIcon className="h-8 w-8 text-green-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Phone Numbers Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Purpose
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assigned To
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {phoneNumbers.map((phone) => (
                  <tr key={phone.id} className="hover:bg-gray-50">
                    {editingId === phone.id ? (
                      <>
                        <td className="px-6 py-4">
                          <Input
                            value={formData.number}
                            onChange={(e) => setFormData(prev => ({ ...prev, number: e.target.value }))}
                            className="text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <select
                            value={formData.type}
                            onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as PhoneNumber['type'] }))}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="twilio">Twilio</option>
                            <option value="byod">BYOD</option>
                            <option value="virtual">Virtual</option>
                          </select>
                        </td>
                        <td className="px-6 py-4">
                          <select
                            value={formData.status}
                            onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as PhoneNumber['status'] }))}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                            <option value="testing">Testing</option>
                          </select>
                        </td>
                        <td className="px-6 py-4">
                          <Input
                            value={formData.company}
                            onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value }))}
                            className="text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <Input
                            value={formData.purpose}
                            onChange={(e) => setFormData(prev => ({ ...prev, purpose: e.target.value }))}
                            className="text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <Input
                            value={formData.assignedTo}
                            onChange={(e) => setFormData(prev => ({ ...prev, assignedTo: e.target.value }))}
                            className="text-sm"
                            placeholder="Optional"
                          />
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
                            <PhoneIcon className="h-5 w-5 text-gray-400 mr-2" />
                            <span className="text-sm font-medium text-gray-900">{phone.number}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={typeColors[phone.type]}>
                            {phone.type.toUpperCase()}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={statusColors[phone.status]}>
                            {phone.status}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {phone.company}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {phone.purpose}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {phone.assignedTo || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleEdit(phone)}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              <PencilIcon className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => handleDelete(phone.id)}
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

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-lg font-semibold mb-4">Add New Phone Number</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <Input
                  value={formData.number}
                  onChange={(e) => setFormData(prev => ({ ...prev, number: e.target.value }))}
                  placeholder="+49 30 12345678"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as PhoneNumber['type'] }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="twilio">Twilio</option>
                  <option value="byod">BYOD (Own Number)</option>
                  <option value="virtual">Virtual</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
                <Input
                  value={formData.company}
                  onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value }))}
                  placeholder="Company name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Purpose</label>
                <Input
                  value={formData.purpose}
                  onChange={(e) => setFormData(prev => ({ ...prev, purpose: e.target.value }))}
                  placeholder="e.g., Main Support, Sales"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Assigned To (Optional)</label>
                <Input
                  value={formData.assignedTo}
                  onChange={(e) => setFormData(prev => ({ ...prev, assignedTo: e.target.value }))}
                  placeholder="User name"
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <Button variant="secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSave}>
                  Add Number
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PhoneNumbers
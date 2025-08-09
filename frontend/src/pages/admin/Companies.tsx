import { useState } from 'react'
import { Card, CardHeader, CardContent } from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import { 
  BuildingOfficeIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
  CheckIcon
} from '@heroicons/react/24/outline'

type Company = {
  id: number
  name: string
  status: 'active' | 'inactive'
  plan: string
  users: number
  calls: number
}

// Mock data for demo
const initialCompanies: Company[] = [
  { id: 1, name: 'TechCorp GmbH', status: 'active', plan: 'Enterprise', users: 45, calls: 1234 },
  { id: 2, name: 'Sales Masters AG', status: 'active', plan: 'Professional', users: 12, calls: 567 },
  { id: 3, name: 'Support Plus', status: 'active', plan: 'Starter', users: 5, calls: 89 },
  { id: 4, name: 'Demo Company', status: 'inactive', plan: 'Free', users: 2, calls: 0 },
  { id: 5, name: 'Global Services', status: 'active', plan: 'Enterprise', users: 78, calls: 4567 },
]

function Companies() {
  const [companies, setCompanies] = useState(initialCompanies)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    status: 'active' as Company['status'],
    plan: 'Starter',
    users: 0,
    calls: 0
  })

  const handleAdd = () => {
    setFormData({
      name: '',
      status: 'active',
      plan: 'Starter',
      users: 0,
      calls: 0
    })
    setShowAddModal(true)
  }

  const handleEdit = (company: Company) => {
    setFormData({
      name: company.name,
      status: company.status,
      plan: company.plan,
      users: company.users,
      calls: company.calls
    })
    setEditingId(company.id)
  }

  const handleSave = () => {
    if (editingId) {
      setCompanies(prev => prev.map(c => 
        c.id === editingId 
          ? { ...c, ...formData }
          : c
      ))
      setEditingId(null)
    } else {
      const newCompany: Company = {
        id: Math.max(...companies.map(c => c.id)) + 1,
        ...formData
      }
      setCompanies(prev => [...prev, newCompany])
      setShowAddModal(false)
    }
  }

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this company? This will also delete all associated users and data.')) {
      setCompanies(prev => prev.filter(c => c.id !== id))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Companies</h1>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            {companies.filter(c => c.status === 'active').length} Active / {companies.length} Total
          </div>
          <Button onClick={handleAdd} className="flex items-center">
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Company
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Plan
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Users
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Calls
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {companies.map((company) => (
                  <tr key={company.id} className="hover:bg-gray-50">
                    {editingId === company.id ? (
                      <>
                        <td className="px-6 py-4">
                          <Input
                            value={formData.name}
                            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                            className="text-sm"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <select
                            value={formData.status}
                            onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as Company['status'] }))}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                          </select>
                        </td>
                        <td className="px-6 py-4">
                          <select
                            value={formData.plan}
                            onChange={(e) => setFormData(prev => ({ ...prev, plan: e.target.value }))}
                            className="text-sm border border-gray-300 rounded px-2 py-1"
                          >
                            <option value="Free">Free</option>
                            <option value="Starter">Starter</option>
                            <option value="Professional">Professional</option>
                            <option value="Enterprise">Enterprise</option>
                          </select>
                        </td>
                        <td className="px-6 py-4">
                          <Input
                            type="number"
                            value={formData.users}
                            onChange={(e) => setFormData(prev => ({ ...prev, users: parseInt(e.target.value) }))}
                            className="text-sm w-20"
                          />
                        </td>
                        <td className="px-6 py-4">
                          <Input
                            type="number"
                            value={formData.calls}
                            onChange={(e) => setFormData(prev => ({ ...prev, calls: parseInt(e.target.value) }))}
                            className="text-sm w-24"
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
                            <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mr-3" />
                            <div className="text-sm font-medium text-gray-900">{company.name}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={company.status === 'active' ? 'success' : 'default'}>
                            {company.status}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {company.plan}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {company.users}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {company.calls.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleEdit(company)}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              <PencilIcon className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => handleDelete(company.id)}
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

      {/* Add Company Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-lg font-semibold mb-4">Add New Company</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter company name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Plan</label>
                <select
                  value={formData.plan}
                  onChange={(e) => setFormData(prev => ({ ...prev, plan: e.target.value }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="Free">Free</option>
                  <option value="Starter">Starter</option>
                  <option value="Professional">Professional</option>
                  <option value="Enterprise">Enterprise</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as Company['status'] }))}
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
                <Button onClick={handleSave}>
                  Add Company
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Companies
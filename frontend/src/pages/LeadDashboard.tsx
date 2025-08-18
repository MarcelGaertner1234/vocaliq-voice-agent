import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  UserGroupIcon, 
  FireIcon, 
  ChartBarIcon,
  CalendarIcon,
  PlusIcon,
  PhoneIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'
import LeadScoreWidget from '../components/leads/LeadScoreWidget'
import FollowUpCalendar from '../components/leads/FollowUpCalendar'
import LeadPipeline from '../components/leads/LeadPipeline'
import QuickLeadActions from '../components/leads/QuickLeadActions'
import FeatureGate from '../components/FeatureGate'
import apiClient from '../services/api'
import { useAuthStore } from '../stores/authStore'

interface LeadMetrics {
  totalLeads: number
  hotLeads: number
  warmLeads: number
  coldLeads: number
  followUpsDue: number
  conversionRate: number
  averageScore: number
  reactivationCandidates: number
}

interface Lead {
  id: number
  uuid: string
  firstName: string
  lastName: string
  phone: string
  email?: string
  companyName?: string
  leadScore: number
  scoreCategory: 'hot' | 'warm' | 'cold'
  status: string
  lastContactDate?: string
  nextFollowUp?: string
  source: string
}

export default function LeadDashboard() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [metrics, setMetrics] = useState<LeadMetrics | null>(null)
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<'all' | 'hot' | 'warm' | 'cold'>('all')

  useEffect(() => {
    fetchLeadData()
  }, [])

  const fetchLeadData = async () => {
    try {
      setLoading(true)
      
      // Fetch metrics
      const metricsResponse = await apiClient.get('/api/leads/metrics')
      setMetrics(metricsResponse.data)
      
      // Fetch leads
      const leadsResponse = await apiClient.get('/api/leads')
      setLeads(leadsResponse.data)
      
    } catch (error) {
      console.error('Error fetching lead data:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredLeads = leads.filter(lead => {
    if (selectedTab === 'all') return true
    return lead.scoreCategory === selectedTab
  })

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-red-600'
    if (score >= 5) return 'text-yellow-600'
    return 'text-blue-600'
  }

  const getScoreBadge = (category: string) => {
    switch(category) {
      case 'hot':
        return 'bg-red-100 text-red-800'
      case 'warm':
        return 'bg-yellow-100 text-yellow-800'
      case 'cold':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Lead Management</h1>
          <p className="text-gray-600 mt-1">Verwalten Sie Ihre Leads und Follow-Ups</p>
        </div>
        
        <FeatureGate feature="lead_scoring">
          <button
            onClick={() => navigate('/app/leads/new')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5" />
            Neuer Lead
          </button>
        </FeatureGate>
      </div>

      {/* Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Gesamt Leads</p>
              <p className="text-2xl font-bold">{metrics?.totalLeads || 0}</p>
            </div>
            <UserGroupIcon className="h-8 w-8 text-gray-400" />
          </div>
        </div>

        <FeatureGate feature="lead_scoring">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Hot Leads</p>
                <p className="text-2xl font-bold text-red-600">{metrics?.hotLeads || 0}</p>
              </div>
              <FireIcon className="h-8 w-8 text-red-400" />
            </div>
          </div>
        </FeatureGate>

        <FeatureGate feature="manual_follow_up">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Follow-Ups heute</p>
                <p className="text-2xl font-bold text-blue-600">{metrics?.followUpsDue || 0}</p>
              </div>
              <CalendarIcon className="h-8 w-8 text-blue-400" />
            </div>
          </div>
        </FeatureGate>

        <FeatureGate feature="roi_analytics">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Conversion Rate</p>
                <p className="text-2xl font-bold">{metrics?.conversionRate || 0}%</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-green-400" />
            </div>
          </div>
        </FeatureGate>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Lead List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Lead Score Distribution */}
          <FeatureGate feature="lead_scoring">
            <LeadScoreWidget leads={leads} />
          </FeatureGate>

          {/* Lead Table */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Leads</h2>
                
                <FeatureGate feature="lead_scoring">
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedTab('all')}
                      className={`px-3 py-1 rounded-lg text-sm ${
                        selectedTab === 'all' 
                          ? 'bg-gray-200 text-gray-900' 
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      Alle ({leads.length})
                    </button>
                    <button
                      onClick={() => setSelectedTab('hot')}
                      className={`px-3 py-1 rounded-lg text-sm ${
                        selectedTab === 'hot' 
                          ? 'bg-red-100 text-red-900' 
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      Hot ({metrics?.hotLeads || 0})
                    </button>
                    <button
                      onClick={() => setSelectedTab('warm')}
                      className={`px-3 py-1 rounded-lg text-sm ${
                        selectedTab === 'warm' 
                          ? 'bg-yellow-100 text-yellow-900' 
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      Warm ({metrics?.warmLeads || 0})
                    </button>
                    <button
                      onClick={() => setSelectedTab('cold')}
                      className={`px-3 py-1 rounded-lg text-sm ${
                        selectedTab === 'cold' 
                          ? 'bg-blue-100 text-blue-900' 
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      Cold ({metrics?.coldLeads || 0})
                    </button>
                  </div>
                </FeatureGate>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Firma</th>
                    <FeatureGate feature="lead_scoring">
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                    </FeatureGate>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Letzter Kontakt</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aktionen</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredLeads.map(lead => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-medium text-gray-900">
                            {lead.firstName} {lead.lastName}
                          </p>
                          <p className="text-sm text-gray-500">{lead.phone}</p>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {lead.companyName || '-'}
                      </td>
                      <FeatureGate feature="lead_scoring">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <span className={`text-lg font-bold ${getScoreColor(lead.leadScore)}`}>
                              {lead.leadScore}
                            </span>
                            <span className={`px-2 py-1 text-xs rounded-full ${getScoreBadge(lead.scoreCategory)}`}>
                              {lead.scoreCategory}
                            </span>
                          </div>
                        </td>
                      </FeatureGate>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                          {lead.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {lead.lastContactDate 
                          ? new Date(lead.lastContactDate).toLocaleDateString('de-DE')
                          : 'Nie'
                        }
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <button
                            onClick={() => navigate(`/app/leads/${lead.uuid}`)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            Details
                          </button>
                          <FeatureGate feature="manual_follow_up">
                            <button
                              onClick={() => {/* Handle call */}}
                              className="text-green-600 hover:text-green-800"
                            >
                              <PhoneIcon className="h-4 w-4" />
                            </button>
                          </FeatureGate>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {filteredLeads.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Keine Leads gefunden
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Widgets */}
        <div className="space-y-4">
          {/* Quick Actions */}
          <QuickLeadActions onRefresh={fetchLeadData} />
          
          {/* Follow-Up Calendar */}
          <FeatureGate feature="manual_follow_up">
            <FollowUpCalendar />
          </FeatureGate>
          
          {/* Lead Pipeline */}
          <FeatureGate feature="lead_scoring">
            <LeadPipeline leads={leads} />
          </FeatureGate>
        </div>
      </div>
    </div>
  )
}
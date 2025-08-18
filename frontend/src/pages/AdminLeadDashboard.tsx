import React, { useState, useEffect } from 'react'
import { 
  UserGroupIcon, 
  ChartBarIcon,
  PhoneIcon,
  CurrencyEuroIcon,
  ClockIcon,
  FireIcon,
  ArrowTrendingUpIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'
import apiClient from '../services/api'

interface CompanyMetrics {
  companyId: string
  companyName: string
  subscription: string
  totalLeads: number
  hotLeads: number
  conversionRate: number
  revenueGenerated: number
  lastActivity: string
  followUpsDue: number
  reactivationCandidates: number
}

interface SystemMetrics {
  totalCompanies: number
  totalLeads: number
  totalRevenue: number
  averageConversion: number
  activeFollowUps: number
  scheduledReactivations: number
  topPerformers: CompanyMetrics[]
}

export default function AdminLeadDashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [companies, setCompanies] = useState<CompanyMetrics[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d'>('30d')
  
  useEffect(() => {
    fetchMetrics()
  }, [selectedPeriod])
  
  const fetchMetrics = async () => {
    try {
      setLoading(true)
      
      // Fetch system-wide metrics
      const metricsResponse = await apiClient.get(`/api/admin/leads/metrics?period=${selectedPeriod}`)
      setMetrics(metricsResponse.data)
      
      // Fetch company-specific metrics
      const companiesResponse = await apiClient.get('/api/admin/leads/companies')
      setCompanies(companiesResponse.data)
      
    } catch (error) {
      console.error('Error fetching admin metrics:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount)
  }
  
  const getPlanColor = (plan: string) => {
    switch(plan.toLowerCase()) {
      case 'enterprise': return 'text-purple-600 bg-purple-100'
      case 'professional': return 'text-blue-600 bg-blue-100'
      case 'basic': return 'text-gray-600 bg-gray-100'
      default: return 'text-gray-500 bg-gray-50'
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
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Lead Management System</h1>
        <p className="text-gray-600 mt-1">System-weite Übersicht und Verwaltung</p>
      </div>
      
      {/* Period Selector */}
      <div className="flex gap-2">
        {(['7d', '30d', '90d'] as const).map(period => (
          <button
            key={period}
            onClick={() => setSelectedPeriod(period)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedPeriod === period
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {period === '7d' ? '7 Tage' : period === '30d' ? '30 Tage' : '90 Tage'}
          </button>
        ))}
      </div>
      
      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Firmen</p>
              <p className="text-2xl font-bold">{metrics?.totalCompanies || 0}</p>
            </div>
            <BuildingOfficeIcon className="h-8 w-8 text-gray-400" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Gesamt Leads</p>
              <p className="text-2xl font-bold">{metrics?.totalLeads || 0}</p>
            </div>
            <UserGroupIcon className="h-8 w-8 text-blue-400" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Umsatz</p>
              <p className="text-xl font-bold">{formatCurrency(metrics?.totalRevenue || 0)}</p>
            </div>
            <CurrencyEuroIcon className="h-8 w-8 text-green-400" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Ø Conversion</p>
              <p className="text-2xl font-bold">{metrics?.averageConversion || 0}%</p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-purple-400" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Follow-Ups</p>
              <p className="text-2xl font-bold text-orange-600">{metrics?.activeFollowUps || 0}</p>
            </div>
            <ClockIcon className="h-8 w-8 text-orange-400" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Reaktivierungen</p>
              <p className="text-2xl font-bold text-red-600">{metrics?.scheduledReactivations || 0}</p>
            </div>
            <FireIcon className="h-8 w-8 text-red-400" />
          </div>
        </div>
      </div>
      
      {/* Company Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold">Firmen-Übersicht</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Firma</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Leads</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hot Leads</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conversion</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Umsatz</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Follow-Ups</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reaktivierung</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Letzte Aktivität</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aktionen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {companies.map(company => (
                <tr key={company.companyId} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-gray-900">{company.companyName}</p>
                      <p className="text-xs text-gray-500">ID: {company.companyId}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${getPlanColor(company.subscription)}`}>
                      {company.subscription}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {company.totalLeads}
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm font-medium text-red-600">
                      {company.hotLeads}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <span className="text-sm font-medium">
                        {company.conversionRate}%
                      </span>
                      <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${Math.min(company.conversionRate, 100)}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-green-600">
                    {formatCurrency(company.revenueGenerated)}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-sm font-medium ${
                      company.followUpsDue > 0 ? 'text-orange-600' : 'text-gray-500'
                    }`}>
                      {company.followUpsDue}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-sm font-medium ${
                      company.reactivationCandidates > 0 ? 'text-purple-600' : 'text-gray-500'
                    }`}>
                      {company.reactivationCandidates}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(company.lastActivity).toLocaleDateString('de-DE')}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => window.location.href = `/admin/company/${company.companyId}`}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Details
                      </button>
                      <button
                        onClick={() => console.log('Trigger reactivation', company.companyId)}
                        className="text-purple-600 hover:text-purple-800 text-sm"
                      >
                        Reaktivieren
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {companies.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Keine Firmen gefunden
            </div>
          )}
        </div>
      </div>
      
      {/* Insights Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Performers */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Top Performer</h3>
          <div className="space-y-3">
            {metrics?.topPerformers?.slice(0, 5).map((company, index) => (
              <div key={company.companyId} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                  <div>
                    <p className="font-medium">{company.companyName}</p>
                    <p className="text-xs text-gray-500">{formatCurrency(company.revenueGenerated)}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-green-600">{company.conversionRate}%</p>
                  <p className="text-xs text-gray-500">{company.totalLeads} Leads</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* System Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Follow-Up Erfolgsrate</span>
                <span className="text-sm font-medium">73%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '73%' }} />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Reaktivierungs-Erfolg</span>
                <span className="text-sm font-medium">42%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '42%' }} />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-600">Lead Scoring Genauigkeit</span>
                <span className="text-sm font-medium">89%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '89%' }} />
              </div>
            </div>
            
            <div className="mt-4 p-3 bg-green-50 rounded-lg">
              <p className="text-sm text-green-800">
                <strong>30% mehr Umsatz</strong> durch automatisches Follow-Up System
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
import React from 'react'
import { ArrowRightIcon } from '@heroicons/react/24/outline'

interface Lead {
  id: number
  status: string
  leadScore: number
  firstName: string
  lastName: string
}

interface LeadPipelineProps {
  leads: Lead[]
}

export default function LeadPipeline({ leads }: LeadPipelineProps) {
  // Pipeline stages
  const stages = [
    { key: 'new', label: 'Neu', color: 'bg-gray-500' },
    { key: 'contacted', label: 'Kontaktiert', color: 'bg-blue-500' },
    { key: 'qualified', label: 'Qualifiziert', color: 'bg-yellow-500' },
    { key: 'proposal', label: 'Angebot', color: 'bg-orange-500' },
    { key: 'negotiation', label: 'Verhandlung', color: 'bg-purple-500' },
    { key: 'converted', label: 'Abgeschlossen', color: 'bg-green-500' }
  ]
  
  // Group leads by status
  const leadsByStatus = stages.map(stage => ({
    ...stage,
    leads: leads.filter(lead => lead.status.toLowerCase() === stage.key),
    count: leads.filter(lead => lead.status.toLowerCase() === stage.key).length
  }))
  
  const maxCount = Math.max(...leadsByStatus.map(s => s.count), 1)
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Lead Pipeline</h3>
      
      <div className="space-y-3">
        {leadsByStatus.map((stage, index) => (
          <div key={stage.key} className="relative">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">{stage.label}</span>
              <span className="text-sm text-gray-500">{stage.count}</span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-6 relative overflow-hidden">
              <div 
                className={`h-6 rounded-full ${stage.color} transition-all duration-500`}
                style={{ width: `${(stage.count / maxCount) * 100}%` }}
              >
                {stage.count > 0 && (
                  <div className="h-full flex items-center px-2">
                    <span className="text-xs text-white font-medium">
                      {stage.count}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {index < stages.length - 1 && (
              <ArrowRightIcon className="absolute -right-2 top-7 h-4 w-4 text-gray-400" />
            )}
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-500">Conversion Rate</p>
            <p className="text-lg font-bold text-green-600">
              {leads.length > 0 
                ? Math.round((leadsByStatus[5].count / leads.length) * 100) 
                : 0}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">In Pipeline</p>
            <p className="text-lg font-bold text-blue-600">
              {leads.filter(l => l.status !== 'converted' && l.status !== 'lost').length}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
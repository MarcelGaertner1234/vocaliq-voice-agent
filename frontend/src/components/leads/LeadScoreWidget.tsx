import React from 'react'
import { ChartBarIcon } from '@heroicons/react/24/outline'

interface Lead {
  leadScore: number
  scoreCategory: 'hot' | 'warm' | 'cold'
}

interface LeadScoreWidgetProps {
  leads: Lead[]
}

export default function LeadScoreWidget({ leads }: LeadScoreWidgetProps) {
  // Calculate score distribution
  const scoreDistribution = {
    '1-3': 0,
    '4-6': 0,
    '7-8': 0,
    '9-10': 0
  }
  
  leads.forEach(lead => {
    if (lead.leadScore <= 3) scoreDistribution['1-3']++
    else if (lead.leadScore <= 6) scoreDistribution['4-6']++
    else if (lead.leadScore <= 8) scoreDistribution['7-8']++
    else scoreDistribution['9-10']++
  })
  
  const maxCount = Math.max(...Object.values(scoreDistribution))
  
  const getBarColor = (range: string) => {
    switch(range) {
      case '1-3': return 'bg-blue-500'
      case '4-6': return 'bg-yellow-500'
      case '7-8': return 'bg-orange-500'
      case '9-10': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Lead Score Verteilung</h3>
        <ChartBarIcon className="h-5 w-5 text-gray-400" />
      </div>
      
      <div className="space-y-3">
        {Object.entries(scoreDistribution).map(([range, count]) => (
          <div key={range}>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm text-gray-600">Score {range}</span>
              <span className="text-sm font-medium">{count} Leads</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${getBarColor(range)}`}
                style={{ width: maxCount > 0 ? `${(count / maxCount) * 100}%` : '0%' }}
              />
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-xs text-gray-500">Cold</p>
            <p className="text-lg font-bold text-blue-600">
              {leads.filter(l => l.scoreCategory === 'cold').length}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Warm</p>
            <p className="text-lg font-bold text-yellow-600">
              {leads.filter(l => l.scoreCategory === 'warm').length}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Hot</p>
            <p className="text-lg font-bold text-red-600">
              {leads.filter(l => l.scoreCategory === 'hot').length}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
import React from 'react'
import { 
  PlusIcon, 
  PhoneIcon, 
  DocumentArrowDownIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline'
import { useNavigate } from 'react-router-dom'
import FeatureGate from '../FeatureGate'

interface QuickLeadActionsProps {
  onRefresh: () => void
}

export default function QuickLeadActions({ onRefresh }: QuickLeadActionsProps) {
  const navigate = useNavigate()
  
  const actions = [
    {
      label: 'Neuer Lead',
      icon: PlusIcon,
      color: 'bg-blue-600 hover:bg-blue-700',
      feature: 'lead_scoring',
      onClick: () => navigate('/app/leads/new')
    },
    {
      label: 'Lead anrufen',
      icon: PhoneIcon,
      color: 'bg-green-600 hover:bg-green-700',
      feature: 'manual_follow_up',
      onClick: () => navigate('/app/leads/call')
    },
    {
      label: 'Export',
      icon: DocumentArrowDownIcon,
      color: 'bg-purple-600 hover:bg-purple-700',
      feature: 'bulk_operations',
      onClick: () => console.log('Export leads')
    },
    {
      label: 'Aktualisieren',
      icon: ArrowPathIcon,
      color: 'bg-gray-600 hover:bg-gray-700',
      feature: null, // Available for all
      onClick: onRefresh
    }
  ]
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Schnellaktionen</h3>
      
      <div className="space-y-2">
        {actions.map((action, index) => {
          const button = (
            <button
              key={index}
              onClick={action.onClick}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-white transition-colors ${action.color}`}
            >
              <action.icon className="h-5 w-5" />
              <span className="font-medium">{action.label}</span>
            </button>
          )
          
          if (action.feature) {
            return (
              <FeatureGate key={index} feature={action.feature} showLocked>
                {button}
              </FeatureGate>
            )
          }
          
          return button
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <FeatureGate feature="lead_reactivation">
          <div className="text-xs text-gray-500 text-center">
            <p className="mb-2">Automatische Reaktivierung</p>
            <div className="flex justify-center gap-2">
              <span className="px-2 py-1 bg-gray-100 rounded">30 Tage</span>
              <span className="px-2 py-1 bg-gray-100 rounded">60 Tage</span>
              <span className="px-2 py-1 bg-gray-100 rounded">90 Tage</span>
            </div>
          </div>
        </FeatureGate>
        
        <FeatureGate 
          feature="lead_reactivation" 
          fallback={
            <div className="text-xs text-gray-400 text-center">
              <p>Lead Reaktivierung</p>
              <p className="text-orange-600">Enterprise Feature</p>
            </div>
          }
        />
      </div>
    </div>
  )
}
import React, { useState, useEffect } from 'react'
import { CalendarIcon, ClockIcon, PhoneIcon } from '@heroicons/react/24/outline'
import apiClient from '../../services/api'

interface FollowUp {
  id: number
  leadName: string
  scheduledDate: string
  followUpNumber: number
  priority: 'low' | 'medium' | 'high' | 'urgent'
  scriptType: string
}

export default function FollowUpCalendar() {
  const [followUps, setFollowUps] = useState<FollowUp[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchFollowUps()
  }, [])
  
  const fetchFollowUps = async () => {
    try {
      const response = await apiClient.get('/api/leads/follow-ups/upcoming')
      setFollowUps(response.data)
    } catch (error) {
      console.error('Error fetching follow-ups:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const getPriorityColor = (priority: string) => {
    switch(priority) {
      case 'urgent': return 'text-red-600 bg-red-100'
      case 'high': return 'text-orange-600 bg-orange-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-gray-600 bg-gray-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }
  
  const getFollowUpLabel = (number: number) => {
    const labels: Record<number, string> = {
      1: '3 Tage',
      2: '7 Tage',
      3: '14 Tage',
      4: '30 Tage'
    }
    return labels[number] || `Follow-Up ${number}`
  }
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    if (date.toDateString() === today.toDateString()) {
      return `Heute, ${date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })}`
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return `Morgen, ${date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })}`
    } else {
      return date.toLocaleDateString('de-DE', { 
        day: '2-digit', 
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
  
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="space-y-3">
            <div className="h-12 bg-gray-100 rounded"></div>
            <div className="h-12 bg-gray-100 rounded"></div>
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Anstehende Follow-Ups</h3>
        <CalendarIcon className="h-5 w-5 text-gray-400" />
      </div>
      
      {followUps.length === 0 ? (
        <p className="text-gray-500 text-sm text-center py-4">
          Keine Follow-Ups geplant
        </p>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {followUps.map(followUp => (
            <div 
              key={followUp.id}
              className="border rounded-lg p-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-sm">{followUp.leadName}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <ClockIcon className="h-3 w-3 text-gray-400" />
                    <span className="text-xs text-gray-600">
                      {formatDate(followUp.scheduledDate)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getPriorityColor(followUp.priority)}`}>
                      {followUp.priority}
                    </span>
                    <span className="text-xs text-gray-500">
                      {getFollowUpLabel(followUp.followUpNumber)}
                    </span>
                  </div>
                </div>
                <button className="text-green-600 hover:text-green-700 p-1">
                  <PhoneIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <div className="mt-4 pt-4 border-t">
        <div className="text-xs text-gray-500 text-center">
          <p>30% mehr Umsatz durch systematisches Follow-Up</p>
        </div>
      </div>
    </div>
  )
}
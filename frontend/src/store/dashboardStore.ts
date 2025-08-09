import { create } from 'zustand'
import { systemApi, callsApi, type SystemStatus, type CallRecord } from '../services/api'

interface DashboardStats {
  totalCallsToday: number
  avgCallDuration: string
  successfulCalls: number
  failedCalls: number
}

interface DashboardStore {
  stats: DashboardStats
  recentCalls: CallRecord[]
  systemStatus: SystemStatus[]
  isLoading: boolean
  error: string | null
  
  // Actions
  loadDashboardData: () => Promise<void>
  refreshStats: () => Promise<void>
}

const defaultStats: DashboardStats = {
  totalCallsToday: 47,
  avgCallDuration: '3:42',
  successfulCalls: 89,
  failedCalls: 5
}

const defaultRecentCalls = [
  { id: 1, phone: '+49 30 12345678', status: 'completed', duration: '4:23', time: '2 min ago' },
  { id: 2, phone: '+49 30 87654321', status: 'failed', duration: '0:15', time: '8 min ago' },
  { id: 3, phone: '+49 30 11223344', status: 'completed', duration: '2:17', time: '12 min ago' },
  { id: 4, phone: '+49 30 99887766', status: 'completed', duration: '6:45', time: '18 min ago' },
] as unknown as CallRecord[]

const defaultSystemStatus = [
  { service: 'VoiceAI API', status: 'connected', lastCheck: new Date().toISOString() },
  { service: 'Twilio Connection', status: 'connected', lastCheck: new Date().toISOString() },
  { service: 'Database', status: 'connected', lastCheck: new Date().toISOString() },
  { service: 'Knowledge Base', status: 'connected', lastCheck: new Date().toISOString() },
] as SystemStatus[]

export const useDashboardStore = create<DashboardStore>((set) => ({
  stats: defaultStats,
  recentCalls: defaultRecentCalls,
  systemStatus: defaultSystemStatus,
  isLoading: false,
  error: null,

  loadDashboardData: async () => {
    set({ isLoading: true, error: null })
    try {
      // Try to load from API
      const [systemStatus, recentCalls, stats] = await Promise.allSettled([
        systemApi.getStatus(),
        callsApi.getHistory(4),
        systemApi.getStats()
      ])
      
      set({
        systemStatus: systemStatus.status === 'fulfilled' ? systemStatus.value : defaultSystemStatus,
        recentCalls: recentCalls.status === 'fulfilled' ? recentCalls.value : defaultRecentCalls,
        stats: stats.status === 'fulfilled' ? stats.value : defaultStats,
        isLoading: false
      })
    } catch {
      console.warn('Failed to load from API, using default data')
      set({ 
        isLoading: false,
        error: 'Could not connect to backend'
      })
    }
  },

  refreshStats: async () => {
    try {
      const stats = await systemApi.getStats()
      set({ stats })
    } catch {
      console.warn('Failed to refresh stats')
    }
  }
}))
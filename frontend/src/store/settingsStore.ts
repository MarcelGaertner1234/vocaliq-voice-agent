import { create } from 'zustand'
import { settingsApi } from '../services/api'

export interface ScheduleSlot {
  start: string
  end: string
  nextDay?: boolean
}

export interface SettingsData {
  companyName: string
  phoneNumber: string
  openaiApiKey: string
  elevenLabsApiKey: string
  twilioAccountSid: string
  twilioAuthToken: string
  voiceId: string
  language: string
  maxCallDuration: string
  enableRecording: boolean
  enableNotifications: boolean
  
  // Agent Control
  agentEnabled: boolean
  
  // Scheduling
  schedule: {
    monday: ScheduleSlot[]
    tuesday: ScheduleSlot[]
    wednesday: ScheduleSlot[]
    thursday: ScheduleSlot[]
    friday: ScheduleSlot[]
    saturday: ScheduleSlot[]
    sunday: ScheduleSlot[]
  }
  timezone: string
}

interface SettingsStore {
  settings: SettingsData
  isLoading: boolean
  error: string | null
  
  // Actions
  loadSettings: () => Promise<void>
  updateSettings: (newSettings: Partial<SettingsData>) => Promise<void>
  testConnection: (service: string, credentials: Record<string, string>) => Promise<boolean>
  setSettings: (settings: SettingsData) => void
}

const defaultSettings: SettingsData = {
  companyName: 'VocalIQ Demo Company',
  phoneNumber: '+49 30 12345678',
  openaiApiKey: '',
  elevenLabsApiKey: '',
  twilioAccountSid: '',
  twilioAuthToken: '',
  voiceId: 'Antoni',
  language: 'de-DE',
  maxCallDuration: '300',
  enableRecording: true,
  enableNotifications: true,
  
  // Agent Control
  agentEnabled: true,
  
  // Scheduling  
  schedule: {
    monday: [{ start: '09:00', end: '17:00' }],
    tuesday: [{ start: '09:00', end: '17:00' }],
    wednesday: [{ start: '09:00', end: '17:00' }],
    thursday: [{ start: '09:00', end: '17:00' }],
    friday: [{ start: '09:00', end: '17:00' }],
    saturday: [],
    sunday: []
  },
  timezone: 'Europe/Berlin'
}

export const useSettingsStore = create<SettingsStore>((set, get) => ({
      settings: defaultSettings,
      isLoading: false,
      error: null,

      loadSettings: async () => {
        set({ isLoading: true, error: null })
        try {
          const settings = await settingsApi.get() as unknown as SettingsData
          set({ settings, isLoading: false })
        } catch {
          // If API fails, use persisted settings
          console.warn('Failed to load settings from API, using local storage')
          set({ isLoading: false, error: 'Failed to connect to backend' })
        }
      },

      updateSettings: async (newSettings) => {
        set({ isLoading: true, error: null })
        try {
          const updatedSettings = { ...get().settings, ...newSettings }
          
          // Try to save to API
          try {
            await settingsApi.update(newSettings)
          } catch {
            console.warn('Failed to save to API, saving locally')
          }
          
          set({ settings: updatedSettings, isLoading: false })
        } catch {
          set({ error: 'Failed to update settings', isLoading: false })
        }
      },

      testConnection: async (service, credentials) => {
        try {
          return await settingsApi.testConnection(service, credentials)
        } catch {
          return false
        }
      },

      setSettings: (settings) => {
        set({ settings })
        // Also save to localStorage manually
        localStorage.setItem('vocaliq-settings', JSON.stringify(settings))
      }
    }))

    // Load from localStorage on init
    const stored = localStorage.getItem('vocaliq-settings')
    if (stored) {
      try {
        const parsedSettings = JSON.parse(stored)
        useSettingsStore.getState().setSettings({ ...defaultSettings, ...parsedSettings })
      } catch {
        console.warn('Failed to parse stored settings')
      }
    }
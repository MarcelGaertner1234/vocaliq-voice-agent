import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { settingsApi } from '../services/api'

interface SettingsData {
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
  enableNotifications: true
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      settings: defaultSettings,
      isLoading: false,
      error: null,

      loadSettings: async () => {
        set({ isLoading: true, error: null })
        try {
          const settings = await settingsApi.get()
          set({ settings, isLoading: false })
        } catch (error) {
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
          } catch (error) {
            console.warn('Failed to save to API, saving locally')
          }
          
          set({ settings: updatedSettings, isLoading: false })
        } catch (error) {
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
      }
    }),
    {
      name: 'vocaliq-settings',
      partialize: (state) => ({ settings: state.settings }),
    }
  )
)
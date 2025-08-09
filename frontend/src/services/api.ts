import axios from 'axios'

export const API_BASE_URL = 'http://localhost:8001/api'

export const wsUrlFor = (path: string) => {
  const httpBase = API_BASE_URL.replace(/\/$/, '')
  const root = httpBase.endsWith('/api') ? httpBase.slice(0, -4) : httpBase
  const wsBase = root.replace('https://', 'wss://').replace('http://', 'ws://')
  return `${wsBase}${path.startsWith('/') ? path : `/${path}`}`
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
apiClient.interceptors.request.use((config) => {
  // Add auth token if available
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Interface entfernt - wird jetzt im Store definiert

export interface CallRecord {
  id: number
  phone: string
  direction: 'inbound' | 'outbound'
  status: 'completed' | 'failed' | 'in-progress'
  duration: string
  timestamp: string
  transcript: string
  customerName?: string
  intent?: string
}

export interface SystemStatus {
  service: string
  status: 'connected' | 'disconnected'
  lastCheck: string
}

// Settings API
export const settingsApi = {
  get: async (): Promise<unknown> => {
    const response = await apiClient.get('/settings')
    return response.data
  },
  
  update: async (settings: unknown): Promise<unknown> => {
    const response = await apiClient.put('/settings', settings)
    return response.data
  },
  
  testConnection: async (service: string, credentials: unknown): Promise<boolean> => {
    try {
      const response = await apiClient.post(`/settings/test-connection`, {
        service,
        credentials
      })
      return response.data.success
    } catch {
      return false
    }
  }
}

// Calls API
export const callsApi = {
  getHistory: async (limit = 50): Promise<CallRecord[]> => {
    const response = await apiClient.get(`/calls?limit=${limit}`)
    return response.data
  },
  
  getById: async (id: number): Promise<CallRecord> => {
    const response = await apiClient.get(`/calls/${id}`)
    return response.data
  }
}

// System API
export const systemApi = {
  getStatus: async (): Promise<SystemStatus[]> => {
    const response = await apiClient.get('/system/status')
    return response.data
  },
  
  getStats: async () => {
    const response = await apiClient.get('/system/stats')
    return response.data
  }
}

// Knowledge Base API
export const knowledgeApi = {
  getDocuments: async () => {
    const response = await apiClient.get('/knowledge/documents')
    return response.data
  },
  
  uploadDocument: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/knowledge/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  
  deleteDocument: async (id: string) => {
    await apiClient.delete(`/knowledge/documents/${id}`)
  },

  search: async (query: string, limit = 5) => {
    const response = await apiClient.get(`/knowledge/search`, { params: { query, limit } })
    return response.data
  }
}

export default apiClient
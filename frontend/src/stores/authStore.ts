import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import axios from 'axios'

export type UserRole = 'admin' | 'customer' | 'agent'

interface User {
  id: string
  email: string
  name: string
  role: UserRole
  companyId?: string
  companyName?: string
  subscription_plan?: 'free' | 'basic' | 'professional' | 'enterprise'
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  loginAdmin: (email: string, password: string) => Promise<boolean>
  loginCustomer: (email: string, password: string) => Promise<boolean>
  logout: () => void
  checkAuth: () => Promise<void>
  setUser: (user: User | null) => void
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      loginAdmin: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await axios.post(`${API_URL}/api/auth/login`, {
            username: email,
            password,
            remember_me: true
          })

          const { access_token, refresh_token, user } = response.data

          // Check if user is admin (accept both role field and scopes)
          const isAdmin = user.role === 'admin' || 
                         (user.scopes && user.scopes.includes('admin'))
          
          if (!isAdmin) {
            set({ error: 'Access denied. Admin privileges required.', isLoading: false })
            return false
          }

          // Set auth token for axios
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

          set({
            user: {
              id: user.id,
              email: user.email,
              name: user.full_name || user.username,
              role: 'admin',
              subscription_plan: user.subscription_plan || 'enterprise'
            },
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false
          })

          return true
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Login failed', 
            isLoading: false 
          })
          return false
        }
      },

      loginCustomer: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await axios.post(`${API_URL}/api/auth/login`, {
            username: email,
            password,
            remember_me: false
          })

          const { access_token, refresh_token, user } = response.data

          // Set auth token for axios
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

          set({
            user: {
              id: user.id,
              email: user.email,
              name: user.full_name || user.username,
              role: user.role || 'customer',
              companyId: user.organization_id,
              companyName: user.organization_name,
              subscription_plan: user.subscription_plan || 'professional'
            },
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false
          })

          return true
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Login failed', 
            isLoading: false 
          })
          return false
        }
      },

      logout: () => {
        // Clear axios auth header
        delete axios.defaults.headers.common['Authorization']
        
        // Clear state
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null
        })

        // Clear localStorage
        localStorage.removeItem('auth-storage')
        
        // Redirect to login
        window.location.href = '/login'
      },

      checkAuth: async () => {
        const token = get().token
        if (!token) {
          set({ isAuthenticated: false })
          return
        }

        try {
          // Set auth header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
          
          // Verify token with backend
          const response = await axios.get(`${API_URL}/api/auth/me`)
          
          set({
            user: response.data,
            isAuthenticated: true
          })
        } catch (error) {
          // Token invalid, clear auth
          get().logout()
        }
      },

      setUser: (user) => {
        set({ user })
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)

// Axios interceptor for token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          })

          const { access_token } = response.data
          useAuthStore.setState({ token: access_token })
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

          return axios(originalRequest)
        } catch (refreshError) {
          useAuthStore.getState().logout()
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)
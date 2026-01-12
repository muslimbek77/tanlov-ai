import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

const API_BASE = 'http://localhost:8000/api/auth'

interface User {
  id: number
  username: string
  email: string
  role: string
  role_display: string
  first_name: string
  last_name: string
  is_admin: boolean
  can_analyze: boolean
}

interface AuthContextType {
  isAuthenticated: boolean
  user: User | null
  accessToken: string | null
  loading: boolean
  login: (username: string, password: string) => Promise<boolean>
  logout: () => Promise<void>
  refreshToken: () => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Fallback credentials (offline mode)
const FALLBACK_CREDENTIALS = {
  username: 'trest',
  password: 'trest2026'
}

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [user, setUser] = useState<User | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    // LocalStorage dan tekshirish
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')
    const authStatus = localStorage.getItem('isAuthenticated')
    
    if (storedToken && storedUser) {
      setAccessToken(storedToken)
      try {
        setUser(JSON.parse(storedUser))
        setIsAuthenticated(true)
      } catch (e) {
        console.error('User parsing error:', e)
      }
    } else if (authStatus === 'true') {
      // Legacy support
      setIsAuthenticated(true)
    }
    setLoading(false)
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      // API orqali login
      const response = await fetch(`${API_BASE}/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })

      const data = await response.json()

      if (data.success && data.access) {
        setAccessToken(data.access)
        setUser(data.user)
        setIsAuthenticated(true)
        
        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)
        localStorage.setItem('user', JSON.stringify(data.user))
        localStorage.setItem('isAuthenticated', 'true')
        
        return true
      }
      
      return false
    } catch (error) {
      console.error('Login error:', error)
      
      // Fallback - offline mode
      if (username === FALLBACK_CREDENTIALS.username && password === FALLBACK_CREDENTIALS.password) {
        const fallbackUser: User = {
          id: 1,
          username: 'trest',
          email: 'trest@example.com',
          role: 'admin',
          role_display: 'Administrator',
          first_name: 'Admin',
          last_name: 'User',
          is_admin: true,
          can_analyze: true
        }
        
        setUser(fallbackUser)
        setIsAuthenticated(true)
        localStorage.setItem('isAuthenticated', 'true')
        localStorage.setItem('user', JSON.stringify(fallbackUser))
        
        return true
      }
      
      return false
    }
  }

  const logout = async (): Promise<void> => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken && accessToken) {
        await fetch(`${API_BASE}/simple-logout/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
          },
          body: JSON.stringify({ refresh: refreshToken })
        })
      }
    } catch (error) {
      console.error('Logout error:', error)
    }
    
    setIsAuthenticated(false)
    setUser(null)
    setAccessToken(null)
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('isAuthenticated')
  }

  const refreshToken = async (): Promise<boolean> => {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) return false

      const response = await fetch(`${API_BASE}/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh })
      })

      const data = await response.json()

      if (data.access) {
        setAccessToken(data.access)
        localStorage.setItem('access_token', data.access)
        if (data.refresh) {
          localStorage.setItem('refresh_token', data.refresh)
        }
        return true
      }
      
      return false
    } catch (error) {
      console.error('Token refresh error:', error)
      return false
    }
  }

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      user,
      accessToken,
      loading,
      login, 
      logout,
      refreshToken
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// API so'rovlari uchun helper
export const getAuthHeader = (): HeadersInit => {
  const token = localStorage.getItem('access_token')
  if (token) {
    return { 'Authorization': `Bearer ${token}` }
  }
  return {}
}

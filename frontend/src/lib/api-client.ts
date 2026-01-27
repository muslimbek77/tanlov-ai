import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://tanlov.kuprikqurilish.uz/api'

// API client yaratish
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - access token qo'shish
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

let isRefreshing = false
let failedQueue: Array<{
  onSuccess: (token: string) => void
  onFailed: (error: Error) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.onFailed(error)
    } else if (token) {
      prom.onSuccess(token)
    }
  })
  
  isRefreshing = false
  failedQueue = []
}

// Response interceptor - token refresh qo'lini tekshirish
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((onSuccess, onFailed) => {
          failedQueue.push({ onSuccess, onFailed })
        })
          .then(token => {
            if (originalRequest.headers && token) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return apiClient(originalRequest)
          })
          .catch(err => Promise.reject(err))
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        processQueue(new Error('No refresh token'), null)
        // Login sahifasiga yo'naltirish
        window.location.href = '/login'
        return Promise.reject(error)
      }
      
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken
        })
        
        const { access } = response.data
        localStorage.setItem('access_token', access)
        
        // Yangi refresh token bo'lsa saqlash
        if (response.data.refresh) {
          localStorage.setItem('refresh_token', response.data.refresh)
        }
        
        apiClient.defaults.headers.common.Authorization = `Bearer ${access}`
        originalRequest.headers.Authorization = `Bearer ${access}`
        
        processQueue(null, access)
        return apiClient(originalRequest)
      } catch (err) {
        processQueue(err instanceof Error ? err : new Error('Token refresh failed'), null)
        
        // Login sahifasiga yo'naltirish
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        localStorage.removeItem('isAuthenticated')
        window.location.href = '/login'
        
        return Promise.reject(err)
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient

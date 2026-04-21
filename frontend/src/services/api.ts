import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true  // ← send cookies with every request!
})

// Add token to every request automatically
api.interceptors.request.use((config) => {
  const auth = localStorage.getItem('auth-storage')
  if (auth) {
    const { state } = JSON.parse(auth)
    if (state?.accessToken) {
      config.headers.Authorization = `Bearer ${state.accessToken}`
    }
  }
  return config
})

// Handle 401 responses automatically
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth store
      localStorage.removeItem('auth-storage')
      // Redirect to login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const chatAPI = {
  askQuestion: async (question: string) => {
    const response = await api.post('/ask/', { question })
    return response.data
  },
  getHistory: async () => {
    const response = await api.get('/api/chat/history/')
    return response.data;
  },
  clearHistory: async () => {
    const response = await api.delete('/api/chat/history/clear/')
    return response.data;
  }
}

export const authAPI = {
  register: async (username: string, email: string, password: string, password2: string) => {
    const response = await api.post('/api/auth/register/', {
      username, email, password, password2
    })
    return response.data
  },
  login: async (username: string, password: string) => {
    const response = await api.post('/api/auth/login/', {
      username, password
    })
    return response.data
  },
  logout: async (refreshToken: string) => {
    const response = await api.post('/api/auth/logout/', {
      refresh: refreshToken
    })
    return response.data
  },
  profile: async () => {
    const response = await api.get('/api/auth/profile/')
    return response.data
  },
  updateProfile: async (data: {email?: string, first_name?: string, last_name?: string}) => {
    const response = await api.put('/api/auth/profile/update/', data)
    return response.data
  },
  verifyOTP: async (user_id: number, otp: string) => {
    const response = await api.post('/api/auth/verify-otp/', { user_id, otp })
    return response.data
  },
  // TOTP
  verifyTOTPLogin: async (user_id: number, token: string) => {
    const response = await api.post('/api/auth/totp/verify-login/', { user_id, token })
    return response.data
  },
  totpSetup: async () => {
    const response = await api.post('/api/auth/totp/setup/', {})
    return response.data
  },
  totpVerifySetup: async (token: string) => {
    const response = await api.post('/api/auth/totp/verify-setup/', { token })
    return response.data
  },
  totpDisable: async (token: string) => {
    const response = await api.post('/api/auth/totp/disable/', { token })
    return response.data
  },
  totpStatus: async () => {
    const response = await api.get('/api/auth/totp/status/')
    return response.data
  },
}

export default api
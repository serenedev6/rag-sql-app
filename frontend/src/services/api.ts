import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const chatAPI = {
  askQuestion: async (question: string) => {
    const response = await api.post('/ask/', { question })
    return response.data
  },
}

export default api
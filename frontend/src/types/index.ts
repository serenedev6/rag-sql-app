export interface Message {
  id: string
  question: string
  answer: string
  timestamp: Date
  mode?: 'sql' | 'rag'
}

export interface ChatResponse {
  answer: string
  mode?: string
}

export interface User {
  id: string
  username: string
  email: string
}
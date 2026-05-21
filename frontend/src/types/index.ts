export interface Message {
  id: string
  question: string
  answer: string
  timestamp: Date
  mode?: 'sql' | 'rag' | 'agent' | 'auto'
}

export interface ChatResponse {
  answer: string
  mode?: string
}

export interface User {
  id: string
  username: string
  email: string
  first_name?: string
  last_name?: string
}

export interface ChatHistoryItem {
  id: number
  question: string
  answer: string
  mode: 'sql' | 'rag'
  created_at: string
}
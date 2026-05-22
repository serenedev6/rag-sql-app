import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { chatAPI } from '../services/api'
import type { ChatHistoryItem } from '../types'

export const DashboardPage = () => {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [recentHistory, setRecentHistory] = useState<ChatHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const history = await chatAPI.getHistory()
        setRecentHistory(history.slice(0, 5))
      } catch (error) {
        console.error('Error fetching history:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchHistory()
  }, [])

  const stats = [
    { label: 'Total Questions', value: recentHistory.length, icon: '💬' },
    { label: 'SQL Queries', value: recentHistory.filter(h => h.mode === 'sql').length, icon: '🔢' },
    { label: 'RAG Queries', value: recentHistory.filter(h => h.mode === 'rag').length, icon: '🔍' },
  ]

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto min-h-full">
      {/* Welcome header */}
      <div className="mb-6 sm:mb-8">
        <h1 className="text-white text-2xl sm:text-3xl font-bold">
          Welcome back, {user?.username}! 👋
        </h1>
        <p className="text-gray-400 mt-2 text-sm sm:text-base">
          Here's what's happening with your RAG Assistant
        </p>
      </div>

      {/* Stats - Responsive Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-gray-800 border border-gray-700 rounded-xl sm:rounded-2xl p-4 sm:p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl sm:text-3xl">{stat.icon}</span>
              <p className="text-gray-400 text-xs sm:text-sm">{stat.label}</p>
            </div>
            <p className="text-white text-3xl sm:text-4xl font-bold">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Quick actions - Responsive Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
        <button
          onClick={() => navigate('/chat')}
          className="bg-blue-600 hover:bg-blue-700 rounded-xl sm:rounded-2xl p-5 sm:p-6 text-left transition-colors"
        >
          <span className="text-3xl sm:text-4xl mb-2 sm:mb-3 block">🔮</span>
          <h3 className="text-white font-bold text-base sm:text-lg">Start Chatting</h3>
          <p className="text-blue-200 text-xs sm:text-sm mt-1">
            Ask questions about your data
          </p>
        </button>
        <button
          onClick={() => navigate('/history')}
          className="bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-xl sm:rounded-2xl p-5 sm:p-6 text-left transition-colors"
        >
          <span className="text-3xl sm:text-4xl mb-2 sm:mb-3 block">📜</span>
          <h3 className="text-white font-bold text-base sm:text-lg">View History</h3>
          <p className="text-gray-400 text-xs sm:text-sm mt-1">
            Browse your past conversations
          </p>
        </button>
      </div>

      {/* Recent history */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl sm:rounded-2xl p-4 sm:p-6">
        <h2 className="text-white font-bold text-base sm:text-lg mb-4">Recent Questions</h2>
        {isLoading ? (
          <p className="text-gray-400 text-sm">Loading...</p>
        ) : recentHistory.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-400 text-sm">No questions yet!</p>
            <button
              onClick={() => navigate('/chat')}
              className="text-blue-400 hover:text-blue-300 mt-2 text-xs sm:text-sm"
            >
              Start asking questions →
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {recentHistory.map((item) => (
              <div
                key={item.id}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-700 transition-colors"
              >
                <span className="text-base sm:text-lg flex-shrink-0">
                  {item.mode === 'sql' ? '🔢' : '🔍'}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-xs sm:text-sm font-medium truncate">
                    {item.question}
                  </p>
                  <p className="text-gray-400 text-xs truncate mt-1">
                    {item.answer}
                  </p>
                </div>
                <span className="text-xs text-gray-500 whitespace-nowrap hidden sm:block">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
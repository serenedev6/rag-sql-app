import { useEffect, useState } from 'react'
import { chatAPI } from '../services/api'
import type { ChatHistoryItem } from '../types'

export const HistoryPage = () => {
  const [history, setHistory] = useState<ChatHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [clearing, setClearing] = useState(false)

  const fetchHistory = async () => {
    try {
      const data = await chatAPI.getHistory()
      setHistory(data)
    } catch (error) {
      console.error('Error fetching history:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear all chat history?')) return
    setClearing(true)
    try {
      await chatAPI.clearHistory()
      setHistory([])
    } catch (error) {
      console.error('Error clearing history:', error)
    } finally {
      setClearing(false)
    }
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-white text-3xl font-bold">Chat History</h1>
          <p className="text-gray-400 mt-2">All your past conversations</p>
        </div>
        {history.length > 0 && (
          <button
            onClick={handleClearHistory}
            disabled={clearing}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {clearing ? 'Clearing...' : '🗑️ Clear History'}
          </button>
        )}
      </div>

      {/* History list */}
      {isLoading ? (
        <div className="text-center py-20">
          <p className="text-gray-400">Loading history...</p>
        </div>
      ) : history.length === 0 ? (
        <div className="text-center py-20">
          <span className="text-6xl mb-4 block">📜</span>
          <p className="text-gray-400 text-lg">No chat history yet!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item) => (
            <div
              key={item.id}
              className="bg-gray-800 border border-gray-700 rounded-2xl p-6"
            >
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  item.mode === 'sql'
                    ? 'bg-blue-500/20 text-blue-400'
                    : 'bg-purple-500/20 text-purple-400'
                }`}>
                  {item.mode === 'sql' ? '🔢 SQL' : '🔍 RAG'}
                </span>
                <span className="text-gray-500 text-xs">
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </div>
              <p className="text-white font-medium mb-2">{item.question}</p>
              <p className="text-gray-400 text-sm">{item.answer}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
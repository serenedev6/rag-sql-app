import { useState, useRef, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { useChatStore } from '../store/chatStore'
import { chatAPI } from '../services/api'
import { MessageBubble } from '../components/ui/MessageBubble'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export const ChatPage = () => {
  const [question, setQuestion] = useState('')
  const [useAgent, setUseAgent] = useState(false)  // ← New: Agent mode toggle
  const bottomRef = useRef<HTMLDivElement>(null)
  const { messages, isLoading, addMessage, setLoading } = useChatStore()

  // Auto scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!question.trim() || isLoading) return

    const userQuestion = question.trim()
    setQuestion('')
    setLoading(true)

    try {
      // ← Changed: Use agent or regular endpoint based on toggle
      const response = useAgent 
        ? await chatAPI.askAgent(userQuestion)
        : await chatAPI.askQuestion(userQuestion)
        
      addMessage({
        id: uuidv4(),
        question: userQuestion,
        answer: response.answer,
        timestamp: new Date(),
        mode: response.mode || (useAgent ? 'agent' : 'auto'),
      })
    } catch (error) {
      addMessage({
        id: uuidv4(),
        question: userQuestion,
        answer: '❌ Error: Could not get answer. Please try again.',
        timestamp: new Date(),
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend()
  }

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center gap-3">
        <span className="text-2xl">🧠</span>
        <div>
          <h1 className="text-white font-semibold text-lg">RAG SQL Assistant</h1>
          <p className="text-gray-400 text-sm">
            {useAgent ? 'Agent Mode: Multi-tool reasoning' : 'Quick Mode: Fast keyword-based'}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <span className="text-6xl mb-4">🧠</span>
            <h2 className="text-white text-2xl font-semibold mb-2">
              Welcome to RAG SQL Assistant
            </h2>
            <p className="text-gray-400 max-w-md">
              Ask me anything about your data. I can answer questions using
              both RAG and SQL modes.
            </p>
            <div className="mt-6 grid grid-cols-2 gap-3 max-w-lg">
              {[
                'most expensive product',
                'Yoga Mat description',
                'how many customers?',
                'Laptop Pro 15 price',
              ].map((suggestion: string) => (
                <button
                  key={suggestion}
                  onClick={() => setQuestion(suggestion)}
                  className="bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 px-4 py-2 rounded-lg text-sm transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-800 border border-gray-700 text-gray-400 px-4 py-3 rounded-2xl rounded-bl-sm">
                  {useAgent ? '🤖 Agent thinking...' : '⏳ Thinking...'}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </>
        )}
      </div>

      {/* Input area */}
      <div className="bg-gray-800 border-t border-gray-700 px-6 py-4">
        {/* ← New: Mode Toggle */}
        <div className="max-w-4xl mx-auto mb-3 flex items-center justify-center gap-2">
          <button
            onClick={() => setUseAgent(false)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              !useAgent
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            ⚡ Quick Mode
          </button>
          <button
            onClick={() => setUseAgent(true)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              useAgent
                ? 'bg-purple-600 text-white shadow-lg'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            🤖 Agent Mode
          </button>
        </div>
        
        <div className="flex gap-3 max-w-4xl mx-auto">
          <Input
            value={question}
            onChange={setQuestion}
            onKeyPress={handleKeyPress}
            placeholder={
              useAgent
                ? "Ask complex questions (I'll use multiple tools)..."
                : "Ask a question about your data..."
            }
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={isLoading || !question.trim()}
            className="px-6"
          >
            {isLoading ? '...' : 'Send'}
          </Button>
        </div>
      </div>
    </div>
  )
}
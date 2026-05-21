import { useState, useRef, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { useChatStore } from '../store/chatStore'
import { chatAPI } from '../services/api'
import { MessageBubble } from '../components/ui/MessageBubble'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { FileUpload } from '../components/FileUpload'

export const ChatPage = () => {
  const [question, setQuestion] = useState('')
  const [useAgent, setUseAgent] = useState(false)  // ← New: Agent mode toggle
  const bottomRef = useRef<HTMLDivElement>(null)
  const { messages, isLoading, addMessage, setLoading } = useChatStore()

    // ← Add these voice states
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const recognitionRef = useRef<any>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)

  // Auto scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Voice Recognition Setup
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setQuestion(transcript)
        setIsListening(false)
      }

      recognitionRef.current.onerror = () => {
        setIsListening(false)
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }

    synthRef.current = window.speechSynthesis

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (synthRef.current) {
        synthRef.current.cancel()
      }
    }
  }, [])

  // Start/Stop Listening
  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition not supported in this browser. Try Chrome!')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      recognitionRef.current.start()
      setIsListening(true)
    }
  }

  // Speak Answer Aloud
  const speakAnswer = (text: string) => {
    if (!synthRef.current) {
      alert('Text-to-speech not supported in this browser.')
      return
    }

    // Stop any ongoing speech
    synthRef.current.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 1.0
    utterance.pitch = 1.0
    utterance.volume = 1.0

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    synthRef.current.speak(utterance)
  }

  // Stop Speaking
  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel()
      setIsSpeaking(false)
    }
  }

  const handleSend = async () => {
    if (!question.trim() || isLoading) return

    const userQuestion = question.trim()
    setQuestion('')
    setLoading(true)

    // Add user message and placeholder for assistant
    const messageId = uuidv4()
    addMessage({
      id: messageId,
      question: userQuestion,
      answer: '', // Empty initially, will be filled by streaming
      timestamp: new Date(),
      mode: useAgent ? 'agent' : 'auto',
    })

    try {
      let streamedAnswer = ''
      
      const onChunk = (chunk: string) => {
        streamedAnswer += chunk
        // Update the message in real-time
        useChatStore.setState((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === messageId
              ? { ...msg, answer: streamedAnswer }
              : msg
          ),
        }))
      }

      const onDone = () => {
        setLoading(false)
      }

      const onError = (error: string) => {
        useChatStore.setState((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === messageId
              ? { ...msg, answer: `❌ Error: ${error}` }
              : msg
          ),
        }))
        setLoading(false)
      }

      // Use streaming API based on mode
      if (useAgent) {
        chatAPI.askAgentStream(userQuestion, onChunk, onDone, onError)
      } else {
        chatAPI.askQuestionStream(userQuestion, onChunk, onDone, onError)
      }

    } catch (error) {
      useChatStore.setState((state) => ({
        messages: state.messages.map((msg) =>
          msg.id === messageId
            ? { ...msg, answer: '❌ Error: Could not get answer. Please try again.' }
            : msg
        ),
      }))
      setLoading(false)
    }
  }
  
  const handleFileAnalyze = async (file: File, question: string) => {
    setLoading(true)

    const messageId = uuidv4()
    addMessage({
      id: messageId,
      question: `📁 ${file.name}: ${question}`,
      answer: '',
      timestamp: new Date(),
    })

    try {
      let streamedAnswer = ''

      const result = await chatAPI.uploadAndAnalyze(file, question)
      const answer = result.answer || JSON.stringify(result.file_info, null, 2)

      // Simulate streaming for consistency
      const words = answer.split(' ')
      for (const word of words) {
        streamedAnswer += word + ' '
        useChatStore.setState((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === messageId ? { ...msg, answer: streamedAnswer } : msg
          ),
        }))
        await new Promise((resolve) => setTimeout(resolve, 30))
      }
    } catch (error: any) {
      useChatStore.setState((state) => ({
        messages: state.messages.map((msg) =>
          msg.id === messageId
            ? { ...msg, answer: `❌ Error: ${error.message || 'File analysis failed'}` }
            : msg
        ),
      }))
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
        <span className="text-2xl">🔮</span>
        <div>
          <h1 className="text-white font-semibold text-lg">RAG SQL Assistant</h1>
          <p className="text-gray-400 text-sm">
            {useAgent ? 'Agent Mode: Multi-tool reasoning' : 'Quick Mode: Fast keyword-based'}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {/* ← Add FileUpload here */}
        <FileUpload onAnalyze={handleFileAnalyze} isLoading={isLoading} />
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <span className="text-6xl mb-4">🔮</span>
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
          {/* ← Add Microphone Button */}
          <button
            onClick={toggleListening}
            disabled={isLoading}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              isListening
                ? 'bg-red-600 text-white animate-pulse'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
            title={isListening ? 'Stop listening' : 'Start voice input'}
          >
            {isListening ? '🎙️ Listening...' : '🎤'}
          </button>

          <Input
            value={question}
            onChange={setQuestion}
            onKeyPress={handleKeyPress}
            placeholder={
              isListening
                ? 'Listening...'
                : useAgent
                ? "Ask complex questions (I'll use multiple tools)..."
                : "Ask a question about your data..."
            }
            disabled={isLoading || isListening}
          />
          <Button
            onClick={handleSend}
            disabled={isLoading || !question.trim()}
            className="px-6"
          >
            {isLoading ? '...' : 'Send'}
          </Button>

          {/* ← Add Speaker Button */}
          {messages.length > 0 && (
            <button
              onClick={() => {
                if (isSpeaking) {
                  stopSpeaking()
                } else {
                  const lastMessage = messages[messages.length - 1]
                  speakAnswer(lastMessage.answer)
                }
              }}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                isSpeaking
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
              title={isSpeaking ? 'Stop speaking' : 'Read last answer aloud'}
            >
              {isSpeaking ? '🔊 Stop' : '🔊'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
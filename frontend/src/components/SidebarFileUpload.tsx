import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { chatAPI } from '../services/api'
import { useChatStore } from '../store/chatStore'
import { v4 as uuidv4 } from 'uuid'

export const SidebarFileUpload = () => {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const navigate = useNavigate()
  const { addMessage } = useChatStore()

  const handleFileSelect = async (file: File) => {
    if (!file) return

    setIsUploading(true)

    try {
      // Auto-ask question based on file type
      const question = file.type.startsWith('image/') 
        ? "What's in this image?" 
        : "Summarize this file"

      const messageId = uuidv4()
      addMessage({
        id: messageId,
        question: `📁 ${file.name}: ${question}`,
        answer: '',
        timestamp: new Date(),
      })

      const result = await chatAPI.uploadAndAnalyze(file, question)
      const answer = result.answer || JSON.stringify(result.file_info, null, 2)

      // Stream the answer
      let streamedAnswer = ''
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

      // Navigate to chat to see result
      navigate('/chat')
    } catch (error: any) {
      console.error('Upload error:', error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => !isUploading && document.getElementById('sidebar-file-input')?.click()}
      className={`border-2 border-dashed rounded-lg p-3 text-center cursor-pointer transition-all ${
        isDragging
          ? 'border-purple-500 bg-purple-500/10'
          : 'border-gray-700 hover:border-gray-600'
      } ${isUploading ? 'opacity-50 cursor-wait' : ''}`}
    >
      <input
        id="sidebar-file-input"
        type="file"
        onChange={(e) => e.target.files && handleFileSelect(e.target.files[0])}
        className="hidden"
        accept=".csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg,.docx,.txt"
        disabled={isUploading}
      />

      {isUploading ? (
        <div className="text-purple-400 text-sm">
          <div className="animate-spin text-xl mb-1">⏳</div>
          <div>Analyzing...</div>
        </div>
      ) : (
        <div className="text-gray-400 text-xs">
          <div className="text-2xl mb-1">📎</div>
          <div>Drop or click</div>
          <div className="text-gray-500 mt-1">Auto-analyze</div>
        </div>
      )}
    </div>
  )
}
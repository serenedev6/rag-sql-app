import { useState } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { useNavigate } from 'react-router-dom'
import { chatAPI } from '../services/api'
import { useChatStore } from '../store/chatStore'
import { Button } from '../components/ui/Button'

export const FileUploadPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [question, setQuestion] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const navigate = useNavigate()
  const { addMessage } = useChatStore()

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
      setResult(null) // Clear previous result
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0])
      setResult(null)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleAnalyze = async () => {
    if (!selectedFile || !question.trim()) return

    setIsUploading(true)
    setResult(null)

    try {
      const response = await chatAPI.uploadAndAnalyze(selectedFile, question)
      setResult(response)

      // Also add to chat history
      const messageId = uuidv4()
      addMessage({
        id: messageId,
        question: `📁 ${selectedFile.name}: ${question}`,
        answer: response.answer || JSON.stringify(response.file_info, null, 2),
        timestamp: new Date(),
      })
    } catch (error: any) {
      setResult({
        error: error.response?.data?.error || error.message || 'Upload failed'
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleClear = () => {
    setSelectedFile(null)
    setQuestion('')
    setResult(null)
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6 sm:mb-8">
        <h1 className="text-white text-2xl sm:text-3xl font-bold flex items-center gap-3">
          <span>📁</span> File Upload & Analysis
        </h1>
        <p className="text-gray-400 mt-2 text-sm sm:text-base">
          Upload files and ask questions - supports CSV, Excel, PDF, Images, Word, Text
        </p>
      </div>

      {/* File Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => document.getElementById('file-upload-input')?.click()}
        className="border-2 border-dashed border-gray-600 hover:border-gray-500 rounded-xl p-12 text-center cursor-pointer transition-all bg-gray-800/50 mb-6"
      >
        <input
          id="file-upload-input"
          type="file"
          onChange={handleFileSelect}
          className="hidden"
          accept=".csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg,.docx,.txt"
        />

        {selectedFile ? (
          <div className="text-green-400">
            <div className="text-5xl mb-3">✅</div>
            <p className="text-lg font-semibold">{selectedFile.name}</p>
            <p className="text-sm text-gray-400 mt-1">
              {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </div>
        ) : (
          <div className="text-gray-400">
            <div className="text-6xl mb-4">📎</div>
            <p className="text-lg mb-2">Drop file here or click to browse</p>
            <p className="text-sm text-gray-500">
              Supports: CSV, Excel, PDF, Images (JPG, PNG), Word, Text
            </p>
          </div>
        )}
      </div>

      {/* Question Input & Analyze Button */}
      {selectedFile && (
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
          <label className="block text-white font-semibold mb-3">
            Ask a question about this file:
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="E.g., What's in this image? Summarize this document. What's the average in column X?"
            className="w-full bg-gray-900 border border-gray-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-purple-500 resize-none"
            rows={3}
            disabled={isUploading}
          />

          <div className="flex gap-3 mt-4">
            <Button
              onClick={handleAnalyze}
              disabled={isUploading || !question.trim()}
              className="flex-1"
            >
              {isUploading ? '🔮 Analyzing...' : '🔮 Analyze File'}
            </Button>
            <button
              onClick={handleClear}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors"
              disabled={isUploading}
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Result Display */}
      {result && (
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-white font-bold text-lg mb-4 flex items-center gap-2">
            <span>💬</span> Analysis Result
          </h2>

          {result.error ? (
            <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-red-400">
              ❌ {result.error}
            </div>
          ) : (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-gray-300 whitespace-pre-wrap">
              {result.answer}
            </div>
          )}

          <div className="mt-4 flex gap-3">
            <button
              onClick={() => navigate('/chat')}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              → View in Chat History
            </button>
            <button
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-300 text-sm"
            >
              Upload Another File
            </button>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="mt-8 bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
          <span>💡</span> Tips
        </h3>
        <ul className="text-gray-400 text-sm space-y-2">
          <li>• <strong>Images:</strong> Ask "What's in this image?" or "Describe this"</li>
          <li>• <strong>CSV/Excel:</strong> Ask about averages, totals, or specific columns</li>
          <li>• <strong>PDFs/Word:</strong> Ask for summaries or specific information</li>
          <li>• <strong>OCR:</strong> Images with text will be extracted automatically</li>
        </ul>
      </div>
    </div>
  )
}
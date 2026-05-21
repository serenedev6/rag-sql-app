import { useState } from 'react'
import { Button } from './ui/Button'

interface FileUploadProps {
  onAnalyze: (file: File, question: string) => void
  isLoading: boolean
}

export const FileUpload = ({ onAnalyze, isLoading }: FileUploadProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [question, setQuestion] = useState('')

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleAnalyze = () => {
    if (selectedFile && question.trim()) {
      onAnalyze(selectedFile, question)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-4">
      <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
        📁 Upload & Analyze Files
      </h3>

      {/* File Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center mb-4 hover:border-gray-500 transition-colors cursor-pointer"
        onClick={() => document.getElementById('file-input')?.click()}
      >
        {selectedFile ? (
          <div className="text-green-400">
            ✅ {selectedFile.name}
            <p className="text-gray-400 text-sm mt-1">
              {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </div>
        ) : (
          <div className="text-gray-400">
            <p className="mb-2">📎 Drop file here or click to browse</p>
            <p className="text-xs">
              Supports: CSV, Excel, PDF, Images, Word, Text
            </p>
          </div>
        )}
      </div>

      <input
        id="file-input"
        type="file"
        onChange={handleFileSelect}
        className="hidden"
        accept=".csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg,.docx,.txt"
      />

      {/* Question Input */}
      {selectedFile && (
        <div className="space-y-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this file..."
            className="w-full bg-gray-900 border border-gray-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-purple-500"
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isLoading) {
                handleAnalyze()
              }
            }}
          />

          <div className="flex gap-2">
            <Button
              onClick={handleAnalyze}
              disabled={isLoading || !question.trim()}
              className="flex-1"
            >
              {isLoading ? '🔮 Analyzing...' : '🔮 Analyze File'}
            </Button>
            <button
              onClick={() => {
                setSelectedFile(null)
                setQuestion('')
              }}
              className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600"
            >
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
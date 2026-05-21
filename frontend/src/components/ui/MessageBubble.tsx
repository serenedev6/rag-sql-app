import type { Message } from '../../types'

interface MessageBubbleProps {
  message: Message
}

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  return (
    <div className="flex flex-col gap-3 mb-4">
      {/* User question */}
      <div className="flex justify-end">
        <div className="max-w-[75%] bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-br-sm">
          {message.question}
        </div>
      </div>

      {/* Bot answer */}
      <div className="flex justify-start">
        <div className="max-w-[75%] bg-gray-800 border border-gray-700 text-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-blue-400 text-xs font-medium">
              🔮 RAG Assistant
            </span>
            {message.mode && (
              <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded-full">
                {message.mode.toUpperCase()}
              </span>
            )}
          </div>
          {message.answer}
        </div>
      </div>
    </div>
  )
}
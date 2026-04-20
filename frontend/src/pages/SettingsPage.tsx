import { useAuthStore } from '../store/authStore'
import { useChatStore } from '../store/chatStore'

export const SettingsPage = () => {
  const { user } = useAuthStore()
  const { clearMessages } = useChatStore()

  return (
    <div className="p-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-white text-3xl font-bold">Settings</h1>
        <p className="text-gray-400 mt-2">Manage your preferences</p>
      </div>

      {/* Account section */}
      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 mb-6">
        <h2 className="text-white font-bold text-lg mb-4">Account</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-3 border-b border-gray-700">
            <div>
              <p className="text-white text-sm font-medium">Username</p>
              <p className="text-gray-400 text-xs">{user?.username}</p>
            </div>
          </div>
          <div className="flex items-center justify-between py-3">
            <div>
              <p className="text-white text-sm font-medium">Email</p>
              <p className="text-gray-400 text-xs">{user?.email}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat section */}
      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 mb-6">
        <h2 className="text-white font-bold text-lg mb-4">Chat</h2>
        <div className="flex items-center justify-between py-3">
          <div>
            <p className="text-white text-sm font-medium">Clear current session</p>
            <p className="text-gray-400 text-xs">Clear messages from current chat session</p>
          </div>
          <button
            onClick={() => {
              clearMessages()
              alert('Chat session cleared!')
            }}
            className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* App info */}
      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6">
        <h2 className="text-white font-bold text-lg mb-4">About</h2>
        <div className="space-y-2">
          <div className="flex justify-between">
            <p className="text-gray-400 text-sm">App</p>
            <p className="text-white text-sm">RAG SQL Assistant</p>
          </div>
          <div className="flex justify-between">
            <p className="text-gray-400 text-sm">Version</p>
            <p className="text-white text-sm">1.0.0</p>
          </div>
          <div className="flex justify-between">
            <p className="text-gray-400 text-sm">Backend</p>
            <p className="text-white text-sm">Django 6 + Groq</p>
          </div>
          <div className="flex justify-between">
            <p className="text-gray-400 text-sm">Frontend</p>
            <p className="text-white text-sm">React 19 + TypeScript</p>
          </div>
        </div>
      </div>
    </div>
  )
}
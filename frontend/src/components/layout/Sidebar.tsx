import { NavLink, useNavigate } from "react-router-dom"
import { useAuthStore } from "../../store/authStore"
import { authAPI } from "../../services/api";
import { useState } from 'react'  // ← Add this

const navItems = [
  { path: '/', icon: '🏠', label: 'Dashboard' },
  { path: '/chat', icon: '🔮', label: 'Chat' },
  { path: '/file-upload', icon: '📁', label: 'File Upload' },  // ← Add this
  { path: '/history', icon: '📜', label: 'History' },
  { path: '/profile', icon: '👤', label: 'Profile' },
  { path: '/settings', icon: '⚙️', label: 'Settings' },
]

export const Sidebar = () => {
    const {user, refreshToken, clearAuth } = useAuthStore()
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(true)  // ← Add sidebar state

    const handleLogout = async () => {
        try {
            if (refreshToken) {
                await authAPI.logout(refreshToken);
            }
        } catch (error) {
            console.error('Logout error: ',error)
        } finally {
            clearAuth()
            navigate('/login');
        }
    }

    return(
      <>
        {/* Mobile Overlay - close sidebar when clicked */}
        {isOpen && (
          <div 
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setIsOpen(false)}
          />
        )}

        {/* Sidebar */}
        <div className={`
          w-64 bg-gray-900 border-r border-gray-700 flex flex-col h-screen
          fixed left-0 top-0 z-50 transition-transform duration-300
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0
        `}>
          {/* Close Button (Mobile Only) */}
          <button
            onClick={() => setIsOpen(false)}
            className="absolute top-4 right-4 text-gray-400 hover:text-white lg:hidden"
          >
            ✕
          </button>

          {/* Logo */}
          <div className="p-6 border-b border-gray-700">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🔮</span>
              <div>
                <h1 className="text-white font-bold text-lg">RAG Assistant</h1>
                <p className="text-gray-400 text-xs">AI Powered</p>
              </div>
            </div>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                onClick={() => setIsOpen(false)} // ← Close sidebar on mobile after click
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                  }`
                }
              >
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </NavLink>
            ))}
          </nav>

          {/* User info + Logout */}
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white text-sm font-bold">
                  {user?.username?.[0]?.toUpperCase()}
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-white text-sm font-medium truncate">{user?.username}</p>
                <p className="text-gray-400 text-xs truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
            >
              <span>🚪</span>
              <span className="text-sm font-medium">Logout</span>
            </button>
          </div>
        </div>

        {/* Toggle Button (Mobile) */}
        <button
          onClick={() => setIsOpen(true)}
          className={`
            fixed top-4 left-4 z-30 bg-gray-800 text-white p-3 rounded-lg
            shadow-lg lg:hidden
            ${isOpen ? 'hidden' : 'block'}
          `}
        >
          ☰
        </button>
      </>
    )
}
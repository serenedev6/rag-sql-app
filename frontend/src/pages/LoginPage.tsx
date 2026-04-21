import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export const LoginPage = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogin = async () => {
    if (!username || !password) {
      setError('Please fill in all fields')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await authAPI.login(username, password)
      if (response.mfa_required) {
        navigate('/verify-otp', {
          state: {
            user_id: response.user_id,
            message: response.message,
            mfa_type: response.mfa_type  // ← add this
          }
        })
        return
      }

      setAuth(response.user, response.access, response.refresh)
      navigate('/')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status?: number,  data?: { error?: string } } }
        if (axiosErr.response?.status === 429) {
          setError('Too many login attempts. Please try again in a minute.')
        } else {
          setError(axiosErr.response?.data?.error || 'Invalid credentials')
        }
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleLogin()
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <span className="text-6xl">🧠</span>
          <h1 className="text-white text-3xl font-bold mt-4">
            RAG SQL Assistant
          </h1>
          <p className="text-gray-400 mt-2">Sign in to your account</p>
        </div>

        {/* Form */}
        <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700">
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                Username
              </label>
              <Input
                value={username}
                onChange={setUsername}
                onKeyPress={handleKeyPress}
                placeholder="Enter your username"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                Password
              </label>
              <Input
                value={password}
                onChange={setPassword}
                onKeyPress={handleKeyPress}
                placeholder="Enter your password"
                disabled={isLoading}
              />
            </div>
          </div>

          <Button
            onClick={handleLogin}
            disabled={isLoading}
            className="w-full mt-6 py-3"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </Button>

          <p className="text-center text-gray-400 mt-6 text-sm">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="text-blue-400 hover:text-blue-300 font-medium"
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
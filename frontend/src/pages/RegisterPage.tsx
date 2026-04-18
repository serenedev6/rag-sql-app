import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export const RegisterPage = () => {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleRegister = async () => {
    if (!username || !email || !password || !password2) {
      setError('Please fill in all fields')
      return
    }

    if (password !== password2) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await authAPI.register(username, email, password, password2)
      setAuth(response.user, response.access, response.refresh)
      navigate('/')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: Record<string, string[]> } }
        const errors = axiosErr.response?.data
        if (errors) {
          const firstError = Object.values(errors)[0]
          setError(Array.isArray(firstError) ? firstError[0] : 'Registration failed')
        }
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleRegister()
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
          <p className="text-gray-400 mt-2">Create your account</p>
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
                placeholder="Choose a username"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                Email
              </label>
              <Input
                value={email}
                onChange={setEmail}
                onKeyPress={handleKeyPress}
                placeholder="Enter your email"
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
                placeholder="Min 8 characters"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                Confirm Password
              </label>
              <Input
                value={password2}
                onChange={setPassword2}
                onKeyPress={handleKeyPress}
                placeholder="Repeat your password"
                disabled={isLoading}
              />
            </div>
          </div>

          <Button
            onClick={handleRegister}
            disabled={isLoading}
            className="w-full mt-6 py-3"
          >
            {isLoading ? 'Creating account...' : 'Create Account'}
          </Button>

          <p className="text-center text-gray-400 mt-6 text-sm">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-blue-400 hover:text-blue-300 font-medium"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
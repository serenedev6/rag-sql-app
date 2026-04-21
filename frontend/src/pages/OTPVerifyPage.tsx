import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export const OTPVerifyPage = () => {
  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  // Get user_id and message passed from login page
  const { user_id, message } = location.state || {}

  const handleVerify = async () => {
    if (!otp.trim()) {
      setError('Please enter the OTP')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await authAPI.verifyOTP(user_id, otp)
      setAuth(response.user, response.access, response.refresh)
      navigate('/')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        setError(axiosErr.response?.data?.error || 'Invalid OTP')
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleVerify()
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <span className="text-6xl">🔐</span>
          <h1 className="text-white text-3xl font-bold mt-4">
            Verify Your Identity
          </h1>
          <p className="text-gray-400 mt-2">
            {message || 'Enter the OTP sent to your email'}
          </p>
        </div>

        {/* Form */}
        <div className="bg-gray-800 rounded-2xl p-8 border border-gray-700">
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="text-gray-300 text-sm font-medium mb-2 block">
              Enter 6-digit OTP
            </label>
            <Input
              value={otp}
              onChange={setOtp}
              onKeyPress={handleKeyPress}
              placeholder="Enter OTP"
              disabled={isLoading}
              className="text-center text-2xl tracking-widest"
            />
            <p className="text-gray-500 text-xs mt-2">
              OTP expires in 10 minutes
            </p>
          </div>

          <Button
            onClick={handleVerify}
            disabled={isLoading || !otp.trim()}
            className="w-full mt-6 py-3"
          >
            {isLoading ? 'Verifying...' : 'Verify OTP'}
          </Button>

          <button
            onClick={() => navigate('/login')}
            className="w-full mt-4 text-gray-400 hover:text-white text-sm transition-colors"
          >
            ← Back to Login
          </button>
        </div>
      </div>
    </div>
  )
}
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

  const { user_id, message, mfa_type } = location.state || {}
  const isTOTP = mfa_type === 'totp'

  const handleVerify = async () => {
    if (!otp.trim()) {
      setError('Please enter the code')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      let response
      if (isTOTP) {
        response = await authAPI.verifyTOTPLogin(user_id, otp)
      } else {
        response = await authAPI.verifyOTP(user_id, otp)
      }
      setAuth(response.user, response.access, response.refresh)
      navigate('/')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        setError(axiosErr.response?.data?.error || 'Invalid code')
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="text-6xl">{isTOTP ? '📱' : '🔐'}</span>
          <h1 className="text-gray-900 dark:text-white text-3xl font-bold mt-4">
            {isTOTP ? 'Authenticator Code' : 'Verify Your Identity'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {message || (isTOTP
              ? 'Enter the 6-digit code from your authenticator app'
              : 'Enter the OTP sent to your email'
            )}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700">
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="text-gray-700 dark:text-gray-300 text-sm font-medium mb-2 block">
              {isTOTP ? 'Authenticator Code' : '6-digit OTP'}
            </label>
            <Input
              value={otp}
              onChange={setOtp}
              placeholder="Enter 6-digit code"
              disabled={isLoading}
            />
            {!isTOTP && (
              <p className="text-gray-500 dark:text-gray-500 text-xs mt-2">OTP expires in 10 minutes</p>
            )}
            {isTOTP && (
              <p className="text-gray-500 dark:text-gray-500 text-xs mt-2">Code refreshes every 30 seconds</p>
            )}
          </div>

          <Button
            onClick={handleVerify}
            disabled={isLoading || !otp.trim()}
            className="w-full mt-6 py-3"
          >
            {isLoading ? 'Verifying...' : 'Verify'}
          </Button>

          <button
            onClick={() => navigate('/login')}
            className="w-full mt-4 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-sm transition-colors"
          >
            ← Back to Login
          </button>
        </div>
      </div>
    </div>
  )
}
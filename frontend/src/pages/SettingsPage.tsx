import { useState, useEffect } from 'react'
import { authAPI } from '../services/api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export const SettingsPage = () => {
  const [totpEnabled, setTotpEnabled] = useState(false)
  const [showSetup, setShowSetup] = useState(false)
  const [qrCode, setQrCode] = useState('')
  const [secretKey, setSecretKey] = useState('')
  const [token, setToken] = useState('')
  const [disableToken, setDisableToken] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showDisable, setShowDisable] = useState(false)

  useEffect(() => {
    fetchTOTPStatus()
  }, [])

  const fetchTOTPStatus = async () => {
    try {
      const data = await authAPI.totpStatus()
      setTotpEnabled(data.enabled)
    } catch (err) {
      console.error('Error fetching TOTP status:', err)
    }
  }

  const handleSetupTOTP = async () => {
    setIsLoading(true)
    setError('')
    setMessage('')
    try {
      const data = await authAPI.totpSetup()
      setQrCode(data.qr_code)
      setSecretKey(data.secret_key)
      setShowSetup(true)
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        setError(axiosErr.response?.data?.error || 'Failed to setup TOTP')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifySetup = async () => {
    if (!token.trim()) {
      setError('Please enter the token')
      return
    }
    setIsLoading(true)
    setError('')
    try {
      await authAPI.totpVerifySetup(token)
      setMessage('✅ Google Authenticator enabled successfully!')
      setTotpEnabled(true)
      setShowSetup(false)
      setToken('')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        setError(axiosErr.response?.data?.error || 'Invalid token')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleDisableTOTP = async () => {
    if (!disableToken.trim()) {
      setError('Please enter the token')
      return
    }
    setIsLoading(true)
    setError('')
    try {
      await authAPI.totpDisable(disableToken)
      setMessage('Google Authenticator disabled')
      setTotpEnabled(false)
      setShowDisable(false)
      setDisableToken('')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { error?: string } } }
        setError(axiosErr.response?.data?.error || 'Invalid token')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-2xl bg-gray-50 dark:bg-gray-900 min-h-full">
      <div className="mb-8">
        <h1 className="text-gray-900 dark:text-white text-3xl font-bold">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">Manage your security settings</p>
      </div>

      {/* Success/Error messages */}
      {message && (
        <div className="bg-green-500/10 border border-green-500/50 text-green-400 px-4 py-3 rounded-lg mb-6 text-sm">
          {message}
        </div>
      )}
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm">
          {error}
        </div>
      )}

      {/* TOTP Section */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📱</span>
            <div>
              <h2 className="text-gray-900 dark:text-white font-semibold">Google Authenticator</h2>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Two-factor authentication using TOTP
              </p>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            totpEnabled
              ? 'bg-green-500/20 text-green-400'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
          }`}>
            {totpEnabled ? '✅ Enabled' : 'Disabled'}
          </span>
        </div>

        {/* Setup TOTP */}
        {!totpEnabled && !showSetup && (
          <Button onClick={handleSetupTOTP} disabled={isLoading}>
            {isLoading ? 'Setting up...' : 'Enable Google Authenticator'}
          </Button>
        )}

        {/* QR Code Setup */}
        {showSetup && (
          <div className="mt-4">
            <p className="text-gray-700 dark:text-gray-300 text-sm mb-4">
              Scan this QR code with Google Authenticator:
            </p>

            {/* QR Code */}
            {qrCode && (
              <div className="bg-white p-4 rounded-lg inline-block mb-4">
                <img src={qrCode} alt="QR Code" className="w-48 h-48" />
              </div>
            )}

            {/* Manual entry */}
            <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-3 mb-4">
              <p className="text-gray-600 dark:text-gray-400 text-xs mb-1">Or enter manually:</p>
              <p className="text-gray-900 dark:text-white font-mono text-sm break-all">{secretKey}</p>
            </div>

            {/* Verify token */}
            <div>
              <label className="text-gray-700 dark:text-gray-300 text-sm font-medium mb-2 block">
                Enter code from app to verify:
              </label>
              <Input
                value={token}
                onChange={setToken}
                placeholder="Enter 6-digit code"
              />
            </div>

            <div className="flex gap-3 mt-4">
              <Button onClick={handleVerifySetup} disabled={isLoading}>
                {isLoading ? 'Verifying...' : 'Verify & Enable'}
              </Button>
              <button
                onClick={() => { setShowSetup(false); setToken('') }}
                className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-sm transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Disable TOTP */}
        {totpEnabled && !showDisable && (
          <button
            onClick={() => setShowDisable(true)}
            className="text-red-400 hover:text-red-300 text-sm transition-colors"
          >
            Disable Google Authenticator
          </button>
        )}

        {showDisable && (
          <div className="mt-4">
            <p className="text-gray-700 dark:text-gray-300 text-sm mb-3">
              Enter code from Google Authenticator to disable:
            </p>
            <Input
              value={disableToken}
              onChange={setDisableToken}
              placeholder="Enter 6-digit code"
            />
            <div className="flex gap-3 mt-3">
              <Button
                onClick={handleDisableTOTP}
                disabled={isLoading}
                className="bg-red-600 hover:bg-red-700"
              >
                {isLoading ? 'Disabling...' : 'Disable'}
              </Button>
              <button
                onClick={() => { setShowDisable(false); setDisableToken('') }}
                className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-sm transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* App Info */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 mt-4">
        <h2 className="text-gray-900 dark:text-white font-semibold mb-4">App Info</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Version</span>
            <span className="text-gray-900 dark:text-white">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Backend</span>
            <span className="text-gray-900 dark:text-white">Django 6.0.4</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">AI Model</span>
            <span className="text-gray-900 dark:text-white">Groq LLaMA</span>
          </div>
        </div>
      </div>
    </div>
  )
}
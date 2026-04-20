import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../services/api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export const ProfilePage = () => {
  const { user, setAuth, refreshToken, accessToken } = useAuthStore()
  const [email, setEmail] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  // Fetch fresh profile data on load
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const freshUser = await authAPI.profile()
        setEmail(freshUser.email || '')
        setFirstName(freshUser.first_name || '')
        setLastName(freshUser.last_name || '')
        setAuth(freshUser, accessToken!, refreshToken!)
      } catch (err) {
        console.error('Error fetching profile:', err)
      } finally {
        setIsFetching(false)
      }
    }
    fetchProfile()
  }, [])

  const handleUpdate = async () => {
    setIsLoading(true)
    setSuccess('')
    setError('')

    try {
      const updatedUser = await authAPI.updateProfile({
        email,
        first_name: firstName,
        last_name: lastName,
      })
      setAuth(updatedUser, accessToken!, refreshToken!)
      setSuccess('Profile updated successfully!')
    } catch (err) {
      setError('Failed to update profile. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isFetching) {
    return (
      <div className="p-8 flex items-center justify-center">
        <p className="text-gray-400">Loading profile...</p>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-white text-3xl font-bold">Profile</h1>
        <p className="text-gray-400 mt-2">Manage your account settings</p>
      </div>

      {/* Avatar */}
      <div className="flex items-center gap-4 mb-8">
        <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-white text-3xl font-bold">
            {user?.username?.[0]?.toUpperCase()}
          </span>
        </div>
        <div>
          <h2 className="text-white text-xl font-bold">
            {firstName && lastName ? `${firstName} ${lastName}` : user?.username}
          </h2>
          <p className="text-gray-400">{email}</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6">
        {success && (
          <div className="bg-green-500/10 border border-green-500/50 text-green-400 px-4 py-3 rounded-lg mb-6 text-sm">
            {success}
          </div>
        )}
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
              value={user?.username || ''}
              onChange={() => {}}
              disabled={true}
              className="opacity-50"
            />
            <p className="text-gray-500 text-xs mt-1">Username cannot be changed</p>
          </div>

          <div>
            <label className="text-gray-300 text-sm font-medium mb-2 block">
              Email
            </label>
            <Input
              value={email}
              onChange={setEmail}
              placeholder="Enter your email"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                First Name
              </label>
              <Input
                value={firstName}
                onChange={setFirstName}
                placeholder="First name"
              />
            </div>
            <div>
              <label className="text-gray-300 text-sm font-medium mb-2 block">
                Last Name
              </label>
              <Input
                value={lastName}
                onChange={setLastName}
                placeholder="Last name"
              />
            </div>
          </div>
        </div>

        <Button
          onClick={handleUpdate}
          disabled={isLoading}
          className="mt-6"
        >
          {isLoading ? 'Updating...' : 'Update Profile'}
        </Button>
      </div>
    </div>
  )
}
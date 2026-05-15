interface PasswordStrengthProps {
  password: string
}

export const PasswordStrength = ({ password }: PasswordStrengthProps) => {
  const calculateStrength = (pwd: string): { score: number; label: string; color: string } => {
    let score = 0
    
    if (pwd.length === 0) return { score: 0, label: '', color: '' }
    
    // Length
    if (pwd.length >= 8) score++
    if (pwd.length >= 12) score++
    
    // Character types
    if (/[a-z]/.test(pwd)) score++  // lowercase
    if (/[A-Z]/.test(pwd)) score++  // uppercase
    if (/[0-9]/.test(pwd)) score++  // numbers
    if (/[^a-zA-Z0-9]/.test(pwd)) score++  // special chars
    
    // Determine strength
    if (score <= 2) return { score: 1, label: 'Weak', color: 'bg-red-500' }
    if (score <= 4) return { score: 2, label: 'Fair', color: 'bg-yellow-500' }
    if (score <= 5) return { score: 3, label: 'Good', color: 'bg-blue-500' }
    return { score: 4, label: 'Strong', color: 'bg-green-500' }
  }
  
  const { score, label, color } = calculateStrength(password)
  
  if (!password) return null
  
  return (
    <div className="mt-2">
      <div className="flex gap-1 mb-1">
        {[1, 2, 3, 4].map((level) => (
          <div
            key={level}
            className={`h-1 flex-1 rounded-full transition-colors ${
              level <= score ? color : 'bg-gray-700'
            }`}
          />
        ))}
      </div>
      <p className="text-xs text-gray-400">
        Password strength: <span className={`font-medium ${
          score === 1 ? 'text-red-400' :
          score === 2 ? 'text-yellow-400' :
          score === 3 ? 'text-blue-400' :
          'text-green-400'
        }`}>{label}</span>
      </p>
    </div>
  )
}
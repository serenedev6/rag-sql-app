interface InputProps {
  value: string
  onChange: (value: string) => void
  onKeyPress?: (e: React.KeyboardEvent) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export const Input = ({
  value,
  onChange,
  onKeyPress,
  placeholder,
  disabled,
  className = '',
}: InputProps) => {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyPress={onKeyPress}
      placeholder={placeholder}
      disabled={disabled}
      className={`
        w-full px-4 py-3 rounded-lg
        bg-gray-800 border border-gray-700
        text-white placeholder-gray-500
        focus:outline-none focus:border-blue-500
        disabled:opacity-50 disabled:cursor-not-allowed
        transition-colors duration-200
        ${className}
      `}
    />
  )
}
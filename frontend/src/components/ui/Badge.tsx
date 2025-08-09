interface BadgeProps {
  variant?: 'success' | 'warning' | 'error' | 'default'
  children: React.ReactNode
  className?: string
}

function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  const variants = {
    success: 'bg-success-100 text-success-700',
    warning: 'bg-warning-100 text-warning-700',
    error: 'bg-error-100 text-error-700',
    default: 'bg-gray-100 text-gray-700'
  }

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  )
}

export default Badge
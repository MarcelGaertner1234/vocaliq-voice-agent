import type { InputHTMLAttributes } from 'react'
import { forwardRef } from 'react'

const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className = '', type = 'text', ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={`
          w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
          placeholder-gray-400 focus:outline-none focus:ring-2 
          focus:ring-primary-500 focus:border-primary-500
          disabled:bg-gray-50 disabled:text-gray-500
          ${className}
        `}
        {...props}
      />
    )
  }
)

Input.displayName = 'Input'

export default Input
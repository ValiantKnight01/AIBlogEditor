import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Card } from '@/components/ui/card'
import { LoginCredentials, RegisterCredentials } from '@/services/auth'

interface AuthFormsProps {
  onLogin: (credentials: LoginCredentials) => Promise<void>
  onRegister: (credentials: RegisterCredentials) => Promise<void>
}

// Validation schemas
const loginSchema = z.object({
  email: z.string().email('Invalid email format').min(1, 'Email is required'),
  password: z.string().min(1, 'Password is required'),
})

const registerSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters').min(1, 'Username is required'),
  email: z.string().email('Invalid email format').min(1, 'Email is required'),
  password: z.string().min(6, 'Password must be at least 6 characters').min(1, 'Password is required'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
})

type LoginFormData = z.infer<typeof loginSchema>
type RegisterFormData = z.infer<typeof registerSchema>

export const AuthForms: React.FC<AuthFormsProps> = ({ onLogin, onRegister }) => {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login')
  const [isLoading, setIsLoading] = useState(false)

  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const registerForm = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const handleLogin = async (data: LoginFormData) => {
    setIsLoading(true)
    try {
      await onLogin(data)
    } catch (error) {
      loginForm.setError('root', {
        message: error instanceof Error ? error.message : 'Login failed'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegister = async (data: RegisterFormData) => {
    setIsLoading(true)
    try {
      await onRegister(data)
    } catch (error) {
      registerForm.setError('root', {
        message: error instanceof Error ? error.message : 'Registration failed'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const InputField: React.FC<{
    label: string
    name: string
    type?: string
    form: any
    placeholder?: string
  }> = ({ label, name, type = 'text', form, placeholder }) => {
    const error = form.formState.errors[name]
    
    return (
      <div>
        <label htmlFor={name} className="block text-sm font-medium text-gray-700">
          {label}
        </label>
        <input
          id={name}
          type={type}
          placeholder={placeholder}
          {...form.register(name)}
          className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
            error ? 'border-red-300' : 'border-gray-300'
          }`}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600">{error.message}</p>
        )}
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto">
      <Card className="p-6">
        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
          <button
            role="tab"
            onClick={() => setActiveTab('login')}
            className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'login'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Sign In
          </button>
          <button
            role="tab"
            onClick={() => setActiveTab('register')}
            className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'register'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Register
          </button>
        </div>

        {/* Login Form */}
        {activeTab === 'login' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>
            <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-6">
              <InputField
                label="Email"
                name="email"
                type="email"
                form={loginForm}
                placeholder="Enter your email"
              />
              
              <InputField
                label="Password"
                name="password"
                type="password"
                form={loginForm}
                placeholder="Enter your password"
              />

              {loginForm.formState.errors.root && (
                <div className="text-red-600 text-sm">
                  {loginForm.formState.errors.root.message}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Signing In...' : 'Sign In'}
              </button>
            </form>
          </div>
        )}

        {/* Register Form */}
        {activeTab === 'register' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Account</h2>
            <form onSubmit={registerForm.handleSubmit(handleRegister)} className="space-y-6">
              <InputField
                label="Username"
                name="username"
                form={registerForm}
                placeholder="Choose a username"
              />
              
              <InputField
                label="Email"
                name="email"
                type="email"
                form={registerForm}
                placeholder="Enter your email"
              />
              
              <InputField
                label="Password"
                name="password"
                type="password"
                form={registerForm}
                placeholder="Create a password"
              />
              
              <InputField
                label="Confirm Password"
                name="confirmPassword"
                type="password"
                form={registerForm}
                placeholder="Confirm your password"
              />

              {registerForm.formState.errors.root && (
                <div className="text-red-600 text-sm">
                  {registerForm.formState.errors.root.message}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </button>
            </form>
          </div>
        )}

        {/* Additional Links */}
        <div className="mt-6 text-center">
          <div className="text-sm text-gray-500">
            {activeTab === 'login' ? (
              <>
                Don't have an account?{' '}
                <button
                  onClick={() => setActiveTab('register')}
                  className="font-medium text-indigo-600 hover:text-indigo-500 transition-colors"
                >
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <button
                  onClick={() => setActiveTab('login')}
                  className="font-medium text-indigo-600 hover:text-indigo-500 transition-colors"
                >
                  Sign in
                </button>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
}

export default AuthForms
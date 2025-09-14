import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '@/services/auth'
import { AuthForms } from '@/components/AuthForms'
import { LoginCredentials, RegisterCredentials } from '@/services/auth'

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login, register, isAuthenticated } = useAuth()

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const redirectTo = searchParams.get('redirect') || '/admin'
      navigate(redirectTo, { replace: true })
    }
  }, [isAuthenticated, navigate, searchParams])

  const handleLogin = async (credentials: LoginCredentials) => {
    try {
      await login(credentials)
      // Navigation will be handled by useEffect when isAuthenticated changes
    } catch (error) {
      // Error handling is done in AuthForms component
      throw error
    }
  }

  const handleRegister = async (credentials: RegisterCredentials) => {
    try {
      await register(credentials)
      // Navigation will be handled by useEffect when isAuthenticated changes
    } catch (error) {
      // Error handling is done in AuthForms component  
      throw error
    }
  }

  // Don't render if already authenticated (prevents flash)
  if (isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome Back
          </h1>
          <p className="text-slate-300">
            Sign in to access your personal blog dashboard
          </p>
        </div>

        {/* Login Form */}
        <AuthForms 
          onLogin={handleLogin}
          onRegister={handleRegister}
        />

        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-slate-800/50 rounded-lg backdrop-blur-sm border border-slate-700">
          <h3 className="text-sm font-medium text-slate-300 mb-2">Demo Credentials:</h3>
          <div className="text-xs text-slate-400 space-y-1">
            <div><strong>Email:</strong> test@example.com</div>
            <div><strong>Password:</strong> TestP@ss_w0rd!</div>
          </div>
        </div>

        {/* Back to Blog Link */}
        <div className="mt-6 text-center">
          <a 
            href="/"
            className="text-slate-400 hover:text-white text-sm transition-colors"
          >
            ← Back to Blog
          </a>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
import React, { createContext, useContext, useState, useEffect } from 'react'
import { login as apiLogin, logout as apiLogout, getCurrentUser, User } from './api'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
  confirmPassword: string
}

export interface AuthResponse {
  accessToken: string
  refreshToken: string
  user: User
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<AuthResponse>
  logout: () => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<AuthResponse>
}

const AuthContext = createContext<AuthContextType | null>(null)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Load user on mount if token exists
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('accessToken')
      if (token) {
        try {
          const userData = await getCurrentUser()
          setUser(userData)
        } catch (error) {
          // Token might be expired or invalid
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          console.warn('Failed to load user, token may be expired:', error)
        }
      }
      setIsLoading(false)
    }

    loadUser()
  }, [])

  const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      const response = await apiLogin(credentials.email, credentials.password)
      
      // Store tokens
      localStorage.setItem('accessToken', response.accessToken)
      localStorage.setItem('refreshToken', response.refreshToken)
      
      // Update state
      setUser(response.user)
      
      return response
    } catch (error) {
      throw new Error('Invalid credentials')
    }
  }

  const logout = async (): Promise<void> => {
    try {
      await apiLogout()
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error)
    } finally {
      // Clear local storage and user state
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      setUser(null)
    }
  }

  const register = async (credentials: RegisterCredentials): Promise<AuthResponse> => {
    if (credentials.password !== credentials.confirmPassword) {
      throw new Error('Passwords do not match')
    }

    // For now, registration would use a separate API endpoint
    // This is a placeholder implementation for single-user blog
    throw new Error('This is a personal blog. Please use the existing admin credentials.')
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user && !!localStorage.getItem('accessToken'),
    isLoading,
    login,
    logout,
    register,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// React hooks for auth state
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Legacy service for backward compatibility
class AuthService {
  private user: User | null = null

  constructor() {
    // Initialize user from localStorage if token exists
    const token = localStorage.getItem('accessToken')
    if (token) {
      this.loadUser()
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiLogin(credentials.email, credentials.password)
      
      // Store tokens
      localStorage.setItem('accessToken', response.accessToken)
      localStorage.setItem('refreshToken', response.refreshToken)
      
      // Store user
      this.user = response.user
      
      return response
    } catch (error) {
      throw new Error('Invalid credentials')
    }
  }

  async logout(): Promise<void> {
    try {
      await apiLogout()
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error)
    } finally {
      // Clear local storage and user state
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      this.user = null
    }
  }

  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    if (credentials.password !== credentials.confirmPassword) {
      throw new Error('Passwords do not match')
    }

    // For now, registration would use a separate API endpoint
    // This is a placeholder implementation
    throw new Error('Registration not implemented yet')
  }

  async loadUser(): Promise<User | null> {
    try {
      const user = await getCurrentUser()
      this.user = user
      return user
    } catch (error) {
      // Token might be expired or invalid
      this.logout()
      return null
    }
  }

  getCurrentUser(): User | null {
    return this.user
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('accessToken') && !!this.user
  }

  getToken(): string | null {
    return localStorage.getItem('accessToken')
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refreshToken')
  }

  // Token refresh logic (placeholder)
  async refreshToken(): Promise<string | null> {
    const refreshToken = this.getRefreshToken()
    if (!refreshToken) {
      return null
    }

    try {
      // This would call a refresh endpoint
      // For now, just return the existing token
      return this.getToken()
    } catch (error) {
      // If refresh fails, logout user
      await this.logout()
      return null
    }
  }
}

// Create singleton instance
export const authService = new AuthService()

export default authService
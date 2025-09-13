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

// React hooks for auth state
export const useAuth = () => {
  return {
    user: authService.getCurrentUser(),
    isAuthenticated: authService.isAuthenticated(),
    login: authService.login.bind(authService),
    logout: authService.logout.bind(authService),
    register: authService.register.bind(authService),
  }
}

export default authService
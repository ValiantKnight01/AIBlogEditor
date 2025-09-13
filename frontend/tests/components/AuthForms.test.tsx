import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthForms } from '@/components/AuthForms'

const mockOnLogin = vi.fn()
const mockOnRegister = vi.fn()

describe('AuthForms', () => {
  beforeEach(() => {
    mockOnLogin.mockClear()
    mockOnRegister.mockClear()
  })

  describe('Login Form', () => {
    it('should render login form by default', () => {
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    })

    it('should submit login form with valid data', async () => {
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.type(screen.getByLabelText(/email/i), 'test@example.com')
      await user.type(screen.getByLabelText(/password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(mockOnLogin).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123'
        })
      })
    })

    it('should show validation errors for empty login form', async () => {
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument()
        expect(screen.getByText(/password is required/i)).toBeInTheDocument()
      })
      expect(mockOnLogin).not.toHaveBeenCalled()
    })

    it('should show validation error for invalid email format', async () => {
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.type(screen.getByLabelText(/email/i), 'invalid-email')
      await user.type(screen.getByLabelText(/password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/invalid email format/i)).toBeInTheDocument()
      })
      expect(mockOnLogin).not.toHaveBeenCalled()
    })
  })

  describe('Register Form', () => {
    it('should switch to register form when clicking register tab', async () => {
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.click(screen.getByRole('tab', { name: /register/i }))
      
      expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
    })

    it('should submit register form with valid data', async () => {
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.click(screen.getByRole('tab', { name: /register/i }))
      
      await user.type(screen.getByLabelText(/username/i), 'testuser')
      await user.type(screen.getByLabelText(/email/i), 'test@example.com')
      await user.type(screen.getByLabelText(/password/i), 'password123')
      await user.type(screen.getByLabelText(/confirm password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(mockOnRegister).toHaveBeenCalledWith({
          username: 'testuser',
          email: 'test@example.com',
          password: 'password123',
          confirmPassword: 'password123'
        })
      })
    })

    it('should show validation errors for empty register form', async () => {
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.click(screen.getByRole('tab', { name: /register/i }))
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/username is required/i)).toBeInTheDocument()
        expect(screen.getByText(/email is required/i)).toBeInTheDocument()
        expect(screen.getByText(/password is required/i)).toBeInTheDocument()
      })
      expect(mockOnRegister).not.toHaveBeenCalled()
    })

    it('should show validation error for password mismatch', async () => {
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.click(screen.getByRole('tab', { name: /register/i }))
      
      await user.type(screen.getByLabelText(/username/i), 'testuser')
      await user.type(screen.getByLabelText(/email/i), 'test@example.com')
      await user.type(screen.getByLabelText(/password/i), 'password123')
      await user.type(screen.getByLabelText(/confirm password/i), 'differentpassword')
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
      })
      expect(mockOnRegister).not.toHaveBeenCalled()
    })
  })

  describe('Form Loading States', () => {
    it('should show loading state during login submission', async () => {
      mockOnLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)))
      
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.type(screen.getByLabelText(/email/i), 'test@example.com')
      await user.type(screen.getByLabelText(/password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /signing in/i })).toBeDisabled()
    })

    it('should show loading state during register submission', async () => {
      mockOnRegister.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)))
      
      const user = userEvent.setup()
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      await user.click(screen.getByRole('tab', { name: /register/i }))
      await user.type(screen.getByLabelText(/username/i), 'testuser')
      await user.type(screen.getByLabelText(/email/i), 'test@example.com')
      await user.type(screen.getByLabelText(/password/i), 'password123')
      await user.type(screen.getByLabelText(/confirm password/i), 'password123')
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      expect(screen.getByRole('button', { name: /creating account/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /creating account/i })).toBeDisabled()
    })
  })

  describe('Form Styling', () => {
    it('should render with proper form styling', () => {
      const { container } = render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      const form = container.querySelector('form')
      expect(form).toHaveClass('space-y-6')
    })

    it('should have proper input styling', () => {
      render(<AuthForms onLogin={mockOnLogin} onRegister={mockOnRegister} />)
      
      const emailInput = screen.getByLabelText(/email/i)
      expect(emailInput).toHaveClass('block', 'w-full', 'rounded-md', 'border-gray-300')
    })
  })
})
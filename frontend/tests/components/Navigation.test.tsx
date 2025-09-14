import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Navigation } from '@/components/Navigation'

// Mock user data
const mockUser = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  bio: 'Test user bio',
  profileImageUrl: null,
  isActive: true,
  createdAt: '2024-01-01T00:00:00Z',
}

// Wrapper component to provide router context
const RouterWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
)

describe('Navigation', () => {
  it('should render main navigation links', () => {
    render(
      <RouterWrapper>
        <Navigation user={null} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /blog/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /projects/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /about/i })).toBeInTheDocument()
  })

  it('should show login link when user is not authenticated', () => {
    render(
      <RouterWrapper>
        <Navigation user={null} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument()
  })

  it('should show user menu when user is authenticated', () => {
    render(
      <RouterWrapper>
        <Navigation user={mockUser} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    expect(screen.getByText(mockUser.username)).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /login/i })).not.toBeInTheDocument()
  })

  it('should show dashboard link for authenticated users', () => {
    render(
      <RouterWrapper>
        <Navigation user={mockUser} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    // Click on user menu to open dropdown
    const userMenuButton = screen.getByRole('button', { name: mockUser.username })
    fireEvent.click(userMenuButton)
    
    expect(screen.getByRole('link', { name: /dashboard/i })).toBeInTheDocument()
  })

  it('should show profile link for authenticated users', () => {
    render(
      <RouterWrapper>
        <Navigation user={mockUser} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    // Click on user menu to open dropdown
    const userMenuButton = screen.getByRole('button', { name: mockUser.username })
    fireEvent.click(userMenuButton)
    
    expect(screen.getByRole('link', { name: /profile/i })).toBeInTheDocument()
  })

  it('should call onLogout when logout is clicked', () => {
    const mockOnLogout = vi.fn()
    render(
      <RouterWrapper>
        <Navigation user={mockUser} onLogout={mockOnLogout} />
      </RouterWrapper>
    )
    
    // Click on user menu to open dropdown
    const userMenuButton = screen.getByRole('button', { name: mockUser.username })
    fireEvent.click(userMenuButton)
    
    // Click logout button
    const logoutButton = screen.getByRole('button', { name: /logout/i })
    fireEvent.click(logoutButton)
    
    expect(mockOnLogout).toHaveBeenCalledOnce()
  })

  it('should have proper navigation links with correct hrefs', () => {
    render(
      <RouterWrapper>
        <Navigation user={null} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    expect(screen.getByRole('link', { name: /home/i })).toHaveAttribute('href', '/')
    expect(screen.getByRole('link', { name: /blog/i })).toHaveAttribute('href', '/blog')
    expect(screen.getByRole('link', { name: /projects/i })).toHaveAttribute('href', '/projects')
    expect(screen.getByRole('link', { name: /about/i })).toHaveAttribute('href', '/about')
  })

  it('should be responsive with mobile menu toggle', () => {
    render(
      <RouterWrapper>
        <Navigation user={null} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    // Mobile menu button should be present (usually hidden on desktop)
    const mobileMenuButton = screen.getByRole('button', { name: /toggle menu/i })
    expect(mobileMenuButton).toBeInTheDocument()
  })

  it('should toggle mobile menu when mobile toggle is clicked', () => {
    render(
      <RouterWrapper>
        <Navigation user={null} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    const mobileMenuButton = screen.getByRole('button', { name: /toggle menu/i })
    
    // Mobile menu should initially be hidden
    const mobileNav = screen.getByTestId('mobile-nav')
    expect(mobileNav).toHaveClass('hidden')
    
    // Click to open mobile menu
    fireEvent.click(mobileMenuButton)
    expect(mobileNav).not.toHaveClass('hidden')
    
    // Click again to close mobile menu
    fireEvent.click(mobileMenuButton)
    expect(mobileNav).toHaveClass('hidden')
  })

  it('should render with proper styling classes', () => {
    const { container } = render(
      <RouterWrapper>
        <Navigation user={null} onLogout={vi.fn()} />
      </RouterWrapper>
    )
    
    const nav = container.querySelector('nav')
    expect(nav).toHaveClass('bg-white', 'border-b')
  })
})
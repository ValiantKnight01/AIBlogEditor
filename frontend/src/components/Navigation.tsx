import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ThemeToggle } from '@/components/ThemeToggle'

interface NavigationProps {
  user?: { username: string; email: string } | null
  onLogout: () => void
}

export const Navigation: React.FC<NavigationProps> = ({ user, onLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const location = useLocation()

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen)
  const toggleUserMenu = () => setIsUserMenuOpen(!isUserMenuOpen)

  const isActive = (path: string) => location.pathname === path

  const NavLink: React.FC<{ to: string; children: React.ReactNode }> = ({ to, children }) => (
    <Link
      to={to}
      className={`transition-colors hover:text-foreground/80 ${
        isActive(to) ? 'text-foreground' : 'text-foreground/60'
      }`}
    >
      {children}
    </Link>
  )

  const MobileNavLink: React.FC<{ to: string; children: React.ReactNode }> = ({ to, children }) => (
    <Link
      to={to}
      className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
        isActive(to)
          ? 'bg-primary/10 text-primary'
          : 'text-foreground/60 hover:text-foreground hover:bg-muted'
      }`}
      onClick={() => setIsMenuOpen(false)}
    >
      {children}
    </Link>
  )

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container flex h-14 items-center justify-between">
        {/* Logo/Brand */}
        <div className="flex-shrink-0">
          <Link to="/" className="flex items-center space-x-2 font-bold">
            <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">B</span>
            </div>
            <span className="text-xl text-foreground">My Blog</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-6">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/blog">Blog</NavLink>
          <NavLink to="/projects">Projects</NavLink>
          <NavLink to="/about">About</NavLink>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* User Menu */}
          {user ? (
            <div className="relative">
              <button
                onClick={toggleUserMenu}
                className="flex items-center space-x-3 text-sm font-medium text-foreground/80 hover:text-foreground transition-colors"
              >
                <div className="h-8 w-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <span className="text-primary font-medium">
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
                <span>{user.username}</span>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* User Dropdown Menu */}
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-popover border rounded-md shadow-lg z-50">
                  <div className="py-1">
                    <Link
                      to="/admin/dashboard"
                      className="block px-4 py-2 text-sm text-popover-foreground hover:bg-muted transition-colors"
                      onClick={() => setIsUserMenuOpen(false)}
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="/admin/profile"
                      className="block px-4 py-2 text-sm text-popover-foreground hover:bg-muted transition-colors"
                      onClick={() => setIsUserMenuOpen(false)}
                    >
                      Profile
                    </Link>
                    <div className="border-t my-1"></div>
                    <button
                      onClick={() => {
                        onLogout()
                        setIsUserMenuOpen(false)
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-popover-foreground hover:bg-muted transition-colors"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link
              to="/login"
              className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-primary-foreground bg-primary hover:bg-primary/90 rounded-md transition-colors"
            >
              Login
            </Link>
          )}
        </div>

        {/* Mobile menu button */}
        <div className="md:hidden">
          <button
            onClick={toggleMenu}
            className="inline-flex items-center justify-center p-2 rounded-md text-foreground/60 hover:text-foreground hover:bg-muted transition-colors"
            aria-expanded="false"
            data-testid="mobile-menu-button"
          >
            <span className="sr-only">Open main menu</span>
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      <div className={`md:hidden ${isMenuOpen ? 'block' : 'hidden'}`} data-testid="mobile-nav">
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-background border-t">
          <MobileNavLink to="/">Home</MobileNavLink>
          <MobileNavLink to="/blog">Blog</MobileNavLink>
          <MobileNavLink to="/projects">Projects</MobileNavLink>
          <MobileNavLink to="/about">About</MobileNavLink>
          
          {user ? (
            <>
              <div className="border-t pt-4 pb-3 mt-3">
                <div className="flex items-center px-3 mb-3">
                  <div className="h-8 w-8 bg-primary/10 rounded-full flex items-center justify-center">
                    <span className="text-primary font-medium">
                      {user.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="ml-3">
                    <div className="text-base font-medium text-foreground">{user.username}</div>
                    <div className="text-sm text-muted-foreground">{user.email}</div>
                  </div>
                </div>
                <MobileNavLink to="/admin/dashboard">Dashboard</MobileNavLink>
                <MobileNavLink to="/admin/profile">Profile</MobileNavLink>
                <button
                  onClick={() => {
                    onLogout()
                    setIsMenuOpen(false)
                  }}
                  className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-foreground/60 hover:text-foreground hover:bg-muted transition-colors"
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <div className="border-t pt-4 pb-3 mt-3">
              <Link
                to="/login"
                className="block mx-3 text-center bg-primary text-primary-foreground px-4 py-2 rounded-md text-base font-medium hover:bg-primary/90 transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Login
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Click outside to close menus */}
      {(isMenuOpen || isUserMenuOpen) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setIsMenuOpen(false)
            setIsUserMenuOpen(false)
          }}
        />
      )}
    </nav>
  )
}

export default Navigation
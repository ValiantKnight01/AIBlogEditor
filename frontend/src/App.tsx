import React from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/services/auth'
import { Navigation } from '@/components/Navigation'
import { HomePage } from '@/pages/HomePage'
import { BlogPostPage } from '@/pages/BlogPostPage'
import { ProjectPage } from '@/pages/ProjectPage'
import { AdminDashboard } from '@/pages/AdminDashboard'

// Protected Route wrapper
interface ProtectedRouteProps {
  children: React.ReactNode
  requireAuth?: boolean
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireAuth = true 
}) => {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (requireAuth && !isAuthenticated) {
    // Redirect to home with return URL
    return <Navigate to={`/?redirect=${encodeURIComponent(location.pathname)}`} replace />
  }

  return <>{children}</>
}

// Blog list component (simple placeholder for now)
const BlogListPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">All Blog Posts</h1>
        <p className="text-gray-600">Blog list coming soon...</p>
      </div>
    </div>
  )
}

// Projects list component (simple placeholder for now)
const ProjectListPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">All Projects</h1>
        <p className="text-gray-600">Projects list coming soon...</p>
      </div>
    </div>
  )
}

// About page
const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">About Me</h1>
        
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="prose prose-lg max-w-none">
            <p className="text-xl text-gray-600 mb-6">
              Welcome to my corner of the web! I'm a passionate developer who loves 
              building amazing digital experiences and sharing knowledge with the community.
            </p>
            
            <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">What I Do</h2>
            <p className="text-gray-700 mb-4">
              I specialize in full-stack web development with a focus on modern technologies 
              like React, Node.js, Python, and PostgreSQL. I enjoy creating clean, 
              maintainable code and building applications that solve real-world problems.
            </p>
            
            <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">My Journey</h2>
            <p className="text-gray-700 mb-4">
              My journey in software development has been driven by curiosity and a 
              desire to continuously learn. Through this blog, I share my experiences, 
              tutorials, and insights from my ongoing adventure in tech.
            </p>
            
            <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">Let's Connect</h2>
            <p className="text-gray-700 mb-4">
              I'm always excited to connect with fellow developers and tech enthusiasts. 
              Feel free to reach out if you want to collaborate, have questions about my 
              projects, or just want to chat about technology!
            </p>
            
            <div className="mt-8 flex space-x-4">
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-indigo-600 hover:text-indigo-500"
              >
                GitHub
              </a>
              <a 
                href="https://linkedin.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-indigo-600 hover:text-indigo-500"
              >
                LinkedIn
              </a>
              <a 
                href="https://twitter.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-indigo-600 hover:text-indigo-500"
              >
                Twitter
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Contact page
const ContactPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Contact Me</h1>
        
        <div className="bg-white rounded-lg shadow-sm p-8">
          <p className="text-xl text-gray-600 mb-8">
            I'd love to hear from you! Whether you have questions about my projects, 
            want to collaborate, or just want to say hello, feel free to reach out.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Get In Touch</h2>
              <div className="space-y-4">
                <div>
                  <p className="font-medium text-gray-900">Email</p>
                  <a 
                    href="mailto:hello@myblog.com" 
                    className="text-indigo-600 hover:text-indigo-500"
                  >
                    hello@myblog.com
                  </a>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Social Media</p>
                  <div className="flex space-x-4 mt-2">
                    <a 
                      href="https://github.com" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-500"
                    >
                      GitHub
                    </a>
                    <a 
                      href="https://linkedin.com" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-500"
                    >
                      LinkedIn
                    </a>
                    <a 
                      href="https://twitter.com" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:text-indigo-500"
                    >
                      Twitter
                    </a>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Links</h2>
              <div className="space-y-2">
                <div>
                  <a href="/blog" className="text-indigo-600 hover:text-indigo-500">
                    Browse my blog posts
                  </a>
                </div>
                <div>
                  <a href="/projects" className="text-indigo-600 hover:text-indigo-500">
                    Check out my projects
                  </a>
                </div>
                <div>
                  <a href="/about" className="text-indigo-600 hover:text-indigo-500">
                    Learn more about me
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 404 Not Found page
const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <h2 className="text-2xl font-bold text-gray-700 mb-4">Page Not Found</h2>
        <p className="text-gray-600 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <a 
          href="/" 
          className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
        >
          Go Home
        </a>
      </div>
    </div>
  )
}

export const App: React.FC = () => {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation user={user} onLogout={logout} />
      
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/blog" element={<BlogListPage />} />
        <Route path="/blog/:slug" element={<BlogPostPage />} />
        <Route path="/projects" element={<ProjectListPage />} />
        <Route path="/projects/:slug" element={<ProjectPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        
        {/* Protected Routes */}
        <Route 
          path="/admin" 
          element={
            <ProtectedRoute requireAuth={true}>
              <AdminDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/*" 
          element={
            <ProtectedRoute requireAuth={true}>
              <AdminDashboard />
            </ProtectedRoute>
          } 
        />
        
        {/* Fallback Route */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  )
}
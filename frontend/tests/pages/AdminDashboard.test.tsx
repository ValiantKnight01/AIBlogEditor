import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AdminDashboard } from '@/pages/AdminDashboard'

// Mock the auth context
const mockUser = {
  id: '1',
  username: 'admin',
  email: 'admin@example.com',
  bio: 'Site administrator',
  profileImageUrl: null,
  isActive: true,
  createdAt: '2024-01-01T00:00:00Z'
}

// Mock the API service
vi.mock('@/services/api', () => ({
  getMyPosts: vi.fn(() => Promise.resolve({
    posts: [
      {
        id: '1',
        title: 'Draft Post',
        slug: 'draft-post',
        status: 'draft',
        createdAt: '2024-01-15T10:00:00Z',
        viewCount: 0
      },
      {
        id: '2',
        title: 'Published Post',
        slug: 'published-post',
        status: 'published',
        createdAt: '2024-01-14T09:00:00Z',
        viewCount: 150
      }
    ],
    pagination: { page: 1, perPage: 10, total: 2, totalPages: 1 }
  })),
  getMyProjects: vi.fn(() => Promise.resolve({
    projects: [
      {
        id: '1',
        name: 'My Project',
        slug: 'my-project',
        status: 'published',
        createdAt: '2024-01-10T12:00:00Z',
        viewCount: 200
      }
    ],
    pagination: { page: 1, perPage: 10, total: 1, totalPages: 1 }
  })),
  getDashboardStats: vi.fn(() => Promise.resolve({
    totalPosts: 15,
    publishedPosts: 12,
    draftPosts: 3,
    totalProjects: 8,
    publishedProjects: 6,
    totalViews: 2450,
    thisMonthViews: 320
  })),
  createPost: vi.fn(() => Promise.resolve({
    id: '3',
    title: 'New Post',
    slug: 'new-post',
    status: 'draft'
  })),
  createProject: vi.fn(() => Promise.resolve({
    id: '2',
    name: 'New Project',
    slug: 'new-project',
    status: 'draft'
  }))
}))

// Test wrapper with necessary providers
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('AdminDashboard', () => {
  it('should render dashboard title and welcome message', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument()
    expect(screen.getByText(/welcome back, admin/i)).toBeInTheDocument()
  })

  it('should display dashboard statistics cards', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/total posts/i)).toBeInTheDocument()
      expect(screen.getByText('15')).toBeInTheDocument()
      expect(screen.getByText(/published posts/i)).toBeInTheDocument()
      expect(screen.getByText('12')).toBeInTheDocument()
      expect(screen.getByText(/draft posts/i)).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  it('should display project statistics', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/total projects/i)).toBeInTheDocument()
      expect(screen.getByText('8')).toBeInTheDocument()
      expect(screen.getByText(/published projects/i)).toBeInTheDocument()
      expect(screen.getByText('6')).toBeInTheDocument()
    })
  })

  it('should display view statistics', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/total views/i)).toBeInTheDocument()
      expect(screen.getByText('2,450')).toBeInTheDocument()
      expect(screen.getByText(/this month/i)).toBeInTheDocument()
      expect(screen.getByText('320')).toBeInTheDocument()
    })
  })

  it('should render recent posts section with proper status indicators', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /recent posts/i })).toBeInTheDocument()
      expect(screen.getByText('Draft Post')).toBeInTheDocument()
      expect(screen.getByText('Published Post')).toBeInTheDocument()
      
      // Status badges
      expect(screen.getByText(/draft/i)).toBeInTheDocument()
      expect(screen.getByText(/published/i)).toBeInTheDocument()
    })
  })

  it('should render recent projects section', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /recent projects/i })).toBeInTheDocument()
      expect(screen.getByText('My Project')).toBeInTheDocument()
    })
  })

  it('should have quick action buttons for creating new content', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    expect(screen.getByRole('button', { name: /new post/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /new project/i })).toBeInTheDocument()
  })

  it('should create new post when new post button is clicked', async () => {
    const user = userEvent.setup()
    const { createPost } = await import('@/services/api')
    
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    const newPostButton = screen.getByRole('button', { name: /new post/i })
    await user.click(newPostButton)
    
    await waitFor(() => {
      expect(createPost).toHaveBeenCalled()
    })
  })

  it('should create new project when new project button is clicked', async () => {
    const user = userEvent.setup()
    const { createProject } = await import('@/services/api')
    
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    const newProjectButton = screen.getByRole('button', { name: /new project/i })
    await user.click(newProjectButton)
    
    await waitFor(() => {
      expect(createProject).toHaveBeenCalled()
    })
  })

  it('should have navigation links to manage different content types', () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    expect(screen.getByRole('link', { name: /manage posts/i })).toHaveAttribute('href', '/admin/posts')
    expect(screen.getByRole('link', { name: /manage projects/i })).toHaveAttribute('href', '/admin/projects')
    expect(screen.getByRole('link', { name: /profile settings/i })).toHaveAttribute('href', '/admin/profile')
  })

  it('should display recent activity feed', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /recent activity/i })).toBeInTheDocument()
      expect(screen.getByText(/published post/i)).toBeInTheDocument()
      expect(screen.getByText(/created project/i)).toBeInTheDocument()
    })
  })

  it('should show loading states while fetching dashboard data', () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    expect(screen.getByText(/loading dashboard/i)).toBeInTheDocument()
  })

  it('should handle empty states when no content exists', async () => {
    const { getMyPosts, getMyProjects } = await import('@/services/api')
    vi.mocked(getMyPosts).mockResolvedValueOnce({
      posts: [],
      pagination: { page: 1, perPage: 10, total: 0, totalPages: 0 }
    })
    vi.mocked(getMyProjects).mockResolvedValueOnce({
      projects: [],
      pagination: { page: 1, perPage: 10, total: 0, totalPages: 0 }
    })
    
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/no posts yet/i)).toBeInTheDocument()
      expect(screen.getByText(/no projects yet/i)).toBeInTheDocument()
    })
  })

  it('should have responsive grid layout for dashboard cards', () => {
    const { container } = render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    const statsGrid = container.querySelector('[data-testid="stats-grid"]')
    expect(statsGrid).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4')
  })

  it('should handle edit actions for posts and projects', async () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      const editPostButtons = screen.getAllByRole('button', { name: /edit/i })
      expect(editPostButtons.length).toBeGreaterThan(0)
    })
  })

  it('should handle delete actions with confirmation', async () => {
    const user = userEvent.setup()
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    await waitFor(() => {
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      expect(deleteButtons.length).toBeGreaterThan(0)
    })
    
    const firstDeleteButton = screen.getAllByRole('button', { name: /delete/i })[0]
    await user.click(firstDeleteButton)
    
    expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument()
  })

  it('should display proper user permissions and roles', () => {
    render(
      <TestWrapper>
        <AdminDashboard user={mockUser} />
      </TestWrapper>
    )
    
    expect(screen.getByText(/administrator/i)).toBeInTheDocument()
  })

  it('should redirect unauthorized users', () => {
    const unauthorizedUser = { ...mockUser, id: null }
    
    render(
      <TestWrapper>
        <AdminDashboard user={unauthorizedUser} />
      </TestWrapper>
    )
    
    expect(screen.getByText(/access denied/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument()
  })
})
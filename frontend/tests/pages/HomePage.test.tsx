import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { HomePage } from '@/pages/HomePage'

// Mock the API service
vi.mock('@/services/api', () => ({
  getRecentPosts: vi.fn(() => Promise.resolve({
    posts: [
      {
        id: '1',
        title: 'Latest Blog Post',
        slug: 'latest-blog-post',
        excerpt: 'This is the latest blog post excerpt',
        status: 'published',
        viewCount: 120,
        createdAt: '2024-01-15T10:00:00Z',
        author: { username: 'testauthor' },
        tags: ['React', 'TypeScript']
      },
      {
        id: '2',
        title: 'Another Great Post',
        slug: 'another-great-post',
        excerpt: 'Another interesting blog post',
        status: 'published',
        viewCount: 85,
        createdAt: '2024-01-14T09:00:00Z',
        author: { username: 'testauthor' },
        tags: ['JavaScript', 'Web']
      }
    ],
    pagination: { page: 1, perPage: 6, total: 2, totalPages: 1 }
  })),
  getFeaturedProjects: vi.fn(() => Promise.resolve({
    projects: [
      {
        id: '1',
        name: 'Featured Project',
        slug: 'featured-project',
        description: 'This is a featured project description',
        status: 'published',
        demoUrl: 'https://demo.example.com',
        projectUrl: 'https://github.com/user/project',
        viewCount: 200,
        createdAt: '2024-01-10T12:00:00Z',
        creator: { username: 'testcreator' },
        tags: ['React', 'Node.js']
      }
    ],
    pagination: { page: 1, perPage: 3, total: 1, totalPages: 1 }
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

describe('HomePage', () => {
  it('should render the hero section with personal branding', async () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    // Check for hero content - personal blog branding
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
    expect(screen.getByText(/welcome to my blog/i)).toBeInTheDocument()
    expect(screen.getByText(/developer/i)).toBeInTheDocument()
  })

  it('should display a brief personal introduction', async () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    expect(screen.getByText(/passionate developer/i)).toBeInTheDocument()
    expect(screen.getByText(/sharing insights/i)).toBeInTheDocument()
  })

  it('should render recent blog posts section', async () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    expect(screen.getByRole('heading', { name: /recent posts/i })).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.getByText('Latest Blog Post')).toBeInTheDocument()
      expect(screen.getByText('Another Great Post')).toBeInTheDocument()
    })
  })

  it('should render featured projects section', async () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    expect(screen.getByRole('heading', { name: /featured projects/i })).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.getByText('Featured Project')).toBeInTheDocument()
    })
  })

  it('should have navigation links to blog and projects pages', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    expect(screen.getByRole('link', { name: /view all posts/i })).toHaveAttribute('href', '/blog')
    expect(screen.getByRole('link', { name: /view all projects/i })).toHaveAttribute('href', '/projects')
  })

  it('should display loading states while fetching data', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    // Should show loading indicators initially
    expect(screen.getByText(/loading posts/i)).toBeInTheDocument()
    expect(screen.getByText(/loading projects/i)).toBeInTheDocument()
  })

  it('should show contact/about section', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    expect(screen.getByRole('heading', { name: /get in touch/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /contact me/i })).toBeInTheDocument()
  })

  it('should be responsive with proper mobile layout', () => {
    const { container } = render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    // Check for responsive grid classes
    const postsGrid = container.querySelector('[data-testid="posts-grid"]')
    const projectsGrid = container.querySelector('[data-testid="projects-grid"]')
    
    expect(postsGrid).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-3')
    expect(projectsGrid).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-3')
  })

  it('should have proper SEO structure with meta content', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    // Check for proper heading hierarchy
    const h1Elements = screen.getAllByRole('heading', { level: 1 })
    const h2Elements = screen.getAllByRole('heading', { level: 2 })
    
    expect(h1Elements).toHaveLength(1) // Only one main heading
    expect(h2Elements.length).toBeGreaterThan(0) // Section headings
  })

  it('should handle empty states gracefully', async () => {
    // Mock empty responses
    const { getRecentPosts, getFeaturedProjects } = await import('@/services/api')
    vi.mocked(getRecentPosts).mockResolvedValueOnce({
      posts: [],
      pagination: { page: 1, perPage: 6, total: 0, totalPages: 0 }
    })
    vi.mocked(getFeaturedProjects).mockResolvedValueOnce({
      projects: [],
      pagination: { page: 1, perPage: 3, total: 0, totalPages: 0 }
    })
    
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/no posts available/i)).toBeInTheDocument()
      expect(screen.getByText(/no projects to showcase/i)).toBeInTheDocument()
    })
  })

  it('should display social media links', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    expect(screen.getByRole('link', { name: /github/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /linkedin/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /twitter/i })).toBeInTheDocument()
  })
})
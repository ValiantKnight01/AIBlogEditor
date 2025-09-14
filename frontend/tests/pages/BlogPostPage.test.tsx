import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter, MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BlogPostPage } from '@/pages/BlogPostPage'

// Mock the API service
vi.mock('@/services/api', () => ({
  getPostBySlug: vi.fn(() => Promise.resolve({
    id: '1',
    title: 'Amazing Blog Post',
    slug: 'amazing-blog-post',
    content: `# Introduction

This is a comprehensive blog post about web development. It includes various sections and detailed explanations.

## Section 1: Getting Started

Here's how you can get started with the topic.

### Code Example

\`\`\`javascript
function example() {
  console.log('Hello World');
}
\`\`\`

## Section 2: Advanced Topics

More advanced content goes here.

## Conclusion

This concludes our blog post.`,
    excerpt: 'This is an amazing blog post about web development',
    status: 'published',
    viewCount: 150,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-15T12:00:00Z',
    author: {
      id: '1',
      username: 'testauthor',
      email: 'author@example.com',
      bio: 'Experienced developer and writer',
      profileImageUrl: 'https://example.com/avatar.jpg',
      isActive: true,
      createdAt: '2024-01-01T00:00:00Z'
    },
    tags: ['React', 'JavaScript', 'Web Development', 'Tutorial']
  })),
  getRelatedPosts: vi.fn(() => Promise.resolve({
    posts: [
      {
        id: '2',
        title: 'Related Post 1',
        slug: 'related-post-1',
        excerpt: 'This is a related post',
        status: 'published',
        viewCount: 85,
        createdAt: '2024-01-12T09:00:00Z',
        author: { username: 'testauthor' },
        tags: ['React', 'JavaScript']
      },
      {
        id: '3',
        title: 'Related Post 2',
        slug: 'related-post-2',
        excerpt: 'Another related post',
        status: 'published',
        viewCount: 67,
        createdAt: '2024-01-10T14:30:00Z',
        author: { username: 'testauthor' },
        tags: ['Web Development']
      }
    ],
    pagination: { page: 1, perPage: 3, total: 2, totalPages: 1 }
  }))
}))

// Test wrapper with necessary providers
const TestWrapper = ({ children, initialEntries = ['/posts/amazing-blog-post'] }: { 
  children: React.ReactNode
  initialEntries?: string[]
}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('BlogPostPage', () => {
  it('should render the blog post title', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /amazing blog post/i })).toBeInTheDocument()
    })
  })

  it('should render the blog post content with markdown formatting', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /introduction/i })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: /section 1: getting started/i })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: /code example/i })).toBeInTheDocument()
      expect(screen.getByText(/hello world/i)).toBeInTheDocument()
    })
  })

  it('should display author information', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText('testauthor')).toBeInTheDocument()
      expect(screen.getByText('Experienced developer and writer')).toBeInTheDocument()
    })
  })

  it('should display publish date and last updated date', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/published on/i)).toBeInTheDocument()
      expect(screen.getByText(/jan 15, 2024/i)).toBeInTheDocument()
      expect(screen.getByText(/last updated/i)).toBeInTheDocument()
    })
  })

  it('should display view count', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/150 views/i)).toBeInTheDocument()
    })
  })

  it('should render all tags as clickable elements', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText('React')).toBeInTheDocument()
      expect(screen.getByText('JavaScript')).toBeInTheDocument()
      expect(screen.getByText('Web Development')).toBeInTheDocument()
      expect(screen.getByText('Tutorial')).toBeInTheDocument()
      
      // Tags should be clickable links
      expect(screen.getByRole('link', { name: 'React' })).toHaveAttribute('href', '/tags/react')
    })
  })

  it('should render related posts section', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /related posts/i })).toBeInTheDocument()
      expect(screen.getByText('Related Post 1')).toBeInTheDocument()
      expect(screen.getByText('Related Post 2')).toBeInTheDocument()
    })
  })

  it('should have proper breadcrumb navigation', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /home/i })).toHaveAttribute('href', '/')
      expect(screen.getByRole('link', { name: /blog/i })).toHaveAttribute('href', '/blog')
      expect(screen.getByText(/amazing blog post/i)).toBeInTheDocument()
    })
  })

  it('should display loading state while fetching post', () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    expect(screen.getByText(/loading post/i)).toBeInTheDocument()
  })

  it('should handle 404 error when post is not found', async () => {
    const { getPostBySlug } = await import('@/services/api')
    vi.mocked(getPostBySlug).mockRejectedValueOnce({
      response: { status: 404 }
    })
    
    render(
      <TestWrapper initialEntries={['/posts/non-existent-post']}>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /post not found/i })).toBeInTheDocument()
      expect(screen.getByText(/the post you're looking for doesn't exist/i)).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /back to blog/i })).toHaveAttribute('href', '/blog')
    })
  })

  it('should have proper reading time estimation', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/min read/i)).toBeInTheDocument()
    })
  })

  it('should have social sharing buttons', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /share on twitter/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /share on facebook/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /copy link/i })).toBeInTheDocument()
    })
  })

  it('should have proper table of contents for long posts', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /table of contents/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /introduction/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /section 1: getting started/i })).toBeInTheDocument()
    })
  })

  it('should be mobile responsive with proper typography', async () => {
    const { container } = render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      const article = container.querySelector('article')
      expect(article).toHaveClass('prose', 'prose-lg', 'max-w-none')
    })
  })

  it('should have proper meta tags for SEO', async () => {
    render(
      <TestWrapper>
        <BlogPostPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      // Check if the page sets proper document title
      expect(document.title).toContain('Amazing Blog Post')
    })
  })
})
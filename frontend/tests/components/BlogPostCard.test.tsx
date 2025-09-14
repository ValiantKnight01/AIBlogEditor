import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BlogPostCard } from '@/components/BlogPostCard'

const mockBlogPost = {
  id: '1',
  title: 'Test Blog Post Title',
  slug: 'test-blog-post-title',
  excerpt: 'This is a test excerpt for the blog post',
  status: 'published' as const,
  viewCount: 42,
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T10:30:00Z',
  author: {
    id: '1',
    username: 'testauthor',
    email: 'author@example.com',
    bio: 'Test author bio',
    profileImageUrl: null,
    isActive: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
  tags: ['React', 'TypeScript', 'Testing'],
}

describe('BlogPostCard', () => {
  it('should render blog post title', () => {
    render(<BlogPostCard post={mockBlogPost} />)
    
    expect(screen.getByRole('heading', { name: /test blog post title/i })).toBeInTheDocument()
  })

  it('should render blog post excerpt', () => {
    render(<BlogPostCard post={mockBlogPost} />)
    
    expect(screen.getByText(/this is a test excerpt/i)).toBeInTheDocument()
  })

  it('should render author information', () => {
    render(<BlogPostCard post={mockBlogPost} />)
    
    expect(screen.getByText(/by testauthor/i)).toBeInTheDocument()
  })

  it('should render publish date in readable format', () => {
    render(<BlogPostCard post={mockBlogPost} />)
    
    // Should show formatted date like "Jan 15, 2024"
    expect(screen.getByText(/jan 15, 2024/i)).toBeInTheDocument()
  })

  it('should render view count', () => {
    render(<BlogPostCard post={mockBlogPost} />)
    
    expect(screen.getByText(/42 views/i)).toBeInTheDocument()
  })

  it('should render tags as clickable elements', () => {
    render(<BlogPostCard post={mockBlogPost} />)
    
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
    expect(screen.getByText('Testing')).toBeInTheDocument()
  })

  it('should have a clickable link to the blog post detail page', () => {
    render(<BlogPostCard post={mockBlogPost} />)
    
    const link = screen.getByRole('link', { name: /read more/i })
    expect(link).toHaveAttribute('href', '/posts/test-blog-post-title')
  })

  it('should render with proper card styling and layout', () => {
    const { container } = render(<BlogPostCard post={mockBlogPost} />)
    
    const card = container.firstChild
    expect(card).toHaveClass('border', 'rounded-lg', 'p-6', 'bg-white')
  })

  it('should handle missing author gracefully', () => {
    const postWithoutAuthor = { ...mockBlogPost, author: null }
    render(<BlogPostCard post={postWithoutAuthor} />)
    
    expect(screen.queryByText(/by/i)).not.toBeInTheDocument()
  })

  it('should handle posts with no tags', () => {
    const postWithoutTags = { ...mockBlogPost, tags: [] }
    render(<BlogPostCard post={postWithoutTags} />)
    
    expect(screen.queryByText('React')).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /test blog post title/i })).toBeInTheDocument()
  })
})
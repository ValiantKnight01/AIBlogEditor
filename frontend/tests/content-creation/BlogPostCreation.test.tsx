/**
 * TDD Test Suite: Blog Post Creation Functionality
 * 
 * These tests MUST FAIL FIRST to follow TDD methodology.
 * They test the complete blog post creation flow from form submission to API integration.
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import BlogPostForm from '@/components/BlogPostForm'
import * as apiModule from '@/services/api'

// Mock the API module
vi.mock('@/services/api', () => ({
  createPost: vi.fn(),
}))

const createMockQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
}

const renderBlogPostForm = (props = {}) => {
  const defaultProps = {
    onClose: vi.fn(),
    onSuccess: vi.fn(),
  }
  const queryClient = createMockQueryClient()
  
  return render(
    <QueryClientProvider client={queryClient}>
      <BlogPostForm {...defaultProps} {...props} />
    </QueryClientProvider>
  )
}

describe('TDD: Blog Post Creation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Form Rendering and Validation', () => {
    it('should render all required form fields', () => {
      renderBlogPostForm()
      
      // These assertions MUST FAIL initially to follow TDD
      expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/excerpt/i)).toBeInTheDocument()  
      expect(screen.getByLabelText(/content/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/status/i)).toBeInTheDocument()
      expect(screen.getByText(/tags/i)).toBeInTheDocument()
    })

    it('should show validation errors for empty required fields', async () => {
      const user = userEvent.setup()
      renderBlogPostForm()
      
      const submitButton = screen.getByRole('button', { name: /create post/i })
      await user.click(submitButton)
      
      // These assertions MUST FAIL initially
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument()
        expect(screen.getByText(/content is required/i)).toBeInTheDocument()
      })
    })

    it('should validate title length constraints', async () => {
      const user = userEvent.setup()
      renderBlogPostForm()
      
      const titleInput = screen.getByLabelText(/title/i)
      const longTitle = 'a'.repeat(201) // Exceeds 200 character limit
      
      await user.type(titleInput, longTitle)
      await user.click(screen.getByRole('button', { name: /create post/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/title must be less than 200 characters/i)).toBeInTheDocument()
      })
    })
  })

  describe('Tag Management', () => {
    it('should add tags when user types and presses Enter', async () => {
      const user = userEvent.setup()
      renderBlogPostForm()
      
      const tagInput = screen.getByPlaceholderText(/add a tag/i)
      
      await user.type(tagInput, 'React')
      await user.keyboard('{Enter}')
      
      // This MUST FAIL initially
      expect(screen.getByText('React')).toBeInTheDocument()
      expect(tagInput).toHaveValue('')
    })

    it('should add tags when user clicks Add Tag button', async () => {
      const user = userEvent.setup()
      renderBlogPostForm()
      
      const tagInput = screen.getByPlaceholderText(/add a tag/i)
      const addButton = screen.getByRole('button', { name: /add tag/i })
      
      await user.type(tagInput, 'JavaScript')
      await user.click(addButton)
      
      expect(screen.getByText('JavaScript')).toBeInTheDocument()
      expect(tagInput).toHaveValue('')
    })

    it('should remove tags when user clicks X button', async () => {
      const user = userEvent.setup()
      renderBlogPostForm()
      
      const tagInput = screen.getByPlaceholderText(/add a tag/i)
      await user.type(tagInput, 'TypeScript')
      await user.keyboard('{Enter}')
      
      const removeButton = screen.getByRole('button', { name: /remove/i })
      await user.click(removeButton)
      
      expect(screen.queryByText('TypeScript')).not.toBeInTheDocument()
    })

    it('should prevent duplicate tags', async () => {
      const user = userEvent.setup()
      renderBlogPostForm()
      
      const tagInput = screen.getByPlaceholderText(/add a tag/i)
      
      await user.type(tagInput, 'Node.js')
      await user.keyboard('{Enter}')
      await user.type(tagInput, 'Node.js')
      await user.keyboard('{Enter}')
      
      const tags = screen.getAllByText('Node.js')
      expect(tags).toHaveLength(1)
    })
  })

  describe('API Integration', () => {
    it('should call createPost API with correct data structure', async () => {
      const user = userEvent.setup()
      const mockCreatePost = vi.mocked(apiModule.createPost)
      mockCreatePost.mockResolvedValueOnce({
        id: '123',
        title: 'Test Post',
        slug: 'test-post',
        content: 'Test content',
        excerpt: 'Test excerpt',
        status: 'draft',
        viewCount: 0,
        createdAt: '2023-01-01',
        updatedAt: '2023-01-01',
        author: {
          id: '456',
          username: 'testuser',
          email: 'test@example.com',
          bio: '',
          profileImageUrl: null,
          isActive: true,
          createdAt: '2023-01-01'
        },
        tags: ['React', 'TypeScript']
      })
      
      renderBlogPostForm()
      
      // Fill form
      await user.type(screen.getByLabelText(/title/i), 'Test Post')
      await user.type(screen.getByLabelText(/content/i), 'Test content')
      await user.type(screen.getByLabelText(/excerpt/i), 'Test excerpt')
      
      // Add tags
      const tagInput = screen.getByPlaceholderText(/add a tag/i)
      await user.type(tagInput, 'React')
      await user.keyboard('{Enter}')
      await user.type(tagInput, 'TypeScript')
      await user.keyboard('{Enter}')
      
      // Submit form
      await user.click(screen.getByRole('button', { name: /create post/i }))
      
      await waitFor(() => {
        expect(mockCreatePost).toHaveBeenCalledWith({
          title: 'Test Post',
          content: 'Test content',
          excerpt: 'Test excerpt',
          status: 'draft',
          tagNames: ['React', 'TypeScript']
        })
      })
    })

    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup()
      const mockCreatePost = vi.mocked(apiModule.createPost)
      mockCreatePost.mockRejectedValueOnce(new Error('Failed to create post'))
      
      renderBlogPostForm()
      
      await user.type(screen.getByLabelText(/title/i), 'Test Post')
      await user.type(screen.getByLabelText(/content/i), 'Test content')
      await user.click(screen.getByRole('button', { name: /create post/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/failed to create post/i)).toBeInTheDocument()
      })
    })

    it('should show loading state during API call', async () => {
      const user = userEvent.setup()
      const mockCreatePost = vi.mocked(apiModule.createPost)
      
      // Create a promise that we can control
      let resolvePromise: (value: any) => void
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      mockCreatePost.mockReturnValueOnce(promise)
      
      renderBlogPostForm()
      
      await user.type(screen.getByLabelText(/title/i), 'Test Post')
      await user.type(screen.getByLabelText(/content/i), 'Test content')
      
      const submitButton = screen.getByRole('button', { name: /create post/i })
      await user.click(submitButton)
      
      // Should show loading state
      expect(screen.getByText(/creating\.\.\./i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
      
      // Resolve the promise
      resolvePromise!({
        id: '123',
        title: 'Test Post',
        slug: 'test-post',
        content: 'Test content',
        excerpt: '',
        status: 'draft',
        viewCount: 0,
        createdAt: '2023-01-01',
        updatedAt: '2023-01-01',
        author: {
          id: '456',
          username: 'testuser',
          email: 'test@example.com',
          bio: '',
          profileImageUrl: null,
          isActive: true,
          createdAt: '2023-01-01'
        },
        tags: []
      })
    })

    it('should call onSuccess and onClose callbacks after successful creation', async () => {
      const user = userEvent.setup()
      const mockOnSuccess = vi.fn()
      const mockOnClose = vi.fn()
      const mockCreatePost = vi.mocked(apiModule.createPost)
      
      mockCreatePost.mockResolvedValueOnce({
        id: '123',
        title: 'Test Post',
        slug: 'test-post',
        content: 'Test content',
        excerpt: '',
        status: 'draft',
        viewCount: 0,
        createdAt: '2023-01-01',
        updatedAt: '2023-01-01',
        author: {
          id: '456',
          username: 'testuser',
          email: 'test@example.com',
          bio: '',
          profileImageUrl: null,
          isActive: true,
          createdAt: '2023-01-01'
        },
        tags: []
      })
      
      renderBlogPostForm({
        onSuccess: mockOnSuccess,
        onClose: mockOnClose
      })
      
      await user.type(screen.getByLabelText(/title/i), 'Test Post')
      await user.type(screen.getByLabelText(/content/i), 'Test content')
      await user.click(screen.getByRole('button', { name: /create post/i }))
      
      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalled()
        expect(mockOnClose).toHaveBeenCalled()
      })
    })
  })

  describe('Form Behavior', () => {
    it('should close form when Cancel button is clicked', async () => {
      const user = userEvent.setup()
      const mockOnClose = vi.fn()
      
      renderBlogPostForm({ onClose: mockOnClose })
      
      await user.click(screen.getByRole('button', { name: /cancel/i }))
      
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('should close form when X button is clicked', async () => {
      const user = userEvent.setup()
      const mockOnClose = vi.fn()
      
      renderBlogPostForm({ onClose: mockOnClose })
      
      const closeButton = screen.getByRole('button', { name: /close/i })
      await user.click(closeButton)
      
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('should have draft as default status', () => {
      renderBlogPostForm()
      
      const statusSelect = screen.getByLabelText(/status/i) as HTMLSelectElement
      expect(statusSelect.value).toBe('draft')
    })

    it('should allow changing status to published', async () => {
      const user = userEvent.setup()
      renderBlogPostForm()
      
      const statusSelect = screen.getByLabelText(/status/i)
      await user.selectOptions(statusSelect, 'published')
      
      expect(statusSelect).toHaveValue('published')
    })
  })
})
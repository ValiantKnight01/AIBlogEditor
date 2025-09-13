/**
 * TDD Test Suite: Tag Creation Functionality
 * 
 * These tests MUST FAIL FIRST to follow TDD methodology.
 * They test the complete tag creation flow from form submission to API integration.
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import TagForm from '@/components/TagForm'
import * as apiModule from '@/services/api'

// Mock the API module
vi.mock('@/services/api', () => ({
  createTag: vi.fn(),
}))

const createMockQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
}

const renderTagForm = (props = {}) => {
  const defaultProps = {
    onClose: vi.fn(),
    onSuccess: vi.fn(),
  }
  const queryClient = createMockQueryClient()
  
  return render(
    <QueryClientProvider client={queryClient}>
      <TagForm {...defaultProps} {...props} />
    </QueryClientProvider>
  )
}

describe('TDD: Tag Creation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Form Rendering and Validation', () => {
    it('should render the tag name input field', () => {
      renderTagForm()
      
      // These assertions MUST FAIL initially to follow TDD
      expect(screen.getByLabelText(/tag name/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter tag name/i)).toBeInTheDocument()
    })

    it('should show helper text about tags', () => {
      renderTagForm()
      
      expect(screen.getByText(/tags help organize and categorize/i)).toBeInTheDocument()
      expect(screen.getByText(/use descriptive names/i)).toBeInTheDocument()
    })

    it('should show validation error for empty tag name', async () => {
      const user = userEvent.setup()
      renderTagForm()
      
      const submitButton = screen.getByRole('button', { name: /create tag/i })
      await user.click(submitButton)
      
      // This assertion MUST FAIL initially
      await waitFor(() => {
        expect(screen.getByText(/tag name is required/i)).toBeInTheDocument()
      })
    })

    it('should validate tag name length constraints', async () => {
      const user = userEvent.setup()
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      const longName = 'a'.repeat(51) // Exceeds 50 character limit
      
      await user.type(nameInput, longName)
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/tag name must be less than 50 characters/i)).toBeInTheDocument()
      })
    })

    it('should validate tag name character constraints', async () => {
      const user = userEvent.setup()
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      const invalidName = 'React@#$%' // Contains invalid characters
      
      await user.type(nameInput, invalidName)
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/tag name can only contain letters, numbers/i)).toBeInTheDocument()
      })
    })

    it('should accept valid tag names with allowed characters', async () => {
      const user = userEvent.setup()
      const mockCreateTag = vi.mocked(apiModule.createTag)
      mockCreateTag.mockResolvedValueOnce({
        id: '123',
        name: 'React-Native_2023',
        slug: 'react-native-2023',
        description: '',
        postCount: 0
      })
      
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      await user.type(nameInput, 'React-Native_2023') // Valid characters
      
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
      await waitFor(() => {
        expect(mockCreateTag).toHaveBeenCalledWith({
          name: 'React-Native_2023'
        })
      })
    })
  })

  describe('API Integration', () => {
    it('should call createTag API with correct data structure', async () => {
      const user = userEvent.setup()
      const mockCreateTag = vi.mocked(apiModule.createTag)
      mockCreateTag.mockResolvedValueOnce({
        id: '123',
        name: 'TypeScript',
        slug: 'typescript',
        description: 'JavaScript with static typing',
        postCount: 0
      })
      
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      await user.type(nameInput, 'TypeScript')
      
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
      await waitFor(() => {
        expect(mockCreateTag).toHaveBeenCalledWith({
          name: 'TypeScript'
        })
      })
    })

    it('should trim whitespace from tag names', async () => {
      const user = userEvent.setup()
      const mockCreateTag = vi.mocked(apiModule.createTag)
      mockCreateTag.mockResolvedValueOnce({
        id: '123',
        name: 'JavaScript',
        slug: 'javascript',
        description: '',
        postCount: 0
      })
      
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      await user.type(nameInput, '  JavaScript  ') // With leading/trailing spaces
      
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
      await waitFor(() => {
        expect(mockCreateTag).toHaveBeenCalledWith({
          name: 'JavaScript'
        })
      })
    })

    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup()
      const mockCreateTag = vi.mocked(apiModule.createTag)
      mockCreateTag.mockRejectedValueOnce(new Error('Tag already exists'))
      
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      await user.type(nameInput, 'React')
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/tag already exists/i)).toBeInTheDocument()
      })
    })

    it('should show loading state during API call', async () => {
      const user = userEvent.setup()
      const mockCreateTag = vi.mocked(apiModule.createTag)
      
      // Create a promise that we can control
      let resolvePromise: (value: any) => void
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      mockCreateTag.mockReturnValueOnce(promise)
      
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      await user.type(nameInput, 'Vue.js')
      
      const submitButton = screen.getByRole('button', { name: /create tag/i })
      await user.click(submitButton)
      
      // Should show loading state
      expect(screen.getByText(/creating\.\.\./i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
      
      // Resolve the promise
      resolvePromise!({
        id: '123',
        name: 'Vue.js',
        slug: 'vue-js',
        description: '',
        postCount: 0
      })
    })

    it('should call onSuccess and onClose callbacks after successful creation', async () => {
      const user = userEvent.setup()
      const mockOnSuccess = vi.fn()
      const mockOnClose = vi.fn()
      const mockCreateTag = vi.mocked(apiModule.createTag)
      
      mockCreateTag.mockResolvedValueOnce({
        id: '123',
        name: 'Angular',
        slug: 'angular',
        description: '',
        postCount: 0
      })
      
      renderTagForm({
        onSuccess: mockOnSuccess,
        onClose: mockOnClose
      })
      
      const nameInput = screen.getByLabelText(/tag name/i)
      await user.type(nameInput, 'Angular')
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
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
      
      renderTagForm({ onClose: mockOnClose })
      
      await user.click(screen.getByRole('button', { name: /cancel/i }))
      
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('should close form when X button is clicked', async () => {
      const user = userEvent.setup()
      const mockOnClose = vi.fn()
      
      renderTagForm({ onClose: mockOnClose })
      
      const closeButton = screen.getByRole('button', { name: /close/i })
      await user.click(closeButton)
      
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('should clear form after successful submission', async () => {
      const user = userEvent.setup()
      const mockCreateTag = vi.mocked(apiModule.createTag)
      mockCreateTag.mockResolvedValueOnce({
        id: '123',
        name: 'Svelte',
        slug: 'svelte',
        description: '',
        postCount: 0
      })
      
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      await user.type(nameInput, 'Svelte')
      
      expect(nameInput).toHaveValue('Svelte')
      
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
      // Form should be cleared after successful submission
      await waitFor(() => {
        expect(nameInput).toHaveValue('')
      })
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      renderTagForm()
      
      const nameInput = screen.getByLabelText(/tag name/i)
      expect(nameInput).toHaveAttribute('id', 'name')
      
      const label = screen.getByText('Tag Name')
      expect(label).toHaveAttribute('for', 'name')
    })

    it('should show error messages with proper semantics', async () => {
      const user = userEvent.setup()
      renderTagForm()
      
      await user.click(screen.getByRole('button', { name: /create tag/i }))
      
      await waitFor(() => {
        const errorMessage = screen.getByText(/tag name is required/i)
        expect(errorMessage).toHaveClass('text-red-600')
      })
    })
  })
})
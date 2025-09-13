/**
 * TDD Test Suite: Project Creation Functionality
 * 
 * These tests MUST FAIL FIRST to follow TDD methodology.
 * They test the complete project creation flow from form submission to API integration.
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ProjectForm from '@/components/ProjectForm'
import * as apiModule from '@/services/api'

// Mock the API module
vi.mock('@/services/api', () => ({
  createProject: vi.fn(),
}))

const createMockQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
}

const renderProjectForm = (props = {}) => {
  const defaultProps = {
    onClose: vi.fn(),
    onSuccess: vi.fn(),
  }
  const queryClient = createMockQueryClient()
  
  return render(
    <QueryClientProvider client={queryClient}>
      <ProjectForm {...defaultProps} {...props} />
    </QueryClientProvider>
  )
}

describe('TDD: Project Creation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Form Rendering and Validation', () => {
    it('should render all required form fields', () => {
      renderProjectForm()
      
      // These assertions MUST FAIL initially to follow TDD
      expect(screen.getByLabelText(/project name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/live demo url/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/github url/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/status/i)).toBeInTheDocument()
      expect(screen.getByText(/technologies & tags/i)).toBeInTheDocument()
    })

    it('should show validation errors for empty required fields', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const submitButton = screen.getByRole('button', { name: /create project/i })
      await user.click(submitButton)
      
      // These assertions MUST FAIL initially
      await waitFor(() => {
        expect(screen.getByText(/project name is required/i)).toBeInTheDocument()
        expect(screen.getByText(/description is required/i)).toBeInTheDocument()
      })
    })

    it('should validate project name length constraints', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const nameInput = screen.getByLabelText(/project name/i)
      const longName = 'a'.repeat(201) // Exceeds 200 character limit
      
      await user.type(nameInput, longName)
      await user.click(screen.getByRole('button', { name: /create project/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/name must be less than 200 characters/i)).toBeInTheDocument()
      })
    })

    it('should validate URL formats', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const projectUrlInput = screen.getByLabelText(/live demo url/i)
      const githubUrlInput = screen.getByLabelText(/github url/i)
      
      await user.type(screen.getByLabelText(/project name/i), 'Test Project')
      await user.type(screen.getByLabelText(/description/i), 'Test description')
      await user.type(projectUrlInput, 'invalid-url')
      await user.type(githubUrlInput, 'also-invalid')
      
      await user.click(screen.getByRole('button', { name: /create project/i }))
      
      await waitFor(() => {
        expect(screen.getAllByText(/must be a valid url/i)).toHaveLength(2)
      })
    })
  })

  describe('Tag Management', () => {
    it('should add technology tags when user types and presses Enter', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const tagInput = screen.getByPlaceholderText(/add a technology/i)
      
      await user.type(tagInput, 'React')
      await user.keyboard('{Enter}')
      
      // This MUST FAIL initially
      expect(screen.getByText('React')).toBeInTheDocument()
      expect(tagInput).toHaveValue('')
    })

    it('should add tags when user clicks Add Tag button', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const tagInput = screen.getByPlaceholderText(/add a technology/i)
      const addButton = screen.getByRole('button', { name: /add tag/i })
      
      await user.type(tagInput, 'Docker')
      await user.click(addButton)
      
      expect(screen.getByText('Docker')).toBeInTheDocument()
      expect(tagInput).toHaveValue('')
    })

    it('should remove tags when user clicks X button', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const tagInput = screen.getByPlaceholderText(/add a technology/i)
      await user.type(tagInput, 'Kubernetes')
      await user.keyboard('{Enter}')
      
      const removeButton = screen.getByRole('button', { name: /remove/i })
      await user.click(removeButton)
      
      expect(screen.queryByText('Kubernetes')).not.toBeInTheDocument()
    })

    it('should prevent duplicate tags', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const tagInput = screen.getByPlaceholderText(/add a technology/i)
      
      await user.type(tagInput, 'Node.js')
      await user.keyboard('{Enter}')
      await user.type(tagInput, 'Node.js')
      await user.keyboard('{Enter}')
      
      const tags = screen.getAllByText('Node.js')
      expect(tags).toHaveLength(1)
    })
  })

  describe('API Integration', () => {
    it('should call createProject API with correct data structure', async () => {
      const user = userEvent.setup()
      const mockCreateProject = vi.mocked(apiModule.createProject)
      mockCreateProject.mockResolvedValueOnce({
        id: '123',
        name: 'Test Project',
        slug: 'test-project',
        description: 'Test description',
        content: '',
        status: 'in-progress',
        demoUrl: 'https://demo.example.com',
        projectUrl: 'https://github.com/test/project',
        viewCount: 0,
        createdAt: '2023-01-01',
        updatedAt: '2023-01-01',
        creator: {
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
      
      renderProjectForm()
      
      // Fill form
      await user.type(screen.getByLabelText(/project name/i), 'Test Project')
      await user.type(screen.getByLabelText(/description/i), 'Test description')
      await user.type(screen.getByLabelText(/live demo url/i), 'https://demo.example.com')
      await user.type(screen.getByLabelText(/github url/i), 'https://github.com/test/project')
      
      // Add tags
      const tagInput = screen.getByPlaceholderText(/add a technology/i)
      await user.type(tagInput, 'React')
      await user.keyboard('{Enter}')
      await user.type(tagInput, 'TypeScript')
      await user.keyboard('{Enter}')
      
      // Submit form
      await user.click(screen.getByRole('button', { name: /create project/i }))
      
      await waitFor(() => {
        expect(mockCreateProject).toHaveBeenCalledWith({
          name: 'Test Project',
          description: 'Test description',
          projectUrl: 'https://demo.example.com',
          githubUrl: 'https://github.com/test/project',
          status: 'in-progress',
          tagNames: ['React', 'TypeScript']
        })
      })
    })

    it('should handle optional fields correctly', async () => {
      const user = userEvent.setup()
      const mockCreateProject = vi.mocked(apiModule.createProject)
      mockCreateProject.mockResolvedValueOnce({
        id: '123',
        name: 'Minimal Project',
        slug: 'minimal-project',
        description: 'Simple project',
        content: '',
        status: 'in-progress',
        demoUrl: null,
        projectUrl: null,
        viewCount: 0,
        createdAt: '2023-01-01',
        updatedAt: '2023-01-01',
        creator: {
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
      
      renderProjectForm()
      
      // Fill only required fields
      await user.type(screen.getByLabelText(/project name/i), 'Minimal Project')
      await user.type(screen.getByLabelText(/description/i), 'Simple project')
      
      await user.click(screen.getByRole('button', { name: /create project/i }))
      
      await waitFor(() => {
        expect(mockCreateProject).toHaveBeenCalledWith({
          name: 'Minimal Project',
          description: 'Simple project',
          projectUrl: undefined,
          githubUrl: undefined,
          status: 'in-progress',
          tagNames: []
        })
      })
    })

    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup()
      const mockCreateProject = vi.mocked(apiModule.createProject)
      mockCreateProject.mockRejectedValueOnce(new Error('Failed to create project'))
      
      renderProjectForm()
      
      await user.type(screen.getByLabelText(/project name/i), 'Test Project')
      await user.type(screen.getByLabelText(/description/i), 'Test description')
      await user.click(screen.getByRole('button', { name: /create project/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/failed to create project/i)).toBeInTheDocument()
      })
    })

    it('should show loading state during API call', async () => {
      const user = userEvent.setup()
      const mockCreateProject = vi.mocked(apiModule.createProject)
      
      // Create a promise that we can control
      let resolvePromise: (value: any) => void
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      mockCreateProject.mockReturnValueOnce(promise)
      
      renderProjectForm()
      
      await user.type(screen.getByLabelText(/project name/i), 'Test Project')
      await user.type(screen.getByLabelText(/description/i), 'Test description')
      
      const submitButton = screen.getByRole('button', { name: /create project/i })
      await user.click(submitButton)
      
      // Should show loading state
      expect(screen.getByText(/creating\.\.\./i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
      
      // Resolve the promise
      resolvePromise!({
        id: '123',
        name: 'Test Project',
        slug: 'test-project',
        description: 'Test description',
        content: '',
        status: 'in-progress',
        demoUrl: null,
        projectUrl: null,
        viewCount: 0,
        createdAt: '2023-01-01',
        updatedAt: '2023-01-01',
        creator: {
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
  })

  describe('Form Behavior', () => {
    it('should have in-progress as default status', () => {
      renderProjectForm()
      
      const statusSelect = screen.getByLabelText(/status/i) as HTMLSelectElement
      expect(statusSelect.value).toBe('in-progress')
    })

    it('should allow changing status to completed', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const statusSelect = screen.getByLabelText(/status/i)
      await user.selectOptions(statusSelect, 'completed')
      
      expect(statusSelect).toHaveValue('completed')
    })

    it('should allow changing status to published', async () => {
      const user = userEvent.setup()
      renderProjectForm()
      
      const statusSelect = screen.getByLabelText(/status/i)
      await user.selectOptions(statusSelect, 'published')
      
      expect(statusSelect).toHaveValue('published')
    })

    it('should close form when Cancel button is clicked', async () => {
      const user = userEvent.setup()
      const mockOnClose = vi.fn()
      
      renderProjectForm({ onClose: mockOnClose })
      
      await user.click(screen.getByRole('button', { name: /cancel/i }))
      
      expect(mockOnClose).toHaveBeenCalled()
    })

    it('should call onSuccess and onClose callbacks after successful creation', async () => {
      const user = userEvent.setup()
      const mockOnSuccess = vi.fn()
      const mockOnClose = vi.fn()
      const mockCreateProject = vi.mocked(apiModule.createProject)
      
      mockCreateProject.mockResolvedValueOnce({
        id: '123',
        name: 'Test Project',
        slug: 'test-project',
        description: 'Test description',
        content: '',
        status: 'in-progress',
        demoUrl: null,
        projectUrl: null,
        viewCount: 0,
        createdAt: '2023-01-01',
        updatedAt: '2023-01-01',
        creator: {
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
      
      renderProjectForm({
        onSuccess: mockOnSuccess,
        onClose: mockOnClose
      })
      
      await user.type(screen.getByLabelText(/project name/i), 'Test Project')
      await user.type(screen.getByLabelText(/description/i), 'Test description')
      await user.click(screen.getByRole('button', { name: /create project/i }))
      
      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalled()
        expect(mockOnClose).toHaveBeenCalled()
      })
    })
  })
})
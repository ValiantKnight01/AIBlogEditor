import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter, MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ProjectPage } from '@/pages/ProjectPage'

// Mock the API service
vi.mock('@/services/api', () => ({
  getProjectBySlug: vi.fn(() => Promise.resolve({
    id: '1',
    name: 'Amazing Full-Stack Project',
    slug: 'amazing-fullstack-project',
    description: 'A comprehensive full-stack web application built with modern technologies',
    content: `# Project Overview

This is a comprehensive full-stack project that demonstrates modern web development practices.

## Features

- **Frontend**: React with TypeScript and Tailwind CSS
- **Backend**: Node.js with Express and PostgreSQL
- **Authentication**: JWT-based authentication system
- **Real-time**: WebSocket integration for live updates

## Architecture

The project follows a clean architecture pattern with separation of concerns.

### Frontend Architecture
- Component-based design with React
- State management with Context API
- Type-safe development with TypeScript

### Backend Architecture
- RESTful API design
- Database modeling with PostgreSQL
- Middleware for authentication and validation

## Getting Started

\`\`\`bash
npm install
npm run dev
\`\`\`

## Deployment

The project is deployed on modern cloud infrastructure.`,
    status: 'published',
    demoUrl: 'https://amazing-project.vercel.app',
    projectUrl: 'https://github.com/user/amazing-project',
    viewCount: 250,
    createdAt: '2024-01-10T14:20:00Z',
    updatedAt: '2024-01-15T09:45:00Z',
    creator: {
      id: '1',
      username: 'projectcreator',
      email: 'creator@example.com',
      bio: 'Full-stack developer passionate about building scalable applications',
      profileImageUrl: 'https://example.com/creator-avatar.jpg',
      isActive: true,
      createdAt: '2024-01-01T00:00:00Z'
    },
    tags: ['React', 'TypeScript', 'Node.js', 'PostgreSQL', 'Full-Stack']
  })),
  getRelatedProjects: vi.fn(() => Promise.resolve({
    projects: [
      {
        id: '2',
        name: 'Related Project 1',
        slug: 'related-project-1',
        description: 'Another interesting project',
        status: 'published',
        demoUrl: 'https://project1.example.com',
        projectUrl: 'https://github.com/user/project1',
        viewCount: 120,
        createdAt: '2024-01-08T12:00:00Z',
        creator: { username: 'projectcreator' },
        tags: ['React', 'JavaScript']
      },
      {
        id: '3',
        name: 'Related Project 2',
        slug: 'related-project-2',
        description: 'A cool mobile app project',
        status: 'published',
        demoUrl: null,
        projectUrl: 'https://github.com/user/project2',
        viewCount: 95,
        createdAt: '2024-01-05T16:30:00Z',
        creator: { username: 'projectcreator' },
        tags: ['React Native', 'Mobile']
      }
    ],
    pagination: { page: 1, perPage: 3, total: 2, totalPages: 1 }
  }))
}))

// Test wrapper with necessary providers
const TestWrapper = ({ children, initialEntries = ['/projects/amazing-fullstack-project'] }: { 
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

describe('ProjectPage', () => {
  it('should render the project name as main heading', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /amazing full-stack project/i })).toBeInTheDocument()
    })
  })

  it('should render the project description', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/comprehensive full-stack web application/i)).toBeInTheDocument()
    })
  })

  it('should render the project content with markdown formatting', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /project overview/i })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: /features/i })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: /architecture/i })).toBeInTheDocument()
      expect(screen.getByText(/react with typescript/i)).toBeInTheDocument()
    })
  })

  it('should display creator information', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText('projectcreator')).toBeInTheDocument()
      expect(screen.getByText(/full-stack developer passionate/i)).toBeInTheDocument()
    })
  })

  it('should display creation and update dates', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/created on/i)).toBeInTheDocument()
      expect(screen.getByText(/jan 10, 2024/i)).toBeInTheDocument()
      expect(screen.getByText(/last updated/i)).toBeInTheDocument()
    })
  })

  it('should display view count', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText(/250 views/i)).toBeInTheDocument()
    })
  })

  it('should render all project tags as clickable elements', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByText('React')).toBeInTheDocument()
      expect(screen.getByText('TypeScript')).toBeInTheDocument()
      expect(screen.getByText('Node.js')).toBeInTheDocument()
      expect(screen.getByText('PostgreSQL')).toBeInTheDocument()
      expect(screen.getByText('Full-Stack')).toBeInTheDocument()
      
      // Tags should be clickable links
      expect(screen.getByRole('link', { name: 'React' })).toHaveAttribute('href', '/tags/react')
    })
  })

  it('should render demo and source code links with proper icons', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      const demoLink = screen.getByRole('link', { name: /live demo/i })
      const sourceLink = screen.getByRole('link', { name: /view source/i })
      
      expect(demoLink).toHaveAttribute('href', 'https://amazing-project.vercel.app')
      expect(demoLink).toHaveAttribute('target', '_blank')
      expect(sourceLink).toHaveAttribute('href', 'https://github.com/user/amazing-project')
      expect(sourceLink).toHaveAttribute('target', '_blank')
    })
  })

  it('should render related projects section', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /related projects/i })).toBeInTheDocument()
      expect(screen.getByText('Related Project 1')).toBeInTheDocument()
      expect(screen.getByText('Related Project 2')).toBeInTheDocument()
    })
  })

  it('should have proper breadcrumb navigation', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /home/i })).toHaveAttribute('href', '/')
      expect(screen.getByRole('link', { name: /projects/i })).toHaveAttribute('href', '/projects')
      expect(screen.getByText(/amazing full-stack project/i)).toBeInTheDocument()
    })
  })

  it('should display loading state while fetching project', () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    expect(screen.getByText(/loading project/i)).toBeInTheDocument()
  })

  it('should handle 404 error when project is not found', async () => {
    const { getProjectBySlug } = await import('@/services/api')
    vi.mocked(getProjectBySlug).mockRejectedValueOnce({
      response: { status: 404 }
    })
    
    render(
      <TestWrapper initialEntries={['/projects/non-existent-project']}>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /project not found/i })).toBeInTheDocument()
      expect(screen.getByText(/the project you're looking for doesn't exist/i)).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /back to projects/i })).toHaveAttribute('href', '/projects')
    })
  })

  it('should handle projects without demo URL', async () => {
    const { getProjectBySlug } = await import('@/services/api')
    vi.mocked(getProjectBySlug).mockResolvedValueOnce({
      id: '1',
      name: 'Project Without Demo',
      slug: 'project-without-demo',
      description: 'A project without a live demo',
      content: '# Project content',
      status: 'published',
      demoUrl: null,
      projectUrl: 'https://github.com/user/project',
      viewCount: 50,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      creator: { username: 'creator' },
      tags: ['JavaScript']
    })
    
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.queryByRole('link', { name: /live demo/i })).not.toBeInTheDocument()
      expect(screen.getByRole('link', { name: /view source/i })).toBeInTheDocument()
    })
  })

  it('should have project screenshot/preview section', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('img', { name: /project screenshot/i })).toBeInTheDocument()
    })
  })

  it('should have proper table of contents for long project descriptions', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /table of contents/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /project overview/i })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /features/i })).toBeInTheDocument()
    })
  })

  it('should be mobile responsive with proper layout', async () => {
    const { container } = render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      const projectContent = container.querySelector('[data-testid="project-content"]')
      expect(projectContent).toHaveClass('prose', 'prose-lg', 'max-w-none')
    })
  })

  it('should have social sharing buttons for projects', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /share on twitter/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /share on linkedin/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /copy link/i })).toBeInTheDocument()
    })
  })

  it('should set proper meta tags for SEO', async () => {
    render(
      <TestWrapper>
        <ProjectPage />
      </TestWrapper>
    )
    
    await waitFor(() => {
      expect(document.title).toContain('Amazing Full-Stack Project')
    })
  })
})
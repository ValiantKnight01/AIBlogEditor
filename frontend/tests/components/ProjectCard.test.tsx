import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProjectCard } from '@/components/ProjectCard'

const mockProject = {
  id: '1',
  name: 'Amazing Project',
  slug: 'amazing-project',
  description: 'This is an amazing project that does incredible things',
  status: 'published' as const,
  demoUrl: 'https://demo.example.com',
  projectUrl: 'https://github.com/user/amazing-project',
  viewCount: 150,
  createdAt: '2024-01-10T14:20:00Z',
  updatedAt: '2024-01-10T14:20:00Z',
  creator: {
    id: '1',
    username: 'projectcreator',
    email: 'creator@example.com',
    bio: 'Project creator bio',
    profileImageUrl: null,
    isActive: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
  tags: ['React', 'Node.js', 'PostgreSQL'],
}

describe('ProjectCard', () => {
  it('should render project name as heading', () => {
    render(<ProjectCard project={mockProject} />)
    
    expect(screen.getByRole('heading', { name: /amazing project/i })).toBeInTheDocument()
  })

  it('should render project description', () => {
    render(<ProjectCard project={mockProject} />)
    
    expect(screen.getByText(/this is an amazing project that does incredible things/i)).toBeInTheDocument()
  })

  it('should render creator information', () => {
    render(<ProjectCard project={mockProject} />)
    
    expect(screen.getByText(/by projectcreator/i)).toBeInTheDocument()
  })

  it('should render creation date in readable format', () => {
    render(<ProjectCard project={mockProject} />)
    
    // Should show formatted date like "Jan 10, 2024"
    expect(screen.getByText(/jan 10, 2024/i)).toBeInTheDocument()
  })

  it('should render view count', () => {
    render(<ProjectCard project={mockProject} />)
    
    expect(screen.getByText(/150 views/i)).toBeInTheDocument()
  })

  it('should render project tags as clickable elements', () => {
    render(<ProjectCard project={mockProject} />)
    
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Node.js')).toBeInTheDocument()
    expect(screen.getByText('PostgreSQL')).toBeInTheDocument()
  })

  it('should render demo link when demoUrl is provided', () => {
    render(<ProjectCard project={mockProject} />)
    
    const demoLink = screen.getByRole('link', { name: /live demo/i })
    expect(demoLink).toHaveAttribute('href', 'https://demo.example.com')
    expect(demoLink).toHaveAttribute('target', '_blank')
  })

  it('should render source code link when projectUrl is provided', () => {
    render(<ProjectCard project={mockProject} />)
    
    const sourceLink = screen.getByRole('link', { name: /source code/i })
    expect(sourceLink).toHaveAttribute('href', 'https://github.com/user/amazing-project')
    expect(sourceLink).toHaveAttribute('target', '_blank')
  })

  it('should have a clickable link to the project detail page', () => {
    render(<ProjectCard project={mockProject} />)
    
    const detailLink = screen.getByRole('link', { name: /view project/i })
    expect(detailLink).toHaveAttribute('href', '/projects/amazing-project')
  })

  it('should render with proper card styling and layout', () => {
    const { container } = render(<ProjectCard project={mockProject} />)
    
    const card = container.firstChild
    expect(card).toHaveClass('border', 'rounded-lg', 'p-6', 'bg-white')
  })

  it('should handle missing creator gracefully', () => {
    const projectWithoutCreator = { ...mockProject, creator: null }
    render(<ProjectCard project={projectWithoutCreator} />)
    
    expect(screen.queryByText(/by/i)).not.toBeInTheDocument()
  })

  it('should handle projects with no demo URL', () => {
    const projectWithoutDemo = { ...mockProject, demoUrl: null }
    render(<ProjectCard project={projectWithoutDemo} />)
    
    expect(screen.queryByRole('link', { name: /live demo/i })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: /source code/i })).toBeInTheDocument()
  })

  it('should handle projects with no source URL', () => {
    const projectWithoutSource = { ...mockProject, projectUrl: null }
    render(<ProjectCard project={projectWithoutSource} />)
    
    expect(screen.getByRole('link', { name: /live demo/i })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /source code/i })).not.toBeInTheDocument()
  })

  it('should handle projects with no tags', () => {
    const projectWithoutTags = { ...mockProject, tags: [] }
    render(<ProjectCard project={projectWithoutTags} />)
    
    expect(screen.queryByText('React')).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /amazing project/i })).toBeInTheDocument()
  })
})
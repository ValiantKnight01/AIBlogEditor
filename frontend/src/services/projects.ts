import { 
  Project, 
  PaginationParams, 
  PaginationResponse,
  getProjects,
  getFeaturedProjects,
  getProjectBySlug,
  getRelatedProjects,
  getMyProjects,
  createProject,
  updateProject,
  deleteProject
} from './api'

export interface ProjectFilters extends PaginationParams {
  tag?: string
  status?: 'draft' | 'published'
  creator?: string
  search?: string
}

export class ProjectService {
  async getAllProjects(filters: ProjectFilters = {}): Promise<PaginationResponse<Project>> {
    return getProjects(filters)
  }

  async getFeaturedProjects(limit = 3): Promise<Project[]> {
    const response = await getFeaturedProjects(limit)
    return response.items
  }

  async getProjectBySlug(slug: string): Promise<Project> {
    return getProjectBySlug(slug)
  }

  async getRelatedProjects(slug: string, limit = 3): Promise<Project[]> {
    try {
      const response = await getRelatedProjects(slug, limit)
      return response.items
    } catch (error) {
      // If related projects endpoint doesn't exist, return empty array
      console.warn('Related projects not available:', error)
      return []
    }
  }

  async getMyProjects(filters: PaginationParams = {}): Promise<PaginationResponse<Project>> {
    return getMyProjects(filters)
  }

  async createProject(data: {
    name: string
    description: string
    content?: string
    demoUrl?: string
    projectUrl?: string
    status?: 'draft' | 'published'
    tags?: string[]
  }): Promise<Project> {
    const projectData = {
      name: data.name,
      description: data.description,
      content: data.content || '',
      demoUrl: data.demoUrl || null,
      projectUrl: data.projectUrl || null,
      status: data.status || 'draft',
      tags: data.tags || []
    }
    
    return createProject(projectData)
  }

  async updateProject(slug: string, data: Partial<Project>): Promise<Project> {
    return updateProject(slug, data)
  }

  async deleteProject(slug: string): Promise<void> {
    return deleteProject(slug)
  }

  async publishProject(slug: string): Promise<Project> {
    return this.updateProject(slug, { status: 'published' })
  }

  async draftProject(slug: string): Promise<Project> {
    return this.updateProject(slug, { status: 'draft' })
  }

  // Utility function to format date
  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  // Utility function to format view count
  formatViewCount(count: number): string {
    if (count < 1000) {
      return count.toString()
    } else if (count < 1000000) {
      return (count / 1000).toFixed(1) + 'k'
    } else {
      return (count / 1000000).toFixed(1) + 'm'
    }
  }

  // Utility function to validate URLs
  isValidUrl(url: string): boolean {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  // Utility function to extract repository info from GitHub URL
  getGitHubInfo(url: string): { owner: string; repo: string } | null {
    const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)/)
    if (match) {
      return {
        owner: match[1],
        repo: match[2]
      }
    }
    return null
  }

  // Utility function to get project status badge color
  getStatusBadgeColor(status: 'draft' | 'published'): string {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-800'
      case 'draft':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  // Utility function to generate project preview image URL
  getPreviewImageUrl(project: Project): string {
    // If demo URL exists, use it for preview
    if (project.demoUrl && this.isValidUrl(project.demoUrl)) {
      // Use a service like screenshotapi.net or similar
      return `https://api.screenshotmachine.com/?key=demo&url=${encodeURIComponent(project.demoUrl)}&dimension=1024x768`
    }
    
    // Fallback to a placeholder image
    return `https://via.placeholder.com/600x400/6366f1/ffffff?text=${encodeURIComponent(project.name)}`
  }
}

// Create singleton instance
export const projectService = new ProjectService()
export default projectService
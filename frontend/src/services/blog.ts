import { 
  BlogPost, 
  PaginationParams, 
  PaginationResponse,
  getPosts,
  getRecentPosts,
  getPostBySlug,
  getRelatedPosts,
  getMyPosts,
  createPost,
  updatePost,
  deletePost
} from './api'

export interface BlogPostFilters extends PaginationParams {
  tag?: string
  status?: 'draft' | 'published'
  author?: string
  search?: string
}

export class BlogService {
  async getAllPosts(filters: BlogPostFilters = {}): Promise<PaginationResponse<BlogPost>> {
    return getPosts(filters)
  }

  async getRecentPosts(limit = 6): Promise<BlogPost[]> {
    const response = await getRecentPosts(limit)
    return response.posts
  }

  async getPostBySlug(slug: string): Promise<BlogPost> {
    return getPostBySlug(slug)
  }

  async getRelatedPosts(slug: string, limit = 3): Promise<BlogPost[]> {
    try {
      const response = await getRelatedPosts(slug, limit)
      return response.posts
    } catch (error) {
      // If related posts endpoint doesn't exist, return empty array
      console.warn('Related posts not available:', error)
      return []
    }
  }

  async getMyPosts(filters: PaginationParams = {}): Promise<PaginationResponse<BlogPost>> {
    return getMyPosts(filters)
  }

  async createPost(data: {
    title: string
    content: string
    excerpt?: string
    status?: 'draft' | 'published'
    tags?: string[]
  }): Promise<BlogPost> {
    const postData = {
      title: data.title,
      content: data.content,
      excerpt: data.excerpt || this.generateExcerpt(data.content),
      status: data.status || 'draft',
      tags: data.tags || []
    }
    
    return createPost(postData)
  }

  async updatePost(slug: string, data: Partial<BlogPost>): Promise<BlogPost> {
    return updatePost(slug, data)
  }

  async deletePost(slug: string): Promise<void> {
    return deletePost(slug)
  }

  async publishPost(slug: string): Promise<BlogPost> {
    return this.updatePost(slug, { status: 'published' })
  }

  async draftPost(slug: string): Promise<BlogPost> {
    return this.updatePost(slug, { status: 'draft' })
  }

  // Utility function to generate excerpt from content
  generateExcerpt(content: string, maxLength = 160): string {
    // Remove markdown formatting
    const plainText = content
      .replace(/#{1,6}\s+/g, '') // Headers
      .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
      .replace(/\*(.*?)\*/g, '$1') // Italic
      .replace(/`(.*?)`/g, '$1') // Inline code
      .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Links
      .replace(/!\[.*?\]\(.*?\)/g, '') // Images
      .replace(/```[\s\S]*?```/g, '') // Code blocks
      .trim()

    if (plainText.length <= maxLength) {
      return plainText
    }

    return plainText.substring(0, maxLength).replace(/\s+\S*$/, '') + '...'
  }

  // Utility function to estimate reading time
  estimateReadingTime(content: string): number {
    const wordsPerMinute = 200
    const wordCount = content.split(/\s+/).length
    return Math.ceil(wordCount / wordsPerMinute)
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
}

// Create singleton instance
export const blogService = new BlogService()
export default blogService
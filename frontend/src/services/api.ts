import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface PaginationParams {
  page?: number
  perPage?: number
}

export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

export interface BlogPost {
  id: string
  title: string
  slug: string
  content?: string
  excerpt: string
  status: 'draft' | 'published'
  viewCount: number
  createdAt: string
  updatedAt: string
  author: {
    id: string
    username: string
    email: string
    bio: string
    profileImageUrl: string | null
    isActive: boolean
    createdAt: string
  }
  tags: string[]
}

export interface Project {
  id: string
  name: string
  slug: string
  description: string
  content?: string
  status: 'draft' | 'published'
  demoUrl: string | null
  projectUrl: string | null
  viewCount: number
  createdAt: string
  updatedAt: string
  creator: {
    id: string
    username: string
    email: string
    bio: string
    profileImageUrl: string | null
    isActive: boolean
    createdAt: string
  }
  tags: string[]
}

export interface Tag {
  id: string
  name: string
  slug: string
  description: string
  postCount: number
}

export interface User {
  id: string
  username: string
  email: string
  bio: string
  profileImageUrl: string | null
  isActive: boolean
  createdAt: string
}

// Auth API functions
export const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login', { email, password })
  return response.data
}

export const logout = async () => {
  const response = await api.post('/auth/logout')
  return response.data
}

// User API functions
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/users/me')
  return response.data
}

export const updateProfile = async (data: Partial<User>) => {
  const response = await api.put('/users/me', data)
  return response.data
}

// Blog Posts API functions
export const getPosts = async (params: PaginationParams = {}): Promise<PaginationResponse<BlogPost>> => {
  const response = await api.get('/posts', { params })
  return response.data
}

export const getRecentPosts = async (limit = 6): Promise<PaginationResponse<BlogPost>> => {
  const response = await api.get('/posts', { 
    params: { perPage: limit, page: 1 } 
  })
  return response.data
}

export const getPostBySlug = async (slug: string): Promise<BlogPost> => {
  const response = await api.get(`/posts/${slug}`)
  return response.data
}

export const getRelatedPosts = async (slug: string, limit = 3): Promise<PaginationResponse<BlogPost>> => {
  const response = await api.get(`/posts/${slug}/related`, {
    params: { perPage: limit }
  })
  return response.data
}

export const getMyPosts = async (params: PaginationParams = {}): Promise<PaginationResponse<BlogPost>> => {
  const response = await api.get('/posts', { 
    params: { ...params, author: 'me' } 
  })
  return response.data
}

export const createPost = async (data: Partial<BlogPost>): Promise<BlogPost> => {
  const response = await api.post('/posts', data)
  return response.data
}

export const updatePost = async (slug: string, data: Partial<BlogPost>): Promise<BlogPost> => {
  const response = await api.put(`/posts/${slug}`, data)
  return response.data
}

export const deletePost = async (slug: string): Promise<void> => {
  await api.delete(`/posts/${slug}`)
}

// Projects API functions
export const getProjects = async (params: PaginationParams = {}): Promise<PaginationResponse<Project>> => {
  const response = await api.get('/projects', { params })
  return response.data
}

export const getFeaturedProjects = async (limit = 3): Promise<PaginationResponse<Project>> => {
  const response = await api.get('/projects', { 
    params: { perPage: limit, page: 1 } 
  })
  return response.data
}

export const getProjectBySlug = async (slug: string): Promise<Project> => {
  const response = await api.get(`/projects/${slug}`)
  return response.data
}

export const getRelatedProjects = async (slug: string, limit = 3): Promise<PaginationResponse<Project>> => {
  const response = await api.get(`/projects/${slug}/related`, {
    params: { perPage: limit }
  })
  return response.data
}

export const getMyProjects = async (params: PaginationParams = {}): Promise<PaginationResponse<Project>> => {
  const response = await api.get('/projects', { 
    params: { ...params, creator: 'me' } 
  })
  return response.data
}

export const createProject = async (data: Partial<Project>): Promise<Project> => {
  const response = await api.post('/projects', data)
  return response.data
}

export const updateProject = async (slug: string, data: Partial<Project>): Promise<Project> => {
  const response = await api.put(`/projects/${slug}`, data)
  return response.data
}

export const deleteProject = async (slug: string): Promise<void> => {
  await api.delete(`/projects/${slug}`)
}

// Tags API functions
export const getTags = async (): Promise<PaginationResponse<Tag>> => {
  const response = await api.get('/tags')
  return response.data
}

// Dashboard API functions
export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/stats')
  return response.data
}

export default api
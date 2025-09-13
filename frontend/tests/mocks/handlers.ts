import { rest } from 'msw'

// Mock data
export const mockUser = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  bio: 'Test user bio',
  profileImageUrl: null,
  isActive: true,
  createdAt: '2024-01-01T00:00:00Z',
}

export const mockBlogPosts = [
  {
    id: '1',
    title: 'First Blog Post',
    slug: 'first-blog-post',
    content: 'This is the content of the first blog post',
    excerpt: 'This is the excerpt',
    status: 'published',
    viewCount: 42,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    author: mockUser,
    tags: ['react', 'typescript'],
  },
  {
    id: '2',
    title: 'Second Blog Post',
    slug: 'second-blog-post',
    content: 'This is the content of the second blog post',
    excerpt: 'Another great post',
    status: 'published',
    viewCount: 24,
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z',
    author: mockUser,
    tags: ['javascript', 'web'],
  },
]

export const mockProjects = [
  {
    id: '1',
    name: 'Amazing Project',
    slug: 'amazing-project',
    description: 'This is an amazing project description',
    content: 'Detailed project content here',
    status: 'published',
    demoUrl: 'https://demo.example.com',
    projectUrl: 'https://github.com/user/project',
    viewCount: 100,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    creator: mockUser,
    tags: ['react', 'node'],
  },
  {
    id: '2',
    name: 'Cool App',
    slug: 'cool-app',
    description: 'A really cool application',
    content: 'More details about the cool app',
    status: 'published',
    demoUrl: 'https://coolapp.example.com',
    projectUrl: 'https://github.com/user/cool-app',
    viewCount: 75,
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z',
    creator: mockUser,
    tags: ['vue', 'python'],
  },
]

export const mockTags = [
  { id: '1', name: 'React', slug: 'react', description: 'React framework', postCount: 5 },
  { id: '2', name: 'TypeScript', slug: 'typescript', description: 'TypeScript language', postCount: 3 },
  { id: '3', name: 'JavaScript', slug: 'javascript', description: 'JavaScript language', postCount: 8 },
  { id: '4', name: 'Node.js', slug: 'nodejs', description: 'Node.js runtime', postCount: 4 },
]

// API handlers
export const handlers = [
  // Auth handlers
  rest.post('/api/v1/auth/login', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        user: mockUser,
      })
    )
  }),

  rest.post('/api/v1/auth/logout', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ message: 'Logged out successfully' }))
  }),

  // User profile handlers
  rest.get('/api/v1/users/me', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockUser))
  }),

  // Blog posts handlers
  rest.get('/api/v1/posts', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        posts: mockBlogPosts,
        pagination: {
          page: 1,
          perPage: 10,
          total: mockBlogPosts.length,
          totalPages: 1,
        },
      })
    )
  }),

  rest.get('/api/v1/posts/:slug', (req, res, ctx) => {
    const { slug } = req.params
    const post = mockBlogPosts.find((p) => p.slug === slug)
    if (!post) {
      return res(ctx.status(404), ctx.json({ detail: 'Post not found' }))
    }
    return res(ctx.status(200), ctx.json(post))
  }),

  // Projects handlers
  rest.get('/api/v1/projects', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        projects: mockProjects,
        pagination: {
          page: 1,
          perPage: 10,
          total: mockProjects.length,
          totalPages: 1,
        },
      })
    )
  }),

  rest.get('/api/v1/projects/:slug', (req, res, ctx) => {
    const { slug } = req.params
    const project = mockProjects.find((p) => p.slug === slug)
    if (!project) {
      return res(ctx.status(404), ctx.json({ detail: 'Project not found' }))
    }
    return res(ctx.status(200), ctx.json(project))
  }),

  // Tags handlers
  rest.get('/api/v1/tags', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        tags: mockTags,
        pagination: {
          page: 1,
          perPage: 50,
          total: mockTags.length,
          totalPages: 1,
        },
      })
    )
  }),
]
import React from 'react'
import { Link } from 'react-router-dom'
import { BlogPost } from '@/services/api'
import { blogService } from '@/services/blog'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/Badge'

interface BlogPostCardProps {
  post: BlogPost
  showAuthor?: boolean
  className?: string
}

export const BlogPostCard: React.FC<BlogPostCardProps> = ({ 
  post, 
  showAuthor = true,
  className = ''
}) => {
  const readingTime = blogService.estimateReadingTime(post.content || post.excerpt)
  const formattedDate = blogService.formatDate(post.createdAt)
  const formattedViews = blogService.formatViewCount(post.viewCount)

  return (
    <Card className={`border rounded-lg p-6 bg-white hover:shadow-lg transition-shadow duration-200 ${className}`}>
      <article className="h-full flex flex-col">
        {/* Post Title */}
        <header className="mb-3">
          <h2 className="text-xl font-bold text-gray-900 line-clamp-2 mb-2">
            <Link 
              to={`/posts/${post.slug}`}
              className="hover:text-indigo-600 transition-colors"
            >
              {post.title}
            </Link>
          </h2>
          
          {/* Status Badge for Draft Posts */}
          {post.status === 'draft' && (
            <Badge variant="yellow">Draft</Badge>
          )}
        </header>

        {/* Post Excerpt */}
        <div className="mb-4 flex-grow">
          <p className="text-gray-600 line-clamp-3">
            {post.excerpt}
          </p>
        </div>

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag) => (
                <Link
                  key={tag}
                  to={`/tags/${tag.toLowerCase().replace(/\s+/g, '-')}`}
                  className="inline-block"
                >
                  <Badge variant="secondary" className="hover:bg-indigo-100 transition-colors">
                    {tag}
                  </Badge>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="border-t pt-4 mt-auto">
          <div className="flex items-center justify-between">
            {/* Author and Date */}
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              {showAuthor && post.author && (
                <span>By {post.author.username}</span>
              )}
              <span>{formattedDate}</span>
              <span>{readingTime} min read</span>
            </div>

            {/* View Count */}
            <div className="text-sm text-gray-500">
              {formattedViews} views
            </div>
          </div>

          {/* Read More Link */}
          <div className="mt-3">
            <Link
              to={`/posts/${post.slug}`}
              className="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium text-sm transition-colors"
            >
              Read More
              <svg 
                className="ml-1 h-4 w-4" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </footer>
      </article>
    </Card>
  )
}

export default BlogPostCard
import React from 'react'
import { Link } from 'react-router-dom'
import { BlogPost } from '@/services/api'
import { blogService } from '@/services/blog'
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
  const formattedDate = blogService.formatDate(post.createdAt)
  const formattedViews = blogService.formatViewCount(post.viewCount)

  return (
    <article className={`bg-card text-card-foreground border rounded-lg p-6 hover:shadow-md transition-shadow ${className}`}>
      {/* Post Title */}
      <header className="mb-3">
        <h2 className="text-xl font-semibold mb-2">
          <Link 
            to={`/posts/${post.slug}`}
            className="hover:text-primary transition-colors"
          >
            {post.title}
          </Link>
        </h2>
        
        {/* Status Badge for Draft Posts */}
        {post.status === 'draft' && (
          <Badge variant="secondary">Draft</Badge>
        )}
      </header>

      {/* Post Metadata */}
      <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
        {showAuthor && post.author ? (
          <span>{typeof post.author === 'string' ? post.author : post.author.username}</span>
        ) : (
          <span>{formattedDate}</span>
        )}
        <span>{formattedViews} views</span>
      </div>

      {/* Post Excerpt */}
      <div className="mb-4">
        <p className="text-muted-foreground line-clamp-3 mb-4">
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
                <Badge variant="secondary" className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-xs hover:bg-secondary/80 transition-colors">
                  {tag}
                </Badge>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Read More Link */}
      <div className="mt-auto">
        <Link
          to={`/posts/${post.slug}`}
          className="inline-flex items-center text-primary hover:text-primary/80 font-medium text-sm transition-colors"
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
    </article>
  )
}

export default BlogPostCard
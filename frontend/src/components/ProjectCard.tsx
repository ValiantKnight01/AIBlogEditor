import React from 'react'
import { Link } from 'react-router-dom'
import { Project } from '@/services/api'
import { projectService } from '@/services/projects'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

interface ProjectCardProps {
  project: Project
  showCreator?: boolean
  className?: string
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ 
  project, 
  showCreator = true,
  className = ''
}) => {
  const formattedDate = projectService.formatDate(project.createdAt)
  const formattedViews = projectService.formatViewCount(project.viewCount)
  const previewImageUrl = projectService.getPreviewImageUrl(project)

  return (
    <Card className={`border rounded-lg p-6 bg-white hover:shadow-lg transition-shadow duration-200 ${className}`}>
      <article className="h-full flex flex-col">
        {/* Project Preview Image */}
        <div className="mb-4 relative overflow-hidden rounded-lg bg-gray-100">
          <img
            src={previewImageUrl}
            alt="Project screenshot"
            className="w-full h-48 object-cover hover:scale-105 transition-transform duration-200"
            loading="lazy"
            onError={(e) => {
              // Fallback to placeholder on image error
              e.currentTarget.src = `https://via.placeholder.com/600x400/6366f1/ffffff?text=${encodeURIComponent(project.name)}`
            }}
          />
          {project.status === 'draft' && (
            <div className="absolute top-3 left-3">
              <Badge variant="yellow">Draft</Badge>
            </div>
          )}
        </div>

        {/* Project Name */}
        <header className="mb-3">
          <h2 className="text-xl font-bold text-gray-900 line-clamp-1 mb-2">
            <Link 
              to={`/projects/${project.slug}`}
              className="hover:text-indigo-600 transition-colors"
            >
              {project.name}
            </Link>
          </h2>
        </header>

        {/* Project Description */}
        <div className="mb-4 flex-grow">
          <p className="text-gray-600 line-clamp-2">
            {project.description}
          </p>
        </div>

        {/* Tags */}
        {project.tags && project.tags.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {project.tags.map((tag) => (
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

        {/* Project Links */}
        <div className="mb-4">
          <div className="flex space-x-3">
            {project.demoUrl && (
              <a
                href={project.demoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors"
              >
                <svg className="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Live Demo
              </a>
            )}
            
            {project.projectUrl && (
              <a
                href={project.projectUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1 bg-gray-800 text-white text-sm font-medium rounded-md hover:bg-gray-900 transition-colors"
              >
                <svg className="mr-1 h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                </svg>
                Source Code
              </a>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="border-t pt-4 mt-auto">
          <div className="flex items-center justify-between">
            {/* Creator and Date */}
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              {showCreator && project.creator && (
                <span>By {project.creator.username}</span>
              )}
              <span>{formattedDate}</span>
            </div>

            {/* View Count */}
            <div className="text-sm text-gray-500">
              {formattedViews} views
            </div>
          </div>

          {/* View Project Link */}
          <div className="mt-3">
            <Link
              to={`/projects/${project.slug}`}
              className="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium text-sm transition-colors"
            >
              View Project
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

export default ProjectCard
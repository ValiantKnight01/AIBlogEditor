import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Calendar, ExternalLink, Github, Eye, User } from 'lucide-react'
import { getProjectBySlug } from '@/services/api'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export const ProjectPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>()
  
  const {
    data: project,
    isLoading,
    error
  } = useQuery({
    queryKey: ['project', slug],
    queryFn: () => getProjectBySlug(slug!),
    enabled: !!slug
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2 mb-8"></div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="h-64 bg-gray-300 rounded-lg mb-6"></div>
                <div className="space-y-4">
                  <div className="h-4 bg-gray-300 rounded"></div>
                  <div className="h-4 bg-gray-300 rounded w-5/6"></div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="h-32 bg-gray-300 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Project Not Found
            </h1>
            <p className="text-gray-600 mb-8">
              The project you're looking for doesn't exist or has been removed.
            </p>
            <Link
              to="/projects"
              className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-500"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Projects
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Link
            to="/projects"
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-500 mb-8"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Projects
          </Link>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2">
              <div className="mb-6">
                {project.tags && project.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {project.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}

                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  {project.name}
                </h1>

                {project.description && (
                  <p className="text-xl text-gray-600 mb-6">
                    {project.description}
                  </p>
                )}

                <div className="flex items-center gap-6 text-sm text-gray-500 mb-8">
                  {project.creator && (
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      <span>{project.creator.username}</span>
                    </div>
                  )}
                  {project.createdAt && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <time dateTime={project.createdAt}>
                        {new Date(project.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </time>
                    </div>
                  )}
                  {project.viewCount !== undefined && (
                    <div className="flex items-center gap-2">
                      <Eye className="h-4 w-4" />
                      <span>{project.viewCount} views</span>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-4 mb-8">
                  {project.demoUrl && (
                    <Button asChild>
                      <a
                        href={project.demoUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2"
                      >
                        <ExternalLink className="h-4 w-4" />
                        Live Demo
                      </a>
                    </Button>
                  )}
                  {project.projectUrl && (
                    <Button variant="outline" asChild>
                      <a
                        href={project.projectUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2"
                      >
                        <Github className="h-4 w-4" />
                        Source Code
                      </a>
                    </Button>
                  )}
                </div>
              </div>

              {/* Project Images - TODO: Add to API types */}
              {/* {project.preview_image_url && (
                <div className="mb-8">
                  <img
                    src={project.preview_image_url}
                    alt={project.name}
                    className="w-full h-auto rounded-lg shadow-lg"
                  />
                </div>
              )} */}
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Project Details
                </h3>

                <div className="space-y-4">
                  {project.status && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Status</dt>
                      <dd className="mt-1">
                        <Badge 
                          variant={project.status === 'published' ? 'default' : 'secondary'}
                        >
                          {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                        </Badge>
                      </dd>
                    </div>
                  )}

                  {/* TODO: Add technologies field to API */}
                  {/* {project.technologies && project.technologies.length > 0 && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500 mb-2">Technologies</dt>
                      <dd className="flex flex-wrap gap-2">
                        {project.technologies.map((tech, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                      </dd>
                    </div>
                  )} */}

                  {project.createdAt && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Created</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(project.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </dd>
                    </div>
                  )}

                  {project.updatedAt && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(project.updatedAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </dd>
                    </div>
                  )}
                </div>
              </div>

              {/* Tags */}
              {project.tags && project.tags.length > 0 && (
                <div className="bg-white rounded-lg p-6 shadow-sm mt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {project.tags.map((tag, index) => (
                      <Badge key={index} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Description Content */}
      {project.content && (
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg p-8 shadow-sm">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">About This Project</h2>
              <article className="prose prose-lg max-w-none">
                <div 
                  className="prose-headings:font-bold prose-headings:text-gray-900 
                             prose-p:text-gray-700 prose-p:leading-7 
                             prose-a:text-indigo-600 prose-a:no-underline hover:prose-a:underline
                             prose-strong:text-gray-900 prose-code:text-sm prose-code:bg-gray-100 
                             prose-code:px-1 prose-code:py-0.5 prose-code:rounded"
                  dangerouslySetInnerHTML={{ 
                    __html: (project.content || '').replace(/\n/g, '<br />') 
                  }}
                />
              </article>
            </div>
          </div>

          {/* Navigation */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <Link
                to="/projects"
                className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-500"
              >
                <ArrowLeft className="h-4 w-4" />
                All Projects
              </Link>
              <Link
                to="/"
                className="text-indigo-600 hover:text-indigo-500"
              >
                Home
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
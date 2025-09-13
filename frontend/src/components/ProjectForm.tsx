import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { createProject } from '@/services/api'

// Project form schema
const projectSchema = z.object({
  name: z.string().min(1, 'Project name is required').max(200, 'Name must be less than 200 characters'),
  description: z.string().min(1, 'Description is required'),
  projectUrl: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  githubUrl: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  status: z.enum(['in-progress', 'completed', 'published']).default('in-progress'),
  tags: z.array(z.string()).optional().default([]),
})

type ProjectFormData = z.infer<typeof projectSchema>

interface ProjectFormProps {
  onClose: () => void
  onSuccess?: () => void
}

export const ProjectForm: React.FC<ProjectFormProps> = ({ onClose, onSuccess }) => {
  const [tagInput, setTagInput] = useState('')
  const queryClient = useQueryClient()

  const form = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: '',
      description: '',
      projectUrl: '',
      githubUrl: '',
      status: 'in-progress',
      tags: [],
    },
  })

  const createProjectMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      form.setError('root', {
        message: error instanceof Error ? error.message : 'Failed to create project'
      })
    },
  })

  const handleSubmit = async (data: ProjectFormData) => {
    try {
      await createProjectMutation.mutateAsync({
        name: data.name,
        description: data.description,
        projectUrl: data.projectUrl || undefined,
        githubUrl: data.githubUrl || undefined,
        status: data.status,
        tagNames: data.tags,
      })
    } catch (error) {
      // Error handling done in mutation
      console.error('Project creation error:', error)
    }
  }

  const addTag = () => {
    if (tagInput.trim() && !form.getValues('tags').includes(tagInput.trim())) {
      const currentTags = form.getValues('tags')
      form.setValue('tags', [...currentTags, tagInput.trim()])
      setTagInput('')
    }
  }

  const removeTag = (tagToRemove: string) => {
    const currentTags = form.getValues('tags')
    form.setValue('tags', currentTags.filter(tag => tag !== tagToRemove))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addTag()
    }
  }

  const InputField: React.FC<{
    label: string
    name: keyof ProjectFormData
    type?: string
    placeholder?: string
    isTextarea?: boolean
  }> = ({ label, name, type = 'text', placeholder, isTextarea = false }) => {
    const error = form.formState.errors[name]
    
    return (
      <div>
        <label htmlFor={name} className="block text-sm font-medium text-gray-900 mb-1">
          {label}
        </label>
        {isTextarea ? (
          <textarea
            id={name}
            rows={4}
            placeholder={placeholder}
            {...form.register(name)}
            className={`block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
          />
        ) : (
          <input
            id={name}
            type={type}
            placeholder={placeholder}
            {...form.register(name)}
            className={`block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
              error ? 'border-red-300' : 'border-gray-300'
            }`}
          />
        )}
        {error && (
          <p className="mt-1 text-sm text-red-600">{error.message}</p>
        )}
      </div>
    )
  }

  const SelectField: React.FC<{
    label: string
    name: keyof ProjectFormData
    options: { value: string; label: string }[]
  }> = ({ label, name, options }) => {
    const error = form.formState.errors[name]
    
    return (
      <div>
        <label htmlFor={name} className="block text-sm font-medium text-gray-900 mb-1">
          {label}
        </label>
        <select
          id={name}
          {...form.register(name)}
          className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
            error ? 'border-red-300' : 'border-gray-300'
          }`}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && (
          <p className="mt-1 text-sm text-red-600">{error.message}</p>
        )}
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Create New Project</CardTitle>
              <CardDescription>Showcase your work and share what you've built</CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <InputField
              label="Project Name"
              name="name"
              placeholder="Enter your project name"
            />
            
            <InputField
              label="Description"
              name="description"
              placeholder="Describe what your project does and the technologies used"
              isTextarea
            />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField
                label="Live Demo URL"
                name="projectUrl"
                type="url"
                placeholder="https://your-project.com (optional)"
              />
              
              <InputField
                label="GitHub URL"
                name="githubUrl"
                type="url"
                placeholder="https://github.com/username/repo (optional)"
              />
            </div>
            
            <SelectField
              label="Status"
              name="status"
              options={[
                { value: 'in-progress', label: 'In Progress' },
                { value: 'completed', label: 'Completed' },
                { value: 'published', label: 'Published' },
              ]}
            />
            
            {/* Tags Section */}
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Technologies & Tags
              </label>
              <div className="space-y-2">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Add a technology or tag..."
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  />
                  <Button type="button" onClick={addTag}>
                    Add Tag
                  </Button>
                </div>
                
                {form.watch('tags').length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {form.watch('tags').map((tag, index) => (
                      <Badge key={index} variant="secondary" className="flex items-center gap-1">
                        {tag}
                        <button
                          type="button"
                          onClick={() => removeTag(tag)}
                          className="text-gray-500 hover:text-gray-700"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {form.formState.errors.root && (
              <div className="text-red-600 text-sm">
                {form.formState.errors.root.message}
              </div>
            )}

            <div className="flex justify-end space-x-3">
              <Button type="button" variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={createProjectMutation.isPending}
              >
                {createProjectMutation.isPending ? 'Creating...' : 'Create Project'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default ProjectForm
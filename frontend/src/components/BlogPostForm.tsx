import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { createPost } from '@/services/api'

// Blog post form schema
const blogPostSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be less than 200 characters'),
  content: z.string().min(1, 'Content is required'),
  excerpt: z.string().max(500, 'Excerpt must be less than 500 characters').optional(),
  status: z.enum(['draft', 'published']).default('draft'),
  tags: z.array(z.string()).optional().default([]),
})

type BlogPostFormData = z.infer<typeof blogPostSchema>

interface BlogPostFormProps {
  onClose: () => void
  onSuccess?: () => void
}

export const BlogPostForm: React.FC<BlogPostFormProps> = ({ onClose, onSuccess }) => {
  const [tagInput, setTagInput] = useState('')
  const queryClient = useQueryClient()

  const form = useForm<BlogPostFormData>({
    resolver: zodResolver(blogPostSchema),
    defaultValues: {
      title: '',
      content: '',
      excerpt: '',
      status: 'draft',
      tags: [],
    },
  })

  const createPostMutation = useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      form.setError('root', {
        message: error instanceof Error ? error.message : 'Failed to create post'
      })
    },
  })

  const handleSubmit = async (data: BlogPostFormData) => {
    try {
      await createPostMutation.mutateAsync({
        title: data.title,
        content: data.content,
        excerpt: data.excerpt || '',
        status: data.status,
        tagNames: data.tags,
      })
    } catch (error) {
      // Error handling done in mutation
      console.error('Post creation error:', error)
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
    name: keyof BlogPostFormData
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
            rows={name === 'content' ? 10 : 3}
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
    name: keyof BlogPostFormData
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
              <CardTitle>Create New Blog Post</CardTitle>
              <CardDescription>Share your thoughts and insights with the world</CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <InputField
              label="Title"
              name="title"
              placeholder="Enter a compelling title for your post"
            />
            
            <InputField
              label="Excerpt"
              name="excerpt"
              placeholder="A brief summary that appears in post previews (optional)"
              isTextarea
            />
            
            <InputField
              label="Content"
              name="content"
              placeholder="Write your blog post content here... (Markdown supported)"
              isTextarea
            />
            
            <SelectField
              label="Status"
              name="status"
              options={[
                { value: 'draft', label: 'Draft' },
                { value: 'published', label: 'Published' },
              ]}
            />
            
            {/* Tags Section */}
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Tags
              </label>
              <div className="space-y-2">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Add a tag..."
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
                disabled={createPostMutation.isPending}
              >
                {createPostMutation.isPending ? 'Creating...' : 'Create Post'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default BlogPostForm
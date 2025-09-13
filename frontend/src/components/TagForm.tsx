import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { createTag } from '@/services/api'

// Tag form schema
const tagSchema = z.object({
  name: z.string()
    .min(1, 'Tag name is required')
    .max(50, 'Tag name must be less than 50 characters')
    .regex(/^[a-zA-Z0-9\-_\s]+$/, 'Tag name can only contain letters, numbers, spaces, hyphens, and underscores'),
})

type TagFormData = z.infer<typeof tagSchema>

interface TagFormProps {
  onClose: () => void
  onSuccess?: () => void
}

export const TagForm: React.FC<TagFormProps> = ({ onClose, onSuccess }) => {
  const queryClient = useQueryClient()

  const form = useForm<TagFormData>({
    resolver: zodResolver(tagSchema),
    defaultValues: {
      name: '',
    },
  })

  const createTagMutation = useMutation({
    mutationFn: createTag,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] })
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      form.setError('root', {
        message: error instanceof Error ? error.message : 'Failed to create tag'
      })
    },
  })

  const handleSubmit = async (data: TagFormData) => {
    try {
      await createTagMutation.mutateAsync({
        name: data.name.trim(),
      })
    } catch (error) {
      // Error handling done in mutation
      console.error('Tag creation error:', error)
    }
  }

  const InputField: React.FC<{
    label: string
    name: keyof TagFormData
    type?: string
    placeholder?: string
  }> = ({ label, name, type = 'text', placeholder }) => {
    const error = form.formState.errors[name]
    
    return (
      <div>
        <label htmlFor={name} className="block text-sm font-medium text-gray-900 mb-1">
          {label}
        </label>
        <input
          id={name}
          type={type}
          placeholder={placeholder}
          {...form.register(name)}
          className={`block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
            error ? 'border-red-300' : 'border-gray-300'
          }`}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600">{error.message}</p>
        )}
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Create New Tag</CardTitle>
              <CardDescription>Add a new tag to organize your content</CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <InputField
              label="Tag Name"
              name="name"
              placeholder="Enter tag name (e.g., React, TypeScript, Machine Learning)"
            />

            <div className="text-sm text-gray-500">
              <p>Tags help organize and categorize your posts and projects.</p>
              <p>Use descriptive names that readers can easily understand.</p>
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
                disabled={createTagMutation.isPending}
              >
                {createTagMutation.isPending ? 'Creating...' : 'Create Tag'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default TagForm
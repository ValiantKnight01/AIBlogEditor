import React from 'react'
import { cn } from '@/lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode
}

interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className, 
  ...props 
}) => {
  return (
    <div
      className={cn(
        "rounded-lg border border-gray-200 bg-white dark:bg-slate-800 dark:border-slate-700 shadow-sm",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export const CardHeader: React.FC<CardHeaderProps> = ({ 
  children, 
  className, 
  ...props 
}) => {
  return (
    <div
      className={cn("flex flex-col space-y-1.5 p-6", className)}
      {...props}
    >
      {children}
    </div>
  )
}

export const CardContent: React.FC<CardContentProps> = ({ 
  children, 
  className, 
  ...props 
}) => {
  return (
    <div
      className={cn("p-6 pt-0", className)}
      {...props}
    >
      {children}
    </div>
  )
}

export const CardTitle: React.FC<CardTitleProps> = ({ 
  children, 
  className, 
  ...props 
}) => {
  return (
    <h3
      className={cn("text-2xl font-semibold leading-none tracking-tight", className)}
      {...props}
    >
      {children}
    </h3>
  )
}

export const CardDescription: React.FC<CardDescriptionProps> = ({ 
  children, 
  className, 
  ...props 
}) => {
  return (
    <p
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    >
      {children}
    </p>
  )
}

export default Card
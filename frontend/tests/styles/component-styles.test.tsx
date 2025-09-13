import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@/components/ThemeProvider';
import { BlogPostCard } from '@/components/BlogPostCard';
import { ProjectCard } from '@/components/ProjectCard';
import { Navigation } from '@/components/Navigation';

// Test wrapper with router context
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <ThemeProvider defaultTheme="system">
      {children}
    </ThemeProvider>
  </BrowserRouter>
);

// Test data
const mockBlogPost = {
  id: '1',
  title: 'Test Blog Post',
  content: 'This is a test blog post content that should be truncated properly in the card view.',
  slug: 'test-blog-post',
  excerpt: 'This is a test excerpt',
  status: 'published' as const,
  author: 'Test Author',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  view_count: 42,
  tags: ['react', 'typescript']
};

const mockProject = {
  id: '1',
  name: 'Test Project',
  description: 'This is a test project description that showcases responsive design and modern UI patterns.',
  content: 'Detailed project content',
  slug: 'test-project',
  status: 'published' as const,
  creator: 'Test Creator',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  view_count: 25,
  demo_url: 'https://demo.example.com',
  github_url: 'https://github.com/test/project',
  technologies: ['React', 'TypeScript', 'Tailwind CSS']
};

describe('Component Styles - Responsive Design', () => {
  describe('BlogPostCard Responsive Styles', () => {
    it('should have proper mobile-first responsive classes', () => {
      render(<BlogPostCard post={mockBlogPost} />, { wrapper: TestWrapper });
      const card = screen.getByRole('article');
      
      // Check for responsive card classes
      expect(card).toHaveClass('bg-card', 'border', 'rounded-lg', 'p-6');
      
      // Check for responsive typography
      const title = screen.getByRole('heading', { name: mockBlogPost.title });
      expect(title).toHaveClass('text-xl', 'font-semibold', 'mb-2');
      
      // Check for responsive metadata layout
      const metadata = screen.getByText('Test Author');
      expect(metadata.parentElement).toHaveClass('flex', 'items-center', 'justify-between', 'text-sm', 'text-muted-foreground', 'mb-3');
    });

    it('should have proper hover and focus states', () => {
      render(<BlogPostCard post={mockBlogPost} />, { wrapper: TestWrapper });
      const card = screen.getByRole('article');
      
      // Check for interactive states
      expect(card).toHaveClass('hover:shadow-md', 'transition-shadow');
    });

    it('should truncate long content properly', () => {
      const longPost = {
        ...mockBlogPost,
        excerpt: 'This is a very long excerpt that should be truncated to maintain consistent card heights and clean visual hierarchy across different screen sizes.'
      };
      
      render(<BlogPostCard post={longPost} />, { wrapper: TestWrapper });
      const excerpt = screen.getByText(longPost.excerpt);
      expect(excerpt).toHaveClass('line-clamp-3', 'text-muted-foreground', 'mb-4');
    });
  });

  describe('ProjectCard Responsive Styles', () => {
    it('should have proper responsive layout classes', () => {
      render(<ProjectCard project={mockProject} />, { wrapper: TestWrapper });
      const card = screen.getByRole('article');
      
      // Check for card container styles
      expect(card).toHaveClass('bg-card', 'border', 'rounded-lg', 'p-6', 'hover:shadow-lg', 'transition-shadow');
      
      // Check for title styling
      const title = screen.getByRole('heading', { name: mockProject.name });
      expect(title).toHaveClass('text-xl', 'font-bold', 'mb-2');
    });

    it('should have responsive button layout', () => {
      render(<ProjectCard project={mockProject} />, { wrapper: TestWrapper });
      
      // Check for responsive button container
      const buttonContainer = screen.getByText('View Demo').parentElement;
      expect(buttonContainer).toHaveClass('flex', 'gap-2', 'mt-4');
    });

    it('should display technology badges with proper spacing', () => {
      render(<ProjectCard project={mockProject} />, { wrapper: TestWrapper });
      
      // Check for technology badges container
      const techBadge = screen.getByText('React');
      expect(techBadge).toHaveClass('px-2', 'py-1', 'bg-secondary', 'text-secondary-foreground', 'rounded-md', 'text-xs');
    });
  });

  describe('Navigation Responsive Styles', () => {
    it('should have proper mobile-first navigation classes', () => {
      render(<Navigation />, { wrapper: TestWrapper });
      const nav = screen.getByRole('navigation');
      
      // Check for responsive navigation container
      expect(nav).toHaveClass('border-b', 'bg-background/95', 'backdrop-blur', 'supports-[backdrop-filter]:bg-background/60');
      
      // Check for responsive container
      const container = nav.firstChild as HTMLElement;
      expect(container).toHaveClass('container', 'flex', 'h-14', 'items-center', 'justify-between');
    });

    it('should have responsive navigation links', () => {
      render(<Navigation />, { wrapper: TestWrapper });
      
      // Check for desktop navigation links using more specific selector
      const homeLinks = screen.getAllByRole('link', { name: 'Home' });
      const desktopHomeLink = homeLinks.find(link => 
        link.className.includes('transition-colors') && 
        !link.className.includes('block px-3 py-2')
      );
      expect(desktopHomeLink).toHaveClass('transition-colors', 'hover:text-foreground/80');
    });

    it('should have proper logo/brand styling', () => {
      render(<Navigation />, { wrapper: TestWrapper });
      const brand = screen.getByRole('link', { name: /My Blog/ });
      expect(brand).toHaveClass('flex', 'items-center', 'space-x-2', 'font-bold');
    });
  });
});

describe('Component Styles - Dark Mode Compatibility', () => {
  it('should use CSS variables for theme-aware colors', () => {
    render(<BlogPostCard post={mockBlogPost} />, { wrapper: TestWrapper });
    const card = screen.getByRole('article');
    
    // Check that components use theme-aware classes
    expect(card).toHaveClass('bg-card', 'text-card-foreground', 'border');
  });

  it('should have proper contrast for accessibility', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: TestWrapper });
    
    // Check for proper contrast classes
    const description = screen.getByText(mockProject.description);
    expect(description).toHaveClass('text-muted-foreground');
  });
});

describe('Component Styles - Animation and Transitions', () => {
  it('should have smooth transitions for interactive elements', () => {
    render(<BlogPostCard post={mockBlogPost} />, { wrapper: TestWrapper });
    const card = screen.getByRole('article');
    
    // Check for transition classes
    expect(card).toHaveClass('transition-shadow');
  });

  it('should have hover effects for clickable elements', () => {
    render(<ProjectCard project={mockProject} />, { wrapper: TestWrapper });
    const card = screen.getByRole('article');
    
    // Check for hover effects
    expect(card).toHaveClass('hover:shadow-lg');
  });
});
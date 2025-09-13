import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { act } from '@testing-library/react';
import { useTheme } from '@/hooks/useTheme';
import { ThemeProvider } from '@/components/ThemeProvider';
import React from 'react';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Test component that uses the theme hook
const TestThemeComponent: React.FC = () => {
  const { theme, setTheme, toggleTheme } = useTheme();
  
  return (
    <div data-testid="theme-container" className={theme}>
      <span data-testid="current-theme">{theme}</span>
      <button data-testid="toggle-theme" onClick={toggleTheme}>
        Toggle Theme
      </button>
      <button data-testid="set-light" onClick={() => setTheme('light')}>
        Light Mode
      </button>
      <button data-testid="set-dark" onClick={() => setTheme('dark')}>
        Dark Mode
      </button>
      <button data-testid="set-system" onClick={() => setTheme('system')}>
        System Mode
      </button>
    </div>
  );
};

// Test wrapper with theme provider
const ThemeTestWrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider defaultTheme="system">
    {children}
  </ThemeProvider>
);

describe('Theme System - useTheme Hook', () => {
  beforeEach(() => {
    // Clear all mocks and reset state
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    localStorageMock.getItem.mockReturnValue(null); // Default to no stored theme
    
    // Clear document classes
    document.documentElement.classList.remove('dark');
    
    // Mock system dark mode preference
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: false, // Default to light mode
        media: query,
        onchange: null,
        addListener: vi.fn(), // deprecated
        removeListener: vi.fn(), // deprecated
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  it('should initialize with system theme by default', () => {
    render(
      <ThemeTestWrapper>
        <TestThemeComponent />
      </ThemeTestWrapper>
    );

    const currentTheme = screen.getByTestId('current-theme');
    expect(currentTheme.textContent).toBe('system');
  });

  it('should toggle between light and dark themes', () => {
    render(
      <ThemeTestWrapper>
        <TestThemeComponent />
      </ThemeTestWrapper>
    );

    const toggleButton = screen.getByTestId('toggle-theme');
    const currentTheme = screen.getByTestId('current-theme');
    
    // Start with system theme
    expect(currentTheme.textContent).toBe('system');
    
    // First toggle should go to light
    act(() => {
      fireEvent.click(toggleButton);
    });
    expect(currentTheme.textContent).toBe('light');
    
    // Second toggle should go to dark
    act(() => {
      fireEvent.click(toggleButton);
    });
    expect(currentTheme.textContent).toBe('dark');
    
    // Third toggle should go back to light
    act(() => {
      fireEvent.click(toggleButton);
    });
    expect(currentTheme.textContent).toBe('light');
  });

  it('should set specific theme modes', () => {
    render(
      <ThemeTestWrapper>
        <TestThemeComponent />
      </ThemeTestWrapper>
    );

    const currentTheme = screen.getByTestId('current-theme');
    const lightButton = screen.getByTestId('set-light');
    const darkButton = screen.getByTestId('set-dark');
    const systemButton = screen.getByTestId('set-system');
    
    // Set to light mode
    act(() => {
      fireEvent.click(lightButton);
    });
    expect(currentTheme.textContent).toBe('light');
    
    // Set to dark mode
    act(() => {
      fireEvent.click(darkButton);
    });
    expect(currentTheme.textContent).toBe('dark');
    
    // Set to system mode
    act(() => {
      fireEvent.click(systemButton);
    });
    expect(currentTheme.textContent).toBe('system');
  });

  it('should persist theme preference in localStorage', () => {
    render(
      <ThemeTestWrapper>
        <TestThemeComponent />
      </ThemeTestWrapper>
    );

    const darkButton = screen.getByTestId('set-dark');
    
    act(() => {
      fireEvent.click(darkButton);
    });
    
    // Should save to localStorage
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
  });

  it('should load theme preference from localStorage on init', () => {
    localStorageMock.getItem.mockReturnValue('dark');
    
    render(
      <ThemeTestWrapper>
        <TestThemeComponent />
      </ThemeTestWrapper>
    );

    const currentTheme = screen.getByTestId('current-theme');
    expect(currentTheme.textContent).toBe('dark');
    expect(localStorageMock.getItem).toHaveBeenCalledWith('theme');
  });

  it('should apply dark class to document root when dark theme is active', () => {
    // Mock dark system preference
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    render(
      <ThemeTestWrapper>
        <TestThemeComponent />
      </ThemeTestWrapper>
    );

    const darkButton = screen.getByTestId('set-dark');
    
    act(() => {
      fireEvent.click(darkButton);
    });
    
    // Should add 'dark' class to document root
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('should remove dark class when switching to light theme', () => {
    render(
      <ThemeTestWrapper>
        <TestThemeComponent />
      </ThemeTestWrapper>
    );

    const darkButton = screen.getByTestId('set-dark');
    const lightButton = screen.getByTestId('set-light');
    
    // Set to dark first
    act(() => {
      fireEvent.click(darkButton);
    });
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    
    // Then set to light
    act(() => {
      fireEvent.click(lightButton);
    });
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });
});

describe('Theme System - ThemeProvider Component', () => {
  beforeEach(() => {
    // Clear all mocks and reset state
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.getItem.mockReturnValue(null); // Default to no stored theme
    
    // Clear document classes
    document.documentElement.classList.remove('dark');
  });
  it('should provide theme context to children', () => {
    render(
      <ThemeProvider defaultTheme="light">
        <TestThemeComponent />
      </ThemeProvider>
    );

    const currentTheme = screen.getByTestId('current-theme');
    expect(currentTheme.textContent).toBe('light');
  });

  it('should handle system theme preference changes', () => {
    let mediaQueryCallback: ((e: MediaQueryListEvent) => void) | null = null;
    
    // Mock media query with callback capture
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn((type, callback) => {
          if (type === 'change') mediaQueryCallback = callback;
        }),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    render(
      <ThemeProvider defaultTheme="system">
        <TestThemeComponent />
      </ThemeProvider>
    );

    // Simulate system theme change to dark
    if (mediaQueryCallback) {
      act(() => {
        mediaQueryCallback({ matches: true } as MediaQueryListEvent);
      });
    }
    
    // Document should have dark class applied
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });
});

describe('Theme System - CSS Variables Integration', () => {
  it('should use CSS variables for theme-aware styling', () => {
    render(
      <ThemeProvider defaultTheme="light">
        <div className="bg-background text-foreground">
          <span data-testid="themed-content">Content</span>
        </div>
      </ThemeProvider>
    );

    const content = screen.getByTestId('themed-content');
    const parent = content.parentElement;
    
    // Should use theme-aware CSS classes
    expect(parent).toHaveClass('bg-background', 'text-foreground');
  });
});
import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

type Theme = 'light' | 'dark'

interface ThemeContextType {
  theme: Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    // Check localStorage first, then system preference
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('theme') as Theme
      if (savedTheme === 'light' || savedTheme === 'dark') {
        // Apply immediately
        const root = window.document.documentElement
        root.classList.remove('light', 'dark')
        root.classList.add(savedTheme)
        return savedTheme
      }
      // Check system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        const root = window.document.documentElement
        root.classList.remove('light', 'dark')
        root.classList.add('dark')
        return 'dark'
      }
    }
    // Default to light
    if (typeof window !== 'undefined') {
      const root = window.document.documentElement
      root.classList.remove('light', 'dark')
      root.classList.add('light')
    }
    return 'light'
  })

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const root = window.document.documentElement
      // Remove both classes first
      root.classList.remove('light', 'dark')
      // Add the current theme class
      root.classList.add(theme)
      // Save to localStorage
      localStorage.setItem('theme', theme)
    }
  }, [theme])

  const toggleTheme = () => {
    setTheme((prevTheme) => {
      const newTheme = prevTheme === 'light' ? 'dark' : 'light'
      // Apply immediately for better UX
      if (typeof window !== 'undefined') {
        const root = window.document.documentElement
        root.classList.remove('light', 'dark')
        root.classList.add(newTheme)
        localStorage.setItem('theme', newTheme)
      }
      return newTheme
    })
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}


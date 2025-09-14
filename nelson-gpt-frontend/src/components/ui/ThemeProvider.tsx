import React, { createContext, useContext, useEffect, useState } from 'react'
import { useUserStore } from '../../store/userStore'
import type { ThemeMode } from '../../types'

interface ThemeContextType {
  theme: ThemeMode
  setTheme: (theme: ThemeMode) => void
  isDark: boolean
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: React.ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const { preferences, updatePreferences } = useUserStore()
  const [isDark, setIsDark] = useState(false)

  const setTheme = (theme: ThemeMode) => {
    updatePreferences({ theme })
  }

  useEffect(() => {
    const root = document.documentElement
    
    const applyTheme = (theme: ThemeMode) => {
      if (theme === 'auto') {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        const systemIsDark = mediaQuery.matches
        
        root.classList.toggle('dark', systemIsDark)
        setIsDark(systemIsDark)
        
        // Listen for system theme changes
        const handleChange = (e: MediaQueryListEvent) => {
          root.classList.toggle('dark', e.matches)
          setIsDark(e.matches)
        }
        
        mediaQuery.addEventListener('change', handleChange)
        return () => mediaQuery.removeEventListener('change', handleChange)
      } else {
        const darkMode = theme === 'dark'
        root.classList.toggle('dark', darkMode)
        setIsDark(darkMode)
      }
    }

    const cleanup = applyTheme(preferences.theme)
    
    return cleanup
  }, [preferences.theme])

  const value: ThemeContextType = {
    theme: preferences.theme,
    setTheme,
    isDark
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}


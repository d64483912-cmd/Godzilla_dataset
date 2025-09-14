import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { User, UserPreferences, ThemeMode } from '../types'

interface UserState {
  user: User | null
  isAuthenticated: boolean
  preferences: UserPreferences
  
  // Actions
  setUser: (user: User) => void
  clearUser: () => void
  updatePreferences: (preferences: Partial<UserPreferences>) => void
  loadUserPreferences: () => Promise<void>
  saveUserPreferences: () => Promise<void>
}

const defaultPreferences: UserPreferences = {
  theme: 'auto',
  fontSize: 'base',
  responseStyle: 'detailed',
  showMedicalDisclaimer: false,
  enableNotifications: true,
  autoSave: true
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      preferences: defaultPreferences,

      setUser: (user: User) => {
        set({ 
          user, 
          isAuthenticated: true,
          preferences: { ...defaultPreferences, ...user.preferences }
        })
      },

      clearUser: () => {
        set({ 
          user: null, 
          isAuthenticated: false,
          preferences: defaultPreferences
        })
      },

      updatePreferences: (newPreferences: Partial<UserPreferences>) => {
        const currentPreferences = get().preferences
        const updatedPreferences = { ...currentPreferences, ...newPreferences }
        
        set({ preferences: updatedPreferences })
        
        // Update user object if exists
        const user = get().user
        if (user) {
          set({
            user: {
              ...user,
              preferences: updatedPreferences
            }
          })
        }
        
        // Apply theme changes immediately
        if (newPreferences.theme) {
          applyTheme(newPreferences.theme)
        }
        
        // Apply font size changes
        if (newPreferences.fontSize) {
          applyFontSize(newPreferences.fontSize)
        }
        
        // Save to backend if user is authenticated
        if (get().isAuthenticated) {
          get().saveUserPreferences()
        }
      },

      loadUserPreferences: async () => {
        try {
          // Load from localStorage first (handled by persist middleware)
          const preferences = get().preferences
          
          // Apply theme and font size
          applyTheme(preferences.theme)
          applyFontSize(preferences.fontSize)
          
          // If user is authenticated, sync with backend
          if (get().isAuthenticated) {
            // TODO: Implement API call to load user preferences
            console.log('Loading user preferences from backend...')
          }
        } catch (error) {
          console.error('Failed to load user preferences:', error)
        }
      },

      saveUserPreferences: async () => {
        try {
          if (!get().isAuthenticated) return
          
          const preferences = get().preferences
          
          // TODO: Implement API call to save user preferences
          console.log('Saving user preferences to backend:', preferences)
          
        } catch (error) {
          console.error('Failed to save user preferences:', error)
        }
      }
    }),
    {
      name: 'nelson-gpt-user',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        preferences: state.preferences,
        user: state.user ? {
          ...state.user,
          // Don't persist sensitive data
          lastActive: undefined
        } : null
      })
    }
  )
)

// Theme application helper
function applyTheme(theme: ThemeMode) {
  const root = document.documentElement
  
  if (theme === 'auto') {
    // Use system preference
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const isDark = mediaQuery.matches
    
    root.classList.toggle('dark', isDark)
    
    // Listen for system theme changes
    const handleChange = (e: MediaQueryListEvent) => {
      root.classList.toggle('dark', e.matches)
    }
    
    mediaQuery.addEventListener('change', handleChange)
    
    // Cleanup function would be needed in a real implementation
    return () => mediaQuery.removeEventListener('change', handleChange)
  } else {
    root.classList.toggle('dark', theme === 'dark')
  }
}

// Font size application helper
function applyFontSize(fontSize: UserPreferences['fontSize']) {
  const root = document.documentElement
  
  // Remove existing font size classes
  root.classList.remove('text-sm', 'text-base', 'text-lg')
  
  // Apply new font size class
  root.classList.add(`text-${fontSize}`)
  
  // Also set CSS custom property for more granular control
  const fontSizeMap = {
    sm: '14px',
    base: '16px',
    lg: '18px'
  }
  
  root.style.setProperty('--base-font-size', fontSizeMap[fontSize])
}

// Accessibility helpers
export const useAccessibilityPreferences = () => {
  const preferences = useUserStore(state => state.preferences)
  const updatePreferences = useUserStore(state => state.updatePreferences)
  
  return {
    highContrast: preferences.theme === 'dark',
    fontSize: preferences.fontSize,
    reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    
    toggleHighContrast: () => {
      updatePreferences({
        theme: preferences.theme === 'dark' ? 'light' : 'dark'
      })
    },
    
    increaseFontSize: () => {
      const sizes: UserPreferences['fontSize'][] = ['sm', 'base', 'lg']
      const currentIndex = sizes.indexOf(preferences.fontSize)
      const nextIndex = Math.min(currentIndex + 1, sizes.length - 1)
      updatePreferences({ fontSize: sizes[nextIndex] })
    },
    
    decreaseFontSize: () => {
      const sizes: UserPreferences['fontSize'][] = ['sm', 'base', 'lg']
      const currentIndex = sizes.indexOf(preferences.fontSize)
      const nextIndex = Math.max(currentIndex - 1, 0)
      updatePreferences({ fontSize: sizes[nextIndex] })
    }
  }
}


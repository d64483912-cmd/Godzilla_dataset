import React, { createContext, useContext, useEffect, useState } from 'react'
import { useUserStore } from '../../store/userStore'
import { a11yUtils } from '../../utils/helpers'

interface AccessibilityContextType {
  highContrast: boolean
  reducedMotion: boolean
  fontSize: 'sm' | 'base' | 'lg'
  screenReaderOptimized: boolean
  keyboardNavigation: boolean
  
  // Actions
  toggleHighContrast: () => void
  toggleReducedMotion: () => void
  increaseFontSize: () => void
  decreaseFontSize: () => void
  announceToScreenReader: (message: string) => void
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined)

export function useAccessibility() {
  const context = useContext(AccessibilityContext)
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider')
  }
  return context
}

interface AccessibilityProviderProps {
  children: React.ReactNode
}

export function AccessibilityProvider({ children }: AccessibilityProviderProps) {
  const { preferences, updatePreferences } = useUserStore()
  const [highContrast, setHighContrast] = useState(false)
  const [reducedMotion, setReducedMotion] = useState(false)
  const [screenReaderOptimized, setScreenReaderOptimized] = useState(false)
  const [keyboardNavigation, setKeyboardNavigation] = useState(false)

  // Initialize accessibility preferences
  useEffect(() => {
    // Check system preferences
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)')
    
    setReducedMotion(prefersReducedMotion.matches)
    setHighContrast(prefersHighContrast.matches || preferences.theme === 'dark')
    
    // Listen for changes
    const handleReducedMotionChange = (e: MediaQueryListEvent) => {
      setReducedMotion(e.matches)
      document.documentElement.classList.toggle('reduce-motion', e.matches)
    }
    
    const handleHighContrastChange = (e: MediaQueryListEvent) => {
      setHighContrast(e.matches)
      document.documentElement.classList.toggle('high-contrast', e.matches)
    }
    
    prefersReducedMotion.addEventListener('change', handleReducedMotionChange)
    prefersHighContrast.addEventListener('change', handleHighContrastChange)
    
    // Apply initial classes
    document.documentElement.classList.toggle('reduce-motion', prefersReducedMotion.matches)
    document.documentElement.classList.toggle('high-contrast', prefersHighContrast.matches)
    
    return () => {
      prefersReducedMotion.removeEventListener('change', handleReducedMotionChange)
      prefersHighContrast.removeEventListener('change', handleHighContrastChange)
    }
  }, [preferences.theme])

  // Detect screen reader usage
  useEffect(() => {
    const detectScreenReader = () => {
      // Check for common screen reader indicators
      const hasScreenReader = 
        navigator.userAgent.includes('NVDA') ||
        navigator.userAgent.includes('JAWS') ||
        navigator.userAgent.includes('VoiceOver') ||
        window.speechSynthesis?.getVoices().length > 0
      
      setScreenReaderOptimized(hasScreenReader)
      
      if (hasScreenReader) {
        document.documentElement.classList.add('screen-reader-optimized')
      }
    }
    
    // Check immediately and after voices are loaded
    detectScreenReader()
    window.speechSynthesis?.addEventListener('voiceschanged', detectScreenReader)
    
    return () => {
      window.speechSynthesis?.removeEventListener('voiceschanged', detectScreenReader)
    }
  }, [])

  // Detect keyboard navigation
  useEffect(() => {
    let isUsingKeyboard = false
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        isUsingKeyboard = true
        setKeyboardNavigation(true)
        document.documentElement.classList.add('keyboard-navigation')
      }
    }
    
    const handleMouseDown = () => {
      if (isUsingKeyboard) {
        isUsingKeyboard = false
        setKeyboardNavigation(false)
        document.documentElement.classList.remove('keyboard-navigation')
      }
    }
    
    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('mousedown', handleMouseDown)
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('mousedown', handleMouseDown)
    }
  }, [])

  // Apply font size changes
  useEffect(() => {
    const root = document.documentElement
    const fontSizeMap = {
      sm: '14px',
      base: '16px',
      lg: '18px'
    }
    
    root.style.setProperty('--base-font-size', fontSizeMap[preferences.fontSize])
    root.classList.remove('text-sm', 'text-base', 'text-lg')
    root.classList.add(`text-${preferences.fontSize}`)
  }, [preferences.fontSize])

  const toggleHighContrast = () => {
    const newHighContrast = !highContrast
    setHighContrast(newHighContrast)
    document.documentElement.classList.toggle('high-contrast', newHighContrast)
    
    // Update theme preference
    updatePreferences({
      theme: newHighContrast ? 'dark' : 'light'
    })
    
    a11yUtils.announceToScreenReader(
      newHighContrast ? 'High contrast mode enabled' : 'High contrast mode disabled'
    )
  }

  const toggleReducedMotion = () => {
    const newReducedMotion = !reducedMotion
    setReducedMotion(newReducedMotion)
    document.documentElement.classList.toggle('reduce-motion', newReducedMotion)
    
    a11yUtils.announceToScreenReader(
      newReducedMotion ? 'Reduced motion enabled' : 'Reduced motion disabled'
    )
  }

  const increaseFontSize = () => {
    const sizes: Array<'sm' | 'base' | 'lg'> = ['sm', 'base', 'lg']
    const currentIndex = sizes.indexOf(preferences.fontSize)
    const nextIndex = Math.min(currentIndex + 1, sizes.length - 1)
    
    if (nextIndex !== currentIndex) {
      updatePreferences({ fontSize: sizes[nextIndex] })
      a11yUtils.announceToScreenReader(`Font size increased to ${sizes[nextIndex]}`)
    }
  }

  const decreaseFontSize = () => {
    const sizes: Array<'sm' | 'base' | 'lg'> = ['sm', 'base', 'lg']
    const currentIndex = sizes.indexOf(preferences.fontSize)
    const nextIndex = Math.max(currentIndex - 1, 0)
    
    if (nextIndex !== currentIndex) {
      updatePreferences({ fontSize: sizes[nextIndex] })
      a11yUtils.announceToScreenReader(`Font size decreased to ${sizes[nextIndex]}`)
    }
  }

  const announceToScreenReader = (message: string) => {
    a11yUtils.announceToScreenReader(message)
  }

  const value: AccessibilityContextType = {
    highContrast,
    reducedMotion,
    fontSize: preferences.fontSize,
    screenReaderOptimized,
    keyboardNavigation,
    
    toggleHighContrast,
    toggleReducedMotion,
    increaseFontSize,
    decreaseFontSize,
    announceToScreenReader
  }

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
      
      {/* Skip to main content link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-medical-primary text-white px-4 py-2 rounded-lg z-50 focus:z-50"
        onFocus={() => announceToScreenReader('Skip to main content link focused')}
      >
        Skip to main content
      </a>
      
      {/* Accessibility toolbar for keyboard users */}
      {keyboardNavigation && (
        <div
          className="fixed top-0 left-0 right-0 bg-medical-primary text-white p-2 z-40 flex items-center justify-center space-x-4 text-sm"
          role="toolbar"
          aria-label="Accessibility options"
        >
          <button
            onClick={toggleHighContrast}
            className="px-2 py-1 rounded hover:bg-medical-primary-dark focus:bg-medical-primary-dark"
            aria-pressed={highContrast}
          >
            {highContrast ? 'Disable' : 'Enable'} High Contrast
          </button>
          <button
            onClick={decreaseFontSize}
            className="px-2 py-1 rounded hover:bg-medical-primary-dark focus:bg-medical-primary-dark"
            disabled={preferences.fontSize === 'sm'}
          >
            A-
          </button>
          <button
            onClick={increaseFontSize}
            className="px-2 py-1 rounded hover:bg-medical-primary-dark focus:bg-medical-primary-dark"
            disabled={preferences.fontSize === 'lg'}
          >
            A+
          </button>
          <button
            onClick={toggleReducedMotion}
            className="px-2 py-1 rounded hover:bg-medical-primary-dark focus:bg-medical-primary-dark"
            aria-pressed={reducedMotion}
          >
            {reducedMotion ? 'Enable' : 'Reduce'} Motion
          </button>
        </div>
      )}
    </AccessibilityContext.Provider>
  )
}


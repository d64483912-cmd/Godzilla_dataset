import { clsx, type ClassValue } from 'clsx'

/**
 * Utility function to combine class names
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

/**
 * Generate a unique ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Format date for display
 */
export function formatDate(date: Date, format: 'short' | 'long' | 'time' = 'short'): string {
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  // Less than a minute ago
  if (diffInSeconds < 60) {
    return 'Just now'
  }
  
  // Less than an hour ago
  if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  }
  
  // Less than a day ago
  if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  }
  
  // Less than a week ago
  if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days} day${days > 1 ? 's' : ''} ago`
  }
  
  // Format based on requested format
  switch (format) {
    case 'long':
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    case 'time':
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    default:
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      })
  }
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Throttle function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * Format file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Truncate text
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * Validate email
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Medical unit conversion utilities
 */
export const medicalUnits = {
  // Weight conversions
  kgToLbs: (kg: number): number => kg * 2.20462,
  lbsToKg: (lbs: number): number => lbs / 2.20462,
  
  // Height conversions
  cmToInches: (cm: number): number => cm / 2.54,
  inchesToCm: (inches: number): number => inches * 2.54,
  
  // Temperature conversions
  celsiusToFahrenheit: (celsius: number): number => (celsius * 9/5) + 32,
  fahrenheitToCelsius: (fahrenheit: number): number => (fahrenheit - 32) * 5/9,
  
  // Dosage calculations
  calculateDosePerKg: (totalDose: number, weightKg: number): number => totalDose / weightKg,
  calculateTotalDose: (dosePerKg: number, weightKg: number): number => dosePerKg * weightKg
}

/**
 * Age calculation utilities
 */
export const ageUtils = {
  calculateAge: (birthDate: Date): { years: number; months: number; days: number } => {
    const now = new Date()
    const birth = new Date(birthDate)
    
    let years = now.getFullYear() - birth.getFullYear()
    let months = now.getMonth() - birth.getMonth()
    let days = now.getDate() - birth.getDate()
    
    if (days < 0) {
      months--
      const lastMonth = new Date(now.getFullYear(), now.getMonth(), 0)
      days += lastMonth.getDate()
    }
    
    if (months < 0) {
      years--
      months += 12
    }
    
    return { years, months, days }
  },
  
  ageInMonths: (birthDate: Date): number => {
    const now = new Date()
    const birth = new Date(birthDate)
    
    const yearDiff = now.getFullYear() - birth.getFullYear()
    const monthDiff = now.getMonth() - birth.getMonth()
    
    return yearDiff * 12 + monthDiff
  },
  
  ageInDays: (birthDate: Date): number => {
    const now = new Date()
    const birth = new Date(birthDate)
    
    const timeDiff = now.getTime() - birth.getTime()
    return Math.floor(timeDiff / (1000 * 3600 * 24))
  }
}

/**
 * Pediatric growth percentile utilities
 */
export const growthUtils = {
  // WHO growth standards (simplified - in production, use actual WHO data)
  getWeightPercentile: (weightKg: number, ageMonths: number, gender: 'male' | 'female'): number => {
    // This is a simplified calculation - in production, use WHO growth charts
    // Return mock percentile for demonstration
    return Math.min(Math.max(Math.random() * 100, 3), 97)
  },
  
  getHeightPercentile: (heightCm: number, ageMonths: number, gender: 'male' | 'female'): number => {
    // This is a simplified calculation - in production, use WHO growth charts
    return Math.min(Math.max(Math.random() * 100, 3), 97)
  },
  
  getBMIPercentile: (weightKg: number, heightCm: number, ageMonths: number, gender: 'male' | 'female'): number => {
    const bmi = weightKg / Math.pow(heightCm / 100, 2)
    // This is a simplified calculation - in production, use CDC BMI charts
    return Math.min(Math.max(Math.random() * 100, 3), 97)
  }
}

/**
 * Medical calculation utilities
 */
export const medicalCalcs = {
  // Body Surface Area (Mosteller formula)
  calculateBSA: (weightKg: number, heightCm: number): number => {
    return Math.sqrt((weightKg * heightCm) / 3600)
  },
  
  // Ideal Body Weight (pediatric)
  calculateIBW: (heightCm: number, ageYears: number): number => {
    if (ageYears < 1) {
      // For infants, use weight-for-length charts
      return heightCm * 0.1 // Simplified calculation
    } else if (ageYears < 18) {
      // Simplified pediatric IBW calculation
      return (heightCm - 100) * 0.9
    }
    return heightCm - 100 // Adult formula (simplified)
  },
  
  // Creatinine clearance (Schwartz formula for pediatrics)
  calculateCreatinineClearance: (heightCm: number, serumCreatinine: number, k: number = 0.413): number => {
    return (k * heightCm) / serumCreatinine
  }
}

/**
 * Text processing utilities for medical content
 */
export const textUtils = {
  // Extract medical units from text
  extractMedicalUnits: (text: string): Array<{ value: number; unit: string; context: string }> => {
    const unitRegex = /(\d+(?:\.\d+)?)\s*(mg|kg|ml|mcg|g|l|mmol|mEq|units?|iu|mg\/kg|ml\/hr|bpm|mmHg)/gi
    const matches = text.matchAll(unitRegex)
    
    return Array.from(matches).map(match => ({
      value: parseFloat(match[1]),
      unit: match[2].toLowerCase(),
      context: match[0]
    }))
  },
  
  // Highlight search terms in text
  highlightSearchTerms: (text: string, searchTerms: string[]): string => {
    let highlightedText = text
    
    searchTerms.forEach(term => {
      const regex = new RegExp(`(${term})`, 'gi')
      highlightedText = highlightedText.replace(regex, '<mark>$1</mark>')
    })
    
    return highlightedText
  },
  
  // Clean and format medical text
  formatMedicalText: (text: string): string => {
    return text
      .replace(/\s+/g, ' ') // Normalize whitespace
      .replace(/([a-z])([A-Z])/g, '$1 $2') // Add space before capital letters
      .trim()
  }
}

/**
 * Accessibility utilities
 */
export const a11yUtils = {
  // Generate accessible IDs
  generateA11yId: (prefix: string = 'element'): string => {
    return `${prefix}-${generateId()}`
  },
  
  // Check if user prefers reduced motion
  prefersReducedMotion: (): boolean => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  },
  
  // Announce to screen readers
  announceToScreenReader: (message: string): void => {
    const announcement = document.createElement('div')
    announcement.setAttribute('aria-live', 'polite')
    announcement.setAttribute('aria-atomic', 'true')
    announcement.className = 'sr-only'
    announcement.textContent = message
    
    document.body.appendChild(announcement)
    
    setTimeout(() => {
      document.body.removeChild(announcement)
    }, 1000)
  }
}

/**
 * Error handling utilities
 */
export const errorUtils = {
  // Format error messages for display
  formatErrorMessage: (error: unknown): string => {
    if (error instanceof Error) {
      return error.message
    }
    if (typeof error === 'string') {
      return error
    }
    return 'An unexpected error occurred'
  },
  
  // Check if error is network-related
  isNetworkError: (error: unknown): boolean => {
    if (error instanceof Error) {
      return error.message.toLowerCase().includes('network') ||
             error.message.toLowerCase().includes('fetch') ||
             error.message.toLowerCase().includes('connection')
    }
    return false
  }
}

/**
 * Local storage utilities with error handling
 */
export const storageUtils = {
  setItem: (key: string, value: any): boolean => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
      return true
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
      return false
    }
  },
  
  getItem: <T>(key: string, defaultValue: T): T => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue
    } catch (error) {
      console.error('Failed to read from localStorage:', error)
      return defaultValue
    }
  },
  
  removeItem: (key: string): boolean => {
    try {
      localStorage.removeItem(key)
      return true
    } catch (error) {
      console.error('Failed to remove from localStorage:', error)
      return false
    }
  }
}


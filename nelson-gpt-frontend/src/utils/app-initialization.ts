/**
 * Application initialization utilities
 * Handles PWA setup, error monitoring, and initial app configuration
 */

import { storageUtils, a11yUtils } from './helpers'

interface InitializationConfig {
  enableErrorReporting: boolean
  enableAnalytics: boolean
  enablePerformanceMonitoring: boolean
}

/**
 * Initialize the application
 */
export async function initializeApp(config: InitializationConfig = {
  enableErrorReporting: true,
  enableAnalytics: false, // Disabled for medical privacy
  enablePerformanceMonitoring: true
}): Promise<void> {
  console.log('🏥 Initializing Nelson-GPT...')
  
  try {
    // Initialize error reporting
    if (config.enableErrorReporting) {
      await initializeErrorReporting()
    }
    
    // Initialize performance monitoring
    if (config.enablePerformanceMonitoring) {
      await initializePerformanceMonitoring()
    }
    
    // Initialize accessibility features
    await initializeAccessibility()
    
    // Initialize PWA features
    await initializePWA()
    
    // Initialize medical compliance features
    await initializeMedicalCompliance()
    
    // Initialize offline capabilities
    await initializeOfflineCapabilities()
    
    console.log('✅ Nelson-GPT initialized successfully')
    
  } catch (error) {
    console.error('❌ Failed to initialize Nelson-GPT:', error)
    throw error
  }
}

/**
 * Initialize error reporting and monitoring
 */
async function initializeErrorReporting(): Promise<void> {
  // Global error handler
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error)
    
    // Log error details (in production, send to monitoring service)
    const errorInfo = {
      message: event.error?.message || 'Unknown error',
      stack: event.error?.stack,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    }
    
    // Store error locally for debugging
    const errors = storageUtils.getItem('nelson-gpt-errors', [])
    errors.push(errorInfo)
    
    // Keep only last 10 errors to prevent storage bloat
    if (errors.length > 10) {
      errors.splice(0, errors.length - 10)
    }
    
    storageUtils.setItem('nelson-gpt-errors', errors)
  })
  
  // Unhandled promise rejection handler
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason)
    
    const errorInfo = {
      type: 'unhandledrejection',
      reason: event.reason?.toString() || 'Unknown rejection',
      timestamp: new Date().toISOString(),
      url: window.location.href
    }
    
    const errors = storageUtils.getItem('nelson-gpt-errors', [])
    errors.push(errorInfo)
    storageUtils.setItem('nelson-gpt-errors', errors)
  })
}

/**
 * Initialize performance monitoring
 */
async function initializePerformanceMonitoring(): Promise<void> {
  // Monitor Core Web Vitals in production
  if (import.meta.env.PROD) {
    try {
      const { getCLS, getFID, getFCP, getLCP, getTTFB } = await import('web-vitals')
      
      const vitalsCallback = (metric: any) => {
        console.log(`📊 ${metric.name}:`, metric.value)
        
        // Store performance metrics
        const metrics = storageUtils.getItem('nelson-gpt-performance', [])
        metrics.push({
          name: metric.name,
          value: metric.value,
          timestamp: new Date().toISOString()
        })
        
        // Keep only last 50 metrics
        if (metrics.length > 50) {
          metrics.splice(0, metrics.length - 50)
        }
        
        storageUtils.setItem('nelson-gpt-performance', metrics)
      }
      
      getCLS(vitalsCallback)
      getFID(vitalsCallback)
      getFCP(vitalsCallback)
      getLCP(vitalsCallback)
      getTTFB(vitalsCallback)
      
    } catch (error) {
      console.warn('Failed to initialize performance monitoring:', error)
    }
  }
  
  // Monitor bundle size and loading performance
  if (performance.getEntriesByType) {
    const navigationEntries = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[]
    if (navigationEntries.length > 0) {
      const navigation = navigationEntries[0]
      console.log('📈 Page load performance:', {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        totalTime: navigation.loadEventEnd - navigation.fetchStart
      })
    }
  }
}

/**
 * Initialize accessibility features
 */
async function initializeAccessibility(): Promise<void> {
  // Set up focus management
  document.addEventListener('keydown', (event) => {
    // Skip to main content with Alt+M
    if (event.altKey && event.key === 'm') {
      event.preventDefault()
      const mainContent = document.getElementById('main-content')
      if (mainContent) {
        mainContent.focus()
        a11yUtils.announceToScreenReader('Skipped to main content')
      }
    }
    
    // Toggle high contrast with Alt+H
    if (event.altKey && event.key === 'h') {
      event.preventDefault()
      document.documentElement.classList.toggle('high-contrast')
      const isHighContrast = document.documentElement.classList.contains('high-contrast')
      a11yUtils.announceToScreenReader(
        isHighContrast ? 'High contrast mode enabled' : 'High contrast mode disabled'
      )
    }
  })
  
  // Detect and respect user preferences
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
  if (prefersReducedMotion.matches) {
    document.documentElement.classList.add('reduce-motion')
  }
  
  prefersReducedMotion.addEventListener('change', (e) => {
    document.documentElement.classList.toggle('reduce-motion', e.matches)
  })
  
  // High contrast preference
  const prefersHighContrast = window.matchMedia('(prefers-contrast: high)')
  if (prefersHighContrast.matches) {
    document.documentElement.classList.add('high-contrast')
  }
  
  prefersHighContrast.addEventListener('change', (e) => {
    document.documentElement.classList.toggle('high-contrast', e.matches)
  })
}

/**
 * Initialize PWA features
 */
async function initializePWA(): Promise<void> {
  // Check if app is running as PWA
  const isPWA = window.matchMedia('(display-mode: standalone)').matches ||
                (window.navigator as any).standalone ||
                document.referrer.includes('android-app://')
  
  if (isPWA) {
    console.log('🚀 Running as PWA')
    document.documentElement.classList.add('pwa-mode')
  }
  
  // Handle app install prompt
  let deferredPrompt: any
  
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt = e
    
    // Show custom install button
    const installEvent = new CustomEvent('pwa-install-available', {
      detail: { prompt: deferredPrompt }
    })
    window.dispatchEvent(installEvent)
  })
  
  // Handle successful installation
  window.addEventListener('appinstalled', () => {
    console.log('✅ PWA installed successfully')
    deferredPrompt = null
    
    // Track installation
    const installEvent = new CustomEvent('pwa-installed')
    window.dispatchEvent(installEvent)
  })
  
  // Handle online/offline status
  const updateOnlineStatus = () => {
    const isOnline = navigator.onLine
    document.documentElement.classList.toggle('offline', !isOnline)
    
    const statusEvent = new CustomEvent('network-status-change', {
      detail: { isOnline }
    })
    window.dispatchEvent(statusEvent)
    
    if (!isOnline) {
      a11yUtils.announceToScreenReader('You are now offline. Some features may be limited.')
    } else {
      a11yUtils.announceToScreenReader('You are back online.')
    }
  }
  
  window.addEventListener('online', updateOnlineStatus)
  window.addEventListener('offline', updateOnlineStatus)
  
  // Initial status check
  updateOnlineStatus()
}

/**
 * Initialize medical compliance features
 */
async function initializeMedicalCompliance(): Promise<void> {
  // Set up HIPAA-compliant session management
  const sessionTimeout = 30 * 60 * 1000 // 30 minutes
  let sessionTimer: NodeJS.Timeout
  
  const resetSessionTimer = () => {
    clearTimeout(sessionTimer)
    sessionTimer = setTimeout(() => {
      // Warn user about session timeout
      const timeoutEvent = new CustomEvent('session-timeout-warning')
      window.dispatchEvent(timeoutEvent)
      
      // Auto-logout after additional 5 minutes
      setTimeout(() => {
        const logoutEvent = new CustomEvent('session-timeout-logout')
        window.dispatchEvent(logoutEvent)
      }, 5 * 60 * 1000)
      
    }, sessionTimeout)
  }
  
  // Reset timer on user activity
  const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
  activityEvents.forEach(event => {
    document.addEventListener(event, resetSessionTimer, { passive: true })
  })
  
  // Initialize timer
  resetSessionTimer()
  
  // Set up audit logging
  const logUserAction = (action: string, details?: any) => {
    const auditLog = {
      timestamp: new Date().toISOString(),
      action,
      details,
      sessionId: storageUtils.getItem('session-id', null),
      userAgent: navigator.userAgent
    }
    
    const logs = storageUtils.getItem('audit-logs', [])
    logs.push(auditLog)
    
    // Keep only last 100 audit logs
    if (logs.length > 100) {
      logs.splice(0, logs.length - 100)
    }
    
    storageUtils.setItem('audit-logs', logs)
  }
  
  // Log page views
  logUserAction('page_view', { url: window.location.href })
  
  // Set up medical disclaimer tracking
  const disclaimerVersion = '1.0'
  const acknowledgedVersion = storageUtils.getItem('disclaimer-acknowledged', null)
  
  if (acknowledgedVersion !== disclaimerVersion) {
    const disclaimerEvent = new CustomEvent('medical-disclaimer-required', {
      detail: { version: disclaimerVersion }
    })
    window.dispatchEvent(disclaimerEvent)
  }
}

/**
 * Initialize offline capabilities
 */
async function initializeOfflineCapabilities(): Promise<void> {
  // Set up offline queue for failed requests
  const offlineQueue = storageUtils.getItem('offline-queue', [])
  
  // Process offline queue when back online
  const processOfflineQueue = async () => {
    if (!navigator.onLine || offlineQueue.length === 0) return
    
    console.log(`📤 Processing ${offlineQueue.length} offline requests...`)
    
    const processedItems = []
    
    for (const item of offlineQueue) {
      try {
        // TODO: Implement actual request processing
        console.log('Processing offline item:', item)
        processedItems.push(item.id)
      } catch (error) {
        console.error('Failed to process offline item:', error)
        
        // Increment retry count
        item.retryCount = (item.retryCount || 0) + 1
        
        // Remove if max retries exceeded
        if (item.retryCount >= (item.maxRetries || 3)) {
          processedItems.push(item.id)
        }
      }
    }
    
    // Remove processed items from queue
    const updatedQueue = offlineQueue.filter(item => !processedItems.includes(item.id))
    storageUtils.setItem('offline-queue', updatedQueue)
    
    if (processedItems.length > 0) {
      console.log(`✅ Processed ${processedItems.length} offline requests`)
    }
  }
  
  // Process queue when coming back online
  window.addEventListener('online', processOfflineQueue)
  
  // Initial queue processing if online
  if (navigator.onLine) {
    setTimeout(processOfflineQueue, 1000)
  }
  
  // Set up background sync for PWA
  if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
    try {
      const registration = await navigator.serviceWorker.ready
      
      // Register background sync
      await registration.sync.register('background-sync')
      console.log('📱 Background sync registered')
      
    } catch (error) {
      console.warn('Failed to register background sync:', error)
    }
  }
}

/**
 * Get application health status
 */
export function getAppHealthStatus() {
  return {
    isOnline: navigator.onLine,
    isPWA: window.matchMedia('(display-mode: standalone)').matches,
    hasServiceWorker: 'serviceWorker' in navigator,
    storageAvailable: typeof Storage !== 'undefined',
    performanceSupported: 'performance' in window,
    errors: storageUtils.getItem('nelson-gpt-errors', []),
    performanceMetrics: storageUtils.getItem('nelson-gpt-performance', [])
  }
}


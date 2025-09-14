import React, { useState, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import SplashScreen from './components/SplashScreen'
import MainLayout from './components/layout/MainLayout'
import { ChatInterface } from './components/chat/ChatInterface'
import { NavigationDrawer } from './components/navigation/NavigationDrawer'
import { ThemeProvider } from './components/ui/ThemeProvider'
import { AccessibilityProvider } from './components/ui/AccessibilityProvider'
import { PWAUpdateNotification } from './components/ui/PWAUpdateNotification'
import { ToastProvider } from './components/ui/ToastProvider'
import { useUserStore } from './store/userStore'
import { useChatStore } from './store/chatStore'
import { initializeApp } from './utils/app-initialization'

function App() {
  const [showSplash, setShowSplash] = useState(true)
  const [isInitialized, setIsInitialized] = useState(false)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const { user, loadUserPreferences } = useUserStore()
  const { initializeChatHistory } = useChatStore()

  useEffect(() => {
    const initialize = async () => {
      try {
        // Initialize application
        await initializeApp()
        
        // Load user preferences
        await loadUserPreferences()
        
        // Initialize chat history
        await initializeChatHistory()
        
        setIsInitialized(true)
        
        // Show splash screen for minimum duration
        const minSplashDuration = 2500 // 2.5 seconds
        setTimeout(() => {
          setShowSplash(false)
        }, minSplashDuration)
        
      } catch (error) {
        console.error('App initialization error:', error)
        setIsInitialized(true)
        setShowSplash(false)
      }
    }

    initialize()
  }, [loadUserPreferences, initializeChatHistory])

  // Handle PWA update events
  useEffect(() => {
    const handlePWAUpdate = (event: CustomEvent) => {
      // PWA update notification will be handled by PWAUpdateNotification component
      console.log('PWA update available:', event.detail)
    }

    const handlePWAOfflineReady = () => {
      console.log('PWA is ready for offline use')
      // Could show a toast notification here
    }

    window.addEventListener('pwa-update-available', handlePWAUpdate as EventListener)
    window.addEventListener('pwa-offline-ready', handlePWAOfflineReady)

    return () => {
      window.removeEventListener('pwa-update-available', handlePWAUpdate as EventListener)
      window.removeEventListener('pwa-offline-ready', handlePWAOfflineReady)
    }
  }, [])

  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-morphic-bg">
        <div className="flex flex-col items-center space-y-4">
          <div className="spinner-medical"></div>
          <p className="text-medical-text-secondary">Initializing Nelson-GPT...</p>
        </div>
      </div>
    )
  }

  return (
    <ThemeProvider>
      <AccessibilityProvider>
        <ToastProvider>
          <div className="App">
            <AnimatePresence mode="wait">
              {showSplash ? (
                <SplashScreen key="splash" />
              ) : (
                <MainLayout key="main" onMenuClick={() => setIsDrawerOpen(true)}>
                  <ChatInterface className="h-full" />
                </MainLayout>
              )}
            </AnimatePresence>
            
            {/* Navigation Drawer */}
            <NavigationDrawer
              isOpen={isDrawerOpen}
              onClose={() => setIsDrawerOpen(false)}
            />
            
            {/* PWA Update Notification */}
            <PWAUpdateNotification />
            
            {/* Medical Disclaimer Modal - shown on first visit */}
            {user && !user.preferences.showMedicalDisclaimer && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                <div className="bg-morphic-bg rounded-xl p-6 max-w-md w-full">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-10 h-10 bg-medical-warning/10 rounded-full flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-medical-warning"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                        />
                      </svg>
                    </div>
                    <h2 className="text-lg font-semibold text-medical-text-primary">
                      Medical Disclaimer
                    </h2>
                  </div>
                  <p className="text-medical-text-secondary mb-6 text-sm leading-relaxed">
                    Nelson-GPT provides educational information based on the Nelson Textbook of Pediatrics. 
                    This information is not intended as a substitute for professional medical advice, 
                    diagnosis, or treatment. Always seek the advice of qualified healthcare providers 
                    with questions about medical conditions.
                  </p>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => {
                        useUserStore.getState().updatePreferences({
                          showMedicalDisclaimer: true
                        })
                      }}
                      className="btn-medical-primary flex-1"
                    >
                      I Understand
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ToastProvider>
      </AccessibilityProvider>
    </ThemeProvider>
  )
}

export default App

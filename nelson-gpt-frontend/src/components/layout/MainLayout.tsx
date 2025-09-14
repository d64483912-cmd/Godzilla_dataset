import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Header from './Header'
import NavigationDrawer from './NavigationDrawer'
import ChatInterface from '../chat/ChatInterface'
import { useChatStore } from '../../store/chatStore'
import { useUserStore } from '../../store/userStore'
import { PWAInstallPrompt } from '../ui/PWAUpdateNotification'

const MainLayout: React.FC = () => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const { currentSession } = useChatStore()
  const { user } = useUserStore()

  // Handle responsive behavior
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768
      setIsMobile(mobile)
      
      // Auto-close drawer on mobile when screen size changes
      if (mobile && isDrawerOpen) {
        setIsDrawerOpen(false)
      }
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    
    return () => window.removeEventListener('resize', checkMobile)
  }, [isDrawerOpen])

  // Handle drawer toggle
  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen)
  }

  // Close drawer when clicking outside on mobile
  const handleOverlayClick = () => {
    if (isMobile && isDrawerOpen) {
      setIsDrawerOpen(false)
    }
  }

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Toggle drawer with Ctrl/Cmd + B
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault()
        toggleDrawer()
      }
      
      // Close drawer with Escape
      if (e.key === 'Escape' && isDrawerOpen) {
        setIsDrawerOpen(false)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isDrawerOpen])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-morphic-bg flex flex-col"
    >
      {/* Header */}
      <Header 
        onMenuClick={toggleDrawer}
        isDrawerOpen={isDrawerOpen}
      />

      <div className="flex flex-1 relative">
        {/* Navigation Drawer */}
        <NavigationDrawer
          isOpen={isDrawerOpen}
          onClose={() => setIsDrawerOpen(false)}
          isMobile={isMobile}
        />

        {/* Mobile Overlay */}
        {isMobile && isDrawerOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-30 md:hidden"
            onClick={handleOverlayClick}
          />
        )}

        {/* Main Content */}
        <main
          id="main-content"
          className={`
            flex-1 flex flex-col transition-all duration-300 ease-in-out
            ${isDrawerOpen && !isMobile ? 'ml-80' : 'ml-0'}
          `}
          tabIndex={-1}
        >
          {/* Chat Interface */}
          <div className="flex-1 flex flex-col">
            <ChatInterface />
          </div>

          {/* Footer */}
          <footer className="border-t border-morphic-border bg-morphic-bg-secondary px-4 py-3">
            <div className="max-w-4xl mx-auto">
              <div className="flex flex-col sm:flex-row items-center justify-between text-sm text-medical-text-muted">
                <div className="flex items-center space-x-4 mb-2 sm:mb-0">
                  <span>Nelson-GPT — Evidence-based Pediatric Care</span>
                  <span className="hidden sm:inline">•</span>
                  <span className="text-xs">Powered by Nelson Textbook of Pediatrics</span>
                </div>
                
                <div className="flex items-center space-x-4">
                  {/* Online/Offline Status */}
                  <div className="flex items-center space-x-1">
                    <div 
                      className={`w-2 h-2 rounded-full ${
                        navigator.onLine ? 'bg-medical-success' : 'bg-medical-warning'
                      }`}
                    />
                    <span className="text-xs">
                      {navigator.onLine ? 'Online' : 'Offline'}
                    </span>
                  </div>
                  
                  {/* Version Info */}
                  <span className="text-xs opacity-75">
                    v1.0.0
                  </span>
                </div>
              </div>
              
              {/* Medical Disclaimer */}
              <div className="mt-2 pt-2 border-t border-morphic-border">
                <p className="text-xs text-medical-text-muted text-center">
                  <strong>Medical Disclaimer:</strong> This application provides educational information only. 
                  Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.
                </p>
              </div>
            </div>
          </footer>
        </main>
      </div>

      {/* PWA Install Prompt */}
      <PWAInstallPrompt />

      {/* Accessibility Announcements */}
      <div
        id="accessibility-announcements"
        className="sr-only"
        aria-live="polite"
        aria-atomic="true"
      />
    </motion.div>
  )
}

export default MainLayout


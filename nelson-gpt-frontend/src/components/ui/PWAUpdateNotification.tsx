import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Download, X, RefreshCw } from 'lucide-react'
import { useToastActions } from './ToastProvider'

interface PWAUpdateInfo {
  updateSW: () => void
}

export function PWAUpdateNotification() {
  const [updateInfo, setUpdateInfo] = useState<PWAUpdateInfo | null>(null)
  const [showNotification, setShowNotification] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  const { success, error } = useToastActions()

  useEffect(() => {
    const handleUpdateAvailable = (event: CustomEvent<PWAUpdateInfo>) => {
      setUpdateInfo(event.detail)
      setShowNotification(true)
    }

    const handleOfflineReady = () => {
      success(
        'App Ready for Offline Use',
        'Nelson-GPT is now available offline. You can use core features without an internet connection.'
      )
    }

    window.addEventListener('pwa-update-available', handleUpdateAvailable as EventListener)
    window.addEventListener('pwa-offline-ready', handleOfflineReady)

    return () => {
      window.removeEventListener('pwa-update-available', handleUpdateAvailable as EventListener)
      window.removeEventListener('pwa-offline-ready', handleOfflineReady)
    }
  }, [success])

  const handleUpdate = async () => {
    if (!updateInfo) return

    setIsUpdating(true)
    
    try {
      // Call the update function provided by the service worker
      await updateInfo.updateSW()
      
      success(
        'Update Successful',
        'Nelson-GPT has been updated to the latest version.'
      )
      
      // The page will reload automatically after update
      
    } catch (err) {
      console.error('Failed to update:', err)
      error(
        'Update Failed',
        'Failed to update the application. Please refresh the page manually.'
      )
      setIsUpdating(false)
    }
  }

  const handleDismiss = () => {
    setShowNotification(false)
    setUpdateInfo(null)
  }

  return (
    <AnimatePresence>
      {showNotification && updateInfo && (
        <motion.div
          initial={{ opacity: 0, y: 100 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 100 }}
          className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-md z-50"
        >
          <div className="bg-morphic-bg border border-morphic-border rounded-xl shadow-morphic-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-medical-primary/10 rounded-full flex items-center justify-center">
                  <Download className="w-5 h-5 text-medical-primary" />
                </div>
              </div>
              
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-medical-text-primary">
                  Update Available
                </h3>
                <p className="text-sm text-medical-text-secondary mt-1">
                  A new version of Nelson-GPT is ready to install with the latest medical updates and improvements.
                </p>
                
                <div className="flex items-center space-x-3 mt-4">
                  <button
                    onClick={handleUpdate}
                    disabled={isUpdating}
                    className="btn-medical-primary text-sm px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {isUpdating ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Updating...</span>
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4" />
                        <span>Update Now</span>
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleDismiss}
                    className="text-sm text-medical-text-secondary hover:text-medical-text-primary transition-colors"
                  >
                    Later
                  </button>
                </div>
              </div>
              
              <button
                onClick={handleDismiss}
                className="flex-shrink-0 text-medical-text-muted hover:text-medical-text-secondary transition-colors"
                aria-label="Dismiss update notification"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// PWA Install Prompt Component
export function PWAInstallPrompt() {
  const [installPrompt, setInstallPrompt] = useState<any>(null)
  const [showPrompt, setShowPrompt] = useState(false)
  const [isInstalling, setIsInstalling] = useState(false)
  const { success, error } = useToastActions()

  useEffect(() => {
    const handleInstallAvailable = (event: CustomEvent) => {
      setInstallPrompt(event.detail.prompt)
      setShowPrompt(true)
    }

    const handleInstalled = () => {
      setShowPrompt(false)
      setInstallPrompt(null)
      success(
        'App Installed',
        'Nelson-GPT has been installed successfully. You can now access it from your home screen.'
      )
    }

    window.addEventListener('pwa-install-available', handleInstallAvailable as EventListener)
    window.addEventListener('pwa-installed', handleInstalled)

    return () => {
      window.removeEventListener('pwa-install-available', handleInstallAvailable as EventListener)
      window.removeEventListener('pwa-installed', handleInstalled)
    }
  }, [success])

  const handleInstall = async () => {
    if (!installPrompt) return

    setIsInstalling(true)

    try {
      // Show the install prompt
      const result = await installPrompt.prompt()
      
      if (result.outcome === 'accepted') {
        console.log('User accepted the install prompt')
      } else {
        console.log('User dismissed the install prompt')
      }
      
      setShowPrompt(false)
      setInstallPrompt(null)
      
    } catch (err) {
      console.error('Failed to install:', err)
      error(
        'Installation Failed',
        'Failed to install the application. Please try again later.'
      )
    } finally {
      setIsInstalling(false)
    }
  }

  const handleDismiss = () => {
    setShowPrompt(false)
    setInstallPrompt(null)
  }

  return (
    <AnimatePresence>
      {showPrompt && installPrompt && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        >
          <div className="bg-morphic-bg rounded-xl p-6 max-w-md w-full">
            <div className="text-center">
              <div className="w-16 h-16 bg-medical-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl text-white">📖</span>
              </div>
              
              <h2 className="text-xl font-semibold text-medical-text-primary mb-2">
                Install Nelson-GPT
              </h2>
              
              <p className="text-medical-text-secondary mb-6">
                Install Nelson-GPT on your device for quick access to pediatric medical guidance. 
                Works offline and provides a native app experience.
              </p>
              
              <div className="flex space-x-3">
                <button
                  onClick={handleInstall}
                  disabled={isInstalling}
                  className="btn-medical-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isInstalling ? 'Installing...' : 'Install App'}
                </button>
                
                <button
                  onClick={handleDismiss}
                  className="btn-medical-secondary flex-1"
                >
                  Not Now
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}


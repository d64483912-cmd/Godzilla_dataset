import React, { createContext, useContext, useState, useCallback } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import type { ToastMessage } from '../../types'
import { generateId } from '../../utils/helpers'

interface ToastContextType {
  toasts: ToastMessage[]
  addToast: (toast: Omit<ToastMessage, 'id'>) => void
  removeToast: (id: string) => void
  clearAllToasts: () => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function useToast() {
  const context = useContext(ToastContext)
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

interface ToastProviderProps {
  children: React.ReactNode
  maxToasts?: number
}

export function ToastProvider({ children, maxToasts = 5 }: ToastProviderProps) {
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const addToast = useCallback((toast: Omit<ToastMessage, 'id'>) => {
    const id = generateId()
    const newToast: ToastMessage = {
      ...toast,
      id,
      duration: toast.duration ?? 5000
    }

    setToasts(prev => {
      const updated = [newToast, ...prev]
      // Limit number of toasts
      return updated.slice(0, maxToasts)
    })

    // Auto-remove toast after duration
    if (newToast.duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, newToast.duration)
    }
  }, [maxToasts])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const clearAllToasts = useCallback(() => {
    setToasts([])
  }, [])

  const value: ToastContextType = {
    toasts,
    addToast,
    removeToast,
    clearAllToasts
  }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  )
}

interface ToastContainerProps {
  toasts: ToastMessage[]
  onRemove: (id: string) => void
}

function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div
      className="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full"
      role="region"
      aria-label="Notifications"
      aria-live="polite"
    >
      <AnimatePresence>
        {toasts.map(toast => (
          <Toast key={toast.id} toast={toast} onRemove={onRemove} />
        ))}
      </AnimatePresence>
    </div>
  )
}

interface ToastProps {
  toast: ToastMessage
  onRemove: (id: string) => void
}

function Toast({ toast, onRemove }: ToastProps) {
  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-medical-success" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-medical-error" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-medical-warning" />
      case 'info':
      default:
        return <Info className="w-5 h-5 text-medical-primary" />
    }
  }

  const getBorderColor = () => {
    switch (toast.type) {
      case 'success':
        return 'border-l-medical-success'
      case 'error':
        return 'border-l-medical-error'
      case 'warning':
        return 'border-l-medical-warning'
      case 'info':
      default:
        return 'border-l-medical-primary'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 300, scale: 0.3 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.5, transition: { duration: 0.2 } }}
      className={`
        bg-morphic-bg border-l-4 ${getBorderColor()} rounded-lg shadow-morphic-lg p-4
        flex items-start space-x-3 max-w-sm w-full
      `}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex-shrink-0">
        {getIcon()}
      </div>
      
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-medium text-medical-text-primary">
          {toast.title}
        </h4>
        <p className="text-sm text-medical-text-secondary mt-1">
          {toast.message}
        </p>
        
        {toast.action && (
          <button
            onClick={toast.action.onClick}
            className="mt-2 text-sm font-medium text-medical-primary hover:text-medical-primary-dark transition-colors"
          >
            {toast.action.label}
          </button>
        )}
      </div>
      
      <button
        onClick={() => onRemove(toast.id)}
        className="flex-shrink-0 text-medical-text-muted hover:text-medical-text-secondary transition-colors"
        aria-label="Dismiss notification"
      >
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  )
}

// Convenience hooks for different toast types
export function useToastActions() {
  const { addToast } = useToast()

  return {
    success: (title: string, message: string, options?: Partial<ToastMessage>) =>
      addToast({ type: 'success', title, message, ...options }),
    
    error: (title: string, message: string, options?: Partial<ToastMessage>) =>
      addToast({ type: 'error', title, message, duration: 0, ...options }),
    
    warning: (title: string, message: string, options?: Partial<ToastMessage>) =>
      addToast({ type: 'warning', title, message, ...options }),
    
    info: (title: string, message: string, options?: Partial<ToastMessage>) =>
      addToast({ type: 'info', title, message, ...options }),
    
    medicalAlert: (title: string, message: string, action?: ToastMessage['action']) =>
      addToast({
        type: 'warning',
        title,
        message,
        duration: 0, // Don't auto-dismiss medical alerts
        action
      }),
    
    offlineNotice: () =>
      addToast({
        type: 'warning',
        title: 'You are offline',
        message: 'Some features may be limited. Your data will sync when you reconnect.',
        duration: 0
      }),
    
    updateAvailable: (onUpdate: () => void) =>
      addToast({
        type: 'info',
        title: 'Update Available',
        message: 'A new version of Nelson-GPT is available.',
        duration: 0,
        action: {
          label: 'Update Now',
          onClick: onUpdate
        }
      })
  }
}


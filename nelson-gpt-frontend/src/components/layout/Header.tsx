import React from 'react'
import { motion } from 'framer-motion'
import { Menu, Settings, User, Bell, Search } from 'lucide-react'
import { useUserStore } from '../../store/userStore'
import { useChatStore } from '../../store/chatStore'
import { useTheme } from '../ui/ThemeProvider'

interface HeaderProps {
  onMenuClick: () => void
  isDrawerOpen: boolean
}

const Header: React.FC<HeaderProps> = ({ onMenuClick, isDrawerOpen }) => {
  const { user, isAuthenticated } = useUserStore()
  const { currentSession } = useChatStore()
  const { isDark } = useTheme()

  return (
    <header className="bg-morphic-bg border-b border-morphic-border sticky top-0 z-40">
      <div className="flex items-center justify-between h-16 px-4">
        {/* Left Section */}
        <div className="flex items-center space-x-4">
          {/* Menu Button */}
          <button
            onClick={onMenuClick}
            className="p-2 rounded-lg hover:bg-morphic-bg-secondary transition-colors focus:ring-2 focus:ring-medical-primary focus:ring-offset-2"
            aria-label={isDrawerOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={isDrawerOpen}
          >
            <Menu className="w-5 h-5 text-medical-text-secondary" />
          </button>

          {/* Logo and Title */}
          <motion.div
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <div className="w-8 h-8 bg-medical-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-semibold text-sm">📖</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-semibold text-medical-text-primary">
                Nelson-GPT
              </h1>
              <p className="text-xs text-medical-text-secondary -mt-1">
                powered by Nelson Book 📖 of Pediatrics
              </p>
            </div>
          </motion.div>
        </div>

        {/* Center Section - Current Chat Title */}
        <div className="flex-1 max-w-md mx-4 hidden md:block">
          {currentSession && (
            <div className="text-center">
              <h2 className="text-sm font-medium text-medical-text-primary truncate">
                {currentSession.title}
              </h2>
              <p className="text-xs text-medical-text-secondary">
                {currentSession.messages.length} messages
              </p>
            </div>
          )}
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-2">
          {/* Search Button */}
          <button
            className="p-2 rounded-lg hover:bg-morphic-bg-secondary transition-colors focus:ring-2 focus:ring-medical-primary focus:ring-offset-2"
            aria-label="Search conversations"
            title="Search conversations (Ctrl+K)"
          >
            <Search className="w-5 h-5 text-medical-text-secondary" />
          </button>

          {/* Notifications */}
          <button
            className="p-2 rounded-lg hover:bg-morphic-bg-secondary transition-colors focus:ring-2 focus:ring-medical-primary focus:ring-offset-2 relative"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5 text-medical-text-secondary" />
            {/* Notification Badge */}
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-medical-error rounded-full text-xs text-white flex items-center justify-center">
              <span className="sr-only">2 unread notifications</span>
            </span>
          </button>

          {/* Settings */}
          <button
            className="p-2 rounded-lg hover:bg-morphic-bg-secondary transition-colors focus:ring-2 focus:ring-medical-primary focus:ring-offset-2"
            aria-label="Settings"
          >
            <Settings className="w-5 h-5 text-medical-text-secondary" />
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-2">
            {isAuthenticated && user ? (
              <button
                className="flex items-center space-x-2 p-2 rounded-lg hover:bg-morphic-bg-secondary transition-colors focus:ring-2 focus:ring-medical-primary focus:ring-offset-2"
                aria-label="User menu"
              >
                {user.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="w-6 h-6 rounded-full"
                  />
                ) : (
                  <div className="w-6 h-6 bg-medical-primary rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-medium">
                      {user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                )}
                <span className="hidden sm:inline text-sm font-medium text-medical-text-primary">
                  {user.name}
                </span>
              </button>
            ) : (
              <button
                className="flex items-center space-x-2 px-3 py-2 bg-medical-primary text-white rounded-lg hover:bg-medical-primary-dark transition-colors focus:ring-2 focus:ring-medical-primary focus:ring-offset-2"
                aria-label="Sign in"
              >
                <User className="w-4 h-4" />
                <span className="hidden sm:inline text-sm font-medium">
                  Sign In
                </span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Current Chat Title */}
      {currentSession && (
        <div className="md:hidden px-4 pb-2 border-t border-morphic-border bg-morphic-bg-secondary">
          <div className="text-center py-2">
            <h2 className="text-sm font-medium text-medical-text-primary truncate">
              {currentSession.title}
            </h2>
            <p className="text-xs text-medical-text-secondary">
              {currentSession.messages.length} messages
            </p>
          </div>
        </div>
      )}

      {/* Breadcrumb Navigation */}
      <nav
        className="hidden lg:block px-4 py-2 bg-morphic-bg-secondary border-t border-morphic-border"
        aria-label="Breadcrumb"
      >
        <ol className="flex items-center space-x-2 text-sm">
          <li>
            <a
              href="#"
              className="text-medical-primary hover:text-medical-primary-dark transition-colors"
            >
              Home
            </a>
          </li>
          {currentSession && (
            <>
              <li className="text-medical-text-muted">/</li>
              <li>
                <span className="text-medical-text-secondary">
                  Chat Session
                </span>
              </li>
              <li className="text-medical-text-muted">/</li>
              <li>
                <span className="text-medical-text-primary font-medium truncate max-w-xs">
                  {currentSession.title}
                </span>
              </li>
            </>
          )}
        </ol>
      </nav>
    </header>
  )
}

export default Header


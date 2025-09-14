import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '../../store/chatStore';
import { useUserStore } from '../../store/userStore';
import { ChatSession } from '../../types';
import { formatDistanceToNow } from 'date-fns';

interface NavigationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NavigationDrawer: React.FC<NavigationDrawerProps> = ({
  isOpen,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'sessions' | 'tools' | 'settings'>('sessions');
  
  const {
    sessions,
    currentSession,
    createNewSession,
    switchToSession,
    deleteSession,
    clearAllSessions
  } = useChatStore();
  
  const { preferences, updatePreferences } = useUserStore();

  const handleNewSession = () => {
    createNewSession();
    onClose();
  };

  const handleSessionSelect = (sessionId: string) => {
    switchToSession(sessionId);
    onClose();
  };

  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      deleteSession(sessionId);
    }
  };

  const renderSessions = () => (
    <div className="flex flex-col h-full">
      {/* Sessions Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Conversations
        </h3>
        <button
          onClick={handleNewSession}
          className="p-2 text-medical-primary hover:bg-medical-primary/10 rounded-lg transition-colors"
          aria-label="New conversation"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-6">
            <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              No conversations yet. Start a new one!
            </p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => handleSessionSelect(session.id)}
                className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                  currentSession?.id === session.id
                    ? 'bg-medical-primary/10 text-medical-primary'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {session.title || 'New Conversation'}
                      </p>
                      <p className="text-xs opacity-75 truncate">
                        {session.messages.length} messages • {formatDistanceToNow(session.updatedAt, { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={(e) => handleDeleteSession(session.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all"
                  aria-label="Delete conversation"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Clear All Button */}
      {sessions.length > 0 && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={() => {
              if (confirm('Are you sure you want to delete all conversations?')) {
                clearAllSessions();
              }
            }}
            className="w-full p-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          >
            Clear All Conversations
          </button>
        </div>
      )}
    </div>
  );

  const renderTools = () => (
    <div className="p-4 space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Medical Tools
      </h3>
      
      <div className="grid grid-cols-1 gap-3">
        {/* Drug Dosing Calculator */}
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">Drug Dosing</h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">Calculate pediatric doses</p>
            </div>
          </div>
          <button className="w-full p-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm">
            Open Calculator
          </button>
        </div>

        {/* Growth Charts */}
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">Growth Charts</h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">Track growth percentiles</p>
            </div>
          </div>
          <button className="w-full p-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm">
            Open Charts
          </button>
        </div>

        {/* Emergency Protocols */}
        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex items-center space-x-3 mb-2">
            <div className="w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">Emergency Protocols</h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">Quick access to critical care</p>
            </div>
          </div>
          <button className="w-full p-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm">
            View Protocols
          </button>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="p-4 space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
        Settings
      </h3>

      {/* Theme Settings */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          Appearance
        </h4>
        <div className="space-y-2">
          {(['auto', 'light', 'dark'] as const).map((theme) => (
            <label key={theme} className="flex items-center space-x-3 cursor-pointer">
              <input
                type="radio"
                name="theme"
                value={theme}
                checked={preferences.theme === theme}
                onChange={(e) => updatePreferences({ theme: e.target.value as any })}
                className="w-4 h-4 text-medical-primary focus:ring-medical-primary"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                {theme}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Accessibility Settings */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          Accessibility
        </h4>
        <div className="space-y-3">
          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Reduce motion
            </span>
            <input
              type="checkbox"
              checked={preferences.reduceMotion}
              onChange={(e) => updatePreferences({ reduceMotion: e.target.checked })}
              className="w-4 h-4 text-medical-primary focus:ring-medical-primary rounded"
            />
          </label>
          
          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-sm text-gray-700 dark:text-gray-300">
              High contrast
            </span>
            <input
              type="checkbox"
              checked={preferences.highContrast}
              onChange={(e) => updatePreferences({ highContrast: e.target.checked })}
              className="w-4 h-4 text-medical-primary focus:ring-medical-primary rounded"
            />
          </label>
        </div>
      </div>

      {/* Medical Settings */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          Medical Preferences
        </h4>
        <div className="space-y-3">
          <div>
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
              Default units
            </label>
            <select
              value={preferences.units}
              onChange={(e) => updatePreferences({ units: e.target.value as any })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
            >
              <option value="metric">Metric (kg, cm, °C)</option>
              <option value="imperial">Imperial (lbs, in, °F)</option>
            </select>
          </div>
          
          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Show medical warnings
            </span>
            <input
              type="checkbox"
              checked={preferences.showMedicalWarnings}
              onChange={(e) => updatePreferences({ showMedicalWarnings: e.target.checked })}
              className="w-4 h-4 text-medical-primary focus:ring-medical-primary rounded"
            />
          </label>
        </div>
      </div>
    </div>
  );

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-80 bg-white dark:bg-gray-900 shadow-xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-medical-primary rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">N</span>
                </div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Nelson GPT
                </h2>
              </div>
              
              <button
                onClick={onClose}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                aria-label="Close navigation"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700">
              {[
                { id: 'sessions', label: 'Chats', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
                { id: 'tools', label: 'Tools', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
                { id: 'settings', label: 'Settings', icon: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex-1 flex items-center justify-center space-x-2 py-3 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'text-medical-primary border-b-2 border-medical-primary'
                      : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon} />
                  </svg>
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden">
              {activeTab === 'sessions' && renderSessions()}
              {activeTab === 'tools' && renderTools()}
              {activeTab === 'settings' && renderSettings()}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

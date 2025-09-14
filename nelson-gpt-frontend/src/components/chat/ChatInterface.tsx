import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '../../store/chatStore';
import { useUserStore } from '../../store/userStore';
import { Message, ChatSession } from '../../types';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { CitationPanel } from './CitationPanel';
import { EmergencyAlert } from './EmergencyAlert';

interface ChatInterfaceProps {
  className?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '' }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showCitations, setShowCitations] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<string | null>(null);
  
  const {
    currentSession,
    messages,
    isTyping,
    sendMessage,
    clearSession,
    emergencyAlert
  } = useChatStore();
  
  const { preferences } = useUserStore();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string, attachments?: File[]) => {
    if (!content.trim()) return;
    
    await sendMessage(content, attachments);
  };

  const handleCitationClick = (citationId: string) => {
    setSelectedCitation(citationId);
    setShowCitations(true);
  };

  const handleEmergencyDismiss = () => {
    // Handle emergency alert dismissal
    useChatStore.getState().clearEmergencyAlert();
  };

  return (
    <div className={`flex flex-col h-full bg-white dark:bg-gray-900 ${className}`}>
      {/* Emergency Alert */}
      <AnimatePresence>
        {emergencyAlert && (
          <EmergencyAlert
            alert={emergencyAlert}
            onDismiss={handleEmergencyDismiss}
          />
        )}
      </AnimatePresence>

      {/* Chat Header */}
      <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-medical-primary rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-semibold">N</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Nelson GPT
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Pediatric Medical Assistant
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowCitations(!showCitations)}
              className="p-2 text-gray-500 hover:text-medical-primary dark:text-gray-400 dark:hover:text-medical-primary transition-colors"
              aria-label="Toggle citations"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>
            
            <button
              onClick={clearSession}
              className="p-2 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 transition-colors"
              aria-label="Clear conversation"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto px-4 py-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-medical-primary/10 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-medical-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Welcome to Nelson GPT
              </h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md">
                I'm here to help with pediatric medical questions. Ask me about diagnoses, 
                treatments, drug dosing, or reference the Nelson Textbook of Pediatrics.
              </p>
              <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg">
                <button
                  onClick={() => handleSendMessage("What are the signs of dehydration in infants?")}
                  className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    Dehydration Signs
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Infant assessment
                  </div>
                </button>
                <button
                  onClick={() => handleSendMessage("Calculate acetaminophen dose for 2-year-old, 12kg")}
                  className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    Drug Dosing
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Medication calculator
                  </div>
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  onCitationClick={handleCitationClick}
                />
              ))}
              
              {isTyping && <TypingIndicator />}
              
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Chat Input */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isTyping}
          placeholder="Ask about pediatric medicine, drug dosing, or reference Nelson Textbook..."
        />
      </div>

      {/* Citation Panel */}
      <AnimatePresence>
        {showCitations && (
          <CitationPanel
            isOpen={showCitations}
            onClose={() => setShowCitations(false)}
            selectedCitation={selectedCitation}
            onCitationSelect={setSelectedCitation}
          />
        )}
      </AnimatePresence>

      {/* Medical Disclaimer */}
      <div className="flex-shrink-0 px-4 py-2 bg-yellow-50 dark:bg-yellow-900/20 border-t border-yellow-200 dark:border-yellow-800">
        <p className="text-xs text-yellow-800 dark:text-yellow-200 text-center">
          ⚠️ For educational purposes only. Always consult healthcare professionals for medical decisions.
        </p>
      </div>
    </div>
  );
};

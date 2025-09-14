import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Message } from '../../types';
import { formatDistanceToNow } from 'date-fns';

interface MessageBubbleProps {
  message: Message;
  onCitationClick?: (citationId: string) => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ 
  message, 
  onCitationClick 
}) => {
  const [showTimestamp, setShowTimestamp] = useState(false);
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  const handleCitationClick = (citationId: string) => {
    onCitationClick?.(citationId);
  };

  const renderContent = () => {
    if (typeof message.content === 'string') {
      return (
        <div className="prose prose-sm max-w-none dark:prose-invert">
          {message.content.split('\n').map((line, index) => (
            <p key={index} className="mb-2 last:mb-0">
              {line}
            </p>
          ))}
        </div>
      );
    }

    // Handle rich content with citations
    return (
      <div className="space-y-3">
        {message.content.map((block, index) => {
          if (block.type === 'text') {
            return (
              <div key={index} className="prose prose-sm max-w-none dark:prose-invert">
                {block.content.split('\n').map((line, lineIndex) => (
                  <p key={lineIndex} className="mb-2 last:mb-0">
                    {line}
                  </p>
                ))}
              </div>
            );
          }

          if (block.type === 'citation') {
            return (
              <button
                key={index}
                onClick={() => handleCitationClick(block.citationId)}
                className="inline-flex items-center px-2 py-1 text-xs bg-medical-primary/10 text-medical-primary rounded-md hover:bg-medical-primary/20 transition-colors"
              >
                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {block.title}
              </button>
            );
          }

          if (block.type === 'calculation') {
            return (
              <div key={index} className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
                <div className="flex items-center mb-2">
                  <svg className="w-4 h-4 text-blue-600 dark:text-blue-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    Medical Calculation
                  </span>
                </div>
                <div className="text-sm text-blue-800 dark:text-blue-200">
                  {block.content}
                </div>
              </div>
            );
          }

          if (block.type === 'warning') {
            return (
              <div key={index} className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-center mb-2">
                  <svg className="w-4 h-4 text-yellow-600 dark:text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                    Clinical Warning
                  </span>
                </div>
                <div className="text-sm text-yellow-800 dark:text-yellow-200">
                  {block.content}
                </div>
              </div>
            );
          }

          return null;
        })}
      </div>
    );
  };

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-center"
      >
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-3 py-2 text-sm text-gray-600 dark:text-gray-400">
          {message.content}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-medical-primary text-white' 
              : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
          }`}>
            {isUser ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            ) : (
              <span className="text-sm font-semibold">N</span>
            )}
          </div>
        </div>

        {/* Message Content */}
        <div className="flex flex-col">
          <div
            className={`rounded-2xl px-4 py-3 ${
              isUser
                ? 'bg-medical-primary text-white rounded-br-md'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-bl-md'
            }`}
            onClick={() => setShowTimestamp(!showTimestamp)}
          >
            {renderContent()}
          </div>

          {/* Timestamp */}
          {showTimestamp && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className={`text-xs text-gray-500 dark:text-gray-400 mt-1 ${
                isUser ? 'text-right' : 'text-left'
              }`}
            >
              {formatDistanceToNow(message.timestamp, { addSuffix: true })}
            </motion.div>
          )}

          {/* Citations */}
          {message.citations && message.citations.length > 0 && (
            <div className={`mt-2 flex flex-wrap gap-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
              {message.citations.map((citation) => (
                <button
                  key={citation.id}
                  onClick={() => handleCitationClick(citation.id)}
                  className="inline-flex items-center px-2 py-1 text-xs bg-medical-primary/10 text-medical-primary rounded-md hover:bg-medical-primary/20 transition-colors"
                >
                  <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  {citation.title}
                </button>
              ))}
            </div>
          )}

          {/* Attachments */}
          {message.attachments && message.attachments.length > 0 && (
            <div className={`mt-2 space-y-2 ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
              {message.attachments.map((attachment, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-2 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 text-sm"
                >
                  <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  <span className="text-gray-700 dark:text-gray-300">{attachment.name}</span>
                  <span className="text-gray-500 text-xs">
                    ({(attachment.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Citation {
  id: string;
  title: string;
  chapter?: string;
  page?: number;
  section?: string;
  content: string;
  url?: string;
}

interface CitationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  selectedCitation: string | null;
  onCitationSelect: (citationId: string) => void;
}

export const CitationPanel: React.FC<CitationPanelProps> = ({
  isOpen,
  onClose,
  selectedCitation,
  onCitationSelect
}) => {
  // Mock citations data - in real app, this would come from props or store
  const citations: Citation[] = [
    {
      id: 'nelson-ch1-p15',
      title: 'Growth and Development',
      chapter: 'Chapter 1',
      page: 15,
      section: 'Physical Growth',
      content: 'Physical growth in children follows predictable patterns, with periods of rapid growth alternating with periods of slower growth. The most rapid growth occurs during infancy and adolescence.',
      url: 'https://example.com/nelson/ch1#p15'
    },
    {
      id: 'nelson-ch5-p89',
      title: 'Fever and Antipyretic Therapy',
      chapter: 'Chapter 5',
      page: 89,
      section: 'Fever Management',
      content: 'Fever is a common symptom in pediatric patients. Acetaminophen and ibuprofen are the most commonly used antipyretic agents in children.',
      url: 'https://example.com/nelson/ch5#p89'
    }
  ];

  const selectedCitationData = citations.find(c => c.id === selectedCitation);

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
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-96 bg-white dark:bg-gray-900 shadow-xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Citations
              </h2>
              <button
                onClick={onClose}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                aria-label="Close citations"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              {selectedCitationData ? (
                /* Selected Citation Detail */
                <div className="p-4">
                  <button
                    onClick={() => onCitationSelect('')}
                    className="flex items-center text-medical-primary hover:text-medical-primary/80 mb-4 text-sm"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to all citations
                  </button>

                  <div className="space-y-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                        {selectedCitationData.title}
                      </h3>
                      <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
                        <span className="bg-medical-primary/10 text-medical-primary px-2 py-1 rounded">
                          {selectedCitationData.chapter}
                        </span>
                        {selectedCitationData.page && (
                          <span>Page {selectedCitationData.page}</span>
                        )}
                        {selectedCitationData.section && (
                          <>
                            <span>•</span>
                            <span>{selectedCitationData.section}</span>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="prose prose-sm max-w-none dark:prose-invert">
                      <p>{selectedCitationData.content}</p>
                    </div>

                    {selectedCitationData.url && (
                      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <a
                          href={selectedCitationData.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-medical-primary hover:text-medical-primary/80 text-sm"
                        >
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          View in Nelson Textbook
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                /* Citations List */
                <div className="p-4 space-y-3">
                  {citations.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 text-center">
                      <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
                        <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <p className="text-gray-500 dark:text-gray-400 text-sm">
                        No citations available for this conversation.
                      </p>
                    </div>
                  ) : (
                    citations.map((citation) => (
                      <motion.div
                        key={citation.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                        onClick={() => onCitationSelect(citation.id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                              {citation.title}
                            </h4>
                            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                              <span className="bg-medical-primary/10 text-medical-primary px-2 py-1 rounded text-xs">
                                {citation.chapter}
                              </span>
                              {citation.page && (
                                <span className="text-xs">Page {citation.page}</span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                              {citation.content}
                            </p>
                          </div>
                          <svg className="w-4 h-4 text-gray-400 ml-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
              <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>
                  Citations from Nelson Textbook of Pediatrics, 21st Edition
                </span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

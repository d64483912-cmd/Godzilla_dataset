import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { ChatSession, ChatMessage, MedicalContext } from '../types'
import { generateId } from '../utils/helpers'

interface ChatState {
  sessions: ChatSession[]
  currentSessionId: string | null
  isTyping: boolean
  
  // Getters
  currentSession: ChatSession | null
  
  // Actions
  createSession: (title?: string, medicalContext?: MedicalContext) => string
  deleteSession: (sessionId: string) => void
  updateSession: (sessionId: string, updates: Partial<ChatSession>) => void
  setCurrentSession: (sessionId: string | null) => void
  
  // Message actions
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => void
  deleteMessage: (sessionId: string, messageId: string) => void
  
  // Typing indicator
  setTyping: (isTyping: boolean) => void
  
  // Bulk operations
  clearAllSessions: () => void
  exportSession: (sessionId: string) => string
  importSession: (sessionData: string) => void
  
  // Search
  searchMessages: (query: string) => { session: ChatSession; message: ChatMessage }[]
  
  // Initialization
  initializeChatHistory: () => Promise<void>
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      sessions: [],
      currentSessionId: null,
      isTyping: false,
      
      get currentSession() {
        const { sessions, currentSessionId } = get()
        return sessions.find(s => s.id === currentSessionId) || null
      },

      createSession: (title?: string, medicalContext?: MedicalContext) => {
        const sessionId = generateId()
        const now = new Date()
        
        const newSession: ChatSession = {
          id: sessionId,
          title: title || `Chat ${get().sessions.length + 1}`,
          messages: [],
          createdAt: now,
          updatedAt: now,
          isPinned: false,
          tags: [],
          medicalContext
        }
        
        set(state => ({
          sessions: [newSession, ...state.sessions],
          currentSessionId: sessionId
        }))
        
        return sessionId
      },

      deleteSession: (sessionId: string) => {
        set(state => ({
          sessions: state.sessions.filter(s => s.id !== sessionId),
          currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId
        }))
      },

      updateSession: (sessionId: string, updates: Partial<ChatSession>) => {
        set(state => ({
          sessions: state.sessions.map(session =>
            session.id === sessionId
              ? { ...session, ...updates, updatedAt: new Date() }
              : session
          )
        }))
      },

      setCurrentSession: (sessionId: string | null) => {
        set({ currentSessionId: sessionId })
      },

      addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
        const messageId = generateId()
        const now = new Date()
        
        const newMessage: ChatMessage = {
          ...message,
          id: messageId,
          timestamp: now
        }
        
        set(state => ({
          sessions: state.sessions.map(session =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: [...session.messages, newMessage],
                  updatedAt: now,
                  // Auto-generate title from first user message
                  title: session.messages.length === 0 && message.role === 'user'
                    ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
                    : session.title
                }
              : session
          )
        }))
      },

      updateMessage: (sessionId: string, messageId: string, updates: Partial<ChatMessage>) => {
        set(state => ({
          sessions: state.sessions.map(session =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: session.messages.map(message =>
                    message.id === messageId
                      ? { ...message, ...updates }
                      : message
                  ),
                  updatedAt: new Date()
                }
              : session
          )
        }))
      },

      deleteMessage: (sessionId: string, messageId: string) => {
        set(state => ({
          sessions: state.sessions.map(session =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: session.messages.filter(m => m.id !== messageId),
                  updatedAt: new Date()
                }
              : session
          )
        }))
      },

      setTyping: (isTyping: boolean) => {
        set({ isTyping })
      },

      clearAllSessions: () => {
        set({
          sessions: [],
          currentSessionId: null,
          isTyping: false
        })
      },

      exportSession: (sessionId: string) => {
        const session = get().sessions.find(s => s.id === sessionId)
        if (!session) throw new Error('Session not found')
        
        return JSON.stringify({
          ...session,
          exportedAt: new Date().toISOString(),
          version: '1.0'
        }, null, 2)
      },

      importSession: (sessionData: string) => {
        try {
          const session = JSON.parse(sessionData)
          
          // Validate session structure
          if (!session.id || !session.messages || !Array.isArray(session.messages)) {
            throw new Error('Invalid session format')
          }
          
          // Generate new ID to avoid conflicts
          const newSession: ChatSession = {
            ...session,
            id: generateId(),
            createdAt: new Date(session.createdAt),
            updatedAt: new Date(),
            title: `${session.title} (Imported)`
          }
          
          set(state => ({
            sessions: [newSession, ...state.sessions]
          }))
          
        } catch (error) {
          throw new Error('Failed to import session: Invalid format')
        }
      },

      searchMessages: (query: string) => {
        const { sessions } = get()
        const results: { session: ChatSession; message: ChatMessage }[] = []
        
        const searchTerm = query.toLowerCase()
        
        sessions.forEach(session => {
          session.messages.forEach(message => {
            if (
              message.content.toLowerCase().includes(searchTerm) ||
              message.citations?.some(citation => 
                citation.title.toLowerCase().includes(searchTerm) ||
                citation.excerpt.toLowerCase().includes(searchTerm)
              )
            ) {
              results.push({ session, message })
            }
          })
        })
        
        return results.sort((a, b) => 
          b.message.timestamp.getTime() - a.message.timestamp.getTime()
        )
      },

      initializeChatHistory: async () => {
        try {
          // Load from localStorage (handled by persist middleware)
          const state = get()
          
          // If no sessions exist, create a welcome session
          if (state.sessions.length === 0) {
            const welcomeSessionId = get().createSession('Welcome to Nelson-GPT')
            
            // Add welcome message
            get().addMessage(welcomeSessionId, {
              role: 'assistant',
              content: `Welcome to Nelson-GPT! 👋

I'm your AI assistant powered by the Nelson Textbook of Pediatrics. I can help you with:

• **Pediatric conditions** and differential diagnoses
• **Treatment guidelines** and evidence-based recommendations  
• **Drug dosing** calculations for pediatric patients
• **Growth and development** assessments
• **Emergency protocols** and critical care guidance
• **Vaccination schedules** and immunization questions

How can I assist you with pediatric care today?`,
              citations: [{
                id: 'nelson-welcome',
                source: 'Nelson Textbook of Pediatrics',
                title: 'Welcome Guide',
                excerpt: 'Comprehensive pediatric medical reference',
                relevanceScore: 1.0
              }],
              evidenceLevel: 'high'
            })
          }
          
          // TODO: Sync with backend if user is authenticated
          console.log('Chat history initialized')
          
        } catch (error) {
          console.error('Failed to initialize chat history:', error)
        }
      }
    }),
    {
      name: 'nelson-gpt-chat',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sessions: state.sessions.map(session => ({
          ...session,
          // Limit stored messages to prevent localStorage bloat
          messages: session.messages.slice(-100) // Keep last 100 messages per session
        })),
        currentSessionId: state.currentSessionId
      })
    }
  )
)

// Utility hooks
export const useCurrentSession = () => {
  return useChatStore(state => state.currentSession)
}

export const useSessionMessages = (sessionId?: string) => {
  return useChatStore(state => {
    const targetSessionId = sessionId || state.currentSessionId
    const session = state.sessions.find(s => s.id === targetSessionId)
    return session?.messages || []
  })
}

export const useChatActions = () => {
  const store = useChatStore()
  
  return {
    sendMessage: async (content: string, medicalContext?: MedicalContext) => {
      let sessionId = store.currentSessionId
      
      // Create new session if none exists
      if (!sessionId) {
        sessionId = store.createSession(undefined, medicalContext)
      }
      
      // Add user message
      store.addMessage(sessionId, {
        role: 'user',
        content
      })
      
      // Set typing indicator
      store.setTyping(true)
      
      try {
        // TODO: Implement API call to get AI response
        // For now, simulate response
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        store.addMessage(sessionId, {
          role: 'assistant',
          content: 'This is a simulated response. The actual AI integration will be implemented with the backend API.',
          citations: [],
          evidenceLevel: 'moderate'
        })
        
      } catch (error) {
        store.addMessage(sessionId, {
          role: 'assistant',
          content: 'I apologize, but I encountered an error processing your request. Please try again.',
          error: error instanceof Error ? error.message : 'Unknown error'
        })
      } finally {
        store.setTyping(false)
      }
    },
    
    regenerateResponse: async (sessionId: string, messageId: string) => {
      // TODO: Implement response regeneration
      console.log('Regenerating response for message:', messageId)
    },
    
    copyMessage: (content: string) => {
      navigator.clipboard.writeText(content).catch(console.error)
    }
  }
}


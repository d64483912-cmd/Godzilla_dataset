import { useState, useEffect, useRef } from 'react'

interface UseTypewriterOptions {
  delay?: number
  onComplete?: () => void
  cursor?: boolean
  loop?: boolean
}

export const useTypewriter = (
  text: string,
  options: UseTypewriterOptions = {}
) => {
  const {
    delay = 100,
    onComplete,
    cursor = true,
    loop = false
  } = options

  const [displayText, setDisplayText] = useState('')
  const [isComplete, setIsComplete] = useState(false)
  const [showCursor, setShowCursor] = useState(cursor)
  const indexRef = useRef(0)
  const timeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    const typeNextCharacter = () => {
      if (indexRef.current < text.length) {
        setDisplayText(text.slice(0, indexRef.current + 1))
        indexRef.current++
        timeoutRef.current = setTimeout(typeNextCharacter, delay)
      } else {
        setIsComplete(true)
        if (onComplete) {
          onComplete()
        }
        
        if (loop) {
          setTimeout(() => {
            indexRef.current = 0
            setDisplayText('')
            setIsComplete(false)
            typeNextCharacter()
          }, 2000)
        } else if (cursor) {
          // Hide cursor after completion
          setTimeout(() => {
            setShowCursor(false)
          }, 1000)
        }
      }
    }

    // Start typing
    timeoutRef.current = setTimeout(typeNextCharacter, delay)

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [text, delay, onComplete, loop, cursor])

  // Cursor blinking effect
  useEffect(() => {
    if (!showCursor) return

    const cursorInterval = setInterval(() => {
      setShowCursor(prev => !prev)
    }, 530)

    return () => clearInterval(cursorInterval)
  }, [showCursor])

  return displayText + (cursor && showCursor ? '|' : '')
}


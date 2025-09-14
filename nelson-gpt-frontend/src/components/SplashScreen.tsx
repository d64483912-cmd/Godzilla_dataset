import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useTypewriter } from '../hooks/useTypewriter'

const SplashScreen: React.FC = () => {
  const [showSubtitle, setShowSubtitle] = useState(false)
  const [showFooter, setShowFooter] = useState(false)
  
  const titleText = useTypewriter('Nelson-GPT', {
    delay: 100,
    onComplete: () => {
      setTimeout(() => setShowSubtitle(true), 500)
    }
  })

  useEffect(() => {
    // Show footer after subtitle animation
    const footerTimer = setTimeout(() => {
      setShowFooter(true)
    }, 2000)

    return () => clearTimeout(footerTimer)
  }, [])

  return (
    <motion.div
      className="min-h-screen flex flex-col items-center justify-center bg-morphic-bg px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center max-w-2xl w-full">
        {/* Logo/Icon */}
        <motion.div
          className="w-20 h-20 bg-medical-primary rounded-2xl flex items-center justify-center mx-auto mb-8 medical-shadow-lg"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{
            type: "spring",
            stiffness: 260,
            damping: 20,
            delay: 0.2
          }}
        >
          <span className="text-3xl text-white font-semibold">📖</span>
        </motion.div>

        {/* Main Title with Typewriter Effect */}
        <div className="mb-4">
          <h1 className="text-4xl md:text-5xl font-bold text-medical-text-primary">
            <span className="inline-block overflow-hidden whitespace-nowrap border-r-2 border-medical-primary">
              {titleText}
            </span>
          </h1>
        </div>

        {/* Subtitle */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={showSubtitle ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="mb-12"
        >
          <p className="text-xl text-medical-text-secondary font-medium">
            Trusted Pediatric AI
          </p>
          <p className="text-medical-text-muted mt-2">
            Powered by Nelson Textbook of Pediatrics
          </p>
        </motion.div>

        {/* Loading Animation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex items-center justify-center space-x-2">
            <div className="flex space-x-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 bg-medical-primary rounded-full"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: i * 0.2
                  }}
                />
              ))}
            </div>
            <span className="text-medical-text-secondary text-sm ml-3">
              Loading medical knowledge base...
            </span>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={showFooter ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="text-center"
        >
          <p className="text-medical-text-muted text-sm">
            Nelson-GPT — Evidence-based Pediatric Care
          </p>
          <p className="text-medical-text-muted text-xs mt-1">
            Powered by Nelson Textbook of Pediatrics
          </p>
        </motion.div>
      </div>

      {/* Background Pattern */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-medical-primary/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-medical-primary/5 rounded-full blur-3xl" />
      </div>

      {/* Medical Icons Animation */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[
          { icon: '🩺', delay: 0.5, x: '10%', y: '20%' },
          { icon: '💊', delay: 1.0, x: '80%', y: '30%' },
          { icon: '🏥', delay: 1.5, x: '20%', y: '70%' },
          { icon: '📊', delay: 2.0, x: '70%', y: '80%' },
          { icon: '🧬', delay: 2.5, x: '90%', y: '60%' },
          { icon: '⚕️', delay: 3.0, x: '5%', y: '50%' }
        ].map((item, index) => (
          <motion.div
            key={index}
            className="absolute text-2xl opacity-20"
            style={{ left: item.x, top: item.y }}
            initial={{ opacity: 0, scale: 0, rotate: -180 }}
            animate={{ opacity: 0.2, scale: 1, rotate: 0 }}
            transition={{
              delay: item.delay,
              duration: 0.8,
              type: "spring",
              stiffness: 100
            }}
          >
            {item.icon}
          </motion.div>
        ))}
      </div>

      {/* Accessibility: Reduced motion support */}
      <style jsx>{`
        @media (prefers-reduced-motion: reduce) {
          * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
    </motion.div>
  )
}

export default SplashScreen


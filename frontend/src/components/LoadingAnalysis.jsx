import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { analysisMessages } from '../styles/theme'

function LoadingAnalysis({ active }) {
  const [step, setStep] = useState(0)

  useEffect(() => {
    if (!active) return undefined
    const timer = setInterval(() => {
      setStep((prev) => (prev + 1) % analysisMessages.length)
    }, 1400)
    return () => clearInterval(timer)
  }, [active])

  return (
    <AnimatePresence>
      {active ? (
        <motion.div
          className="analysis-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div className="glass-card loading-analysis" initial={{ scale: 0.95 }} animate={{ scale: 1 }}>
            <div className="spinner large" />
            <h3>AI is thinking...</h3>
            <p>{analysisMessages[step]}</p>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}

export default LoadingAnalysis

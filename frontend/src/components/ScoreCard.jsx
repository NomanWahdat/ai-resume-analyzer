import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

function ScoreCard({ title, score, accent = 'blue' }) {
  const [displayScore, setDisplayScore] = useState(0)
  const normalized = Math.max(0, Math.min(100, score || 0))
  const ringDegrees = Math.round((normalized / 100) * 360)

  useEffect(() => {
    let frame
    let current = 0
    const step = () => {
      current += 2
      if (current >= normalized) {
        setDisplayScore(normalized)
        return
      }
      setDisplayScore(current)
      frame = requestAnimationFrame(step)
    }
    step()
    return () => cancelAnimationFrame(frame)
  }, [normalized])

  return (
    <motion.div
      className={`glass-card score-card ${accent}`}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <p className="card-label">{title}</p>
      <div
        className="score-ring"
        style={{
          background: `conic-gradient(var(--ring-color) ${ringDegrees}deg, rgba(104, 126, 171, 0.2) 0deg)`,
        }}
      >
        <div className="score-ring-inner">
          <h3>{displayScore}</h3>
          <span>/100</span>
        </div>
      </div>
    </motion.div>
  )
}

export default ScoreCard

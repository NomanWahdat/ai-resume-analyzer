import { motion } from 'framer-motion'

function ResultCard({ result }) {
  if (!result) {
    return null
  }

  return (
    <motion.div
      className="result-card glass-card"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h3>Extraction Result</h3>
      <p>
        <strong>Filename:</strong> {result.filename}
      </p>
      <div className="text-preview">
        {result.extracted_text || 'No extractable text found in this PDF.'}
      </div>
    </motion.div>
  )
}

export default ResultCard

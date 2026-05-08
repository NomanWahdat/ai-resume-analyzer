import { motion } from 'framer-motion'

const mockHistory = [
  { id: 1, name: 'backend_engineer_resume.pdf', score: 86, ats: 81, time: '2 hours ago' },
  { id: 2, name: 'ai_automation_resume.pdf', score: 91, ats: 88, time: 'Yesterday' },
  { id: 3, name: 'fullstack_portfolio_resume.pdf', score: 79, ats: 75, time: '3 days ago' },
]

function HistoryPage() {
  return (
    <section className="page-grid">
      <div className="glass-card">
        <h2>Analysis History</h2>
        <p>Static preview for upcoming history integration.</p>
      </div>

      <div className="history-list">
        {mockHistory.map((item, index) => (
          <motion.button
            type="button"
            key={item.id}
            className="glass-card history-item"
            initial={{ opacity: 0, x: 12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.07 }}
          >
            <div>
              <h3>{item.name}</h3>
              <p>{item.time}</p>
            </div>
            <div className="history-badges">
              <span className="score-badge">Resume: {item.score}</span>
              <span className="score-badge soft">ATS: {item.ats}</span>
            </div>
          </motion.button>
        ))}
      </div>
    </section>
  )
}

export default HistoryPage

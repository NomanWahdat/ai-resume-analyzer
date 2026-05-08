import { motion } from 'framer-motion'
import ScoreCard from './ScoreCard'
import SkillsCard from './SkillsCard'
import SuggestionsCard from './SuggestionsCard'

function AnalysisDashboard({ analysis, provider }) {
  if (!analysis) {
    return null
  }

  return (
    <motion.section
      className="analysis-grid"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
    >
      <motion.div className="glass-card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <div className="card-head">
          <h2>AI Resume Analysis</h2>
          <span className="provider-tag">Provider: {provider}</span>
        </div>
        <p>{analysis.summary || 'No summary provided.'}</p>
      </motion.div>

      <div className="score-grid">
        <ScoreCard title="Resume Score" score={analysis.resume_score ?? 0} accent="blue" />
        <ScoreCard title="ATS Score" score={analysis.ats_score ?? 0} accent="violet" />
      </div>

      <div className="split-grid">
        <SkillsCard title="Technical Skills" skills={analysis.technical_skills} icon="T" />
        <SkillsCard title="Soft Skills" skills={analysis.soft_skills} icon="S" />
      </div>

      <div className="split-grid">
        <div className="glass-card">
          <h3>
            + Strengths
          </h3>
          <ul className="list-clean">
            {(analysis.strengths || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="glass-card">
          <h3>
            ! Weaknesses
          </h3>
          <ul className="list-clean">
            {(analysis.weaknesses || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      <SuggestionsCard suggestions={analysis.improvement_suggestions} />
    </motion.section>
  )
}

export default AnalysisDashboard

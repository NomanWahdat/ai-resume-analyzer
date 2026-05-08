import { useState } from 'react'
import { motion } from 'framer-motion'
import { useResumeContext } from '../context/ResumeContext'
import { generateJobMatch } from '../services/aiFeaturesService'

function getErrorMessage(error, fallbackMessage) {
  return (
    error?.response?.data?.error?.message ||
    error?.response?.data?.error ||
    error?.message ||
    fallbackMessage
  )
}

function getRiskLevel(matchPercentage) {
  if (matchPercentage >= 80) return 'low'
  if (matchPercentage >= 60) return 'medium'
  return 'high'
}

function JobMatchPage() {
  const { resumeData, analysisResult } = useResumeContext()
  const [jobDescription, setJobDescription] = useState('')
  const [matchResult, setMatchResult] = useState(null)
  const [providerUsed, setProviderUsed] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState('')

  const handleAnalyze = async () => {
    if (!resumeData?.id) {
      setError('Upload a resume first, then analyze the job match.')
      return
    }

    if (!jobDescription.trim()) {
      setError('Paste a job description to compare against the current resume.')
      return
    }

    setIsAnalyzing(true)
    setError('')

    try {
      const response = await generateJobMatch(resumeData.id, jobDescription)
      setMatchResult(response.match)
      setProviderUsed(response.provider_used)
    } catch (analysisError) {
      setError(getErrorMessage(analysisError, 'Job match analysis failed.'))
    } finally {
      setIsAnalyzing(false)
    }
  }

  const matchPercentage = matchResult?.match_percentage ?? 0
  const gaugeStyle = {
    background: `conic-gradient(var(--ring-color) ${matchPercentage * 3.6}deg, rgba(22, 42, 82, 0.55) 0deg)`,
  }

  return (
    <main className="dashboard-content">
      <section className="page-grid">
        <header className="glass-card hero-card">
          <h2>Job Match Analyzer</h2>
          <p>Compare the current resume against a target role and surface skill gaps instantly.</p>
        </header>

        <div className="glass-card feature-panel">
          <div className="feature-panel-head stack-on-mobile">
            <div>
              <h3>Paste Job Description</h3>
              <p>Run an ATS-style comparison with matching skills, gaps, risk insights, and fit level.</p>
            </div>
            <button type="button" className="primary-btn" onClick={handleAnalyze} disabled={isAnalyzing}>
              {isAnalyzing ? 'Analyzing...' : 'Analyze Match'}
            </button>
          </div>

          <textarea
            className="textarea-field"
            rows="9"
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(event) => setJobDescription(event.target.value)}
          />

          <div className="status-strip">
            <span className="score-badge">Resume: {resumeData?.filename || 'No resume loaded'}</span>
            <span className="score-badge soft">Analysis: {analysisResult ? 'Available' : 'Not run yet'}</span>
          </div>

          {error ? <div className="error-card">{error}</div> : null}
        </div>

        {matchResult ? (
          <motion.div
            className="match-layout"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="glass-card match-score-card">
              <div className="match-gauge" style={gaugeStyle}>
                <div className="match-gauge-inner">
                  <h3>{matchPercentage}%</h3>
                  <span>Match</span>
                </div>
              </div>
              <div className={`risk-badge ${getRiskLevel(matchPercentage)}`}>
                {getRiskLevel(matchPercentage).toUpperCase()} RISK
              </div>
              <p>{matchResult.risk_analysis}</p>
              <p className="muted-copy">Salary fit: {matchResult.salary_level_fit.toUpperCase()}</p>
            </div>

            <div className="glass-card match-detail-card">
              <h3>Matching Skills</h3>
              <div className="tag-wrap">
                {(matchResult.matching_skills || []).map((skill) => (
                  <span className="chip" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>

              <h3>Missing Skills</h3>
              <div className="tag-wrap">
                {(matchResult.missing_skills || []).map((skill) => (
                  <span className="chip missing" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>

              <h3>Recommendations</h3>
              <ul className="list-clean">
                {(matchResult.recommendations || []).map((recommendation) => (
                  <li key={recommendation}>{recommendation}</li>
                ))}
              </ul>

              {providerUsed ? <div className="provider-note">Provider used: {providerUsed.toUpperCase()}</div> : null}
            </div>
          </motion.div>
        ) : (
          <div className="glass-card empty-state">
            <span className="empty-icon">M</span>
            <h3>No job match analyzed yet</h3>
            <p>Paste a role description to generate the match report.</p>
          </div>
        )}
      </section>
    </main>
  )
}

export default JobMatchPage

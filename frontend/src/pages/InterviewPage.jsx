import { useState } from 'react'
import { motion } from 'framer-motion'
import { useResumeContext } from '../context/ResumeContext'
import { generateInterviewQuestions } from '../services/aiFeaturesService'

const questionGroups = [
  { key: 'hr_questions', label: 'HR' },
  { key: 'technical_questions', label: 'Technical' },
  { key: 'behavioral_questions', label: 'Behavioral' },
  { key: 'project_based_questions', label: 'Projects' },
]

function getErrorMessage(error, fallbackMessage) {
  return (
    error?.response?.data?.error?.message ||
    error?.response?.data?.error ||
    error?.message ||
    fallbackMessage
  )
}

function InterviewPage() {
  const { resumeData, analysisResult } = useResumeContext()
  const [questions, setQuestions] = useState(null)
  const [providerUsed, setProviderUsed] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!resumeData?.id) {
      setError('Upload a resume first, then generate interview questions.')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const response = await generateInterviewQuestions(resumeData.id)
      setQuestions(response.questions)
      setProviderUsed(response.provider_used)
    } catch (generationError) {
      setError(getErrorMessage(generationError, 'Interview question generation failed.'))
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <main className="dashboard-content">
      <section className="page-grid">
        <header className="glass-card hero-card">
          <h2>Interview Prep</h2>
          <p>Generate realistic interview questions tailored to the current resume profile.</p>
        </header>

        <div className="glass-card feature-panel">
          <div className="feature-panel-head">
            <div>
              <h3>Interview Question Generator</h3>
              <p>Uses the same AI provider stack and resumes analysis context when available.</p>
            </div>
            <button type="button" className="primary-btn" onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? 'Generating...' : 'Generate Interview Questions'}
            </button>
          </div>

          {resumeData ? (
            <div className="status-strip">
              <span className="score-badge">Resume: {resumeData.filename}</span>
              <span className="score-badge soft">Analysis: {analysisResult ? 'Available' : 'Not run yet'}</span>
            </div>
          ) : (
            <div className="empty-inline">Upload a resume to unlock interview preparation.</div>
          )}

          {error ? <div className="error-card">{error}</div> : null}
        </div>

        {questions ? (
          <motion.div
            className="question-accordion-grid"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {questionGroups.map((group) => (
              <details key={group.key} className="glass-card accordion-card" open={group.key === 'technical_questions'}>
                <summary>
                  <span>{group.label}</span>
                  <span className="accordion-count">{questions[group.key]?.length || 0}</span>
                </summary>
                <ul className="question-list">
                  {(questions[group.key] || []).map((question) => (
                    <li key={question}>{question}</li>
                  ))}
                </ul>
              </details>
            ))}

            {providerUsed ? (
              <div className="glass-card provider-note">
                <h3>Provider Used</h3>
                <p>{providerUsed.toUpperCase()}</p>
              </div>
            ) : null}
          </motion.div>
        ) : (
          <div className="glass-card empty-state">
            <span className="empty-icon">Q</span>
            <h3>No questions generated yet</h3>
            <p>Click the button above to generate a full interview question set.</p>
          </div>
        )}
      </section>
    </main>
  )
}

export default InterviewPage

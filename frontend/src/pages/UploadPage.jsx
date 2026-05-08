import { motion } from 'framer-motion'
import { useResumeContext } from '../context/ResumeContext'
import UploadCard from '../components/UploadCard'
import ResultCard from '../components/ResultCard'
import AnalysisDashboard from '../components/AnalysisDashboard'
import LoadingAnalysis from '../components/LoadingAnalysis'

function UploadPage() {
  const {
    resumeData,
    analysisResult,
    analysisProvider,
    uploadProgress,
    isUploading,
    isAnalyzing,
    error,
    analysisError,
    handleUpload,
    handleAnalyze,
  } = useResumeContext()

  return (
    <main className="dashboard-content">
      <section className="page-grid">
        <header className="glass-card hero-card">
          <h2>Upload and Analyze</h2>
          <p>Production-style AI workflow for resume evaluation and ATS insights.</p>
        </header>

        <UploadCard onUpload={handleUpload} isUploading={isUploading} progress={uploadProgress} />
        {error ? <div className="error-card">{error}</div> : null}
        <ResultCard result={resumeData} />

        {!resumeData ? (
          <motion.div
            className="glass-card empty-state"
            initial={{ opacity: 0.4 }}
            animate={{ opacity: 1 }}
          >
            <span className="empty-icon">R</span>
            <h3>No resume analyzed yet</h3>
            <p>Upload a resume PDF to start the AI analysis journey.</p>
          </motion.div>
        ) : null}

        {resumeData?.id ? (
          <div className="glass-card">
            <div className="analyze-row">
              <div>
                <h3>Run AI Analysis</h3>
                <p>Run AI analysis for summary, skills, ATS score, and suggestions.</p>
              </div>
              <button
                type="button"
                className="primary-btn"
                onClick={handleAnalyze}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Resume'}
              </button>
            </div>
          </div>
        ) : null}

        <LoadingAnalysis active={isAnalyzing} />
        {analysisError ? <div className="error-card">{analysisError}</div> : null}
        <AnalysisDashboard analysis={analysisResult} provider={analysisProvider} />
      </section>
    </main>
  )
}

export default UploadPage

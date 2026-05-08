import { createContext, useContext, useMemo, useState } from 'react'
import { analyzeResume } from '../services/analysisService'
import { uploadResume } from '../services/resumeService'

const ResumeContext = createContext(null)

function getApiErrorMessage(error, fallbackMessage) {
  return (
    error?.response?.data?.error?.message ||
    error?.response?.data?.error ||
    error?.message ||
    fallbackMessage
  )
}

export function ResumeProvider({ children }) {
  const [resumeData, setResumeData] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [analysisProvider, setAnalysisProvider] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [analysisError, setAnalysisError] = useState('')

  const handleUpload = async (file) => {
    setIsUploading(true)
    setUploadProgress(0)
    setError('')
    setAnalysisError('')

    try {
      const data = await uploadResume(file, (event) => {
        if (!event.total) return
        setUploadProgress(Math.round((event.loaded * 100) / event.total))
      })

      setResumeData(data)
      setAnalysisResult(data.analysis_result || null)
      setAnalysisProvider(data.analysis_result ? 'stored' : '')
    } catch (uploadError) {
      setError(getApiErrorMessage(uploadError, 'Upload failed. Please try again.'))
    } finally {
      setIsUploading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!resumeData?.id) return

    setIsAnalyzing(true)
    setAnalysisError('')

    try {
      const response = await analyzeResume(resumeData.id)
      setAnalysisResult(response.analysis)
      setAnalysisProvider(response.provider_used)
    } catch (analyzeError) {
      setAnalysisError(getApiErrorMessage(analyzeError, 'AI analysis failed. Please try again.'))
    } finally {
      setIsAnalyzing(false)
    }
  }

  const value = useMemo(
    () => ({
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
    }),
    [
      resumeData,
      analysisResult,
      analysisProvider,
      uploadProgress,
      isUploading,
      isAnalyzing,
      error,
      analysisError,
    ],
  )

  return <ResumeContext.Provider value={value}>{children}</ResumeContext.Provider>
}

export function useResumeContext() {
  const context = useContext(ResumeContext)
  if (!context) {
    throw new Error('useResumeContext must be used within ResumeProvider')
  }
  return context
}

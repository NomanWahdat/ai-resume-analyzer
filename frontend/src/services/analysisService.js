import apiClient from '../api/client'

export async function analyzeResume(resumeId) {
  const response = await apiClient.post(`/analyze-resume/${resumeId}/`)
  return response.data
}

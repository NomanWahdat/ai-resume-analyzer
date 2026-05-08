import apiClient from '../api/client'

export async function generateInterviewQuestions(resumeId) {
  const response = await apiClient.post(`/generate-interview-questions/${resumeId}/`)
  return response.data
}

export async function generateJobMatch(resumeId, jobDescription) {
  const response = await apiClient.post(`/job-match/${resumeId}/`, {
    job_description: jobDescription,
  })
  return response.data
}

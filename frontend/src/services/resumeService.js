import apiClient from '../api/client'

export async function uploadResume(file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post('/upload-resume/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
  })

  return response.data
}

import axios from 'axios'

const apiClient = axios.create({
  baseURL: "https://ai-resume-analyzer-production-ca21.up.railway.app/api",
  timeout: 30000,
})

export default apiClient

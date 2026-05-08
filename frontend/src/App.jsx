import { Route, Routes } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import HistoryPage from './pages/HistoryPage'
import InterviewPage from './pages/InterviewPage'
import JobMatchPage from './pages/JobMatchPage'
import SettingsPage from './pages/SettingsPage'
import UploadPage from './pages/UploadPage'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<UploadPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/interview" element={<InterviewPage />} />
        <Route path="/job-match" element={<JobMatchPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}

export default App

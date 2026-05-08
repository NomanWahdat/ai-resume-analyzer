import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { ResumeProvider } from './context/ResumeContext'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('app')).render(
  <React.StrictMode>
    <ResumeProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ResumeProvider>
  </React.StrictMode>,
)

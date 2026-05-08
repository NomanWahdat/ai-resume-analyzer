import { useState } from 'react'

function SettingsPage() {
  const [selectedProvider, setSelectedProvider] = useState('local')
  const [theme, setTheme] = useState('dark')

  return (
    <section className="page-grid">
      <div className="glass-card">
        <h2>Settings</h2>
        <p>UI mock controls for provider and theme preferences.</p>
      </div>

      <div className="glass-card">
        <h3>AI Provider</h3>
        <div className="toggle-list">
          {[
            { id: 'local', label: 'Local AI (Ollama)' },
            { id: 'groq', label: 'Groq' },
            { id: 'gemini', label: 'Gemini' },
          ].map((option) => (
            <button
              type="button"
              key={option.id}
              className={`toggle-chip ${selectedProvider === option.id ? 'selected' : ''}`}
              onClick={() => setSelectedProvider(option.id)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="glass-card">
        <h3>Theme</h3>
        <div className="toggle-list">
          {['dark', 'light'].map((mode) => (
            <button
              key={mode}
              type="button"
              className={`toggle-chip ${theme === mode ? 'selected' : ''}`}
              onClick={() => setTheme(mode)}
            >
              {mode.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}

export default SettingsPage

import { useRef, useState } from 'react'
import { motion } from 'framer-motion'

function UploadCard({ onUpload, isUploading, progress }) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  const handleFileSelection = (files) => {
    if (!files || !files.length) {
      return
    }

    const file = files[0]
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file only.')
      return
    }

    onUpload(file)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    handleFileSelection(event.dataTransfer.files)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`upload-card glass-card ${isDragging ? 'dragging' : ''}`}
      whileHover={{ y: -2 }}
      onDragOver={(event) => {
        event.preventDefault()
        setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <div className="upload-icon">
        U
      </div>
      <h2>Upload Your Resume</h2>
      <p>Drop your PDF here or browse from your device.</p>
      <button
        type="button"
        className="primary-btn"
        onClick={() => inputRef.current?.click()}
        disabled={isUploading}
      >
        {isUploading ? 'Uploading...' : 'Choose PDF'}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        hidden
        onChange={(event) => handleFileSelection(event.target.files)}
      />

      {isUploading && (
        <div className="progress-wrap">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <div className="progress-meta">
            <span>{progress}% uploaded</span>
            <div className="spinner" />
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default UploadCard

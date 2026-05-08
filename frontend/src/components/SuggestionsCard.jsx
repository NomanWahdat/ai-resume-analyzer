import { useState } from 'react'

function SuggestionsCard({ suggestions }) {
  const [isOpen, setIsOpen] = useState(true)
  const withPriority = (suggestions || []).map((item, index) => ({
    text: item,
    priority: index === 0 ? 'high' : index < 3 ? 'medium' : 'low',
  }))

  return (
    <div className="glass-card">
      <div className="card-head">
        <h3>Improvement Suggestions</h3>
        <button type="button" className="link-btn" onClick={() => setIsOpen((prev) => !prev)}>
          {isOpen ? 'Collapse' : 'Expand'}
        </button>
      </div>
      {isOpen ? (
        withPriority.length ? (
          <ul className="list-clean">
            {withPriority.map((item) => (
              <li key={item.text}>
                <span className={`priority-badge ${item.priority}`}>{item.priority}</span> {item.text}
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-text">No suggestions available</p>
        )
      ) : null}
    </div>
  )
}

export default SuggestionsCard

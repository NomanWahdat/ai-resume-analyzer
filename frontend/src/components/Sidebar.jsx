import { NavLink } from 'react-router-dom'

const navItems = [
  { label: 'Upload & Analysis', to: '/', icon: 'U' },
  { label: 'Interview Prep', to: '/interview', icon: 'I' },
  { label: 'Job Match Analyzer', to: '/job-match', icon: 'J' },
  { label: 'History', to: '/history', icon: 'H' },
  { label: 'Settings', to: '/settings', icon: 'S' },
]

function Sidebar({ isOpen, onClose }) {
  return (
    <aside className={`sidebar glass-card ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h2>Dashboard</h2>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(({ label, to, icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            onClick={onClose}
          >
            <span>{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar

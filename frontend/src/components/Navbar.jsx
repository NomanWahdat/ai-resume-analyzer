function Navbar({ onToggleSidebar }) {
  return (
    <header className="navbar glass-card">
      <button type="button" className="icon-btn mobile-only" onClick={onToggleSidebar}>
        ☰
      </button>
      <h1 className="brand-title">AI Resume Analyzer</h1>
      <div className="nav-right">
        <button type="button" className="icon-btn" aria-label="Search">
          S
        </button>
        <button type="button" className="icon-btn" aria-label="Notifications">
          N
        </button>
      </div>
    </header>
  )
}

export default Navbar

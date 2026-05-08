function SkillsCard({ title, skills, icon }) {
  return (
    <div className="glass-card">
      <h3>
        {icon} {title}
      </h3>
      <div className="chips-wrap">
        {(skills || []).length ? (
          skills.map((skill) => (
            <span className="chip" key={`${title}-${skill}`} title={`Skill detected: ${skill}`}>
              {skill}
            </span>
          ))
        ) : (
          <span className="empty-text">No data available</span>
        )}
      </div>
    </div>
  )
}

export default SkillsCard

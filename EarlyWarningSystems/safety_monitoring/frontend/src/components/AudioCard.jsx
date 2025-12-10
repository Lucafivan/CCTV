function AudioCard({ title, icon, data }) {
  const noiseLevel = data.noise_level || 0
  const threshold = data.threshold || 85
  const alert = data.alert || false
  
  const percentage = Math.min((noiseLevel / 120) * 100, 100)
  
  let progressClass = ''
  if (noiseLevel >= threshold) {
    progressClass = 'danger'
  } else if (noiseLevel >= threshold * 0.8) {
    progressClass = 'warning'
  }

  return (
    <div className={`stat-card ${alert ? 'alert' : ''}`}>
      <div className="card-header">
        <span className="card-title">{title}</span>
        <span className="card-icon">{icon}</span>
      </div>

      <div className="stat-value">{noiseLevel.toFixed(1)} dB</div>
      <div className="stat-label">
        Current Noise Level
        {threshold && ` (Threshold: ${threshold} dB)`}
      </div>

      <div className="progress-bar">
        <div 
          className={`progress-fill ${progressClass}`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>

      {alert && (
        <div style={{ 
          marginTop: '1rem',
          padding: '0.75rem',
          background: '#fef2f2',
          borderRadius: '8px',
          border: '1px solid #fecaca',
          color: '#991b1b',
          fontWeight: '600',
          fontSize: '0.875rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span>🔊</span>
          <span>NOISE THRESHOLD EXCEEDED!</span>
        </div>
      )}

      <div style={{ 
        marginTop: '1rem', 
        fontSize: '0.75rem', 
        color: '#6b7280',
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <span>0 dB</span>
        <span>{threshold} dB</span>
        <span>120 dB</span>
      </div>
    </div>
  )
}

export default AudioCard
function CameraCard({ title, icon, data, isPPE = false }) {
  if (isPPE) {
    const total = data.total_detected || 0
    const compliant = data.ppe_compliant || 0
    const nonCompliant = data.ppe_non_compliant || 0
    const complianceRate = total > 0 ? Math.round((compliant / total) * 100) : 0

    return (
      <div className={`stat-card ${nonCompliant > 0 ? 'alert' : ''}`}>
        <div className="card-header">
          <span className="card-title">{title}</span>
          <span className="card-icon">{icon}</span>
        </div>

        <div className="stat-value">{complianceRate}%</div>
        <div className="stat-label">PPE Compliance Rate</div>

        <div className="ppe-status">
          <div className="ppe-item">
            <div className="ppe-item-value" style={{ color: '#10b981' }}>
              {compliant}
            </div>
            <div className="ppe-item-label">✓ Compliant</div>
          </div>
          <div className="ppe-item">
            <div className="ppe-item-value" style={{ color: '#ef4444' }}>
              {nonCompliant}
            </div>
            <div className="ppe-item-label">✗ Non-Compliant</div>
          </div>
        </div>

        {data.missing_items && data.missing_items.length > 0 && (
          <div style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#ef4444' }}>
            Missing: {data.missing_items.join(', ')}
          </div>
        )}

        <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#6b7280' }}>
          FPS: {data.fps?.toFixed(1) || '0.0'}
        </div>
      </div>
    )
  }

  // Regular camera card (Cam0)
  const peopleCount = data.people_count || 0
  const accidentDetected = data.accident_detected || false

  return (
    <div className={`stat-card ${accidentDetected ? 'alert' : ''}`}>
      <div className="card-header">
        <span className="card-title">{title}</span>
        <span className="card-icon">{icon}</span>
      </div>

      <div className="stat-value">{peopleCount}</div>
      <div className="stat-label">People Detected</div>

      {accidentDetected && (
        <div style={{ 
          marginTop: '1rem',
          padding: '0.75rem',
          background: '#fef2f2',
          borderRadius: '8px',
          border: '1px solid #fecaca'
        }}>
          <div style={{ 
            color: '#991b1b',
            fontWeight: '600',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>⚠️</span>
            <span>ACCIDENT DETECTED!</span>
          </div>
          {data.accident_type && (
            <div style={{ 
              color: '#991b1b',
              fontSize: '0.75rem',
              marginTop: '0.25rem'
            }}>
              Type: {data.accident_type.replace(/_/g, ' ')}
            </div>
          )}
        </div>
      )}

      <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#6b7280' }}>
        FPS: {data.fps?.toFixed(1) || '0.0'}
      </div>
    </div>
  )
}

export default CameraCard
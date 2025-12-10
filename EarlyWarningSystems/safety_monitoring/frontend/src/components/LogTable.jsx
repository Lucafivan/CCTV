function LogTable({ logs }) {
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '-'
    return new Date(timestamp).toLocaleTimeString()
  }

  const formatData = (log) => {
    const data = log.data
    
    if (log.source === 'cam0') {
      return `People: ${data.people_count || 0}${data.accident_detected ? ' | ⚠️ ACCIDENT' : ''}`
    } else if (log.source === 'cam10') {
      return `PPE: ${data.ppe_compliant || 0} ✓ / ${data.ppe_non_compliant || 0} ✗`
    } else if (log.source === 'audio') {
      return `${(data.noise_level || 0).toFixed(1)} dB${data.alert ? ' | 🔊 ALERT' : ''}`
    }
    
    return JSON.stringify(data).substring(0, 50) + '...'
  }

  return (
    <div className="log-section">
      <div className="log-header">
        <h2 className="log-title">Recent Events</h2>
        <span className="log-count">{logs.length} events</span>
      </div>

      <div className="log-table-container">
        {logs.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '2rem', 
            color: '#6b7280' 
          }}>
            No events yet. Waiting for data...
          </div>
        ) : (
          <table className="log-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Source</th>
                <th>Event Type</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td>{formatTimestamp(log.timestamp)}</td>
                  <td>
                    <span className={`log-source ${log.source}`}>
                      {log.source}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.8rem' }}>
                    {log.type || '-'}
                  </td>
                  <td>
                    {formatData(log)}
                    {log.data.accident_detected && (
                      <span className="alert-badge" style={{ marginLeft: '0.5rem' }}>
                        ALERT
                      </span>
                    )}
                    {log.data.alert && (
                      <span className="alert-badge" style={{ marginLeft: '0.5rem' }}>
                        NOISE
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default LogTable
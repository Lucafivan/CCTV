import { useState, useEffect, useRef } from 'react'
import CameraCard from './CameraCard'
import AudioCard from './AudioCard'
import LogTable from './LogTable'

function Dashboard() {
  const [connected, setConnected] = useState(false)
  const [data, setData] = useState({
    cam0: { people_count: 0, accident_detected: false, fps: 0 },
    cam10: { ppe_compliant: 0, ppe_non_compliant: 0, total_detected: 0, fps: 0 },
    audio: { noise_level: 0, alert: false }
  })
  const [logs, setLogs] = useState([])
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  useEffect(() => {
    connectWebSocket()
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [])

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/dashboard')
    wsRef.current = ws

    ws.onopen = () => {
      console.log('✅ WebSocket connected')
      setConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        handleMessage(message)
      } catch (error) {
        console.error('Error parsing message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected')
      setConnected(false)
      
      // Attempt reconnection after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('🔄 Reconnecting...')
        connectWebSocket()
      }, 3000)
    }
  }

  const handleMessage = (message) => {
    // Handle different message types
    if (message.type === 'connection' || message.type === 'pong' || message.type === 'keepalive') {
      return // Ignore connection messages
    }

    // Update data based on source
    if (message.source === 'cam0') {
      setData(prev => ({
        ...prev,
        cam0: {
          people_count: message.people_count || 0,
          accident_detected: message.accident_detected || false,
          accident_type: message.accident_type,
          fps: message.fps || 0
        }
      }))
    } else if (message.source === 'cam10') {
      setData(prev => ({
        ...prev,
        cam10: {
          ppe_compliant: message.ppe_compliant || 0,
          ppe_non_compliant: message.ppe_non_compliant || 0,
          total_detected: message.total_detected || 0,
          missing_items: message.missing_items || [],
          fps: message.fps || 0
        }
      }))
    } else if (message.source === 'audio') {
      setData(prev => ({
        ...prev,
        audio: {
          noise_level: message.noise_level || 0,
          threshold: message.threshold || 85,
          alert: message.alert || false
        }
      }))
    }

    // Add to logs
    setLogs(prev => {
      const newLogs = [{
        id: Date.now(),
        timestamp: message.timestamp,
        source: message.source,
        type: message.type,
        data: message
      }, ...prev]
      
      // Keep only last 50 logs
      return newLogs.slice(0, 50)
    })
  }

  // Send ping every 20 seconds to keep connection alive
  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping')
      }
    }, 20000)

    return () => clearInterval(interval)
  }, [])

  if (!connected) {
    return (
      <div className="loading">
        <h2>Connecting to server...</h2>
        <p>Please make sure the backend is running on port 8000</p>
      </div>
    )
  }

  return (
    <div>
      <div className="stats-grid">
        <CameraCard
          title="Camera 0 - People & Accidents"
          icon="👥"
          data={data.cam0}
        />
        
        <CameraCard
          title="Camera 10 - PPE Compliance"
          icon="🦺"
          data={data.cam10}
          isPPE={true}
        />
        
        <AudioCard
          title="Noise Monitoring"
          icon="🔊"
          data={data.audio}
        />
      </div>

      <LogTable logs={logs} />
    </div>
  )
}

export default Dashboard
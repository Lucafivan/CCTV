import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>
            <span className="status-indicator"></span>
            Safety Monitoring System
          </h1>
          <div className="connection-status">
            <span>🟢</span>
            <span>System Active</span>
          </div>
        </div>
      </header>
      
      <main className="main-content">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
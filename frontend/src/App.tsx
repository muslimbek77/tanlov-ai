import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import DashboardSimple from './pages/DashboardSimple'
import TenderAnalysis from './pages/TenderAnalysis'
import AnalysisHistory from './pages/AnalysisHistory'
import AntiFraud from './pages/AntiFraud'
import Settings from './pages/Settings'
import './index.css'

// Himoyalangan route komponenti
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-background">
      <Routes>
        {/* Login sahifasi */}
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} 
        />
        
        {/* Himoyalangan sahifalar */}
        <Route 
          path="/*" 
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<DashboardSimple />} />
                  <Route path="/analysis" element={<TenderAnalysis />} />
                  <Route path="/history" element={<AnalysisHistory />} />
                  <Route path="/anti-fraud" element={<AntiFraud />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          } 
        />
      </Routes>
    </div>
  )
}

export default App

import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import DashboardSimple from './pages/DashboardSimple'
import TenderAnalysis from './pages/TenderAnalysis'
import AnalysisHistory from './pages/AnalysisHistory'
import Settings from './pages/Settings'
import './index.css'
import { animationClasses } from './lib/animations'

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
    <div className={`min-h-screen ${animationClasses['gradient-bg']} relative overflow-hidden`}>
      {/* Global Creative Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Large floating bubbles */}
        <div className="absolute -top-20 -left-20 w-48 h-48 bg-gradient-to-br from-blue-400/30 to-purple-400/30 rounded-full blur-3xl animate-float"></div>
        <div className="absolute -bottom-20 -right-20 w-56 h-56 bg-gradient-to-tr from-pink-400/30 to-orange-400/30 rounded-full blur-3xl animate-float" style={{ animationDelay: '3s' }}></div>
        <div className="absolute top-1/4 left-1/4 w-40 h-40 bg-gradient-to-bl from-green-400/25 to-teal-400/25 rounded-full blur-2xl animate-float" style={{ animationDelay: '5s' }}></div>
        <div className="absolute bottom-1/4 right-1/4 w-36 h-36 bg-gradient-to-tl from-indigo-400/25 to-blue-400/25 rounded-full blur-2xl animate-float" style={{ animationDelay: '2s' }}></div>
        
        {/* Medium bubbles */}
        <div className="absolute top-1/6 left-1/3 w-28 h-28 bg-gradient-to-br from-yellow-400/20 to-amber-400/20 rounded-full blur-xl animate-float" style={{ animationDelay: '4s' }}></div>
        <div className="absolute top-3/4 right-1/3 w-32 h-32 bg-gradient-to-tr from-cyan-400/20 to-blue-400/20 rounded-full blur-xl animate-float" style={{ animationDelay: '6s' }}></div>
        <div className="absolute bottom-1/6 left-2/3 w-24 h-24 bg-gradient-to-bl from-purple-400/20 to-pink-400/20 rounded-full blur-lg animate-float" style={{ animationDelay: '3.5s' }}></div>
        
        {/* Small bubbles */}
        <div className="absolute top-1/3 left-1/6 w-16 h-16 bg-gradient-to-br from-red-400/15 to-rose-400/15 rounded-full blur-md animate-float" style={{ animationDelay: '2.5s' }}></div>
        <div className="absolute top-2/3 left-1/2 w-18 h-18 bg-gradient-to-tr from-emerald-400/15 to-green-400/15 rounded-full blur-md animate-float" style={{ animationDelay: '4.5s' }}></div>
        <div className="absolute bottom-1/3 right-1/6 w-14 h-14 bg-gradient-to-bl from-violet-400/15 to-purple-400/15 rounded-full blur-md animate-float" style={{ animationDelay: '5.5s' }}></div>
        
        {/* Animated particles */}
        <div className="absolute top-10 left-1/4 w-2 h-2 bg-white/50 rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-1/4 w-3 h-3 bg-white/40 rounded-full animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-2/3 left-1/3 w-2 h-2 bg-white/45 rounded-full animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-1/4 right-1/3 w-2 h-2 bg-white/35 rounded-full animate-pulse" style={{ animationDelay: '3s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-1 h-1 bg-white/60 rounded-full animate-pulse" style={{ animationDelay: '1.5s' }}></div>
        <div className="absolute top-1/6 right-1/2 w-2 h-2 bg-white/40 rounded-full animate-pulse" style={{ animationDelay: '2.5s' }}></div>
        <div className="absolute bottom-1/6 left-1/4 w-1 h-1 bg-white/50 rounded-full animate-pulse" style={{ animationDelay: '3.5s' }}></div>
      </div>
      
      <div className="relative z-10">
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
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          } 
        />
      </Routes>
      </div>
    </div>
  )
}

export default App

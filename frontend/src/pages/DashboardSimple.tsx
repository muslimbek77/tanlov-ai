import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { useTheme } from '../context/ThemeContext'
import { TrendingUp, Users, FileText, AlertTriangle, Shield, CheckCircle, Loader2 } from 'lucide-react'
import { API_BASE_URL } from '../config/api'

const API_BASE = API_BASE_URL

interface Stats {
  total_tenders: number
  active_tenders: number
  total_participants: number
  tender_participants: number
  total_evaluations: number
  fraud_detections: number
  high_risk_frauds: number
  compliance_checks: number
  compliance_passed: number
}

const DashboardSimple: React.FC = () => {
  const { t } = useTheme()
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
    
    // Analysis deleted event listener
    const handleAnalysisDeleted = () => {
      console.log('Analysis deleted, refreshing stats...')
      fetchStats()
    }
    
    window.addEventListener('analysisDeleted', handleAnalysisDeleted)
    
    // LocalStorage change listener (cross-tab/cross-component)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'tender_analysis_history') {
        console.log('Analysis history changed, refreshing stats...')
        fetchStats()
      }
    }
    
    window.addEventListener('storage', handleStorageChange)
    
    return () => {
      window.removeEventListener('analysisDeleted', handleAnalysisDeleted)
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats/`)
      const data = await response.json()
      if (data.success) {
        setStats(data.stats)
      } else {
        setError(data.error || t('dashboard.error_stats'))
      }
    } catch (err) {
      setError(t('dashboard.error_server'))
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">{t('dashboard.loading')}</span>
      </div>
    )
  }

  const statCards = [
    {
      title: t('dashboard.total_tenders'),
      value: stats?.total_tenders || 0,
      subtext: `${stats?.active_tenders || 0} ${t('dashboard.active')}`,
      icon: FileText,
      color: 'text-emerald-600',
      bg: 'bg-emerald-100 dark:bg-emerald-900/30'
    },
    {
      title: t('dashboard.participants'),
      value: stats?.total_participants || 0,
      subtext: `${stats?.tender_participants || 0} ${t('dashboard.applications')}`,
      icon: Users,
      color: 'text-green-600',
      bg: 'bg-green-100 dark:bg-green-900/30'
    },
    {
      title: t('dashboard.evaluations'),
      value: stats?.total_evaluations || 0,
      subtext: t('dashboard.ai_analyses'),
      icon: TrendingUp,
      color: 'text-purple-600',
      bg: 'bg-purple-100 dark:bg-purple-900/30'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">{t('dashboard.title')}</h1>
          <p className="text-muted-foreground">{t('dashboard.subtitle')}</p>
        </div>
        <Button onClick={fetchStats} variant="outline" size="sm">
          {t('dashboard.refresh')}
        </Button>
      </div>

      {error && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-400 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-full ${stat.bg}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.subtext}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Actions */}
      <div className="grid grid-cols-1 gap-6">
        {/* Tender Tahlili */}
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground">
              <TrendingUp className="h-5 w-5 text-primary" />
              {t('dashboard.tender_analysis')}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              {t('dashboard.tender_analysis_desc')}
            </p>
            <ul className="text-sm space-y-2">
              <li className="flex items-center gap-2 text-foreground">
                <CheckCircle className="h-4 w-4 text-green-500" />
                {t('dashboard.feature1')}
              </li>
              <li className="flex items-center gap-2 text-foreground">
                <CheckCircle className="h-4 w-4 text-green-500" />
                {t('dashboard.feature2')}
              </li>
              <li className="flex items-center gap-2 text-foreground">
                <CheckCircle className="h-4 w-4 text-green-500" />
                {t('dashboard.feature3')}
              </li>
            </ul>
            <Link to="/analysis">
              <Button className="w-full">{t('dashboard.start_analysis')}</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default DashboardSimple

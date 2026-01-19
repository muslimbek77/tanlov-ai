import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'
import { useTheme } from '../context/ThemeContext'
import { 
  TrendingUp, 
  Users, 
  FileText, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  DollarSign,
  Shield,
  RefreshCw,
  BarChart3,
  ArrowRight,
  Sparkles
} from 'lucide-react'
import { API_BASE_URL } from '../config/api'
import { fadeIn, slideIn, staggerContainer, cardHover, animationClasses } from '../lib/animations'

const API_BASE = API_BASE_URL

interface DashboardStats {
  totalTenders: number
  activeTenders: number
  totalParticipants: number
  tenderParticipants: number
  totalEvaluations: number
  fraudDetections: number
  highRiskFrauds: number
  complianceChecks: number
  compliancePassed: number
}

interface AnalysisHistory {
  id: number
  date: string
  tender: string
  winner: string
  participantCount: number
  ranking: any[]
}

const Dashboard: React.FC = () => {
  const { t, language } = useTheme()
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats>({
    totalTenders: 0,
    activeTenders: 0,
    totalParticipants: 0,
    tenderParticipants: 0,
    totalEvaluations: 0,
    fraudDetections: 0,
    highRiskFrauds: 0,
    complianceChecks: 0,
    compliancePassed: 0,
  })

  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistory[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    // API dan yuklash
    fetchDashboardData()
    fetchAnalysisHistory()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Yangi dashboard-stats API
      const response = await fetch(`${API_BASE}/evaluations/dashboard-stats/`)
      const data = await response.json()
      
      if (data.success) {
        setStats(prev => ({
          ...prev,
          totalTenders: data.stats.total_tenders || 0,
          activeTenders: data.stats.active_tenders || 0,
          totalParticipants: data.stats.total_participants || 0,
          totalEvaluations: data.stats.total_evaluations || 0,
        }))
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
      // Fallback: localStorage dan
      loadAnalysisHistoryFromLocalStorage()
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const fetchAnalysisHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/evaluations/history/?limit=5`)
      const data = await response.json()
      
      if (data.success && data.history.length > 0) {
        setAnalysisHistory(data.history)
      } else {
        // Fallback: localStorage dan
        loadAnalysisHistoryFromLocalStorage()
      }
    } catch (error) {
      console.error('Error fetching history:', error)
      loadAnalysisHistoryFromLocalStorage()
    }
  }

  const loadAnalysisHistoryFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem('tender_analysis_history')
      if (saved) {
        const parsed = JSON.parse(saved)
        setAnalysisHistory(parsed.slice(0, 5))
        
        // LocalStorage'dan statistikani hisoblash
        const totalParticipants = parsed.reduce((sum: number, item: any) => sum + (item.participantCount || 0), 0)
        
        setStats(prev => ({
          ...prev,
          totalTenders: Math.max(prev.totalTenders, parsed.length),
          totalEvaluations: Math.max(prev.totalEvaluations, parsed.length),
          totalParticipants: Math.max(prev.totalParticipants, totalParticipants),
          activeTenders: Math.max(prev.activeTenders, parsed.length),
        }))
      }
    } catch (e) {
      console.error('Error loading from localStorage:', e)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    fetchDashboardData()
    fetchAnalysisHistory()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="relative">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary/20 border-t-primary"></div>
          <Sparkles className="absolute inset-0 m-auto h-6 w-6 text-primary animate-pulse" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 relative z-10">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="animate-fade-in">
          <h1 className="text-5xl font-bold tracking-tight text-foreground flex items-center gap-4">
            {t('dashboard.title')}
            <div className="relative">
              <Sparkles className="w-10 h-10 text-yellow-500 animate-pulse" />
              <div className="absolute inset-0 bg-yellow-400/40 rounded-full blur-lg animate-pulse"></div>
            </div>
          </h1>
          <p className="text-muted-foreground text-xl mt-3">
            {t('dashboard.subtitle')}
          </p>
        </div>
        <Button 
          onClick={handleRefresh} 
          disabled={refreshing}
          className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
          <RefreshCw className={`mr-3 h-5 w-5 relative z-10 ${refreshing ? 'animate-spin' : ''}`} />
          <span className="relative z-10 font-semibold">{t('dashboard.refresh')}</span>
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-8 md:grid-cols-2" {...staggerContainer(0.1)}>
        <Card className={`${animationClasses['glass-effect']} border-0 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 hover:scale-[1.02] transition-all duration-400 animate-slide-up relative overflow-hidden group`} style={{ animationDelay: '0.1s' }}>
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-gradient-shift"></div>
          <div className="absolute -top-8 -right-8 w-16 h-16 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-lg animate-float"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3 relative z-10">
            <CardTitle className="text-sm font-semibold">{t('dashboard.total_tenders')}</CardTitle>
            <div className="relative group">
              <FileText className="h-5 w-5 text-blue-500 group-hover:text-blue-600 transition-colors duration-300" />
              <div className="absolute -inset-2 bg-blue-500/20 rounded-full animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </div>
          </CardHeader>
          <CardContent className="relative z-10">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{stats.totalTenders}</div>
            <p className="text-sm text-muted-foreground flex items-center gap-1">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              {stats.activeTenders} {t('dashboard.active')}
            </p>
          </CardContent>
        </Card>

        <Card className={`${animationClasses['glass-effect']} border-0 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 hover:scale-[1.02] transition-all duration-400 animate-slide-up relative overflow-hidden group`} style={{ animationDelay: '0.2s' }}>
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 animate-gradient-shift"></div>
          <div className="absolute -top-8 -right-8 w-16 h-16 bg-gradient-to-br from-green-400/20 to-emerald-400/20 rounded-full blur-lg animate-float"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3 relative z-10">
            <CardTitle className="text-sm font-semibold">{t('dashboard.participants')}</CardTitle>
            <div className="relative group">
              <Users className="h-5 w-5 text-green-500 group-hover:text-green-600 transition-colors duration-300" />
              <div className="absolute -inset-2 bg-green-500/20 rounded-full animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </div>
          </CardHeader>
          <CardContent className="relative z-10">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">{stats.totalParticipants}</div>
            <p className="text-sm text-muted-foreground flex items-center gap-1">
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
              {stats.tenderParticipants} {t('dashboard.applications')}
            </p>
          </CardContent>
        </Card>

        <Card className={`${animationClasses['glass-effect']} border-0 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 hover:scale-[1.02] transition-all duration-400 animate-slide-up relative overflow-hidden group`} style={{ animationDelay: '0.3s' }}>
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 via-green-500 to-teal-500 animate-gradient-shift"></div>
          <div className="absolute -top-8 -right-8 w-16 h-16 bg-gradient-to-br from-emerald-400/20 to-green-400/20 rounded-full blur-lg animate-float"></div>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3 relative z-10">
            <CardTitle className="text-sm font-semibold">{t('dashboard.evaluations')}</CardTitle>
            <div className="relative group">
              <CheckCircle className="h-5 w-5 text-emerald-500 group-hover:text-emerald-600 transition-colors duration-300" />
              <div className="absolute -inset-2 bg-emerald-500/20 rounded-full animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEvaluations}</div>
            <p className="text-xs text-muted-foreground">
              {t('dashboard.ai_analyses')}
            </p>
          </CardContent>
        </Card>

      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-1">
        <Card className="border-2 border-primary/20 hover:border-primary/40 transition-colors cursor-pointer" onClick={() => navigate('/analysis')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground">
              <BarChart3 className="h-5 w-5 text-primary" />
              {language === 'uz_latn' ? 'Tender Tahlili' : language === 'uz_cyrl' ? 'Тендер таҳлили' : 'Анализ тендера'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              {language === 'uz_latn' 
                ? 'AI yordamida tender shartnomasini tahlil qiling va ishtirokchilarni baholang.'
                : language === 'uz_cyrl' 
                ? 'AI ёрдамида тендер шартномасини таҳлил қилиш ва иштирокчиларни баҳоланг.'
                : 'Анализируйте тендерные условия и оценивайте участников с помощью ИИ.'}
            </p>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>✓ {language === 'uz_latn' ? 'Tender talablarini avtomatik aniqlash' : language === 'uz_cyrl' ? 'Тендер талабларини автоматик аниқлаш' : 'Автоматическое определение требований'}</li>
              <li>✓ {language === 'uz_latn' ? 'Ishtirokchilarni har taraflama tahlil' : language === 'uz_cyrl' ? 'Иштирокчиларни ҳар томонлама таҳлил' : 'Всесторонний анализ участников'}</li>
              <li>✓ {language === 'uz_latn' ? "G'olibni aniqlash va tavsiyalar" : language === 'uz_cyrl' ? "Ғолибни аниқлаш ва тавсиялар" : 'Определение победителя и рекомендации'}</li>
            </ul>
            <Button className="w-full">
              {language === 'uz_latn' ? 'Tahlilni Boshlash' : language === 'uz_cyrl' ? 'Таҳилни бошлаш' : 'Начать анализ'}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Analysis History */}
      {analysisHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-foreground">
              {language === 'uz_latn' ? 'So\'nggi Tahlillar' : language === 'uz_cyrl' ? 'Сўнгги таҳиллар' : 'Недавние анализы'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analysisHistory.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <BarChart3 className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground truncate max-w-[300px]">
                        {item.tender}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {language === 'uz_latn' ? "G'olib" : language === 'uz_cyrl' ? "Ғолиб" : 'Победитель'}: {item.winner} • {item.participantCount} {language === 'uz_latn' ? 'ishtirokchi' : language === 'uz_cyrl' ? 'иштирокчи' : 'участников'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="default">
                      {language === 'uz_latn' ? 'Yakunlangan' : language === 'uz_cyrl' ? 'Якунланган' : 'Завершён'}
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(item.date).toLocaleDateString(language === 'uz_latn' ? 'uz-UZ' : language === 'uz_cyrl' ? 'uz-Cyrl' : 'ru-RU')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Dashboard

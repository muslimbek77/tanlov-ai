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
  ArrowRight
} from 'lucide-react'
import { API_BASE_URL } from '../config/api'

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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">{t('dashboard.title')}</h1>
          <p className="text-muted-foreground">
            {t('dashboard.subtitle')}
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          {language === 'uz' ? 'Yangilash' : 'Обновить'}
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.total_tenders')}</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTenders}</div>
            <p className="text-xs text-muted-foreground">
              {stats.activeTenders} {t('dashboard.active')}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.participants')}</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalParticipants}</div>
            <p className="text-xs text-muted-foreground">
              {stats.tenderParticipants} {language === 'uz' ? 'ta ariza' : 'заявок'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.evaluated')}</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEvaluations}</div>
            <p className="text-xs text-muted-foreground">
              {language === 'uz' ? 'AI tahlillari' : 'AI анализы'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.fraud_risks')}</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.fraudDetections}</div>
            <p className="text-xs text-muted-foreground">
              {stats.highRiskFrauds} {language === 'uz' ? 'ta yuqori xavf' : 'высокий риск'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{language === 'uz' ? 'Compliance' : 'Соответствие'}</CardTitle>
            <Shield className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.complianceChecks}</div>
            <p className="text-xs text-muted-foreground">
              {stats.compliancePassed} {language === 'uz' ? "ta o'tdi" : 'прошли'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="border-2 border-primary/20 hover:border-primary/40 transition-colors cursor-pointer" onClick={() => navigate('/analysis')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground">
              <BarChart3 className="h-5 w-5 text-primary" />
              {language === 'uz' ? 'Tender Tahlili' : 'Анализ тендера'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              {language === 'uz' 
                ? 'AI yordamida tender shartnomasini tahlil qiling va ishtirokchilarni baholang.'
                : 'Анализируйте тендерные условия и оценивайте участников с помощью ИИ.'}
            </p>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>✓ {language === 'uz' ? 'Tender talablarini avtomatik aniqlash' : 'Автоматическое определение требований'}</li>
              <li>✓ {language === 'uz' ? 'Ishtirokchilarni har taraflama tahlil' : 'Всесторонний анализ участников'}</li>
              <li>✓ {language === 'uz' ? "G'olibni aniqlash va tavsiyalar" : 'Определение победителя и рекомендации'}</li>
            </ul>
            <Button className="w-full">
              {language === 'uz' ? 'Tahlilni Boshlash' : 'Начать анализ'}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>

        <Card className="border-2 border-amber-500/20 hover:border-amber-500/40 transition-colors cursor-pointer" onClick={() => navigate('/anti-fraud')}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              {language === 'uz' ? 'Anti-Fraud Tizimi' : 'Антифрод система'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              {language === 'uz' 
                ? 'Korrupsiya va firibgarlik belgilarini avtomatik aniqlash.'
                : 'Автоматическое обнаружение признаков коррупции и мошенничества.'}
            </p>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>✓ {language === 'uz' ? "Metadata o'xshashligini tahlil" : 'Анализ сходства метаданных'}</li>
              <li>✓ {language === 'uz' ? 'Narx anomaliyalarini aniqlash' : 'Обнаружение ценовых аномалий'}</li>
              <li>✓ {language === 'uz' ? 'Kelishilgan takliflarni aniqlash' : 'Обнаружение сговора'}</li>
            </ul>
            <Button variant="outline" className="w-full">
              {language === 'uz' ? 'Anti-Fraud Tahlili' : 'Антифрод анализ'}
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
              {language === 'uz' ? 'So\'nggi Tahlillar' : 'Недавние анализы'}
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
                        {language === 'uz' ? "G'olib" : 'Победитель'}: {item.winner} • {item.participantCount} {language === 'uz' ? 'ishtirokchi' : 'участников'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="default">
                      {language === 'uz' ? 'Yakunlangan' : 'Завершён'}
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(item.date).toLocaleDateString(language === 'uz' ? 'uz-UZ' : 'ru-RU')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Risk Indicators - show only if there's data */}
      {(stats.fraudDetections > 0 || stats.complianceChecks > 0) && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-foreground">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                {t('dashboard.fraud_risks')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-foreground">{t('dashboard.detected_risks')}</span>
                <Badge variant="destructive">{stats.fraudDetections}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-foreground">{t('risk.high')}</span>
                <Badge variant="destructive">{stats.highRiskFrauds}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-foreground">{t('risk.medium')}</span>
                <Badge variant="secondary">{Math.max(0, stats.fraudDetections - stats.highRiskFrauds)}</Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-foreground">
                <Shield className="h-5 w-5 text-emerald-500" />
                {t('dashboard.compliance_status')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-foreground">{language === 'uz' ? "Jami tekshiruvlar" : 'Всего проверок'}</span>
                <Badge variant="secondary">{stats.complianceChecks}</Badge>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-foreground">
                  <span>{language === 'uz' ? "O'tganlar" : 'Прошли'}</span>
                  <span>{stats.complianceChecks > 0 ? Math.round((stats.compliancePassed / stats.complianceChecks) * 100) : 0}%</span>
                </div>
                <Progress value={stats.complianceChecks > 0 ? (stats.compliancePassed / stats.complianceChecks) * 100 : 0} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export default Dashboard

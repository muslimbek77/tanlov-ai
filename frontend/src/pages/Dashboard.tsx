import React, { useState, useEffect } from 'react'
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
  Shield
} from 'lucide-react'

interface DashboardStats {
  totalTenders: number
  activeTenders: number
  totalParticipants: number
  totalEvaluations: number
  fraudDetections: number
  complianceIssues: number
  avgScore: number
  totalBudget: number
}

interface RecentActivity {
  id: string
  type: 'tender' | 'evaluation' | 'fraud' | 'compliance'
  title_uz: string
  title_ru: string
  description_uz: string
  description_ru: string
  timestamp: string
  status: string
}

const Dashboard: React.FC = () => {
  const { t, language } = useTheme()
  const [stats, setStats] = useState<DashboardStats>({
    totalTenders: 0,
    activeTenders: 0,
    totalParticipants: 0,
    totalEvaluations: 0,
    fraudDetections: 0,
    complianceIssues: 0,
    avgScore: 0,
    totalBudget: 0,
  })

  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setStats({
        totalTenders: 156,
        activeTenders: 23,
        totalParticipants: 892,
        totalEvaluations: 134,
        fraudDetections: 12,
        complianceIssues: 8,
        avgScore: 78.5,
        totalBudget: 2500000000,
      })

      setRecentActivity([
        {
          id: '1',
          type: 'tender',
          title_uz: 'Yangi tender yaratildi',
          title_ru: 'Создан новый тендер',
          description_uz: '"Ko\'pkap qurilishi" loyihasi uchun tender e\'lon qilindi',
          description_ru: 'Объявлен тендер на проект "Строительство моста"',
          timestamp: '2024-01-07T10:30:00Z',
          status: 'active',
        },
        {
          id: '2',
          type: 'evaluation',
          title_uz: 'Baholash yakunlandi',
          title_ru: 'Оценка завершена',
          description_uz: '15 ta ishtirokchi baholandi, g\'olib aniqlandi',
          description_ru: 'Оценено 15 участников, определён победитель',
          timestamp: '2024-01-07T09:15:00Z',
          status: 'completed',
        },
        {
          id: '3',
          type: 'fraud',
          title_uz: 'Firibgarlik xavfi aniqlandi',
          title_ru: 'Обнаружен риск мошенничества',
          description_uz: '2 ta ishtirokchi o\'rtasida yuqori o\'xshashlik topildi',
          description_ru: 'Обнаружено высокое сходство между 2 участниками',
          timestamp: '2024-01-07T08:45:00Z',
          status: 'high',
        },
        {
          id: '4',
          type: 'compliance',
          title_uz: 'Compliance tekshiruvi',
          title_ru: 'Проверка соответствия',
          description_uz: 'O\'RQ-684 talablariga muvofiqlik tekshirildi',
          description_ru: 'Проверено соответствие требованиям ОРК-684',
          timestamp: '2024-01-07T08:00:00Z',
          status: 'passed',
        },
      ])
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'tender':
        return <FileText className="h-4 w-4" />
      case 'evaluation':
        return <CheckCircle className="h-4 w-4" />
      case 'fraud':
        return <AlertTriangle className="h-4 w-4" />
      case 'compliance':
        return <Shield className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('uz-UZ', {
      style: 'currency',
      currency: 'UZS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
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
        <Button>
          <TrendingUp className="mr-2 h-4 w-4" />
          {t('dashboard.download_report')}
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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
              {t('dashboard.all_time')}
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
              {t('dashboard.avg_score')}: {stats.avgScore}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.total_budget')}</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(stats.totalBudget)}
            </div>
            <p className="text-xs text-muted-foreground">
              {t('dashboard.all_tenders')}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Risk Indicators */}
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
              <Badge variant="destructive">3</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-foreground">{t('risk.medium')}</span>
              <Badge variant="secondary">5</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-foreground">{t('risk.low')}</span>
              <Badge variant="outline">4</Badge>
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
              <span className="text-sm text-foreground">{t('dashboard.compliance_issues')}</span>
              <Badge variant="secondary">{stats.complianceIssues}</Badge>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-foreground">
                <span>{t('dashboard.orq_compliance')}</span>
                <span>87%</span>
              </div>
              <Progress value={87} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-foreground">
                <span>{t('dashboard.docs_complete')}</span>
                <span>92%</span>
              </div>
              <Progress value={92} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-foreground">{t('dashboard.recent_activity')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {language === 'uz' ? activity.title_uz : activity.title_ru}
                  </p>
                  <p className="text-sm text-muted-foreground truncate">
                    {language === 'uz' ? activity.description_uz : activity.description_ru}
                  </p>
                </div>
                <div className="flex-shrink-0 text-right">
                  <Badge 
                    variant={
                      activity.status === 'completed' ? 'default' :
                      activity.status === 'active' ? 'secondary' :
                      activity.status === 'high' ? 'destructive' : 'outline'
                    }
                  >
                    {activity.status}
                  </Badge>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(activity.timestamp).toLocaleString(language === 'uz' ? 'uz-UZ' : 'ru-RU')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard

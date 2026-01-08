import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { useTheme } from '../context/ThemeContext'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'
import { 
  History,
  Award,
  Users,
  Trash2,
  Eye,
  Plus,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Calendar,
  FileText,
  TrendingUp,
  Search
} from 'lucide-react'

interface ParticipantAnalysis {
  participant_name: string
  overall_match_percentage: number
  total_weighted_score: number
  strengths: string[]
  weaknesses: string[]
  price_analysis: {
    proposed_price: string
    price_adequacy: string
    price_score: number
  }
  recommendation: string
  risk_level: string
}

interface SavedResult {
  id: number
  date: string
  tender: string
  winner: string
  ranking: ParticipantAnalysis[]
  summary: string
  participantCount: number
  tenderAnalysis?: any
  participantAnalyses?: ParticipantAnalysis[]
}

const AnalysisHistory: React.FC = () => {
  const navigate = useNavigate()
  const { t } = useTheme()
  const [savedResults, setSavedResults] = useState<SavedResult[]>([])
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [selectedResult, setSelectedResult] = useState<SavedResult | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadSavedResults()
  }, [])

  const loadSavedResults = () => {
    try {
      const saved = localStorage.getItem('tender_analysis_history')
      if (saved) {
        setSavedResults(JSON.parse(saved))
      }
    } catch (e) {
      console.error('Saved results loading error:', e)
    }
  }

  const deleteResult = (id: number) => {
    const updated = savedResults.filter(r => r.id !== id)
    setSavedResults(updated)
    localStorage.setItem('tender_analysis_history', JSON.stringify(updated))
    if (selectedResult?.id === id) {
      setSelectedResult(null)
    }
  }

  const clearAllHistory = () => {
    if (confirm(t('history.delete_all') + '?')) {
      setSavedResults([])
      localStorage.removeItem('tender_analysis_history')
      setSelectedResult(null)
    }
  }

  const continueAnalysis = (result: SavedResult) => {
    localStorage.setItem('continue_analysis', JSON.stringify({
      tenderAnalysis: result.tenderAnalysis,
      participantAnalyses: result.participantAnalyses || result.ranking,
      ranking: result.ranking,
      summary: result.summary
    }))
    navigate('/analysis?continue=true')
  }

  const getRiskBadge = (level: string) => {
    const styles: Record<string, string> = {
      low: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
      medium: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
      high: 'bg-red-500/10 text-red-500 border-red-500/20'
    }
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[level] || 'bg-gray-500/10 text-gray-500'}`}>
        {t(`risk.${level}`)}
      </span>
    )
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('uz-UZ', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filteredResults = savedResults.filter(r => 
    r.tender.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.winner.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getScoreDisplay = (participant: ParticipantAnalysis) => {
    const score = participant.total_weighted_score || participant.overall_match_percentage || 0
    return score
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 p-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-xl">
              <History className="w-8 h-8 text-primary" />
            </div>
            {t('history.title')}
          </h1>
          <p className="text-muted-foreground mt-2">{t('history.subtitle')}</p>
        </div>
        <div className="flex gap-3">
          <Button 
            onClick={() => navigate('/analysis')}
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('analysis.new_analysis')}
          </Button>
          {savedResults.length > 0 && (
            <Button 
              variant="outline" 
              onClick={clearAllHistory}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              {t('history.delete_all')}
            </Button>
          )}
        </div>
      </div>

      {savedResults.length === 0 ? (
        <Card className="border-dashed border-2 bg-card/50 backdrop-blur">
          <CardContent className="py-20 text-center">
            <div className="w-20 h-20 mx-auto bg-muted rounded-full flex items-center justify-center mb-6">
              <History className="w-10 h-10 text-muted-foreground" />
            </div>
            <h3 className="text-2xl font-semibold text-foreground mb-2">{t('history.empty')}</h3>
            <p className="text-muted-foreground mb-6">{t('history.empty_desc')}</p>
            <Button 
              onClick={() => navigate('/analysis')}
            >
              <Plus className="w-4 h-4 mr-2" />
              {t('history.start_first')}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="text"
              placeholder={t('common.search') + '...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-card border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Panel */}
            <div className="lg:col-span-4 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  {t('history.total')}: <span className="font-semibold text-foreground">{filteredResults.length}</span> {t('history.analyses')}
                </span>
              </div>
              
              <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto pr-2">
                {filteredResults.map((result) => (
                  <div 
                    key={result.id} 
                    onClick={() => setSelectedResult(result)}
                    className={`group p-4 rounded-xl border cursor-pointer transition-all duration-200 hover:shadow-md ${
                      selectedResult?.id === result.id 
                        ? 'bg-primary/5 border-primary' 
                        : 'bg-card border-border hover:border-primary/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-foreground truncate">{result.tender}</h4>
                        <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                          <Calendar className="w-3.5 h-3.5" />
                          {formatDate(result.date)}
                        </div>
                        <div className="flex items-center gap-2 mt-3">
                          <Badge variant="secondary" className="text-xs">
                            <Award className="w-3 h-3 mr-1" />
                            {result.winner}
                          </Badge>
                          <Badge variant="secondary" className="text-xs">
                            <Users className="w-3 h-3 mr-1" />
                            {result.participantCount}
                          </Badge>
                        </div>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteResult(result.id)
                        }}
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Panel */}
            <div className="lg:col-span-8">
              {selectedResult ? (
                <div className="space-y-5">
                  {/* Header Card */}
                  <Card className="overflow-hidden border-primary">
                    <CardContent className="p-6">
                      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                        <div>
                          <h3 className="text-2xl font-bold">{selectedResult.tender}</h3>
                          <p className="text-muted-foreground text-sm mt-1 flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            {formatDate(selectedResult.date)}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            onClick={() => continueAnalysis(selectedResult)}
                          >
                            <Plus className="w-4 h-4 mr-2" />
                            {t('analysis.add_participant')}
                          </Button>
                          <Button 
                            variant="outline"
                            onClick={() => continueAnalysis(selectedResult)}
                          >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            {t('history.reanalyze')}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Winner Card */}
                  <Card className="overflow-hidden">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-14 h-14 bg-primary rounded-xl flex items-center justify-center">
                          <Award className="w-7 h-7 text-primary-foreground" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">{t('analysis.winner')}</p>
                          <h4 className="text-xl font-bold">{selectedResult.winner}</h4>
                        </div>
                      </div>
                      
                      {selectedResult.ranking[0] && (
                        <div className="grid grid-cols-3 gap-4 mt-4">
                          <div className="bg-muted rounded-xl p-4 text-center">
                            <p className="text-3xl font-bold text-primary">
                              {getScoreDisplay(selectedResult.ranking[0]).toFixed(1)}%
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">{t('analysis.total_score')}</p>
                          </div>
                          <div className="bg-muted rounded-xl p-4 text-center">
                            <p className="text-3xl font-bold text-primary">
                              {selectedResult.ranking[0].overall_match_percentage || 0}%
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">{t('analysis.match')}</p>
                          </div>
                          <div className="bg-muted rounded-xl p-4 text-center">
                            {getRiskBadge(selectedResult.ranking[0].risk_level)}
                            <p className="text-xs text-muted-foreground mt-2">{t('analysis.risk_level')}</p>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Ranking */}
                  <Card className="border-border/50 shadow-lg">
                    <CardHeader className="pb-2">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <TrendingUp className="w-5 h-5 text-primary" />
                        {t('analysis.ranking')}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        {selectedResult.ranking.map((p, index) => {
                          const score = getScoreDisplay(p)
                          return (
                            <div 
                              key={index}
                              className={`p-4 rounded-xl transition-all ${
                                index === 0 
                                  ? 'bg-primary/5 border border-primary/20' 
                                  : 'bg-muted/30 border border-border hover:bg-muted/50'
                              }`}
                            >
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-3">
                                  <span className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm ${
                                    index === 0 
                                      ? 'bg-primary text-primary-foreground' 
                                      : 'bg-muted text-muted-foreground'
                                  }`}>
                                    {index + 1}
                                  </span>
                                  <span className="font-medium">{p.participant_name}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                  {getRiskBadge(p.risk_level)}
                                  <span className="text-xl font-bold text-primary">
                                    {score.toFixed(1)}%
                                  </span>
                                </div>
                              </div>
                              
                              <Progress value={score} className="h-2 bg-muted" />
                              
                              <button
                                className="w-full mt-3 text-xs text-muted-foreground hover:text-foreground flex items-center justify-center gap-1 transition-colors"
                                onClick={() => setExpandedId(expandedId === index ? null : index)}
                              >
                                {expandedId === index ? (
                                  <>{t('history.hide')} <ChevronUp className="w-4 h-4" /></>
                                ) : (
                                  <>{t('history.details')} <ChevronDown className="w-4 h-4" /></>
                                )}
                              </button>
                              
                              {expandedId === index && (
                                <div className="mt-4 pt-4 border-t border-border grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                  <div className="space-y-2">
                                    <p className="font-medium flex items-center gap-1">
                                      <TrendingUp className="w-4 h-4" /> {t('analysis.strengths')}
                                    </p>
                                    <ul className="space-y-1 text-muted-foreground">
                                      {(p.strengths || []).slice(0, 5).map((s, i) => (
                                        <li key={i} className="flex items-start gap-2">
                                          <span className="mt-1">•</span>
                                          {s}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                  <div className="space-y-2">
                                    <p className="font-medium flex items-center gap-1">
                                      <TrendingUp className="w-4 h-4 rotate-180" /> {t('analysis.weaknesses')}
                                    </p>
                                    <ul className="space-y-1 text-muted-foreground">
                                      {(p.weaknesses || []).slice(0, 5).map((w, i) => (
                                        <li key={i} className="flex items-start gap-2">
                                          <span className="mt-1">•</span>
                                          {w}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                  {p.price_analysis && (
                                    <div className="col-span-full p-3 bg-muted/30 rounded-lg">
                                      <span className="text-muted-foreground">{t('history.price')}: </span>
                                      <span className="font-medium text-foreground">{p.price_analysis.proposed_price}</span>
                                    </div>
                                  )}
                                  {p.recommendation && (
                                    <div className="col-span-full p-3 bg-muted rounded-lg">
                                      <span className="font-medium">{t('analysis.recommendation')}: </span>
                                      {p.recommendation}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Summary */}
                  {selectedResult.summary && (
                    <Card className="border-border/50 shadow-lg">
                      <CardHeader className="pb-2">
                        <CardTitle className="flex items-center gap-2 text-lg">
                        <FileText className="w-5 h-5 text-primary" />
                          {t('analysis.summary')}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-4">
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                          <ReactMarkdown
                            components={{
                              h1: ({children}) => <h1 className="text-xl font-bold mt-4 mb-2">{children}</h1>,
                              h2: ({children}) => <h2 className="text-lg font-bold mt-4 mb-2">{children}</h2>,
                              p: ({children}) => <p className="mb-2 text-muted-foreground">{children}</p>,
                              ul: ({children}) => <ul className="list-disc list-inside mb-2 ml-4 text-muted-foreground">{children}</ul>,
                              strong: ({children}) => <strong className="font-bold text-foreground">{children}</strong>,
                            }}
                          >
                            {selectedResult.summary}
                          </ReactMarkdown>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              ) : (
                <Card className="h-[400px] flex items-center justify-center border-dashed border-2 bg-card/50">
                  <CardContent className="text-center">
                    <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center mb-4">
                      <Eye className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <h3 className="text-xl font-medium text-foreground">{t('history.select')}</h3>
                    <p className="text-muted-foreground mt-2">{t('history.select_desc')}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default AnalysisHistory

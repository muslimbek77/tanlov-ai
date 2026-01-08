import React, { useState, useCallback, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { useTheme } from '../context/ThemeContext'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'
import { 
  Upload, 
  FileText, 
  Users, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  TrendingUp,
  Award,
  Loader2,
  Plus,
  Trash2,
  BarChart3,
  History
} from 'lucide-react'

const API_BASE = 'http://localhost:8000/api/evaluations'

interface Requirement {
  id: string
  category: string
  title: string
  description: string
  is_mandatory: boolean
  weight: number
}

interface ParticipantScore {
  requirement_id: string
  score: number
  matches: boolean
  reason: string
}

interface ParticipantAnalysis {
  participant_name: string
  overall_match_percentage: number
  total_weighted_score: number
  scores: ParticipantScore[]
  strengths: string[]
  weaknesses: string[]
  price_analysis: {
    proposed_price: string
    price_adequacy: string
    price_score: number
  }
  recommendation: string
  risk_level: string
  rank?: number
}

interface TenderAnalysis {
  tender_purpose: string
  tender_type: string
  requirements: Requirement[]
  evaluation_criteria: any[]
  key_conditions: string[]
  warnings: string[]
  requirements_count: number
  mandatory_count: number
}

const TenderAnalysis: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { language, t } = useTheme()
  
  // States
  const [step, setStep] = useState<'tender' | 'participants' | 'results'>('tender')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showHistory, setShowHistory] = useState(false)
  const [savedResults, setSavedResults] = useState<any[]>([])
  
  // Tender
  const [tenderFile, setTenderFile] = useState<File | null>(null)
  const [tenderAnalysis, setTenderAnalysis] = useState<TenderAnalysis | null>(null)
  
  // Participants
  const [participantFiles, setParticipantFiles] = useState<{name: string, file: File}[]>([])
  const [participantAnalyses, setParticipantAnalyses] = useState<ParticipantAnalysis[]>([])
  
  // Results
  const [ranking, setRanking] = useState<ParticipantAnalysis[]>([])
  const [winner, setWinner] = useState<ParticipantAnalysis | null>(null)
  const [summary, setSummary] = useState<string>('')

  // Load saved results on mount and check for continue parameter
  useEffect(() => {
    loadSavedResults()
    
    // Tarixdan davom ettirish
    if (searchParams.get('continue') === 'true') {
      const continueData = localStorage.getItem('continue_analysis')
      if (continueData) {
        try {
          const data = JSON.parse(continueData)
          if (data.tenderAnalysis) {
            setTenderAnalysis(data.tenderAnalysis)
          }
          if (data.participantAnalyses) {
            setParticipantAnalyses(data.participantAnalyses)
          }
          if (data.ranking) {
            setRanking(data.ranking)
            setWinner(data.ranking[0] || null)
          }
          if (data.summary) {
            setSummary(data.summary)
          }
          // Ishtirokchilar sahifasiga o'tish (yangi ishtirokchi qo'shish uchun)
          setStep('participants')
          setParticipantFiles([{ name: '', file: null as any }])
          // localStorage ni tozalash
          localStorage.removeItem('continue_analysis')
        } catch (e) {
          console.error('Continue analysis error:', e)
        }
      }
    }
  }, [searchParams])

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

  const saveCurrentResult = () => {
    if (!ranking.length || !summary) return
    
    const result = {
      id: Date.now(),
      date: new Date().toISOString(),
      tender: tenderAnalysis?.tender_purpose || 'Noma\'lum tender',
      winner: winner?.participant_name || 'Noma\'lum',
      ranking,
      summary,
      participantCount: ranking.length,
      tenderAnalysis,
      participantAnalyses
    }
    
    const updatedResults = [result, ...savedResults].slice(0, 10) // Keep last 10
    setSavedResults(updatedResults)
    localStorage.setItem('tender_analysis_history', JSON.stringify(updatedResults))
  }

  const loadSavedResult = (result: any) => {
    setRanking(result.ranking)
    setSummary(result.summary)
    setWinner(result.ranking[0] || null)
    // Tender ma'lumotlarini tiklash
    if (result.tenderAnalysis) {
      setTenderAnalysis(result.tenderAnalysis)
    }
    // Ishtirokchi analyses ni tiklash
    if (result.participantAnalyses) {
      setParticipantAnalyses(result.participantAnalyses)
    }
    setStep('results')
    setShowHistory(false)
  }

  const deleteSavedResult = (id: number) => {
    const updated = savedResults.filter(r => r.id !== id)
    setSavedResults(updated)
    localStorage.setItem('tender_analysis_history', JSON.stringify(updated))
  }

  // Tender faylini yuklash
  const handleTenderUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setTenderFile(file)
      setError(null)
    }
  }, [])

  // Tender tahlil qilish
  const analyzeTender = async () => {
    if (!tenderFile) {
      setError(language === 'uz' ? 'Tender faylini yuklang' : 'Загрузите файл тендера')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', tenderFile)
      formData.append('language', language)

      const response = await fetch(`${API_BASE}/analyze-tender/`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (data.success) {
        setTenderAnalysis(data.analysis)
        setStep('participants')
      } else {
        setError(data.error || (language === 'uz' ? 'Tahlilda xatolik' : 'Ошибка анализа'))
      }
    } catch (err) {
      setError(language === 'uz' ? 'Server bilan aloqa xatosi' : 'Ошибка соединения с сервером')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Ishtirokchi qo'shish
  const addParticipant = () => {
    setParticipantFiles([...participantFiles, { name: '', file: null as any }])
  }

  // Ishtirokchi o'chirish
  const removeParticipant = (index: number) => {
    setParticipantFiles(participantFiles.filter((_, i) => i !== index))
  }

  // Ishtirokchi faylini yuklash
  const handleParticipantFile = (index: number, file: File) => {
    const updated = [...participantFiles]
    updated[index] = { 
      ...updated[index], 
      file,
      name: updated[index].name || file.name.replace(/\.[^/.]+$/, '')
    }
    setParticipantFiles(updated)
  }

  // Ishtirokchi nomini o'zgartirish
  const handleParticipantName = (index: number, name: string) => {
    const updated = [...participantFiles]
    updated[index] = { ...updated[index], name }
    setParticipantFiles(updated)
  }

  // Barcha ishtirokchilarni tahlil qilish
  const analyzeParticipants = async () => {
    const validParticipants = participantFiles.filter(p => p.file && p.name)
    
    if (validParticipants.length === 0) {
      setError(t('analysis.at_least_one'))
      return
    }

    setLoading(true)
    setError(null)
    // Oldingi tahlillarni saqlash
    const analyses: ParticipantAnalysis[] = [...participantAnalyses]

    try {
      for (const participant of validParticipants) {
        // Allaqachon tahlil qilingan ishtirokchini o'tkazib yuborish
        if (analyses.some(a => a.participant_name === participant.name)) {
          continue
        }
        
        const formData = new FormData()
        formData.append('name', participant.name)
        formData.append('file', participant.file)
        formData.append('language', language)

        const response = await fetch(`${API_BASE}/analyze-participant/`, {
          method: 'POST',
          body: formData
        })

        const data = await response.json()

        if (data.success) {
          analyses.push(data.analysis)
        }
      }

      setParticipantAnalyses(analyses)
      // Fayl ro'yxatini tozalash
      setParticipantFiles([])

      // Solishtirish
      if (analyses.length > 0) {
        const compareResponse = await fetch(`${API_BASE}/compare-participants/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ participants: analyses, language })
        })

        const compareData = await compareResponse.json()

        if (compareData.success) {
          setRanking(compareData.ranking)
          setWinner(compareData.winner)
          setSummary(compareData.summary)
          setStep('results')
          
          // Auto-save result
          setTimeout(() => {
            const result = {
              id: Date.now(),
              date: new Date().toISOString(),
              tender: tenderAnalysis?.tender_purpose || (language === 'uz' ? 'Noma\'lum tender' : 'Неизвестный тендер'),
              winner: compareData.winner?.participant_name || (language === 'uz' ? 'Noma\'lum' : 'Неизвестно'),
              ranking: compareData.ranking,
              summary: compareData.summary,
              participantCount: compareData.ranking.length,
              tenderAnalysis: tenderAnalysis,
              participantAnalyses: analyses
            }
            const saved = JSON.parse(localStorage.getItem('tender_analysis_history') || '[]')
            const updatedResults = [result, ...saved].slice(0, 10)
            setSavedResults(updatedResults)
            localStorage.setItem('tender_analysis_history', JSON.stringify(updatedResults))
          }, 100)
        }
      }
    } catch (err) {
      setError(t('analysis.error_analysis'))
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Qayta boshlash
  const resetAnalysis = async () => {
    try {
      await fetch(`${API_BASE}/reset/`, { method: 'POST' })
    } catch (err) {}
    
    setStep('tender')
    setTenderFile(null)
    setTenderAnalysis(null)
    setParticipantFiles([])
    setParticipantAnalyses([])
    setRanking([])
    setWinner(null)
    setSummary('')
    setError(null)
  }

  // Risk level badge
  const getRiskBadge = (level: string) => {
    const colors: Record<string, string> = {
      low: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      high: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
    }
    const labels: Record<string, string> = {
      low: t('risk.low'),
      medium: t('risk.medium'),
      high: t('risk.high')
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[level] || 'bg-gray-100 dark:bg-gray-800'}`}>
        {labels[level] || level}
      </span>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">{t('analysis.title')}</h1>
          <p className="text-muted-foreground mt-1">
            {t('analysis.subtitle')}
          </p>
        </div>
        <div className="flex gap-2">
          {savedResults.length > 0 && step === 'tender' && (
            <Button variant="outline" onClick={() => setShowHistory(!showHistory)}>
              📋 {t('analysis.history_title')} ({savedResults.length})
            </Button>
          )}
          {step !== 'tender' && (
            <Button variant="outline" onClick={resetAnalysis}>
              {t('analysis.restart')}
            </Button>
          )}
        </div>
      </div>

      {/* History Modal */}
      {showHistory && (
        <Card className="border-2 border-emerald-200 dark:border-emerald-800">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>📋 {t('analysis.history_title')}</span>
              <Button variant="ghost" size="sm" onClick={() => setShowHistory(false)}>✕</Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {savedResults.map((result) => (
                <div key={result.id} className="flex items-center justify-between p-3 bg-muted rounded-lg hover:bg-muted/80">
                  <div className="flex-1">
                    <p className="font-medium text-foreground">{result.tender}</p>
                    <p className="text-sm text-muted-foreground">
                      {t('analysis.history_winner')}: {result.winner} • {result.participantCount} {t('analysis.history_participant')} • 
                      {new Date(result.date).toLocaleDateString(language === 'uz' ? 'uz-UZ' : 'ru-RU')}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => loadSavedResult(result)}>
                      {t('analysis.history_view')}
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => deleteSavedResult(result.id)}>
                      🗑️
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Progress Steps */}
      <div className="flex items-center justify-center space-x-4">
        {['tender', 'participants', 'results'].map((s, i) => (
          <React.Fragment key={s}>
            <div className={`flex items-center space-x-2 ${step === s ? 'text-primary' : 'text-muted-foreground'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step === s ? 'bg-primary text-primary-foreground' : 
                ['tender', 'participants', 'results'].indexOf(step) > i ? 'bg-primary text-primary-foreground' : 'bg-muted'
              }`}>
                {['tender', 'participants', 'results'].indexOf(step) > i ? <CheckCircle className="w-5 h-5" /> : i + 1}
              </div>
              <span className="font-medium">
                {s === 'tender' ? t('analysis.step_tender') : s === 'participants' ? t('analysis.step_participants') : t('analysis.step_results')}
              </span>
            </div>
            {i < 2 && <div className="w-16 h-0.5 bg-muted" />}
          </React.Fragment>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-lg flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      {/* Step 1: Tender Upload */}
      {step === 'tender' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center text-foreground">
              <FileText className="w-5 h-5 mr-2" />
              {t('analysis.upload_tender')}
            </CardTitle>
            <CardDescription>
              {t('analysis.upload_tender_desc')}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors">
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleTenderUpload}
                className="hidden"
                id="tender-upload"
              />
              <label htmlFor="tender-upload" className="cursor-pointer">
                <Upload className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                {tenderFile ? (
                  <div>
                    <p className="text-lg font-medium">{tenderFile.name}</p>
                    <p className="text-sm text-muted-foreground">{(tenderFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-lg font-medium text-foreground">{t('analysis.upload_click')}</p>
                    <p className="text-sm text-muted-foreground">{t('analysis.upload_drag')}</p>
                  </div>
                )}
              </label>
            </div>

            <Button 
              onClick={analyzeTender} 
              disabled={!tenderFile || loading}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  {t('analysis.analyzing')}
                </>
              ) : (
                <>
                  <BarChart3 className="w-5 h-5 mr-2" />
                  {t('analysis.analyze_tender')}
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Participants */}
      {step === 'participants' && tenderAnalysis && (
        <div className="space-y-6">
          {/* Tender Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground">{t('analysis.tender_info')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">{t('analysis.purpose')}</p>
                  <p className="font-medium text-foreground">{tenderAnalysis.tender_purpose}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{t('analysis.type')}</p>
                  <p className="font-medium text-foreground">{tenderAnalysis.tender_type}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{t('analysis.requirements_count')}</p>
                  <p className="font-medium text-foreground">{tenderAnalysis.requirements_count} ({t('analysis.mandatory')}: {tenderAnalysis.mandatory_count})</p>
                </div>
              </div>

              {/* Requirements */}
              <div className="mt-4">
                <p className="text-sm font-medium mb-2 text-foreground">{t('analysis.main_requirements')}:</p>
                <div className="space-y-2">
                  {tenderAnalysis.requirements.slice(0, 5).map((req, i) => (
                    <div key={i} className="flex items-center justify-between bg-muted p-2 rounded">
                      <span className="text-sm text-foreground">{req.title}</span>
                      <div className="flex items-center space-x-2">
                        {req.is_mandatory && (
                          <Badge variant="destructive">{t('analysis.mandatory')}</Badge>
                        )}
                        <span className="text-xs text-muted-foreground">{t('analysis.weight')}: {(req.weight * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Participants Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-foreground">
                <span className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  {t('analysis.participants')}
                </span>
                <Button variant="outline" size="sm" onClick={addParticipant}>
                  <Plus className="w-4 h-4 mr-1" />
                  {t('analysis.add')}
                </Button>
              </CardTitle>
              <CardDescription>
                {t('analysis.participants_desc')}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Allaqachon tahlil qilingan ishtirokchilar */}
              {participantAnalyses.length > 0 && (
                <div className="mb-4 p-4 bg-muted border rounded-lg">
                  <h4 className="font-medium mb-2 text-foreground">✓ {t('analysis.analyzed_participants')}:</h4>
                  <div className="flex flex-wrap gap-2">
                    {participantAnalyses.map((p, i) => (
                      <Badge key={i} variant="secondary">
                        {p.participant_name} - {(p.total_weighted_score || p.overall_match_percentage || 0).toFixed(0)}%
                      </Badge>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    {t('analysis.add_more_desc')}
                  </p>
                </div>
              )}
              
              {participantFiles.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>{t('analysis.add_participant_hint')}</p>
                </div>
              ) : (
                participantFiles.map((p, index) => (
                  <div key={index} className="flex items-center space-x-4 p-4 border rounded-lg">
                    <div className="flex-1">
                      <input
                        type="text"
                        placeholder={t('analysis.company_name')}
                        value={p.name}
                        onChange={(e) => handleParticipantName(index, e.target.value)}
                        className="w-full border rounded px-3 py-2 mb-2 bg-background text-foreground"
                      />
                      <input
                        type="file"
                        accept=".pdf,.docx,.doc,.txt"
                        onChange={(e) => e.target.files?.[0] && handleParticipantFile(index, e.target.files[0])}
                        className="text-sm"
                      />
                      {p.file && (
                        <p className="text-xs text-muted-foreground mt-1">{p.file.name}</p>
                      )}
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => removeParticipant(index)}>
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                ))
              )}

              <Button 
                onClick={analyzeParticipants} 
                disabled={(participantFiles.filter(p => p.file && p.name).length === 0 && participantAnalyses.length === 0) || loading}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    {t('analysis.analyzing')}
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5 mr-2" />
                    {t('analysis.evaluate_participants')}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Step 3: Results */}
      {step === 'results' && (
        <div className="space-y-6">
          {/* Action Buttons */}
          <Card className="bg-muted">
            <CardContent className="py-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h3 className="font-medium text-foreground">{t('analysis.completed')}</h3>
                  <p className="text-sm text-muted-foreground">{t('analysis.auto_saved')}</p>
                </div>
                <div className="flex gap-2">
                  <Button onClick={() => navigate('/history')}>
                    <History className="w-4 h-4 mr-2" />
                    {t('analysis.history')}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setStep('participants')
                      setParticipantFiles([...participantFiles, { name: '', file: null as any }])
                    }}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    {t('analysis.add_new_participant')}
                  </Button>
                  <Button variant="outline" onClick={resetAnalysis}>
                    {t('analysis.new_analysis')}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Winner */}
          {winner && (
            <Card className="border-2 border-primary">
              <CardHeader>
                <CardTitle className="flex items-center text-foreground">
                  <Award className="w-6 h-6 mr-2 text-primary" />
                  {t('analysis.winner')}: {winner.participant_name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary">{winner.total_weighted_score?.toFixed(1) || winner.overall_match_percentage || 0}%</p>
                    <p className="text-sm text-muted-foreground">{t('analysis.total_score')}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary">{winner.overall_match_percentage}%</p>
                    <p className="text-sm text-muted-foreground">{t('analysis.match')}</p>
                  </div>
                  <div className="text-center">
                    {getRiskBadge(winner.risk_level)}
                    <p className="text-sm text-muted-foreground mt-1">{t('analysis.risk_level')}</p>
                  </div>
                </div>
                <p className="mt-4 text-muted-foreground">{winner.recommendation}</p>
              </CardContent>
            </Card>
          )}

          {/* Ranking */}
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground">{t('analysis.ranking')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {ranking.map((p, index) => (
                  <div 
                    key={index} 
                    className={`p-4 rounded-lg border ${index === 0 ? 'border-primary bg-primary/5' : 'bg-card'}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                          index === 0 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
                        }`}>
                          {index + 1}
                        </span>
                        <span className="font-medium">{p.participant_name}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        {getRiskBadge(p.risk_level)}
                        <span className="text-2xl font-bold text-primary">{p.total_weighted_score?.toFixed(1) || p.overall_match_percentage || 0}%</span>
                      </div>
                    </div>
                    
                    <Progress value={p.total_weighted_score || p.overall_match_percentage || 0} className="h-2 mb-3" />
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground mb-1">{t('analysis.strengths')}:</p>
                        <ul className="list-disc list-inside text-foreground">
                          {p.strengths?.slice(0, 3).map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <p className="text-muted-foreground mb-1">{t('analysis.weaknesses')}:</p>
                        <ul className="list-disc list-inside text-foreground">
                          {p.weaknesses?.slice(0, 3).map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    
                    {p.price_analysis && (
                      <div className="mt-3 p-2 bg-muted rounded text-sm">
                        <span className="text-muted-foreground">{t('analysis.price')}: </span>
                        <span className="font-medium">{p.price_analysis.proposed_price}</span>
                        <span className="mx-2 text-muted-foreground">•</span>
                        <span className="font-medium">
                          {p.price_analysis.price_adequacy}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Summary */}
          {summary && (
            <Card>
              <CardHeader>
                <CardTitle className="text-foreground">{t('analysis.summary')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      h1: ({children}) => <h1 className="text-2xl font-bold mt-4 mb-2">{children}</h1>,
                      h2: ({children}) => <h2 className="text-xl font-bold mt-4 mb-2">{children}</h2>,
                      h3: ({children}) => <h3 className="text-lg font-semibold mt-3 mb-1">{children}</h3>,
                      p: ({children}) => <p className="mb-2 text-foreground">{children}</p>,
                      ul: ({children}) => <ul className="list-disc list-inside mb-2 ml-4">{children}</ul>,
                      ol: ({children}) => <ol className="list-decimal list-inside mb-2 ml-4">{children}</ol>,
                      li: ({children}) => <li className="mb-1">{children}</li>,
                      strong: ({children}) => <strong className="font-bold">{children}</strong>,
                      em: ({children}) => <em className="italic">{children}</em>,
                    }}
                  >
                    {summary}
                  </ReactMarkdown>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

export default TenderAnalysis

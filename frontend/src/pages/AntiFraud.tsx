import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'
import { useTheme } from '../context/ThemeContext'
import { 
  Shield, 
  AlertTriangle, 
  DollarSign, 
  FileText, 
  Users,
  Plus,
  Trash2,
  Loader2,
  XCircle,
  CheckCircle,
  Eye
} from 'lucide-react'
import { API_ENDPOINTS } from '../config/api'

const API_BASE = API_ENDPOINTS.antiFraud

interface Participant {
  name: string
  price: string
  documents: string
  details: string
}

interface FraudIndicator {
  type: string
  severity: string
  title: string
  description: string
  involved_participants: string[]
  evidence: string
  risk_score: number
}

interface FraudAnalysis {
  overall_risk_level: string
  overall_risk_score: number
  fraud_indicators: FraudIndicator[]
  price_analysis: {
    min_price: string
    max_price: string
    average_price: string
    price_spread: string
    suspicious_prices: string[]
    analysis: string
  }
  similarity_analysis: {
    document_similarity_score: number
    suspicious_patterns: string[]
    analysis: string
  }
  collusion_analysis: {
    collusion_probability: number
    indicators: string[]
    analysis: string
  }
  recommendations: string[]
  summary: string
}

const AntiFraud: React.FC = () => {
  const { t } = useTheme()
  const [participants, setParticipants] = useState<Participant[]>([
    { name: '', price: '', documents: '', details: '' },
    { name: '', price: '', documents: '', details: '' }
  ])
  const [tenderInfo, setTenderInfo] = useState({
    name: '',
    budget: '',
    deadline: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<FraudAnalysis | null>(null)

  const addParticipant = () => {
    setParticipants([...participants, { name: '', price: '', documents: '', details: '' }])
  }

  const removeParticipant = (index: number) => {
    if (participants.length > 2) {
      setParticipants(participants.filter((_, i) => i !== index))
    }
  }

  const updateParticipant = (index: number, field: keyof Participant, value: string) => {
    const updated = [...participants]
    updated[index][field] = value
    setParticipants(updated)
  }

  const analyzeFraud = async () => {
    const validParticipants = participants.filter(p => p.name && p.price)
    if (validParticipants.length < 2) {
      setError(t('antifraud.min_participants'))
      return
    }

    setLoading(true)
    setError(null)
    setAnalysis(null)

    try {
      const response = await fetch(`${API_BASE}/analyze/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          participants: validParticipants,
          tender_info: tenderInfo.name ? tenderInfo : null
        })
      })

      const data = await response.json()
      if (data.success) {
        setAnalysis(data.analysis)
      } else {
        setError(data.error || t('antifraud.analysis_error'))
      }
    } catch (err) {
      setError(t('antifraud.server_error'))
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-500'
      case 'medium': return 'bg-yellow-500'
      case 'high': return 'bg-orange-500'
      case 'critical': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'low': return <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">{t('risk.low')}</Badge>
      case 'medium': return <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">{t('risk.medium')}</Badge>
      case 'high': return <Badge className="bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400">{t('risk.high')}</Badge>
      case 'critical': return <Badge className="bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">{t('risk.critical')}</Badge>
      default: return <Badge>{level}</Badge>
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'price_anomaly': return <DollarSign className="h-5 w-5 text-amber-500" />
      case 'document_similarity': return <FileText className="h-5 w-5 text-teal-500" />
      case 'collusion': return <Users className="h-5 w-5 text-red-500" />
      default: return <AlertTriangle className="h-5 w-5 text-gray-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2 text-foreground">
          <Shield className="h-8 w-8 text-red-500" />
          {t('antifraud.title')}
        </h1>
        <p className="text-muted-foreground mt-1">
          {t('antifraud.subtitle')}
        </p>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <DollarSign className="h-8 w-8 text-amber-500" />
              <div>
                <h3 className="font-semibold text-foreground">{t('antifraud.price_anomaly')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('antifraud.price_anomaly_desc')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-teal-500">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <FileText className="h-8 w-8 text-teal-500" />
              <div>
                <h3 className="font-semibold text-foreground">{t('antifraud.doc_similarity')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('antifraud.doc_similarity_desc')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-red-500">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <Users className="h-8 w-8 text-red-500" />
              <div>
                <h3 className="font-semibold text-foreground">{t('antifraud.collusion')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('antifraud.collusion_desc')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {!analysis ? (
        <>
          {/* Tender Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground">{t('antifraud.tender_info')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground">{t('antifraud.tender_name')}</label>
                  <input
                    type="text"
                    className="w-full border border-border rounded-md px-3 py-2 bg-card text-foreground"
                    placeholder="IT tizimi loyihasi"
                    value={tenderInfo.name}
                    onChange={(e) => setTenderInfo({...tenderInfo, name: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground">{t('antifraud.budget')}</label>
                  <input
                    type="text"
                    className="w-full border border-border rounded-md px-3 py-2 bg-card text-foreground"
                    placeholder="500,000,000"
                    value={tenderInfo.budget}
                    onChange={(e) => setTenderInfo({...tenderInfo, budget: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground">{t('antifraud.deadline')}</label>
                  <input
                    type="text"
                    className="w-full border border-border rounded-md px-3 py-2 bg-card text-foreground"
                    placeholder="6"
                    value={tenderInfo.deadline}
                    onChange={(e) => setTenderInfo({...tenderInfo, deadline: e.target.value})}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Participants Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-foreground">
                <span>{t('antifraud.participants')}</span>
                <Button onClick={addParticipant} size="sm" variant="outline">
                  <Plus className="h-4 w-4 mr-1" /> {t('common.add')}
                </Button>
              </CardTitle>
              <CardDescription>
                {t('antifraud.participants_desc')}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {participants.map((participant, index) => (
                <div key={index} className="border border-border rounded-lg p-4 space-y-3 bg-card">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-foreground">{t('antifraud.participant')} #{index + 1}</h4>
                    {participants.length > 2 && (
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => removeParticipant(index)}
                        className="text-red-500"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium mb-1 text-foreground">{t('antifraud.company_name')} *</label>
                      <input
                        type="text"
                        className="w-full border border-border rounded-md px-3 py-2 bg-background text-foreground"
                        placeholder="TechSoft MCHJ"
                        value={participant.name}
                        onChange={(e) => updateParticipant(index, 'name', e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-foreground">{t('antifraud.offer_price')} *</label>
                      <input
                        type="text"
                        className="w-full border border-border rounded-md px-3 py-2 bg-background text-foreground"
                        placeholder="450,000,000"
                        value={participant.price}
                        onChange={(e) => updateParticipant(index, 'price', e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-foreground">{t('antifraud.docs_info')}</label>
                      <input
                        type="text"
                        className="w-full border border-border rounded-md px-3 py-2 bg-background text-foreground"
                        placeholder="PDF, 2024-01-05"
                        value={participant.documents}
                        onChange={(e) => updateParticipant(index, 'documents', e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-foreground">{t('antifraud.additional_info')}</label>
                      <input
                        type="text"
                        className="w-full border border-border rounded-md px-3 py-2 bg-background text-foreground"
                        placeholder="ISO sertifikati"
                        value={participant.details}
                        onChange={(e) => updateParticipant(index, 'details', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              ))}

              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-400 px-4 py-3 rounded flex items-center gap-2">
                  <XCircle className="h-5 w-5" />
                  {error}
                </div>
              )}

              <Button 
                onClick={analyzeFraud}
                className="w-full" 
                size="lg"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    {t('antifraud.analyzing')}
                  </>
                ) : (
                  <>
                    <Shield className="h-5 w-5 mr-2" />
                    {t('antifraud.analyze')}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </>
      ) : (
        <>
          {/* Results */}
          <div className="flex justify-end">
            <Button variant="outline" onClick={() => setAnalysis(null)}>
              {t('antifraud.new_analysis')}
            </Button>
          </div>

          {/* Overall Risk */}
          <Card className={`border-2 ${
            analysis.overall_risk_level === 'critical' ? 'border-red-500 bg-red-50 dark:bg-red-900/20' :
            analysis.overall_risk_level === 'high' ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20' :
            analysis.overall_risk_level === 'medium' ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' :
            'border-green-500 bg-green-50 dark:bg-green-900/20'
          }`}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-4 rounded-full ${getRiskColor(analysis.overall_risk_level)}`}>
                    <Shield className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">{t('antifraud.overall_risk')}</h2>
                    <div className="flex items-center gap-2 mt-1">
                      {getRiskBadge(analysis.overall_risk_level)}
                      <span className="text-lg font-semibold text-foreground">{analysis.overall_risk_score}/100</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">{t('antifraud.participants')}</p>
                  <p className="text-3xl font-bold text-foreground">{participants.filter(p => p.name && p.price).length}</p>
                </div>
              </div>
              <div className="mt-4">
                <Progress value={analysis.overall_risk_score} className="h-3" />
              </div>
            </CardContent>
          </Card>

          {/* Fraud Indicators */}
          {analysis.fraud_indicators && analysis.fraud_indicators.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <AlertTriangle className="h-5 w-5 text-amber-500" />
                  {t('antifraud.indicators')} ({analysis.fraud_indicators.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysis.fraud_indicators.map((indicator, index) => (
                  <div key={index} className="border border-border rounded-lg p-4 bg-card">
                    <div className="flex items-start gap-3">
                      {getTypeIcon(indicator.type)}
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold text-foreground">{indicator.title}</h4>
                          {getRiskBadge(indicator.severity)}
                        </div>
                        <p className="text-muted-foreground mt-1">{indicator.description}</p>
                        {indicator.involved_participants && indicator.involved_participants.length > 0 && (
                          <div className="mt-2">
                            <span className="text-sm font-medium text-foreground">{t('antifraud.involved')}: </span>
                            {indicator.involved_participants.map((p, i) => (
                              <Badge key={i} variant="outline" className="mr-1">{p}</Badge>
                            ))}
                          </div>
                        )}
                        {indicator.evidence && (
                          <div className="mt-2 bg-muted p-2 rounded text-sm">
                            <span className="font-medium text-foreground">{t('antifraud.evidence')}: </span>
                            <span className="text-muted-foreground">{indicator.evidence}</span>
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-bold text-foreground">{indicator.risk_score}</span>
                        <span className="text-sm text-muted-foreground">/100</span>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Analysis Details */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Price Analysis */}
            {analysis.price_analysis && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg text-foreground">
                    <DollarSign className="h-5 w-5 text-amber-500" />
                    {t('antifraud.price_analysis')}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">{t('antifraud.min_price')}:</span>
                    <span className="font-medium text-foreground">{analysis.price_analysis.min_price}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">{t('antifraud.max_price')}:</span>
                    <span className="font-medium text-foreground">{analysis.price_analysis.max_price}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">{t('antifraud.avg_price')}:</span>
                    <span className="font-medium text-foreground">{analysis.price_analysis.average_price}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">{t('antifraud.price_spread')}:</span>
                    <span className="font-medium text-foreground">{analysis.price_analysis.price_spread}</span>
                  </div>
                  <div className="pt-2 border-t border-border mt-2">
                    <p className="text-muted-foreground">{analysis.price_analysis.analysis}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Similarity Analysis */}
            {analysis.similarity_analysis && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg text-foreground">
                    <FileText className="h-5 w-5 text-teal-500" />
                    {t('antifraud.similarity_analysis')}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">{t('antifraud.similarity_score')}:</span>
                    <span className="font-medium text-foreground">{analysis.similarity_analysis.document_similarity_score}%</span>
                  </div>
                  <Progress value={analysis.similarity_analysis.document_similarity_score} className="h-2" />
                  {analysis.similarity_analysis.suspicious_patterns &&
                   analysis.similarity_analysis.suspicious_patterns.length > 0 && (
                    <div className="pt-2">
                      <span className="font-medium text-foreground">{t('antifraud.suspicious_patterns')}:</span>
                      <ul className="mt-1 space-y-1">
                        {analysis.similarity_analysis.suspicious_patterns.map((p, i) => (
                          <li key={i} className="text-muted-foreground flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3 text-amber-500" />
                            {p}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="pt-2 border-t border-border mt-2">
                    <p className="text-muted-foreground">{analysis.similarity_analysis.analysis}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Collusion Analysis */}
            {analysis.collusion_analysis && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg text-foreground">
                    <Users className="h-5 w-5 text-red-500" />
                    {t('antifraud.collusion_analysis')}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">{t('antifraud.collusion_probability')}:</span>
                    <span className="font-medium text-foreground">{analysis.collusion_analysis.collusion_probability}%</span>
                  </div>
                  <Progress value={analysis.collusion_analysis.collusion_probability} className="h-2" />
                  {analysis.collusion_analysis.indicators &&
                   analysis.collusion_analysis.indicators.length > 0 && (
                    <div className="pt-2">
                      <span className="font-medium text-foreground">{t('antifraud.collusion_indicators')}:</span>
                      <ul className="mt-1 space-y-1">
                        {analysis.collusion_analysis.indicators.map((ind, i) => (
                          <li key={i} className="text-muted-foreground flex items-center gap-1">
                            <Eye className="h-3 w-3 text-red-500" />
                            {ind}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="pt-2 border-t border-border mt-2">
                    <p className="text-muted-foreground">{analysis.collusion_analysis.analysis}</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Summary & Recommendations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-foreground">{t('antifraud.summary')}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{analysis.summary}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-foreground">{t('antifraud.recommendations')}</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {analysis.recommendations?.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                      <span className="text-foreground">{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}

export default AntiFraud

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Lock, User, AlertCircle, BarChart3 } from 'lucide-react'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const { t } = useTheme()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const success = await login(username, password)
      
      if (success) {
        navigate('/')
      } else {
        setError(t('login.error'))
      }
    } catch (err) {
      setError(t('login.error'))
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <img src="/kqlogo.png" alt="Logo" className="h-[140px] mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-foreground">Tanlov AI</h1>
          <p className="text-muted-foreground mt-1">{t('login.system_desc')}</p>
        </div>

        <Card>
          <CardHeader className="text-center">
            <CardTitle>{t('login.title')}</CardTitle>
            <CardDescription>
              {t('login.subtitle')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-lg flex items-center text-sm">
                  <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground" htmlFor="username">
                  {t('login.username')}
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder={t('login.username_placeholder')}
                    className="w-full pl-10 pr-4 py-2.5 bg-background border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 text-foreground"
                    required
                    autoComplete="username"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground" htmlFor="password">
                  {t('login.password')}
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={t('login.password_placeholder')}
                    className="w-full pl-10 pr-4 py-2.5 bg-background border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 text-foreground"
                    required
                    autoComplete="current-password"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                size="lg"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {t('login.submitting')}
                  </span>
                ) : (
                  t('login.submit')
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-muted-foreground mt-6">
          {t('login.copyright')}
        </p>
      </div>
    </div>
  )
}

export default Login

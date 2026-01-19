import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Lock, User, AlertCircle, BarChart3, Sparkles } from 'lucide-react'
import { fadeIn, scaleIn, animationClasses } from '../lib/animations'

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
    <div className="min-h-screen flex items-center justify-center p-4 relative z-20">
      {/* Local decorative bubbles for Login page */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-10 left-10 w-24 h-24 bg-gradient-to-br from-blue-400/40 to-purple-400/40 rounded-full blur-2xl animate-float"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-gradient-to-tr from-pink-400/40 to-orange-400/40 rounded-full blur-2xl animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/3 w-20 h-20 bg-gradient-to-bl from-green-400/30 to-teal-400/30 rounded-full blur-xl animate-float" style={{ animationDelay: '4s' }}></div>
      </div>
      
      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="text-center mb-8 animate-fade-in relative">
          <div className="relative inline-block">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 rounded-full blur-lg opacity-40 animate-gradient-shift"></div>
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full blur-md opacity-30 animate-pulse"></div>
            <img src="/kqlogo.png" alt="Logo" className="h-[140px] mx-auto mb-4 relative z-10 drop-shadow-2xl transform hover:scale-105 transition-transform duration-300" />
          </div>
          <h1 className="text-4xl font-bold text-foreground mb-3 flex items-center justify-center gap-3">
            Tanlov AI
            <div className="relative">
              <Sparkles className="w-7 h-7 text-yellow-500 animate-pulse" />
              <div className="absolute inset-0 bg-yellow-400/30 rounded-full blur-lg animate-pulse"></div>
            </div>
          </h1>
          <p className="text-muted-foreground text-lg">{t('login.system_desc')}</p>
        </div>

        <Card className={`${animationClasses['glass-effect']} shadow-2xl border-0 animate-slide-up relative overflow-hidden z-30`}>
          {/* Card decoration */}
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-pink-500 animate-gradient-shift"></div>
          <div className="absolute -top-10 -right-10 w-20 h-20 bg-gradient-to-br from-primary/20 to-purple-400/20 rounded-full blur-xl animate-float"></div>
          <div className="absolute -bottom-10 -left-10 w-16 h-16 bg-gradient-to-tr from-blue-400/20 to-cyan-400/20 rounded-full blur-lg animate-float" style={{ animationDelay: '2s' }}></div>
          
          <CardHeader className="text-center space-y-3 relative z-10">
            <CardTitle className="text-2xl font-semibold">{t('login.title')}</CardTitle>
            <CardDescription className="text-base">
              {t('login.subtitle')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-lg flex items-center text-sm animate-fade-in relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-r from-destructive/5 to-destructive/10 animate-shimmer"></div>
                  <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0 relative z-10 animate-pulse" />
                  <span className="relative z-10 font-medium">{error}</span>
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
                    className="w-full pl-10 pr-4 py-3 bg-background/60 backdrop-blur-md border border-muted-foreground/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 text-foreground transition-all duration-300 hover:bg-background/80 focus:bg-background/90"
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
                    className="w-full pl-10 pr-4 py-3 bg-background/60 backdrop-blur-md border border-muted-foreground/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 text-foreground transition-all duration-300 hover:bg-background/80 focus:bg-background/90"
                    required
                    autoComplete="current-password"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-primary via-primary/90 to-primary/80 hover:from-primary/95 hover:via-primary/85 hover:to-primary/75 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group" 
                size="lg"
                disabled={loading}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
                {loading ? (
                  <span className="flex items-center relative z-10">
                    <div className="relative">
                      <svg className="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <div className="absolute inset-0 bg-primary/30 rounded-full animate-pulse"></div>
                    </div>
                    {t('login.submitting')}
                  </span>
                ) : (
                  <span className="flex items-center relative z-10 font-semibold">
                    <div className="relative">
                      <Sparkles className="w-4 h-4 mr-2" />
                      <div className="absolute inset-0 bg-white/30 rounded-full animate-pulse"></div>
                    </div>
                    {t('login.submit')}
                  </span>
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

import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'
import { Button } from './ui/button'
import { 
  Home, 
  Shield, 
  Settings,
  Menu,
  BarChart3,
  History,
  Moon,
  Sun,
  Languages,
  LogOut
} from 'lucide-react'

interface LayoutProps {
  children?: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { theme, setTheme, language, setLanguage, t } = useTheme()
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const menuItems = [
    { icon: Home, label: t('menu.dashboard'), path: '/' },
    { icon: BarChart3, label: t('menu.analysis'), path: '/analysis' },
    { icon: History, label: t('menu.history') || 'Tarix', path: '/history' },
    { icon: Settings, label: t('menu.settings'), path: '/settings' },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card sticky top-0 z-40">
        <div className="px-4 py-2 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden"
            >
              <Menu className="h-4 w-4" />
            </Button>
            <Link to="/" className="cursor-pointer">
              <img src="/kqlogo.png" alt="Logo" className="h-[85px] hover:opacity-80 transition-opacity" />
            </Link>
          </div>
          
          {/* Centered Title */}
          <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center">
            <h1 className="text-xl font-bold text-primary">Tanlov AI</h1>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Language Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLanguage(language === 'uz' ? 'ru' : 'uz')}
              className="flex items-center gap-2"
            >
              <Languages className="h-4 w-4" />
              <span className="text-xs font-medium">{language === 'uz' ? 'UZ' : 'RU'}</span>
            </Button>
            
            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            >
              {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            </Button>
            
            {/* Logout */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-destructive hover:text-destructive"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-64 
          bg-card border-r border-border transition-transform duration-200 ease-in-out
          pt-16 lg:pt-0
        `}>
          <nav className="p-4 space-y-1 mt-4">
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <Link key={item.path} to={item.path}>
                  <Button
                    variant={isActive ? "default" : "ghost"}
                    className={`w-full justify-start transition-all ${
                      isActive 
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'hover:bg-muted'
                    }`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <item.icon className="mr-2 h-4 w-4" />
                    {item.label}
                  </Button>
                </Link>
              )
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 lg:ml-0 min-h-screen bg-background">
          {children}
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default Layout

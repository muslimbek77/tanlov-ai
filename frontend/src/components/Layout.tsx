import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTheme } from "../context/ThemeContext";
import { useAuth } from "../context/AuthContext";
import { Button } from "./ui/button";
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
  LogOut,
  Sparkles,
} from "lucide-react";
import { animationClasses } from "../lib/animations";

interface LayoutProps {
  children?: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, setTheme, language, setLanguage, t } = useTheme();
  const { logout } = useAuth();

  const cycleLanguage = () => {
    if (language === "uz_latn") return setLanguage("uz_cyrl");
    if (language === "uz_cyrl") return setLanguage("ru");
    return setLanguage("uz_latn");
  };

  const languageLabel = () => {
    if (language === "uz_latn") return "UZ";
    if (language === "uz_cyrl") return "ЎЗ";
    return "RU";
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const menuItems = [
    { icon: Home, label: t("menu.dashboard"), path: "/" },
    { icon: BarChart3, label: t("menu.analysis"), path: "/analysis" },
    { icon: History, label: t("menu.history") || "Tarix", path: "/history" },
    { icon: Settings, label: t("menu.settings"), path: "/settings" },
  ];

  return (
    <div className="min-h-screen relative z-10">
      {/* Header */}
      <header className="top-0 z-40 w-full relative h-[76px]">
        {/* Glass morphism header with gradient */}
        <div className="bg-card/90 backdrop-blur-xl border-b border-border/30 shadow-lg w-full h-full">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/8 via-transparent to-primary/8"></div>
          <div className="px-4 py-3 flex items-center justify-between relative z-10 w-full max-w-full h-full">
            <div className="flex items-center space-x-4 flex-shrink-0">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden hover:bg-primary/15 transition-all duration-300 hover:scale-105 relative overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/20 to-primary/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-500"></div>
                <Menu className="h-4 w-4 relative z-10" />
              </Button>
              <Link
                to="/"
                className="cursor-pointer group flex-shrink-0 !ml-12"
              >
                <div className="relative">
                  <img
                    src="/kqlogo.png"
                    alt="Logo"
                    className="h-[90px] transition-all duration-300 group-hover:scale-110 drop-shadow-xl"
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-primary/30 via-purple-400/30 to-primary/30 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                </div>
              </Link>
            </div>

            {/* Centered Title */}
            <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center">
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3 relative">
                <div className="relative">
                  Tanlov AI
                  <div className="absolute -bottom-1 left-0 w-full h-0.5 bg-gradient-to-r from-primary via-purple-500 to-primary rounded-full animate-gradient-shift"></div>
                </div>
                <div className="relative">
                  <Sparkles className="w-6 h-6 text-yellow-500 animate-pulse" />
                  <div className="absolute inset-0 bg-yellow-400/40 rounded-full blur-lg animate-pulse"></div>
                </div>
              </h1>
            </div>

            <div className="flex items-center space-x-3 flex-shrink-0">
              {/* Language Toggle */}
              <Button
                variant="ghost"
                size="sm"
                onClick={cycleLanguage}
                className="bg-gradient-to-r from-primary/15 to-primary/8 hover:from-primary/25 hover:to-primary/15 border border-primary/30 hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg relative overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
                <Languages className="h-4 w-4 mr-1 relative z-10" />
                <span className="relative z-10 font-semibold">
                  {languageLabel()}
                </span>
              </Button>

              {/* Theme Toggle */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="bg-gradient-to-r from-primary/15 to-primary/8 hover:from-primary/25 hover:to-primary/15 border border-primary/30 hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg relative overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
                {theme === "dark" ? (
                  <Sun className="h-4 w-4 relative z-10" />
                ) : (
                  <Moon className="h-4 w-4 relative z-10" />
                )}
              </Button>

              {/* Logout */}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="bg-gradient-to-r from-destructive/15 to-destructive/8 hover:from-destructive/25 hover:to-destructive/15 border border-destructive/30 hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg relative overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
                <LogOut className="h-4 w-4 relative z-10" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-screen">
        {/* Sidebar */}
        <aside
          className={`
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-64 
          bg-card/95 backdrop-blur-xl border-r border-border/30 shadow-xl transition-all duration-300 ease-in-out
          pt-[76px] lg:pt-0
          relative overflow-hidden
          flex-shrink-0
          h-screen lg:h-auto
          overflow-y-auto
        `}
        >
          {/* Sidebar decoration */}
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-primary animate-gradient-shift"></div>
          <div className="absolute -top-10 -right-10 w-20 h-20 bg-gradient-to-br from-primary/20 to-purple-400/20 rounded-full blur-xl animate-float"></div>
          <div
            className="absolute bottom-10 left-10 w-16 h-16 bg-gradient-to-tr from-blue-400/15 to-cyan-400/15 rounded-full blur-lg animate-float"
            style={{ animationDelay: "2s" }}
          ></div>

          <nav className="p-4 space-y-6 mt-6 relative z-10">
            {menuItems.map((item, index) => {
              const isActive = location.pathname === item.path;
              return (
                <Link key={item.path} to={item.path}>
                  <Button
                    variant={isActive ? "default" : "ghost"}
                    className={`w-full justify-start transition-all duration-300 group relative overflow-hidden py-4 mb-6 ${
                      isActive
                        ? "bg-gradient-to-r from-primary to-primary/90 text-primary-foreground shadow-lg border border-primary/50"
                        : "hover:bg-gradient-to-r hover:from-primary/10 hover:to-primary/5 hover:border hover:border-primary/20"
                    }`}
                    onClick={() => setSidebarOpen(false)}
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-500"></div>
                    <div className="relative z-10 flex items-center w-full">
                      <div className="relative">
                        <item.icon className="mr-4 h-4 w-4 group-hover:scale-110 transition-transform duration-200" />
                        {isActive && (
                          <div className="absolute bg-primary-foreground/20 rounded-full animate-pulse"></div>
                        )}
                      </div>
                      <span className="font-medium">{item.label}</span>
                      {isActive && (
                        <div className="ml-auto w-2 h-2 bg-primary-foreground rounded-full animate-pulse"></div>
                      )}
                    </div>
                  </Button>
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 relative z-10 overflow-y-auto">
          <div className="p-4 lg:p-6">{children}</div>
        </main>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden animate-fade-in"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </div>
    </div>
  );
};

export default Layout;

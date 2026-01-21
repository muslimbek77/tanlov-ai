import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  Settings as SettingsIcon,
  Save,
  CheckCircle,
  Sun,
  Moon,
  Languages,
  Palette,
  Shield,
  Sparkles,
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";

interface AnalysisSettings {
  similarity_threshold: number;
  price_deviation_threshold: number;
  min_participants_for_analysis: number;
}

const Settings: React.FC = () => {
  const { theme, language, setTheme, setLanguage, t } = useTheme();

  const [settings, setSettings] = useState<AnalysisSettings>({
    similarity_threshold: 70,
    price_deviation_threshold: 25,
    min_participants_for_analysis: 2,
  });

  const [saved, setSaved] = useState(false);

  useEffect(() => {
    // Load saved settings
    const savedSettings = localStorage.getItem("analysis_settings");
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (e) {
        console.error("Error loading settings");
      }
    }
  }, []);

  const saveSettings = () => {
    localStorage.setItem("analysis_settings", JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  console.log("settings", settings);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-primary/10 rounded-2xl">
            <SettingsIcon className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">
              {t("settings.title")}
            </h1>
            <p className="text-muted-foreground">{t("settings.subtitle")}</p>
          </div>
        </div>
        <Button onClick={saveSettings} className="gap-2" disabled={saved}>
          {saved ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          {saved ? t("settings.saved") : t("settings.save")}
        </Button>
      </div>

      {/* Interface Settings */}
      <Card className="border-border shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Palette className="h-5 w-5 text-primary" />
            </div>
            {t("settings.interface")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Theme */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-3">
                {t("settings.theme")}
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setTheme("light")}
                  className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                    theme === "light"
                      ? "bg-primary text-primary-foreground border-primary shadow-md"
                      : "bg-card text-foreground border-border hover:bg-muted"
                  }`}
                >
                  <Sun className="w-5 h-5" />
                  {t("settings.light")}
                </button>
                <button
                  onClick={() => setTheme("dark")}
                  className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                    theme === "dark"
                      ? "bg-primary text-primary-foreground border-primary shadow-md"
                      : "bg-card text-foreground border-border hover:bg-muted"
                  }`}
                >
                  <Moon className="w-5 h-5" />
                  {t("settings.dark")}
                </button>
              </div>
            </div>

            {/* Language */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-3">
                {t("settings.language")}
              </label>

              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full border border-border rounded-lg px-3 py-3 bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="uz_latn">O'zbek (Lotin)</option>
                <option value="uz_cyrl">Ўзбек (Кирилл)</option>
                <option value="ru">Русский</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Settings */}
      <Card className="border-border/50 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <Shield className="h-5 w-5 text-red-500" />
            </div>
            {t("settings.analysis_params")}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-foreground">
                {t("settings.similarity_threshold")}
              </label>
              <span className="text-sm font-bold text-emerald-500">
                {settings.similarity_threshold}%
              </span>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-emerald-500"
              value={settings.similarity_threshold}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  similarity_threshold: parseInt(e.target.value),
                })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">
              {t("settings.similarity_desc")}
            </p>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-foreground">
                {t("settings.price_deviation")}
              </label>
              <span className="text-sm font-bold text-amber-500">
                {settings.price_deviation_threshold}%
              </span>
            </div>
            <input
              type="range"
              min="10"
              max="50"
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-amber-500"
              value={settings.price_deviation_threshold}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  price_deviation_threshold: parseInt(e.target.value),
                })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">
              {t("settings.price_deviation_desc")}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-foreground">
              {t("settings.min_participants")}
            </label>
            <select
              className="w-full border border-border rounded-lg px-3 py-2 bg-card text-foreground"
              value={settings.min_participants_for_analysis}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  min_participants_for_analysis: parseInt(e.target.value),
                })
              }
            >
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
            </select>
            <p className="text-xs text-muted-foreground mt-1">
              {t("settings.min_participants_desc")}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* About */}
      <Card className="border-border/50 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <div className="p-2 bg-purple-500/10 rounded-lg">
              <Sparkles className="h-5 w-5 text-purple-500" />
            </div>
            {t("settings.about")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary rounded-xl">
                <span className="text-2xl font-bold text-primary-foreground">
                  T
                </span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-foreground">Tanlov AI</h3>
                <p className="text-muted-foreground">
                  {t("settings.version")}: 1.0.0
                </p>
              </div>
            </div>

            <p className="text-muted-foreground">{t("settings.about_desc")}</p>

            <div className="pt-4 border-t border-border">
              <h4 className="font-medium mb-3 text-foreground">
                {t("settings.features")}:
              </h4>
              <ul className="space-y-2 text-sm">
                {[
                  t("settings.feature1"),
                  t("settings.feature2"),
                  t("settings.feature3"),
                  t("settings.feature4"),
                ].map((item, i) => (
                  <li
                    key={i}
                    className="flex items-center gap-2 text-muted-foreground"
                  >
                    <CheckCircle className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;

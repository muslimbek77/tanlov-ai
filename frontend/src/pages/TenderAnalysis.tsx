import React, { useState, useCallback, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { useTheme } from "../context/ThemeContext";
import { latinToCyrillicUz } from "../context/ThemeContext";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import {
  Upload,
  Users,
  AlertTriangle,
  TrendingUp,
  Award,
  Loader2,
  Plus,
  Trash2,
  History,
  Download,
  ArrowRight,
  Sparkles,
  Zap,
  Target,
  Trophy,
  FileText,
} from "lucide-react";
import { API_ENDPOINTS } from "../config/api";

const API_BASE = API_ENDPOINTS.evaluations;

// Types
interface Requirement {
  id: string;
  category: string;
  title: string;
  description: string;
  is_mandatory: boolean;
  weight: number;
}

interface ParticipantScore {
  requirement_id: string;
  score: number;
  matches: boolean;
  reason: string;
}

interface ParticipantAnalysis {
  participant_name: string;
  overall_match_percentage: number;
  total_weighted_score: number;
  scores: ParticipantScore[];
  strengths: string[];
  weaknesses: string[];
  price_analysis: {
    proposed_price: string;
    price_adequacy: string;
    price_score: number;
  };
  recommendation: string;
  risk_level: string;
  rank?: number;
}

interface TenderAnalysis {
  tender_purpose: string;
  tender_type: string;
  requirements: Requirement[];
  evaluation_criteria: any[];
  key_conditions: string[];
  warnings: string[];
  requirements_count: number;
  mandatory_count: number;
}

interface SavedResult {
  id: number;
  date: string;
  tender: string;
  winner: string;
  ranking: ParticipantAnalysis[];
  summary: string;
  participantCount: number;
  tenderAnalysis: TenderAnalysis;
  participantAnalyses: ParticipantAnalysis[];
}

// Constants
const STORAGE_KEYS = {
  TENDER_ANALYSIS: "current_tender_analysis",
  PARTICIPANT_ANALYSES: "current_participant_analyses",
  STEP: "current_analysis_step",
  RANKING: "current_ranking",
  WINNER: "current_winner",
  SUMMARY: "current_summary",
  HISTORY: "tender_analysis_history",
  SETTINGS: "analysis_settings",
  CONTINUE: "continue_analysis",
} as const;

const STEPS = ["tender", "participants", "results"] as const;
type Step = (typeof STEPS)[number];

const STEP_CONFIG = [
  { key: "tender", icon: FileText, label: "analysis.steps.tender" },
  { key: "participants", icon: Users, label: "analysis.steps.participants" },
  { key: "results", icon: Trophy, label: "analysis.steps.results" },
] as const;

// Utility hooks
const useLocalStorage = <T,>(key: string, initialValue: T) => {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStoredValue = useCallback(
    (newValue: T | ((val: T) => T)) => {
      try {
        const valueToStore =
          newValue instanceof Function ? newValue(value) : newValue;
        setValue(valueToStore);
        localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.error(`Error storing ${key}:`, error);
      }
    },
    [key, value],
  );

  return [value, setStoredValue] as const;
};

const TenderAnalysis: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { language, t } = useTheme();

  // Memoized locale helpers
  const { isRu, isUzCyrl, localize, dateLocale } = useMemo(
    () => ({
      isRu: language === "ru",
      isUzCyrl: language === "uz_cyrl",
      localize: (uzLatn: string, ruText: string) => {
        if (language === "ru") return ruText;
        if (language === "uz_cyrl") return latinToCyrillicUz(uzLatn);
        return uzLatn;
      },
      dateLocale: language === "ru" ? "ru-RU" : "uz-UZ",
    }),
    [language],
  );

  // Get settings
  const getMinParticipants = useCallback(() => {
    try {
      const savedSettings = localStorage.getItem(STORAGE_KEYS.SETTINGS);
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        return settings.min_participants_for_analysis || 2;
      }
    } catch (e) {
      console.error("Settings loading error:", e);
    }
    return 2;
  }, []);

  // State
  const [step, setStep] = useLocalStorage<Step>(STORAGE_KEYS.STEP, "tender");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);

  const [tenderFile, setTenderFile] = useState<File | null>(null);
  const [tenderAnalysis, setTenderAnalysis] =
    useLocalStorage<TenderAnalysis | null>(STORAGE_KEYS.TENDER_ANALYSIS, null);

  const [participantFiles, setParticipantFiles] = useState<
    { name: string; file: File | null }[]
  >([{ name: "", file: null }]);
  const [participantAnalyses, setParticipantAnalyses] = useLocalStorage<
    ParticipantAnalysis[]
  >(STORAGE_KEYS.PARTICIPANT_ANALYSES, []);

  const [ranking, setRanking] = useLocalStorage<ParticipantAnalysis[]>(
    STORAGE_KEYS.RANKING,
    [],
  );
  const [winner, setWinner] = useLocalStorage<ParticipantAnalysis | null>(
    STORAGE_KEYS.WINNER,
    null,
  );
  const [summary, setSummary] = useLocalStorage<string>(
    STORAGE_KEYS.SUMMARY,
    "",
  );
  const [savedResults, setSavedResults] = useLocalStorage<SavedResult[]>(
    STORAGE_KEYS.HISTORY,
    [],
  );

  // Load saved results and handle continue
  useEffect(() => {
    if (searchParams.get("continue") === "true") {
      const continueData = localStorage.getItem(STORAGE_KEYS.CONTINUE);
      if (continueData) {
        try {
          const data = JSON.parse(continueData);
          if (data.tenderAnalysis) setTenderAnalysis(data.tenderAnalysis);
          if (data.participantAnalyses)
            setParticipantAnalyses(data.participantAnalyses);
          if (data.ranking) {
            setRanking(data.ranking);
            setWinner(data.ranking[0] || null);
          }
          if (data.summary) setSummary(data.summary);
          setStep("participants");
          setParticipantFiles([{ name: "", file: null }]);
          localStorage.removeItem(STORAGE_KEYS.CONTINUE);
        } catch (e) {
          console.error("Continue analysis error:", e);
        }
      }
    }
  }, [searchParams]);

  // Memoized functions
  const saveCurrentResult = useCallback(() => {
    if (!ranking.length || !summary) return;

    const result: SavedResult = {
      id: Date.now(),
      date: new Date().toISOString(),
      tender:
        tenderAnalysis?.tender_purpose ||
        localize("Noma'lum tender", "Неизвестный тендер"),
      winner: winner?.participant_name || localize("Noma'lum", "Неизвестно"),
      ranking,
      summary,
      participantCount: ranking.length,
      tenderAnalysis: tenderAnalysis!,
      participantAnalyses,
    };

    setSavedResults((prev) => [result, ...prev].slice(0, 10));
  }, [
    ranking,
    summary,
    tenderAnalysis,
    winner,
    participantAnalyses,
    localize,
    setSavedResults,
  ]);

  const loadSavedResult = useCallback(
    (result: SavedResult) => {
      setRanking(result.ranking);
      setSummary(result.summary);
      setWinner(result.ranking[0] || null);
      if (result.tenderAnalysis) setTenderAnalysis(result.tenderAnalysis);
      if (result.participantAnalyses)
        setParticipantAnalyses(result.participantAnalyses);
      setStep("results");
      setShowHistory(false);
    },
    [
      setRanking,
      setSummary,
      setWinner,
      setTenderAnalysis,
      setParticipantAnalyses,
      setStep,
    ],
  );

  const deleteSavedResult = useCallback(
    async (id: number) => {
      try {
        const response = await fetch(`${API_BASE}/history/${id}/delete/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });

        if (response.ok) {
          window.dispatchEvent(
            new CustomEvent("analysisDeleted", { detail: { id } }),
          );
        }
      } catch (err) {
        console.error("Delete error:", err);
      }

      setSavedResults((prev) => prev.filter((r) => r.id !== id));
    },
    [setSavedResults],
  );

  // File handlers
  const handleTenderUpload = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        setTenderFile(file);
        setError(null);
      }
    },
    [],
  );

  const addParticipant = useCallback(() => {
    setParticipantFiles((prev) => [...prev, { name: "", file: null }]);
  }, []);

  const removeParticipant = useCallback((index: number) => {
    setParticipantFiles((prev) => {
      const filtered = prev.filter((_, i) => i !== index);
      return filtered.length === 0 ? [{ name: "", file: null }] : filtered;
    });
  }, []);

  const handleParticipantFile = useCallback((index: number, file: File) => {
    setParticipantFiles((prev) => {
      const updated = [...prev];
      updated[index] = {
        ...updated[index],
        file,
        name: updated[index].name || file.name.replace(/\.[^/.]+$/, ""),
      };
      return updated;
    });
  }, []);

  const handleParticipantName = useCallback((index: number, name: string) => {
    setParticipantFiles((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], name };
      return updated;
    });
  }, []);

  // Analysis functions
  const analyzeTender = async () => {
    if (!tenderFile) {
      setError(t("analysis.error_upload"));
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", tenderFile);
      formData.append("language", language);

      const response = await fetch(`${API_BASE}/analyze-tender/`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setTenderAnalysis(data.analysis);
        setStep("participants");
      } else {
        setError(data.error || t("analysis.error_analysis"));
      }
    } catch (err) {
      setError(t("analysis.error_server"));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const analyzeParticipants = async () => {
    const validParticipants = participantFiles.filter((p) => p.file && p.name);
    const minParticipants = getMinParticipants();

    // If no new participants but have existing analyses
    if (validParticipants.length === 0 && participantAnalyses.length > 0) {
      if (participantAnalyses.length < minParticipants) {
        setError(
          localize(
            `Reyting yaratish uchun kamida ${minParticipants} ta ishtirokchi kerak. Hozircha ${participantAnalyses.length} ta tahlil qilingan. ${minParticipants - participantAnalyses.length} ta boshqasini qo'shing.`,
            `Для создания рейтинга необходимо минимум ${minParticipants} участника. Сейчас проанализировано ${participantAnalyses.length}. Добавьте еще ${minParticipants - participantAnalyses.length}.`,
          ),
        );
        return;
      }

      // Only compare existing
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/compare-participants/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ participants: participantAnalyses, language }),
        });

        const data = await response.json();

        if (data.success) {
          setRanking(data.ranking);
          setWinner(data.winner);
          setSummary(data.summary);
          setStep("results");
        } else {
          setError(data.error || t("analysis.error_analysis"));
        }
      } catch (err) {
        console.error("Compare error:", err);
        setError(t("analysis.error_server"));
      } finally {
        setLoading(false);
      }
      return;
    }

    if (validParticipants.length === 0) {
      setError(t("analysis.at_least_one"));
      return;
    }

    setLoading(true);
    setError(null);
    const analyses: ParticipantAnalysis[] = [...participantAnalyses];

    try {
      // Analyze new participants
      for (const participant of validParticipants) {
        const formData = new FormData();
        formData.append("name", participant.name);
        formData.append("file", participant.file!);
        formData.append("language", language);
        if (tenderAnalysis) {
          formData.append("tender_data", JSON.stringify(tenderAnalysis));
        }

        const response = await fetch(`${API_BASE}/analyze-participant/`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (data.success) {
          const existingIndex = analyses.findIndex(
            (a) => a.participant_name === participant.name,
          );
          if (existingIndex >= 0) {
            analyses[existingIndex] = data.analysis;
          } else {
            analyses.push(data.analysis);
          }
        } else {
          setError(data.error || t("analysis.error_analysis"));
        }
      }

      setParticipantAnalyses(analyses);
      setParticipantFiles([{ name: "", file: null }]);

      if (analyses.length < minParticipants) {
        setError(
          localize(
            `Reyting yaratish uchun kamida ${minParticipants} ta ishtirokchi kerak. Hozircha ${analyses.length} ta tahlil qilingan. ${minParticipants - analyses.length} ta boshqasini qo'shing.`,
            `Для создания рейтинга необходимо минимум ${minParticipants} участника. Сейчас проанализировано ${analyses.length}. Добавьте еще ${minParticipants - analyses.length}.`,
          ),
        );
        setLoading(false);
        return;
      }

      // Compare participants
      const compareResponse = await fetch(`${API_BASE}/compare-participants/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ participants: analyses, language }),
      });

      const compareData = await compareResponse.json();

      if (compareData.success) {
        setRanking(compareData.ranking);
        setWinner(compareData.winner);
        setSummary(compareData.summary);
        setStep("results");

        // Save to server
        try {
          const saveResponse = await fetch(`${API_BASE}/save-result/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              tender: tenderAnalysis,
              participants: analyses,
              ranking: compareData.ranking,
              winner: compareData.winner,
              summary: compareData.summary,
              language,
            }),
          });
          const saveData = await saveResponse.json();
          if (saveData.success) {
            setTimeout(() => saveCurrentResult(), 100);
          }
        } catch (saveErr) {
          console.error("Save error:", saveErr);
        }
      }
    } catch (err) {
      setError(t("analysis.error_analysis"));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = async () => {
    try {
      await fetch(`${API_BASE}/reset/`, { method: "POST" });
    } catch (err) {
      console.error("Reset error:", err);
    }

    // Clear all state
    Object.values(STORAGE_KEYS).forEach((key) => {
      if (key !== STORAGE_KEYS.HISTORY && key !== STORAGE_KEYS.SETTINGS) {
        localStorage.removeItem(key);
      }
    });

    setStep("tender");
    setTenderFile(null);
    setTenderAnalysis(null);
    setParticipantFiles([{ name: "", file: null }]);
    setParticipantAnalyses([]);
    setRanking([]);
    setWinner(null);
    setSummary("");
    setError(null);
  };

  const downloadPDF = async () => {
    if (!ranking.length) return;

    setPdfLoading(true);
    try {
      const response = await fetch(`${API_BASE}/export-pdf/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tender_analysis: tenderAnalysis,
          ranking,
          winner,
          summary,
          language,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `tender_tahlil_${new Date().toISOString().slice(0, 10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setError(t("analysis.error_analysis"));
      }
    } catch (err) {
      console.error("PDF download error:", err);
      setError(t("analysis.error_analysis"));
    } finally {
      setPdfLoading(false);
    }
  };

  const downloadExcel = async () => {
    if (!ranking.length) return;
    const token = localStorage.getItem("access_token");

    try {
      const response = await fetch(`${API_BASE}/download-excel/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          tender: tenderAnalysis,
          ranking,
          summary,
          language,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `tender_tahlil_${new Date().toISOString().slice(0, 10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setError(t("analysis.error_analysis"));
      }
    } catch (err) {
      console.error("Excel download error:", err);
      setError(t("analysis.error_analysis"));
    }
  };

  // Memoized components
  const getRiskBadge = useCallback(
    (level: string) => {
      const colors: Record<string, string> = {
        low: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
        medium:
          "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
        high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
      };
      const labels: Record<string, string> = {
        low: t("risk.low"),
        medium: t("risk.medium"),
        high: t("risk.high"),
      };
      return (
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${colors[level] || "bg-gray-100 dark:bg-gray-800"}`}
        >
          {labels[level] || level}
        </span>
      );
    },
    [t],
  );

  return (
    <div className="space-y-8 relative z-10">
      {/* Header */}
      <div className="relative z-10">
        <div className="flex justify-between items-center">
          <div className="animate-slide-up">
            <h1 className="text-4xl font-bold text-foreground flex items-center gap-3">
              {t("analysis.title")}
              <Sparkles className="w-8 h-8 text-yellow-500 animate-pulse" />
            </h1>
            <p className="text-muted-foreground text-lg mt-2">
              {t("analysis.subtitle")}
            </p>
          </div>
          <div
            className="flex gap-2 animate-fade-in"
            style={{ animationDelay: "0.3s" }}
          >
            {savedResults.length > 0 && step === "tender" && (
              <Button
                variant="outline"
                onClick={() => setShowHistory(!showHistory)}
                className="bg-gradient-to-r from-primary/10 to-primary/5 hover:from-primary/20 hover:to-primary/10 border-primary/20"
              >
                <History className="w-4 h-4 mr-2" />
                {t("analysis.history_title")} ({savedResults.length})
              </Button>
            )}
            <Button
              variant="outline"
              onClick={resetAnalysis}
              className="bg-gradient-to-r from-destructive/10 to-destructive/5 hover:from-destructive/20 hover:to-destructive/10 border-destructive/20"
            >
              <Plus className="w-4 h-4 mr-2" />
              {t("analysis.new_analysis")}
            </Button>
          </div>
        </div>
      </div>

      {/* History Modal */}
      {showHistory && (
        <Card className="border-2 border-emerald-200 dark:border-emerald-800">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>📋 {t("analysis.history_title")}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistory(false)}
              >
                ✕
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {savedResults.map((result) => (
                <div
                  key={result.id}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg hover:bg-muted/80"
                >
                  <div className="flex-1">
                    <p className="font-medium text-foreground">
                      {result.tender}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {t("analysis.history_winner")}: {result.winner} •{" "}
                      {result.participantCount}{" "}
                      {t("analysis.history_participant")} •
                      {new Date(result.date).toLocaleDateString(dateLocale)}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => loadSavedResult(result)}>
                      {t("analysis.history_view")}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => deleteSavedResult(result.id)}
                    >
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
      <div className="flex items-center justify-center mb-8">
        <div className="flex items-center space-x-6">
          {STEP_CONFIG.map((stepItem, index) => (
            <div key={stepItem.key} className="flex items-center">
              <div className="relative group">
                <div
                  className={`flex items-center space-x-3 px-6 py-3 rounded-full transition-all duration-500 transform ${
                    step === stepItem.key
                      ? "bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-xl scale-110"
                      : "bg-muted/80 text-muted-foreground hover:bg-muted hover:scale-105"
                  }`}
                >
                  <stepItem.icon className="w-5 h-5" />
                  <span className="text-sm font-semibold">
                    {t(stepItem.label)}
                  </span>
                </div>
                {step === stepItem.key && (
                  <Sparkles className="absolute -top-2 -right-2 w-4 h-4 text-yellow-500 animate-pulse" />
                )}
              </div>
              {index < 2 && (
                <ArrowRight className="w-5 h-5 mx-3 text-muted-foreground" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-lg flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      {/* Step 1: Tender Upload */}
      {step === "tender" && (
        <Card className="border-0 shadow-xl animate-slide-up">
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2 text-2xl">
              <Target className="w-6 h-6 text-primary" />
              {t("analysis.tender_title")}
              <Sparkles className="w-5 h-5 text-yellow-500 animate-pulse" />
            </CardTitle>
            <CardDescription className="text-base">
              {t("analysis.tender_desc")}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors">
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleTenderUpload}
                className="hidden"
                id="tender-file-input"
              />
              <label htmlFor="tender-file-input" className="cursor-pointer">
                <Upload className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                {tenderFile ? (
                  <div>
                    <p className="text-lg font-medium">{tenderFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(tenderFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-lg font-medium text-foreground">
                      {t("analysis.upload_click")}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {t("analysis.upload_drag")}
                    </p>
                  </div>
                )}
              </label>
            </div>

            <Button
              onClick={analyzeTender}
              disabled={loading || !tenderFile}
              className="w-full bg-gradient-to-r from-primary to-primary/80"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t("analysis.analyzing")}
                </>
              ) : (
                <>
                  <Zap className="mr-2 h-4 w-4" />
                  {t("analysis.start_analysis")}
                </>
              )}
            </Button>
            {loading && (
              <div className="mt-4 flex items-center justify-center gap-2 text-sm text-muted-foreground animate-pulse">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>
                  Tahlil jarayoni fayl hajmiga qarab bir necha daqiqa davom
                  etishi mumkin
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 2: Participants */}
      {step === "participants" && tenderAnalysis && (
        <div className="space-y-6">
          {/* Tender Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground">
                {t("analysis.tender_info")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">
                    {t("analysis.purpose")}
                  </p>
                  <p className="font-medium text-foreground">
                    {tenderAnalysis.tender_purpose}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">
                    {t("analysis.type")}
                  </p>
                  <p className="font-medium text-foreground">
                    {tenderAnalysis.tender_type}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">
                    {t("analysis.requirements_count")}
                  </p>
                  <p className="font-medium text-foreground">
                    {tenderAnalysis.requirements_count} (
                    {t("analysis.mandatory")}: {tenderAnalysis.mandatory_count})
                  </p>
                </div>
              </div>

              {/* Requirements */}
              <div className="mt-4">
                <p className="text-sm font-medium mb-2 text-foreground">
                  {t("analysis.main_requirements")}:
                </p>
                <div className="space-y-2">
                  {tenderAnalysis.requirements.slice(0, 5).map((req, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between bg-muted p-2 rounded"
                    >
                      <span className="text-sm text-foreground">
                        {req.title}
                      </span>
                      <div className="flex items-center space-x-2">
                        {req.is_mandatory && (
                          <Badge variant="destructive">
                            {t("analysis.mandatory")}
                          </Badge>
                        )}
                        <span className="text-xs text-muted-foreground">
                          {t("analysis.weight")}:{" "}
                          {(req.weight * 100).toFixed(0)}%
                        </span>
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
              <CardTitle className="flex items-center text-foreground">
                <Users className="w-5 h-5 mr-2" />
                {t("analysis.participants")}
              </CardTitle>
              <CardDescription>
                {t("analysis.participants_desc")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Allaqachon tahlil qilingan ishtirokchilar */}
              {participantAnalyses.length > 0 && (
                <div className="mb-4 p-4 bg-muted border rounded-lg">
                  <h4 className="font-medium mb-2 text-foreground">
                    ✓ {t("analysis.analyzed_participants")}:
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {participantAnalyses.map((p, i) => (
                      <Badge
                        key={i}
                        variant="secondary"
                        className="flex items-center gap-1 pr-1"
                      >
                        {p.participant_name} -{" "}
                        {(
                          p.total_weighted_score ||
                          p.overall_match_percentage ||
                          0
                        ).toFixed(0)}
                        %
                        <button
                          onClick={() => {
                            const updated = participantAnalyses.filter(
                              (_, idx) => idx !== i,
                            );
                            setParticipantAnalyses(updated);
                          }}
                          className="ml-1 hover:text-red-500 transition-colors"
                          title="O'chirish"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    {t("analysis.add_more_desc")}
                  </p>
                </div>
              )}

              {/* Yangi ishtirokchi qo'shish formasi - har doim ko'rsatiladi */}
              <div className="space-y-4">
                {participantFiles.map((p, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-4 p-4 border rounded-lg"
                  >
                    <div className="flex-1">
                      <input
                        type="text"
                        placeholder={t("analysis.company_name")}
                        value={p.name}
                        onChange={(e) =>
                          handleParticipantName(index, e.target.value)
                        }
                        className="w-full border rounded px-3 py-2 mb-2 bg-background text-foreground"
                      />
                      <input
                        type="file"
                        accept=".pdf,.docx,.doc,.txt"
                        onChange={(e) => {
                          if (e.target.files?.[0]) {
                            handleParticipantFile(index, e.target.files[0]);
                          }
                        }}
                        className="text-sm"
                      />
                      {p.file && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {p.file.name}
                        </p>
                      )}
                    </div>
                    {participantFiles.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeParticipant(index)}
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    )}
                  </div>
                ))}

                {/* Qo'shimcha ishtirokchi qo'shish tugmasi */}
                {participantFiles.length < 10 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={addParticipant}
                    className="w-full"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    {localize(
                      "Yana ishtirokchi qo'shish",
                      "Добавить участника",
                    )}
                  </Button>
                )}
              </div>

              <Button
                onClick={analyzeParticipants}
                disabled={loading}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    {t("analysis.analyzing")}
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5 mr-2" />
                    {t("analysis.evaluate_participants")}
                  </>
                )}
              </Button>
              {loading && (
                <div className="mt-4 flex items-center justify-center gap-2 text-sm text-muted-foreground animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>SI Tahlil jarayonini boshlagan, iltimos kuting.</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      
      {/* Step 3: Results */}

      
      {step === "results" && (
        <div className="space-y-6">
          {/* Action Buttons */}
          <Card className="bg-muted">
            <CardContent className="py-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h3 className="font-medium text-foreground">
                    {t("analysis.completed")}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {t("analysis.auto_saved")}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={downloadPDF}
                    disabled={pdfLoading}
                    variant="default"
                  >
                    {pdfLoading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4 mr-2" />
                    )}
                    {localize("PDF yuklab olish", "Скачать PDF")}
                  </Button>
                  <Button onClick={downloadExcel} variant="outline">
                    <Download className="w-4 h-4 mr-2" />
                    Excel
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setStep("participants");
                      setParticipantFiles([{ name: "", file: null as any }]);
                    }}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    {t("analysis.add_new_participant")}
                  </Button>
                  <Button variant="outline" onClick={resetAnalysis}>
                    {t("analysis.new_analysis")}
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
                  {t("analysis.winner")}: {winner.participant_name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary">
                      {winner.total_weighted_score?.toFixed(1) ||
                        winner.overall_match_percentage ||
                        0}
                      %
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {t("analysis.total_score")}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary">
                      {winner.overall_match_percentage}%
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {t("analysis.match")}
                    </p>
                  </div>
                  <div className="text-center">
                    {getRiskBadge(winner.risk_level)}
                    <p className="text-sm text-muted-foreground mt-1">
                      {t("analysis.risk_level")}
                    </p>
                  </div>
                </div>
                <p className="mt-4 text-muted-foreground">
                  {winner.recommendation}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Ranking */}
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground">
                {t("analysis.ranking")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {ranking.map((p, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border ${index === 0 ? "border-primary bg-primary/5" : "bg-card"}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <span
                          className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                            index === 0
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {index + 1}
                        </span>
                        <span className="font-medium">
                          {p.participant_name}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4">
                        {getRiskBadge(p.risk_level)}
                        <span className="text-2xl font-bold text-primary">
                          {p.total_weighted_score?.toFixed(1) ||
                            p.overall_match_percentage ||
                            0}
                          %
                        </span>
                      </div>
                    </div>

                    <Progress
                      value={
                        p.total_weighted_score ||
                        p.overall_match_percentage ||
                        0
                      }
                      className="h-2 mb-3"
                    />

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground mb-1">
                          {t("analysis.strengths")}:
                        </p>
                        <ul className="list-disc list-inside text-foreground">
                          {p.strengths?.slice(0, 3).map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <p className="text-muted-foreground mb-1">
                          {t("analysis.weaknesses")}:
                        </p>
                        <ul className="list-disc list-inside text-foreground">
                          {p.weaknesses?.slice(0, 3).map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {p.price_analysis && (
                      <div className="mt-3 p-2 bg-muted rounded text-sm">
                        <span className="text-muted-foreground">
                          {t("analysis.price")}:{" "}
                        </span>
                        <span className="font-medium">
                          {p.price_analysis.proposed_price}
                        </span>
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
                <CardTitle className="text-foreground">
                  {t("analysis.summary")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => (
                        <h1 className="text-2xl font-bold mt-4 mb-2">
                          {children}
                        </h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className="text-xl font-bold mt-4 mb-2">
                          {children}
                        </h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className="text-lg font-semibold mt-3 mb-1">
                          {children}
                        </h3>
                      ),
                      p: ({ children }) => (
                        <p className="mb-2 text-foreground">{children}</p>
                      ),
                      ul: ({ children }) => (
                        <ul className="list-disc list-inside mb-2 ml-4">
                          {children}
                        </ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="list-decimal list-inside mb-2 ml-4">
                          {children}
                        </ol>
                      ),
                      li: ({ children }) => (
                        <li className="flex mb-1">{children}</li>
                      ),
                      strong: ({ children }) => (
                        <strong className="font-bold">{children}</strong>
                      ),
                      em: ({ children }) => (
                        <em className="italic">{children}</em>
                      ),
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
  );
};

export default TenderAnalysis;

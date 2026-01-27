import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
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
  Search,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { API_ENDPOINTS } from "../config/api";

// Mock translation function - replace with your actual implementation

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className = "", ...props }, ref) => (
  <div
    ref={ref}
    className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm ${className}`}
    {...props}
  />
));
Card.displayName = "Card";

/* CardHeader */
const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className = "", ...props }, ref) => (
  <div ref={ref} className={`p-6 ${className}`} {...props} />
));
CardHeader.displayName = "CardHeader";

/* CardTitle */
const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className = "", ...props }, ref) => (
  <h3 ref={ref} className={`text-lg font-semibold ${className}`} {...props} />
));
CardTitle.displayName = "CardTitle";

/* CardContent */
const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className = "", ...props }, ref) => (
  <div ref={ref} className={`p-6 ${className}`} {...props} />
));
CardContent.displayName = "CardContent";

type ButtonVariant = "primary" | "outline" | "ghost";
type ButtonSize = "sm" | "md";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "primary", size = "md", ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200";

    const variants: Record<ButtonVariant, string> = {
      primary:
        "bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm hover:shadow-md",
      outline:
        "border-2 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700",
      ghost: "hover:bg-gray-100 dark:hover:bg-gray-700",
    };

    const sizes: Record<ButtonSize, string> = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2",
    };

    return (
      <button
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

type BadgeVariant = "default" | "secondary";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className = "", variant = "default", ...props }, ref) => {
    const variants: Record<BadgeVariant, string> = {
      default: "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200",
      secondary:
        "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200",
    };

    return (
      <span
        ref={ref}
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}
        {...props}
      />
    );
  },
);
Badge.displayName = "Badge";

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ value, className = "", ...props }, ref) => (
    <div
      ref={ref}
      className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden ${className}`}
      {...props}
    >
      <div
        className="bg-emerald-600 h-full rounded-full transition-all duration-500 ease-out"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  ),
);
Progress.displayName = "Progress";

const AnalysisHistory = () => {
  const navigate = useNavigate();
  const { t } = useTheme();
  
  interface AnalysisResult {
    id: number;
    date: string;
    tender: string;
    tender_type?: string;
    winner: string;
    winner_score?: number;
    participantCount: number;
    ranking: any[];
    summary: string;
  }
  
  const [savedResults, setSavedResults] = useState<AnalysisResult[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [selectedResult, setSelectedResult] = useState<AnalysisResult | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSavedResults();
  }, []);

  const loadSavedResults = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("access_token"); // yoki authToken

      const response = await fetch(
        "https://tanlov.kuprikqurilish.uz/api/evaluations/history/",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error("Failed to fetch history");
      }

      const data = await response.json();

      if (data.success && data.history) {
        setSavedResults(data.history);
      }
    } catch (e: any) {
      console.error("Error loading results:", e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteResult = async (id: number) => {
    try {
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      
      let response = await fetch(`${API_ENDPOINTS.evaluations}/history/${id}/delete/`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          ...(accessToken && { "Authorization": `Bearer ${accessToken}` })
        },
      });

      // If 401, try to refresh token
      if (response.status === 401 && refreshToken) {
        try {
          const refreshResponse = await fetch(`${API_ENDPOINTS.auth}/token/refresh/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh: refreshToken }),
          });

          if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            localStorage.setItem('access_token', data.access);
            if (data.refresh) {
              localStorage.setItem('refresh_token', data.refresh);
            }

            // Retry with new token
            response = await fetch(`${API_ENDPOINTS.evaluations}/history/${id}/delete/`, {
              method: "DELETE",
              headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${data.access}`
              },
            });
          }
        } catch (refreshErr) {
          console.error("Token refresh failed:", refreshErr);
          window.location.href = '/login';
          return;
        }
      }

      if (response.ok) {
        const updated = savedResults.filter((r) => r.id !== id);
        setSavedResults(updated);
        if (selectedResult?.id === id) {
          setSelectedResult(null);
        }
      } else {
        console.error("Delete failed:", response.statusText);
      }
    } catch (e) {
      console.error("Error deleting result:", e);
    }
  };

  const clearAllHistory = async () => {
    if (confirm(t("history.delete_all") + "?")) {
      try {
        // Add your clear all API call here
        setSavedResults([]);
        setSelectedResult(null);
      } catch (e) {
        console.error("Error clearing history:", e);
      }
    }
  };

  const continueAnalysis = (result: AnalysisResult) => {
    // Implement navigation to analysis page
    navigate("/analysis?continue=true");
  };

  const getRiskBadge = (level: string) => {
    const styles = {
      low: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
      medium:
        "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
      high: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20",
    };
    return (
      <span
        className={`px-3 py-1 rounded-full text-xs font-medium border ${styles[level as keyof typeof styles] || "bg-gray-500/10 text-gray-500"}`}
      >
        {t(`risk.${level}`)}
      </span>
    );
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("uz-UZ", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const filteredResults = savedResults.filter(
    (r) =>
      r.tender?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.winner?.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const getScoreDisplay = (participant: any) => {
    return (
      participant.total_weighted_score ||
      participant.overall_match_percentage ||
      0
    );
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-4">
        <Card className="border-2 border-dashed">
          <CardContent className="py-20 text-center">
            <Loader2 className="w-12 h-12 mx-auto text-emerald-600 animate-spin mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              {t("history.loading")}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-4">
        <Card className="border-2 border-red-200 dark:border-red-800">
          <CardContent className="py-20 text-center">
            <AlertCircle className="w-12 h-12 mx-auto text-red-600 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {t("history.error")}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
            <Button onClick={loadSavedResults}>
              <RefreshCw className="w-4 h-4 mr-2" />
              {t("history.retry")}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  console.log("filteredResults", filteredResults);
  console.log("savedResults", savedResults);
  console.log("selectedResult", selectedResult);

  return (
    <div className="max-w-7xl mx-auto space-y-6 p-4 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold flex items-center gap-3 text-gray-900 dark:text-white">
            <div className="p-2 bg-emerald-100 dark:bg-emerald-900 rounded-xl">
              <History className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
            </div>
            {t("history.title")}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {t("history.subtitle")}
          </p>
        </div>
        <div className="flex gap-3">
          <Button onClick={() => navigate("/analysis")}>
            <Plus className="w-4 h-4 mr-2" />
            {t("analysis.new_analysis")}
          </Button>
          {savedResults.length > 0 && (
            <Button variant="outline" onClick={clearAllHistory}>
              <Trash2 className="w-4 h-4 mr-2" />
              {t("history.delete_all")}
            </Button>
          )}
        </div>
      </div>

      {savedResults.length === 0 ? (
        <Card className="border-dashed border-2 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900">
          <CardContent className="py-20 text-center">
            <div className="w-20 h-20 mx-auto bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mb-6 animate-pulse">
              <History className="w-10 h-10 text-gray-400 dark:text-gray-500" />
            </div>
            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              {t("history.empty")}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {t("history.empty_desc")}
            </p>
            <Button onClick={() => navigate("/analysis")}>
              <Plus className="w-4 h-4 mr-2" />
              {t("history.start_first")}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Search */}
          <div className="relative group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 group-focus-within:text-emerald-600 transition-colors" />
            <input
              type="text"
              placeholder={t("common.search") + "..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Panel */}
            <div className="lg:col-span-4 space-y-4">
              <div className="flex items-center justify-between px-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {t("history.total")}:{" "}
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {filteredResults.length}
                  </span>{" "}
                  {t("history.analyses")}
                </span>
              </div>

              <div className="space-y-3 flex flex-col items-center max-h-[calc(100vh-300px)] overflow-y-auto pr-2 custom-scrollbar">
                {filteredResults.map((result, index) => (
                  <div
                    key={result.id}
                    onClick={() => setSelectedResult(result)}
                    className={`group w-[95%] mt-1 p-4 rounded-xl border-2 cursor-pointer transition-all duration-300 transform hover:scale-[1.02] animate-in slide-in-from-left ${
                      selectedResult?.id === result.id
                        ? "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-500 shadow-lg"
                        : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-emerald-300 dark:hover:border-emerald-700 hover:shadow-md"
                    }`}
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 dark:text-white truncate">
                          {result.tender || "Nomlanmagan Tender"}
                        </h4>
                        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500 dark:text-gray-400">
                          <Calendar className="w-3.5 h-3.5" />
                          {formatDate(result.date)}
                        </div>
                        <div className="flex items-center gap-2 mt-3 flex-wrap">
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
                          e.stopPropagation();
                          deleteResult(result.id);
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
                <div className="space-y-5 animate-in fade-in slide-in-from-right duration-500">
                  {/* Header Card */}
                  <Card className="overflow-hidden border-2 border-emerald-500">
                    <CardContent className="p-6">
                      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                        <div>
                          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                            {selectedResult.tender}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1 flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            {formatDate(selectedResult.date)}
                          </p>
                        </div>
                        {/* <div className="flex gap-2">
                          <Button
                            onClick={() => continueAnalysis(selectedResult)}
                          >
                            <Plus className="w-4 h-4 mr-2" />
                            {t("analysis.add_participant")}
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => continueAnalysis(selectedResult)}
                          >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            {t("history.reanalyze")}
                          </Button>
                        </div> */}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Winner Card */}
                  <Card className="overflow-hidden border-2 border-gray-200 dark:border-gray-700">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
                          <Award className="w-7 h-7 text-white" />
                        </div>
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {t("analysis.winner")}
                          </p>
                          <h4 className="text-xl font-bold text-gray-900 dark:text-white">
                            {selectedResult.winner}
                          </h4>
                        </div>
                      </div>

                      {selectedResult.ranking[0] && (
                        <div className="grid grid-cols-3 gap-4 mt-4">
                          <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 rounded-xl p-4 text-center border border-emerald-200 dark:border-emerald-800">
                            <p className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
                              {getScoreDisplay(
                                selectedResult.ranking[0],
                              ).toFixed(1)}
                              %
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {t("analysis.total_score")}
                            </p>
                          </div>
                          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-4 text-center border border-blue-200 dark:border-blue-800">
                            <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                              {selectedResult.ranking[0]
                                .overall_match_percentage || 0}
                              %
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {t("analysis.match")}
                            </p>
                          </div>
                          <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-xl p-4 text-center border border-gray-200 dark:border-gray-700">
                            {getRiskBadge(
                              selectedResult.ranking[0].risk_assessment
                                ?.overall_risk || "low",
                            )}
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                              {t("analysis.risk_level")}
                            </p>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Ranking */}
                  <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
                    <CardHeader className="pb-2 border-b border-gray-200 dark:border-gray-700">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <TrendingUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                        {t("analysis.ranking")}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        {selectedResult.ranking.map((p: any, index: number) => {
                          const score = getScoreDisplay(p);
                          const isExpanded = expandedId === index;
                          return (
                            <div
                              key={index}
                              className={`p-4 rounded-xl transition-all duration-300 ${
                                index === 0
                                  ? "bg-gradient-to-br from-emerald-50 to-emerald-100/50 dark:from-emerald-900/20 dark:to-emerald-800/10 border-2 border-emerald-500"
                                  : "bg-gray-50 dark:bg-gray-800/50 border-2 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700/50"
                              }`}
                            >
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-3">
                                  <span
                                    className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm shadow-sm ${
                                      index === 0
                                        ? "bg-gradient-to-br from-emerald-500 to-emerald-600 text-white"
                                        : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                                    }`}
                                  >
                                    {index + 1}
                                  </span>
                                  <span className="font-medium text-gray-900 dark:text-white">
                                    {p.participant_name}
                                  </span>
                                </div>
                                <div className="flex items-center gap-3">
                                  {getRiskBadge(
                                    p.risk_assessment?.overall_risk || "low",
                                  )}
                                  <span className="text-xl font-bold text-emerald-600 dark:text-emerald-400">
                                    {score.toFixed(1)}%
                                  </span>
                                </div>
                              </div>

                              <Progress
                                value={score}
                                className="h-2 bg-gray-200 dark:bg-gray-700"
                              />

                              <button
                                className="w-full mt-3 text-xs text-gray-600 dark:text-gray-400 hover:text-emerald-600 dark:hover:text-emerald-400 flex items-center justify-center gap-1 transition-colors font-medium"
                                onClick={() =>
                                  setExpandedId(isExpanded ? null : index)
                                }
                              >
                                {isExpanded ? (
                                  <>
                                    {t("history.hide")}{" "}
                                    <ChevronUp className="w-4 h-4" />
                                  </>
                                ) : (
                                  <>
                                    {t("history.details")}{" "}
                                    <ChevronDown className="w-4 h-4" />
                                  </>
                                )}
                              </button>

                              {isExpanded && (
                                <div className="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm animate-in slide-in-from-top duration-300">
                                  <div className="space-y-2">
                                    <p className="font-medium flex items-center gap-1 text-gray-900 dark:text-white">
                                      <TrendingUp className="w-4 h-4 text-emerald-600" />
                                      {t("analysis.strengths")}
                                    </p>
                                    <ul className="space-y-1 text-gray-700 dark:text-gray-300">
                                      {(p.strengths || [])
                                        .slice(0, 5)
                                        .map((s: string, i: number) => (
                                          <li
                                            key={i}
                                            className="flex items-start gap-2"
                                          >
                                            <span className="text-emerald-600 mt-1">
                                              •
                                            </span>
                                            {s}
                                          </li>
                                        ))}
                                    </ul>
                                  </div>
                                  <div className="space-y-2">
                                    <p className="font-medium flex items-center gap-1 text-gray-900 dark:text-white">
                                      <TrendingUp className="w-4 h-4 rotate-180 text-red-600" />
                                      {t("analysis.weaknesses")}
                                    </p>
                                    <ul className="space-y-1 text-gray-700 dark:text-gray-300">
                                      {(p.weaknesses || [])
                                        .slice(0, 5)
                                        .map((w: string, i: number) => (
                                          <li
                                            key={i}
                                            className="flex items-start gap-2"
                                          >
                                            <span className="text-red-600 mt-1">
                                              •
                                            </span>
                                            {w}
                                          </li>
                                        ))}
                                    </ul>
                                  </div>
                                  {p.financial_analysis?.proposed_price && (
                                    <div className="col-span-full p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                      <span className="text-gray-700 dark:text-gray-300">
                                        {t("history.price")}:{" "}
                                      </span>
                                      <span className="font-medium text-gray-900 dark:text-white">
                                        {p.financial_analysis.proposed_price}
                                      </span>
                                    </div>
                                  )}
                                  {p.recommendation && (
                                    <div className="col-span-full p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                                      <span className="font-medium text-gray-900 dark:text-white">
                                        {t("analysis.recommendation")}:{" "}
                                      </span>
                                      <span className="text-gray-700 dark:text-gray-300">
                                        {p.recommendation}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Summary */}
                  {selectedResult?.summary && (
                    <Card className="border-2 border-gray-200 dark:border-gray-700 shadow-lg">
                      <CardHeader className="pb-2 border-b border-gray-200 dark:border-gray-700">
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <FileText className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                          {t("analysis.summary")}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-6">
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                          <ReactMarkdown
                            components={{
                              h1: ({ children }) => (
                                <h1 className="text-xl font-bold mt-4 mb-2 text-gray-900 dark:text-white">
                                  {children}
                                </h1>
                              ),
                              h2: ({ children }) => (
                                <h2 className="text-lg font-bold mt-4 mb-2 text-gray-900 dark:text-white">
                                  {children}
                                </h2>
                              ),
                              h3: ({ children }) => (
                                <h3 className="text-base font-bold mt-3 mb-2 text-gray-900 dark:text-white">
                                  {children}
                                </h3>
                              ),
                              p: ({ children }) => (
                                <p className="mb-2 text-gray-700 dark:text-gray-300">
                                  {children}
                                </p>
                              ),
                              ul: ({ children }) => (
                                <ul className="list-disc list-inside mb-2 ml-4 text-gray-700 dark:text-gray-300">
                                  {children}
                                </ul>
                              ),
                              strong: ({ children }) => (
                                <strong className="font-bold text-gray-900 dark:text-white">
                                  {children}
                                </strong>
                              ),
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
                <Card className="border-dashed border-2 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900">
                  <CardContent className="py-20 text-center">
                    <div className="w-20 h-20 mx-auto bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mb-6 animate-pulse">
                      <History className="w-10 h-10 text-gray-400 dark:text-gray-500" />
                    </div>
                    <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                      {t("history.select")}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      {t("history.select_desc")}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AnalysisHistory;

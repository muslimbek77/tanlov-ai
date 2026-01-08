import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency: string = 'UZS'): string {
  return new Intl.NumberFormat('uz-UZ', {
    style: 'currency',
    currency: currency === 'UZS' ? 'UZS' : 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return new Intl.DateTimeFormat('uz-UZ', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(d)
}

export function formatDateTime(date: string | Date): string {
  const d = new Date(date)
  return new Intl.DateTimeFormat('uz-UZ', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(d)
}

export function getRiskLevelColor(riskLevel: string): string {
  switch (riskLevel.toLowerCase()) {
    case 'low':
      return 'text-success'
    case 'medium':
      return 'text-warning'
    case 'high':
      return 'text-danger'
    case 'critical':
      return 'text-destructive'
    default:
      return 'text-muted-foreground'
  }
}

export function getRiskLevelBg(riskLevel: string): string {
  switch (riskLevel.toLowerCase()) {
    case 'low':
      return 'bg-success/10 border-success/20'
    case 'medium':
      return 'bg-warning/10 border-warning/20'
    case 'high':
      return 'bg-danger/10 border-danger/20'
    case 'critical':
      return 'bg-destructive/10 border-destructive/20'
    default:
      return 'bg-muted'
  }
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'active':
      return 'text-success'
    case 'pending':
      return 'text-warning'
    case 'completed':
      return 'text-info'
    case 'cancelled':
      return 'text-destructive'
    case 'failed':
      return 'text-danger'
    default:
      return 'text-muted-foreground'
  }
}

export function getStatusBg(status: string): string {
  switch (status.toLowerCase()) {
    case 'active':
      return 'bg-success/10 border-success/20'
    case 'pending':
      return 'bg-warning/10 border-warning/20'
    case 'completed':
      return 'bg-info/10 border-info/20'
    case 'cancelled':
      return 'bg-destructive/10 border-destructive/20'
    case 'failed':
      return 'bg-danger/10 border-danger/20'
    default:
      return 'bg-muted'
  }
}

export function getScoreColor(score: number): string {
  if (score >= 90) return 'text-success'
  if (score >= 75) return 'text-info'
  if (score >= 60) return 'text-warning'
  return 'text-danger'
}

export function calculatePercentage(value: number, total: number): number {
  if (total === 0) return 0
  return Math.round((value / total) * 100)
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function validatePhone(phone: string): boolean {
  const phoneRegex = /^\+?[\d\s\-\(\)]+$/
  return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 9
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

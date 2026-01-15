// API Configuration
// Uses environment variable or falls back to production URL
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://tanlov.kuprikqurilish.uz/api';

export const API_ENDPOINTS = {
  auth: `${API_BASE_URL}/auth`,
  stats: `${API_BASE_URL}/stats`,
  evaluations: `${API_BASE_URL}/evaluations`,
  antiFraud: `${API_BASE_URL}/anti-fraud`,
  compliance: `${API_BASE_URL}/compliance`,
  tenders: `${API_BASE_URL}/tenders`,
  participants: `${API_BASE_URL}/participants`,
};

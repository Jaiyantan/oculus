/**
 * Oculus API Client
 * 
 * Centralized API calls using Axios.
 * All endpoints go through this module.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// ========================
// Transactions
// ========================

/**
 * Submit a new transaction for fraud evaluation.
 */
export async function submitTransaction(data) {
  const response = await api.post('/api/v1/transactions', data);
  return response.data;
}

// ========================
// Fraud Flags
// ========================

/**
 * List fraud flags with optional status filter.
 */
export async function getFraudFlags(status = null, limit = 50, offset = 0) {
  const params = { limit, offset };
  if (status) params.status = status;
  const response = await api.get('/api/v1/fraud-flags', { params });
  return response.data;
}

/**
 * Get a single fraud flag with full details.
 */
export async function getFraudFlagDetail(flagId) {
  const response = await api.get(`/api/v1/fraud-flags/${flagId}`);
  return response.data;
}

// ========================
// Reviews
// ========================

/**
 * Submit a review action for a fraud flag.
 */
export async function reviewFraudFlag(flagId, reviewData) {
  const response = await api.patch(`/api/v1/fraud-flags/${flagId}/review`, reviewData);
  return response.data;
}

/**
 * List all review actions (audit log).
 */
export async function getReviewActions(limit = 50, offset = 0) {
  const response = await api.get('/api/v1/review-actions', { params: { limit, offset } });
  return response.data;
}

// ========================
// Health
// ========================

/**
 * Check system health.
 */
export async function getHealth() {
  const response = await api.get('/api/v1/health');
  return response.data;
}

export default api;

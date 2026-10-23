/**
 * MAUSAM API Client
 * All API interactions go through this module.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BUSINESS_ID = import.meta.env.VITE_DEMO_BUSINESS_ID || 'demo_ramesh_textiles';

export { BUSINESS_ID };

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const err = await response.json();
      message = err.message || err.detail || message;
    } catch {}
    throw new ApiError(response.status, message);
  }

  return response.json();
}

// ─── Health ──────────────────────────────────────────────────────────────────
export const getHealth = () => request<any>('/api/v1/health');

// ─── Businesses ──────────────────────────────────────────────────────────────
export const getBusinesses = () => request<any>('/api/v1/businesses');
export const getOverview = (id: string) => request<any>(`/api/v1/businesses/${id}/overview`);

// ─── Forecast ────────────────────────────────────────────────────────────────
export const getCashForecast = (id: string) => request<any>(`/api/v1/businesses/${id}/cash-forecast`);
export const runForecast = (id: string, params?: any) =>
  request<any>(`/api/v1/businesses/${id}/forecast/run`, {
    method: 'POST',
    body: JSON.stringify(params || {}),
  });

// ─── Customers ────────────────────────────────────────────────────────────────
export const getCustomers = (id: string, page = 1, limit = 20) =>
  request<any>(`/api/v1/businesses/${id}/customers?page=${page}&limit=${limit}`);
export const getCustomer = (bid: string, cid: string) =>
  request<any>(`/api/v1/businesses/${bid}/customers/${cid}`);

// ─── Invoices ─────────────────────────────────────────────────────────────────
export const getInvoices = (id: string, params?: Record<string, string>) => {
  const qs = params ? '?' + new URLSearchParams(params).toString() : '';
  return request<any>(`/api/v1/businesses/${id}/invoices${qs}`);
};

// ─── Reconciliation ──────────────────────────────────────────────────────────
export const runReconciliation = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/reconciliation/run`, { method: 'POST' });
export const getFindings = (id: string, params?: Record<string, string>) => {
  const qs = params ? '?' + new URLSearchParams(params).toString() : '';
  return request<any>(`/api/v1/businesses/${id}/findings${qs}`);
};
export const updateFinding = (bid: string, fid: string, body: any) =>
  request<any>(`/api/v1/businesses/${bid}/findings/${fid}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });

// ─── Risk ─────────────────────────────────────────────────────────────────────
export const getRiskAssessment = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/risk-assessment`);
export const runRiskAssessment = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/risk-assessment/run`, { method: 'POST' });

// ─── Rescue ──────────────────────────────────────────────────────────────────
export const runRescueSimulation = (id: string, body: any) =>
  request<any>(`/api/v1/businesses/${id}/rescue-simulations`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
export const loanSimulator = (id: string, body: any) =>
  request<any>(`/api/v1/businesses/${id}/rescue-simulations/loan`, {
    method: 'POST',
    body: JSON.stringify(body),
  });

// ─── Committee ────────────────────────────────────────────────────────────────
export const runCommittee = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/committee/run`, { method: 'POST' });
export const getLatestCommittee = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/committee/latest`);

// ─── Alerts ──────────────────────────────────────────────────────────────────
export const getAlerts = (id: string, unreadOnly?: boolean) => {
  const qs = unreadOnly ? '?is_read=false' : '';
  return request<any>(`/api/v1/businesses/${id}/alerts${qs}`);
};
export const markAlertRead = (bid: string, aid: string) =>
  request<any>(`/api/v1/businesses/${bid}/alerts/${aid}/read`, { method: 'POST' });
export const previewAlert = (bid: string, body: any) =>
  request<any>(`/api/v1/businesses/${bid}/alerts/preview`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
export const generateAlerts = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/alerts/generate`, { method: 'POST' });

// ─── Passports ───────────────────────────────────────────────────────────────
export const createPassport = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/passports`, { method: 'POST' });
export const getPassports = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/passports`);
export const verifyPassport = (publicId: string) =>
  request<any>(`/api/v1/passports/${publicId}/verify`);

// ─── Demo ─────────────────────────────────────────────────────────────────────
export const seedDemo = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/demo/seed`, { method: 'POST' });
export const resetDemo = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/demo/reset`, { method: 'POST' });
export const runFullAnalysis = (id: string) =>
  request<any>(`/api/v1/businesses/${id}/demo/run-analysis`, { method: 'POST' });

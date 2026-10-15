/**
 * NagrikSaarathi API Client.
 * Connects directly to the existing FastAPI backend.
 * Uses VITE_API_BASE_URL (defaults to http://127.0.0.1:8000/api).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;
  const token = sessionStorage.getItem('nagrik_token') || localStorage.getItem('nagrik_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || errorDetail;
      } catch (_) {
        // ignore JSON parse failure on non-JSON response
      }
      const err = new Error(errorDetail);
      err.status = response.status;
      throw err;
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error on [${options.method || 'GET'}] ${url}:`, error.message);
    throw error;
  }
}

// ── Endpoints ──────────────────────────────────────────────────────────

export const api = {
  // System & Reference
  getHealth: () => request('/health'),
  getLanguages: (enabledOnly = true) => request(`/languages?enabled_only=${enabledOnly}`),
  getLanguage: (code) => request(`/languages/${code}`),
  getSchemes: (params = {}) => {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.level) query.append('level', params.level);
    if (params.state) query.append('state', params.state);
    if (params.category) query.append('category', params.category);
    if (params.capability) query.append('capability', params.capability);
    if (params.formStatus) query.append('form_status', params.formStatus);
    if (params.page !== undefined && params.page !== null) query.append('page', params.page);
    if (params.pageSize) query.append('page_size', params.pageSize);
    if (params.includeCandidates) query.append('include_candidates', 'true');
    const queryString = query.toString();
    return request(`/schemes${queryString ? `?${queryString}` : ''}`);
  },
  getSchemeDetail: (schemeId, lang = null) => request(`/schemes/${schemeId}${lang ? `?lang=${encodeURIComponent(lang)}` : ''}`),
  getSchemeBenefits: (schemeId, lang = 'en') => request(`/schemes/${schemeId}/benefits?lang=${encodeURIComponent(lang)}`),
  getSchemeGuidance: (schemeId, lang = 'hi') => request(`/schemes/${schemeId}/guidance?lang=${lang}`),
  getSchemeFields: (schemeId) => request(`/schemes/${schemeId}/fields`),
  getSchemeCoverageAudit: () => request('/schemes/coverage-audit'),

  // Voice & Speech Services (Layer B Cloud TTS / ASR)
  speakText: (payload) =>
    request('/voice/speak', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  transcribeAudio: (formData) => {
    const token = sessionStorage.getItem('nagrik_jwt') || localStorage.getItem('nagrik_jwt');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    return fetch('/api/voice/transcribe', {
      method: 'POST',
      headers,
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return res.json();
    });
  },
  submitCandidateScheme: (payload) =>
    request('/schemes/candidate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  extractFormSchema: (payload) =>
    request('/schemes/extract-form', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  adminBulkImport: (items, sourceName = 'ADMIN_CATALOGUE_UPLOAD') =>
    request(`/schemes/admin/import?source_name=${encodeURIComponent(sourceName)}`, {
      method: 'POST',
      body: JSON.stringify(items),
    }),
  seedNationwideSchemes: () =>
    request('/schemes/seed-nationwide', {
      method: 'POST',
    }),

  // Citizen Assisted Sessions
  createSession: (payload) =>
    request('/sessions', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  recordSessionEvent: (sessionId, payload) =>
    request(`/sessions/${sessionId}/events`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateSessionStatus: (sessionId, status) =>
    request(`/sessions/${sessionId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // Multilingual Guidance
  explainField: (payload) =>
    request('/assist/explain', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  validateField: (payload) =>
    request('/assist/validate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Dashboard Analytics
  getDashboardSummary: (includeDemo = true, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/summary?include_demo=${includeDemo}`, { headers });
  },

  getDashboardBarriers: (includeDemo = true, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/barriers?include_demo=${includeDemo}`, { headers });
  },

  getDashboardLanguages: (includeDemo = true, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/languages?include_demo=${includeDemo}`, { headers });
  },

  getDashboardFields: (includeDemo = true, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/fields?include_demo=${includeDemo}`, { headers });
  },

  getDashboardRecovery: (includeDemo = true, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/recovery?include_demo=${includeDemo}`, { headers });
  },

  getDashboardTranslationQuality: (adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request('/dashboard/translation-quality', { headers });
  },

  getDashboardCoverage: (adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request('/dashboard/coverage', { headers });
  },

  getMissingSchemeRadar: (adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request('/dashboard/missing-radar', { headers });
  },

  findBenefitCombinations: (profile) =>
    request('/schemes/benefit-combinations', {
      method: 'POST',
      body: JSON.stringify(profile),
    }),

  // Authentication
  login: (payload) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  logout: () =>
    request('/auth/logout', {
      method: 'POST',
    }),

  getMe: () => request('/auth/me'),

  getDemoCredentials: () => request('/auth/demo-credentials'),

  register: (payload) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  resetPassword: (payload) =>
    request('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateProfile: (payload) =>
    request('/auth/profile', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  // Scheme Requests (Citizen & Admin)
  submitSchemeRequest: (payload) =>
    request('/schemes/requests', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  trackSchemeRequest: (trackingId) => request(`/schemes/requests/track/${encodeURIComponent(trackingId)}`),

  getMySchemeRequests: (contact = null) =>
    request(`/schemes/requests/my${contact ? `?contact=${encodeURIComponent(contact)}` : ''}`),

  getAdminSchemeRequests: (statusFilter = null, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/scheme-requests${statusFilter ? `?status_filter=${encodeURIComponent(statusFilter)}` : ''}`, { headers });
  },

  updateAdminSchemeRequest: (id, payload, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/scheme-requests/${id}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(payload),
    });
  },

  publishSchemeRequest: (id, payload, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/scheme-requests/${id}/publish`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
  },

  // Help & Support Tickets
  createHelpTicket: (payload) =>
    request('/help/tickets', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  trackHelpTicket: (ticketNumber, contact = null) =>
    request(`/help/tickets/track/${encodeURIComponent(ticketNumber)}${contact ? `?contact=${encodeURIComponent(contact)}` : ''}`),

  getMyHelpTickets: (contact = null) =>
    request(`/help/tickets/my${contact ? `?contact=${encodeURIComponent(contact)}` : ''}`),

  submitTicketFeedback: (ticketNumber, feedback) =>
    request(`/help/tickets/${encodeURIComponent(ticketNumber)}/feedback`, {
      method: 'POST',
      body: JSON.stringify(feedback),
    }),

  getAdminHelpTickets: (categoryFilter = null, statusFilter = null, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    const params = new URLSearchParams();
    if (categoryFilter) params.append('category_filter', categoryFilter);
    if (statusFilter) params.append('status_filter', statusFilter);
    const qs = params.toString();
    return request(`/dashboard/help-tickets${qs ? `?${qs}` : ''}`, { headers });
  },

  updateAdminHelpTicket: (id, payload, adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request(`/dashboard/help-tickets/${id}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(payload),
    });
  },

  // Translation Audit
  getTranslationAudit: (adminKey = null) => {
    const headers = adminKey ? { 'X-Admin-API-Key': adminKey } : {};
    return request('/dashboard/translation-audit', { headers });
  },

  // ── Official Invitations & Gov SSO ──────────────────────────────────────
  getInvitationDetails: (token) => request(`/auth/invitation/${encodeURIComponent(token)}`),
  activateInvitation: (payload) =>
    request('/auth/invitation/activate', { method: 'POST', body: JSON.stringify(payload) }),
  getGovSSOConfig: () => request('/auth/gov-sso/config'),
  govSSOCallback: (payload) =>
    request('/auth/gov-sso/callback', { method: 'POST', body: JSON.stringify(payload) }),

  // ── Department Official API ──────────────────────────────────────────────
  getDepartmentsList: (governmentLevel = null) =>
    request(`/department/list${governmentLevel ? `?government_level=${encodeURIComponent(governmentLevel)}` : ''}`),
  getDepartmentSchemes: () => request('/department/my-schemes'),
  getDepartmentStats: () => request('/department/stats'),
  getDepartmentProposals: (statusFilter = null, typeFilter = null) => {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);
    if (typeFilter) params.append('proposal_type', typeFilter);
    const qs = params.toString();
    return request(`/department/proposals${qs ? `?${qs}` : ''}`);
  },
  createSchemeProposal: (payload) =>
    request('/department/proposals', { method: 'POST', body: JSON.stringify(payload) }),
  getProposalDetail: (proposalId) => request(`/department/proposals/${proposalId}`),
  updateSchemeProposal: (proposalId, payload) =>
    request(`/department/proposals/${proposalId}`, { method: 'PATCH', body: JSON.stringify(payload) }),

  // Radar (Department)
  analyzeRadarChanges: (payload) =>
    request('/department/radar/analyze', { method: 'POST', body: JSON.stringify(payload) }),
  submitRadarChange: (payload) =>
    request('/department/radar/submit', { method: 'POST', body: JSON.stringify(payload) }),
  getDepartmentRadar: (status = null) =>
    request(`/department/radar${status ? `?status=${encodeURIComponent(status)}` : ''}`),

  // Heatmap (Department)
  getDepartmentHeatmap: (params = {}) => {
    const q = new URLSearchParams();
    if (params.scheme_id) q.append('scheme_id', params.scheme_id);
    if (params.form_step) q.append('form_step', params.form_step);
    if (params.language) q.append('language', params.language);
    if (params.days) q.append('days', params.days);
    const qs = q.toString();
    return request(`/department/heatmap${qs ? `?${qs}` : ''}`);
  },

  // Evidence (Department)
  getDepartmentEvidence: (params = {}) => {
    const q = new URLSearchParams();
    if (params.scheme_id) q.append('scheme_id', params.scheme_id);
    if (params.verification_status) q.append('verification_status', params.verification_status);
    const qs = q.toString();
    return request(`/department/evidence${qs ? `?${qs}` : ''}`);
  },
  submitDepartmentEvidence: (payload) =>
    request('/department/evidence', { method: 'POST', body: JSON.stringify(payload) }),
  getDepartmentEvidenceSummary: () => request('/department/evidence/summary'),

  // Translation Drift (Department)
  getDepartmentTranslationDrift: (status = null) =>
    request(`/department/translation-drift${status ? `?status=${encodeURIComponent(status)}` : ''}`),

  // ── Principal Administrator API ──────────────────────────────────────────
  getAdminProposals: (statusFilter = null, departmentName = null, proposalType = null) => {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);
    if (departmentName) params.append('department_name', departmentName);
    if (proposalType) params.append('proposal_type', proposalType);
    const qs = params.toString();
    return request(`/admin/proposals${qs ? `?${qs}` : ''}`);
  },
  getAdminProposalDetail: (proposalId) => request(`/admin/proposals/${proposalId}`),
  reviewSchemeProposal: (proposalId, payload) =>
    request(`/admin/proposals/${proposalId}/review`, { method: 'POST', body: JSON.stringify(payload) }),
  getAdminOfficials: (params = {}) => {
    const q = new URLSearchParams();
    if (params.search) q.append('search', params.search);
    if (params.department) q.append('department', params.department);
    if (params.state_scope) q.append('state_scope', params.state_scope);
    if (params.is_active !== undefined && params.is_active !== null) q.append('is_active', params.is_active);
    const qs = q.toString();
    return request(`/admin/officials${qs ? `?${qs}` : ''}`);
  },
  createOfficialAccount: (payload) =>
    request('/admin/officials', { method: 'POST', body: JSON.stringify(payload) }),
  updateOfficialAccount: (officialId, payload) =>
    request(`/admin/officials/${officialId}`, { method: 'PATCH', body: JSON.stringify(payload) }),
  getAdminGovernanceStats: () => request('/admin/stats'),
  getAdminAuditLogs: (params = {}) => {
    const q = new URLSearchParams();
    if (params.action) q.append('action', params.action);
    if (params.resource_type) q.append('resource_type', params.resource_type);
    if (params.department) q.append('department', params.department);
    if (params.limit) q.append('limit', params.limit);
    if (params.offset) q.append('offset', params.offset);
    const qs = q.toString();
    return request(`/admin/audit-logs${qs ? `?${qs}` : ''}`);
  },

  // Admin Invitations & Official Security Management
  getAdminInvitations: (status = null) =>
    request(`/admin/official-invitations${status ? `?status=${encodeURIComponent(status)}` : ''}`),
  createAdminInvitation: (payload) =>
    request('/admin/official-invitations', { method: 'POST', body: JSON.stringify(payload) }),
  reviewAdminInvitation: (invitationId, payload) =>
    request(`/admin/official-invitations/${invitationId}/review`, { method: 'POST', body: JSON.stringify(payload) }),
  revokeAdminInvitation: (invitationId, reason) =>
    request(`/admin/official-invitations/${invitationId}/revoke`, { method: 'POST', body: JSON.stringify({ reason }) }),
  suspendOfficial: (officialId, reason) =>
    request(`/admin/officials/${officialId}/suspend`, { method: 'POST', body: JSON.stringify({ reason }) }),
  activateOfficial: (officialId) =>
    request(`/admin/officials/${officialId}/activate`, { method: 'POST' }),

  // Admin Radar
  getAdminRadar: (status = null) =>
    request(`/admin/radar${status ? `?status=${encodeURIComponent(status)}` : ''}`),
  getAdminRadarDetail: (radarId) => request(`/admin/radar/${radarId}`),
  reviewAdminRadar: (radarId, payload) =>
    request(`/admin/radar/${radarId}/review`, { method: 'POST', body: JSON.stringify(payload) }),

  // Admin Heatmap
  getAdminHeatmap: (params = {}) => {
    const q = new URLSearchParams();
    if (params.department) q.append('department', params.department);
    if (params.scheme_id) q.append('scheme_id', params.scheme_id);
    if (params.form_step) q.append('form_step', params.form_step);
    if (params.language) q.append('language', params.language);
    if (params.days) q.append('days', params.days);
    const qs = q.toString();
    return request(`/admin/heatmap${qs ? `?${qs}` : ''}`);
  },

  // Admin Evidence
  getAdminEvidence: (params = {}) => {
    const q = new URLSearchParams();
    if (params.department) q.append('department', params.department);
    if (params.scheme_id) q.append('scheme_id', params.scheme_id);
    if (params.verification_status) q.append('verification_status', params.verification_status);
    const qs = q.toString();
    return request(`/admin/evidence${qs ? `?${qs}` : ''}`);
  },
  verifyFieldEvidence: (evidenceId, payload) =>
    request(`/admin/evidence/${evidenceId}/verify`, { method: 'POST', body: JSON.stringify(payload) }),

  // Admin Translation Drift
  getAdminTranslationDrift: (status = null) =>
    request(`/admin/translation-drift${status ? `?status=${encodeURIComponent(status)}` : ''}`),
  getAdminTranslationDriftComparison: (alertId) =>
    request(`/admin/translation-drift/${alertId}/compare`),
  reviewAdminTranslationDrift: (alertId, payload) =>
    request(`/admin/translation-drift/${alertId}/review`, { method: 'POST', body: JSON.stringify(payload) }),
};


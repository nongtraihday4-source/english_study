/**
 * Support Portal API — all endpoints for support staff.
 * Base: /api/v1/support/
 */
import api from '@/api/client.js'

export const supportApi = {
  // Dashboard
  getDashboard: () => api.get('/support/dashboard/'),

  // Public request triage inbox (support/admin)
  getPublicRequests: (params = {}) => api.get('/support/public-requests/', { params }),
  convertPublicRequest: (id, data) => api.post(`/support/public-requests/${id}/convert/`, data),

  // User lookup (read-only)
  searchUsers: (params = {}) => api.get('/support/users/', { params }),
  getUserDetail: (id) => api.get(`/support/users/${id}/`),
  resetUserPassword: (id) => api.post(`/support/users/${id}/reset-password/`),

  // Tickets
  getTickets: (params = {}) => api.get('/support/tickets/', { params }),
  getTicket: (id) => api.get(`/support/tickets/${id}/`),
  getTicketDetail: (id) => api.get(`/support/tickets/${id}/`),
  createTicket: (data) => api.post('/support/tickets/', data),
  updateTicket: (id, data) => api.patch(`/support/tickets/${id}/`, data),
  addTicketMessage: (id, data) => api.post(`/support/tickets/${id}/messages/`, data),
  assignTicket: (id, data = {}) => api.post(`/support/tickets/${id}/assign/`, data),

  // Payments (read-only)
  getTransactions: (params = {}) => api.get('/support/transactions/', { params }),
  getSubscriptions: (params = {}) => api.get('/support/subscriptions/', { params }),

  // Coupons (read-only)
  getCoupons: (params = {}) => api.get('/support/coupons/', { params }),

  // Refund Requests
  getRefundRequests: (params = {}) => api.get('/support/refund-requests/', { params }),
  getRefundRequest: (id) => api.get(`/support/refund-requests/${id}/`),
  createRefundRequest: (data) => api.post('/support/refund-requests/', data),
}

export const publicSupportApi = {
  submitRequest: (data) => api.post('/support/public/requests/', data),
}

// Password reset confirm (public — no auth required, uses auth base URL)
export const authPasswordResetConfirm = (data) =>
  api.post('/auth/auth/password-reset/confirm/', data)

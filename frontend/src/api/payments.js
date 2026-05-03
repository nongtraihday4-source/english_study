/**
 * api/payments.js — Payments API calls
 */
import api from './client.js'

export const paymentsApi = {
  /** GET /payments/plans/ — public */
  getPlans: () => api.get('/payments/plans/'),

  /** POST /payments/coupons/validate/ — requires auth */
  validateCoupon: (code, planId) =>
    api.post('/payments/coupons/validate/', { code, plan_id: planId }),

  /** POST /payments/checkout/ — requires auth */
  checkout: (planId, gateway, couponCode = null) =>
    api.post('/payments/checkout/', {
      plan_id: planId,
      gateway,
      ...(couponCode ? { coupon_code: couponCode } : {}),
    }),

  /** GET /payments/transactions/ — requires auth */
  getTransactions: () => api.get('/payments/transactions/'),
}

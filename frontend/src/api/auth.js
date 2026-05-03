import api from './client.js'

export const authApi = {
  login: (email, password, otpCode) =>
    api.post('/auth/auth/login/', { email, password, otp_code: otpCode }),

  register: (data) =>
    api.post('/auth/auth/register/', data),

  logout: () =>
    api.post('/auth/auth/logout/'),

  refreshToken: () =>
    api.post('/auth/auth/token/refresh/'),
    
  // 2FA Endpoints
  generate2FA: () => api.post('/auth/auth/2fa/generate/'),
  verify2FA: (otpCode) => api.post('/auth/auth/2fa/verify/', { otp_code: otpCode }),
  disable2FA: (password) => api.post('/auth/auth/2fa/disable/', { password }),

  getMe: () =>
    api.get('/auth/me/'),

  updateMe: (data) =>
    api.patch('/auth/me/', data),

  changePassword: (oldPassword, newPassword) =>
    api.patch('/auth/me/password/', { old_password: oldPassword, new_password: newPassword }),

  getDevices: () =>
    api.get('/auth/me/devices/'),

  revokeDevice: (id) =>
    api.delete(`/auth/me/devices/${id}/`),
}

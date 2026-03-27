import api from './client.js'

export const usersApi = {
  // GET  /api/v1/auth/me/settings/  (users app is mounted at /auth/ prefix)
  getSettings: () => api.get('/auth/me/settings/'),
  // PATCH /api/v1/auth/me/settings/  — partial update
  updateSettings: (data) => api.patch('/auth/me/settings/', data),
}

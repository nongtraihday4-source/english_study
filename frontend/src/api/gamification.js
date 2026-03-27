import api from './client.js'

export const gamificationApi = {
  getAchievements: () => api.get('/gamification/achievements/'),
  getMyAchievements: () => api.get('/gamification/my-achievements/'),
  getXPLog: () => api.get('/gamification/xp-log/'),
  getLeaderboard: (params = {}) =>
    api.get('/gamification/leaderboard/', { params }),
  getCertificates: () => api.get('/gamification/certificates/'),
}

export const getLeaderboard = (params) => gamificationApi.getLeaderboard(params)

export const notificationsApi = {
  getAll: () => api.get('/notifications/'),
  markRead: (id) => api.patch(`/notifications/${id}/read/`),
}

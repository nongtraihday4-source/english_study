import api from './client.js'

export const adminApi = {
  // ── Dashboard ──────────────────────────────────────────────────
  getDashboard: () => api.get('/admin-portal/dashboard/'),

  // ── Users (existing endpoints in users app) ────────────────────
  getUsers: (params = {}) => api.get('/auth/admin/users/', { params }),
  updateUser: (pk, data) => api.patch(`/auth/admin/users/${pk}/`, data),
  banUser: (pk) => api.post(`/admin-portal/users/${pk}/ban/`),

  // ── Courses ────────────────────────────────────────────────────
  getCourses: (params = {}) => api.get('/admin-portal/courses/', { params }),
  createCourse: (data) => api.post('/admin-portal/courses/', data),
  updateCourse: (pk, data) => api.patch(`/admin-portal/courses/${pk}/`, data),
  deleteCourse: (pk) => api.delete(`/admin-portal/courses/${pk}/`),

  // ── Chapters & Lessons ─────────────────────────────────────────
  getChapters: (coursePk) => api.get(`/admin-portal/courses/${coursePk}/chapters/`),
  createChapter: (coursePk, data) => api.post(`/admin-portal/courses/${coursePk}/chapters/`, data),
  updateChapter: (coursePk, pk, data) => api.patch(`/admin-portal/courses/${coursePk}/chapters/${pk}/`, data),
  deleteChapter: (coursePk, pk) => api.delete(`/admin-portal/courses/${coursePk}/chapters/${pk}/`),

  getLessons: (coursePk, chapterPk) =>
    api.get(`/admin-portal/courses/${coursePk}/chapters/${chapterPk}/lessons/`),
  createLesson: (coursePk, chapterPk, data) =>
    api.post(`/admin-portal/courses/${coursePk}/chapters/${chapterPk}/lessons/`, data),
  updateLesson: (pk, data) => api.patch(`/admin-portal/lessons/${pk}/`, data),
  deleteLesson: (pk) => api.delete(`/admin-portal/lessons/${pk}/`),

  // ── Lesson-Exercise binding ────────────────────────────────────────────
  getLessonExercises: (lessonPk) => api.get(`/admin-portal/lessons/${lessonPk}/exercises/`),
  bindExercise: (lessonPk, data) => api.post(`/admin-portal/lessons/${lessonPk}/exercises/`, data),
  updateBinding: (lessonPk, pk, data) => api.patch(`/admin-portal/lessons/${lessonPk}/exercises/${pk}/`, data),
  unbindExercise: (lessonPk, pk) => api.delete(`/admin-portal/lessons/${lessonPk}/exercises/${pk}/`),

  // ── Exercise CRUD (typed) ─────────────────────────────────────────────
  getExercisesByType: (type, params = {}) => api.get(`/admin-portal/exercises/${type}/`, { params }),
  createExercise: (type, data) => api.post(`/admin-portal/exercises/${type}/`, data),
  updateExercise: (type, pk, data) => api.patch(`/admin-portal/exercises/${type}/${pk}/`, data),
  deleteExercise: (type, pk) => api.delete(`/admin-portal/exercises/${type}/${pk}/`),

  // ── Grammar admin CRUD ────────────────────────────────────────────────
  getGrammarTopics: (params = {}) => api.get('/admin-portal/grammar/topics/', { params }),
  createGrammarTopic: (data) => api.post('/admin-portal/grammar/topics/', data),
  updateGrammarTopic: (pk, data) => api.patch(`/admin-portal/grammar/topics/${pk}/`, data),
  deleteGrammarTopic: (pk) => api.delete(`/admin-portal/grammar/topics/${pk}/`),
  getGrammarRules: (topicPk) => api.get(`/admin-portal/grammar/topics/${topicPk}/rules/`),
  createGrammarRule: (topicPk, data) => api.post(`/admin-portal/grammar/topics/${topicPk}/rules/`, data),
  updateGrammarRule: (topicPk, pk, data) => api.patch(`/admin-portal/grammar/topics/${topicPk}/rules/${pk}/`, data),
  deleteGrammarRule: (topicPk, pk) => api.delete(`/admin-portal/grammar/topics/${topicPk}/rules/${pk}/`),
  getGrammarExamples: (rulePk) => api.get(`/admin-portal/grammar/rules/${rulePk}/examples/`),
  createGrammarExample: (rulePk, data) => api.post(`/admin-portal/grammar/rules/${rulePk}/examples/`, data),
  updateGrammarExample: (rulePk, pk, data) => api.patch(`/admin-portal/grammar/rules/${rulePk}/examples/${pk}/`, data),
  deleteGrammarExample: (rulePk, pk) => api.delete(`/admin-portal/grammar/rules/${rulePk}/examples/${pk}/`),

  // ── CEFR Levels (for form dropdowns) ──────────────────────────
  getCEFRLevels: () => api.get('/admin-portal/cefr-levels/'),

  // ── Plans ──────────────────────────────────────────────────────
  getPlans: (params = {}) => api.get('/admin-portal/plans/', { params }),
  createPlan: (data) => api.post('/admin-portal/plans/', data),
  updatePlan: (pk, data) => api.patch(`/admin-portal/plans/${pk}/`, data),
  deletePlan: (pk) => api.delete(`/admin-portal/plans/${pk}/`),

  // ── Coupons ────────────────────────────────────────────────────
  getCoupons: (params = {}) => api.get('/admin-portal/coupons/', { params }),
  createCoupon: (data) => api.post('/admin-portal/coupons/', data),
  updateCoupon: (pk, data) => api.patch(`/admin-portal/coupons/${pk}/`, data),
  deleteCoupon: (pk) => api.delete(`/admin-portal/coupons/${pk}/`),

  // ── Transactions ───────────────────────────────────────────────
  getTransactions: (params = {}) => api.get('/admin-portal/transactions/', { params }),

  // ── Subscriptions ──────────────────────────────────────────────
  getSubscriptions: (params = {}) => api.get('/admin-portal/subscriptions/', { params }),
  extendSubscription: (pk, days) => api.post(`/admin-portal/subscriptions/${pk}/extend/`, { days }),

  // ── Exam Sets ──────────────────────────────────────────────────
  getExamSets: (params = {}) => api.get('/admin-portal/exam-sets/', { params }),
  createExamSet: (data) => api.post('/admin-portal/exam-sets/', data),
  updateExamSet: (pk, data) => api.patch(`/admin-portal/exam-sets/${pk}/`, data),
  deleteExamSet: (pk) => api.delete(`/admin-portal/exam-sets/${pk}/`),

  // ── Exercises (legacy query-param list, kept for backward compat) ─────
  getExercises: (params = {}) => api.get('/admin-portal/exercises/', { params }),

  // ── AI Grading ─────────────────────────────────────────────────
  getGradingStats: () => api.get('/admin-portal/grading/stats/'),
  getGradingJobs: (params = {}) => api.get('/admin-portal/grading/jobs/', { params }),
  retryGradingJob: (pk) => api.post(`/admin-portal/grading/jobs/${pk}/retry/`),
  getSpeakingSubmissions: (params = {}) => api.get('/admin-portal/grading/submissions/speaking/', { params }),
  getWritingSubmissions: (params = {}) => api.get('/admin-portal/grading/submissions/writing/', { params }),

  // ── Achievements ───────────────────────────────────────────────
  getAchievements: (params = {}) => api.get('/admin-portal/achievements/', { params }),
  createAchievement: (data) => api.post('/admin-portal/achievements/', data),
  updateAchievement: (pk, data) => api.patch(`/admin-portal/achievements/${pk}/`, data),
  deleteAchievement: (pk) => api.delete(`/admin-portal/achievements/${pk}/`),

  // ── Certificates ───────────────────────────────────────────────
  getCertificates: (params = {}) => api.get('/admin-portal/certificates/', { params }),

  // ── XP Log ────────────────────────────────────────────────────
  getXPLog: (params = {}) => api.get('/admin-portal/xp-log/', { params }),
  grantXP: (data) => api.post('/admin-portal/xp-log/grant/', data),

  // ── Notification Templates ─────────────────────────────────────
  getNotificationTemplates: () => api.get('/admin-portal/notification-templates/'),
  updateNotificationTemplate: (notifType, data) =>
    api.patch(`/admin-portal/notification-templates/${notifType}/`, data),

  // ── Broadcast / History ────────────────────────────────────────
  broadcastNotification: (data) => api.post('/admin-portal/notifications/broadcast/', data),
  getNotificationHistory: (params = {}) => api.get('/admin-portal/notifications/history/', { params }),

  // ── Staff RBAC ────────────────────────────────────────────────
  getStaffPermissions: (pk) => api.get(`/admin-portal/staff/${pk}/permissions/`),
  updateStaffPermissions: (pk, data) => api.put(`/admin-portal/staff/${pk}/permissions/`, data),

  // ── Audit Log ─────────────────────────────────────────────────
  getAuditLog: (params = {}) => api.get('/admin-portal/audit-log/', { params }),
  exportAuditLog: (params = {}) => api.get('/admin-portal/audit-log/export/', { params, responseType: 'blob' }),

  // ── Refund Requests ──────────────────────────────────────────
  getRefundRequests: (params = {}) => api.get('/admin-portal/refund-requests/', { params }),
  reviewRefund: (pk, data) => api.post(`/admin-portal/refund-requests/${pk}/review/`, data),

  // ── System Settings ───────────────────────────────────────────
  getSettings: (params = {}) => api.get('/admin-portal/settings/', { params }),
  getSetting: (key) => api.get(`/admin-portal/settings/${key}/`),
  updateSetting: (key, value) => api.patch(`/admin-portal/settings/${key}/`, { value }),
}


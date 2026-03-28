import api from './client.js'

export const teacherApi = {
  // Dashboard stats
  getDashboard: () => api.get('/teacher/dashboard/'),

  // Grading queue: status=pending|completed|all, type=speaking|writing|all, search, sort
  getGradingQueue: (params = {}) => api.get('/teacher/grading-queue/', { params }),

  // Grade a speaking submission
  gradeSpeaking: (pk, payload) => api.post(`/teacher/grade/speaking/${pk}/`, payload),

  // Grade a writing submission
  gradeWriting: (pk, payload) => api.post(`/teacher/grade/writing/${pk}/`, payload),

  // List all active courses with student counts
  getClasses: () => api.get('/teacher/classes/'),

  // Get enrolled students + progress for a course
  getClassStudents: (id) => api.get(`/teacher/classes/${id}/students/`),
}

import api from './client.js'

export const progressApi = {
  getDashboard: () =>
    api.get('/progress/dashboard/'),

  enroll: (courseId) =>
    api.post('/progress/enroll/', { course_id: courseId }),

  enrollCourse: (courseId) =>
    api.post('/progress/enroll/', { course_id: courseId }),

  getLessonProgress: (lessonId) =>
    api.get(`/progress/lessons/${lessonId}/`),

  markLessonComplete: (lessonId, data = {}) =>
    api.post(`/progress/lessons/${lessonId}/complete/`, data),

  submitListening: (payload) =>
    api.post('/progress/submit/listening/', payload),

  submitReading: (payload) =>
    api.post('/progress/submit/reading/', payload),

  submitExam: (payload) =>
    api.post('/progress/submit/exam/', payload),

  submitSpeaking: (payload) =>
    api.post('/progress/submit/speaking/', payload),

  submitWriting: (payload) =>
    api.post('/progress/submit/writing/', payload),

  getSpeakingStatus: (id) =>
    api.get(`/progress/submissions/speaking/${id}/`),

  getWritingStatus: (id) =>
    api.get(`/progress/submissions/writing/${id}/`),

  getListeningResult: (id) =>
    api.get(`/progress/submissions/listening/${id}/`),

  getReadingResult: (id) =>
    api.get(`/progress/submissions/reading/${id}/`),

  getExamResult: (id) =>
    api.get(`/progress/submissions/exam/${id}/`),

  // Assignments given to current student
  getMyAssignments: () => api.get('/progress/my-assignments/'),
}

import api from './client.js'

export const exercisesApi = {
  getExams: (params = {}) =>
    api.get('/exercises/exams/', { params }),

  getExamDetail: (id) =>
    api.get(`/exercises/exams/${id}/`),
}

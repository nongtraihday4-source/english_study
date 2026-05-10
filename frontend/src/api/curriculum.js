import api from './client.js'

export const curriculumApi = {
  getCefrLevels: () =>
    api.get('/curriculum/cefr-levels/'),

  getCourses: (params = {}) =>
    api.get('/curriculum/courses/', { params }),

  getCourse: (id) =>
    api.get(`/curriculum/courses/${id}/`),

  getChapters: (courseId) =>
    api.get(`/curriculum/courses/${courseId}/chapters/`),

  getLessons: (courseId, chapterId) =>
    api.get(`/curriculum/courses/${courseId}/chapters/${chapterId}/lessons/`),

  getLesson: (id) =>
    api.get(`/curriculum/lessons/${id}/`),

  getLessonContent: (id) =>
    api.get(`/curriculum/lessons/${id}/content/`),

  enroll: (courseId) =>
    api.post('/progress/enroll/', { course_id: courseId }),

  markLessonComplete: (lessonId, data = {}) =>
    api.post(`/progress/lessons/${lessonId}/complete/`, data),

  getLessonProgress: (lessonId) =>
    api.get(`/progress/lessons/${lessonId}/`),
}

export const exercisesApi = {
  getListening: (id) =>
    api.get(`/exercises/listening/${id}/`),

  getSpeaking: (id) =>
    api.get(`/exercises/speaking/${id}/`),

  getReading: (id) =>
    api.get(`/exercises/reading/${id}/`),

  getWriting: (id) =>
    api.get(`/exercises/writing/${id}/`),
}

// Named convenience exports for views
export const getCourses = (params) => curriculumApi.getCourses(params)
export const getCourse = (id) => curriculumApi.getCourse(id)

export const grammarApi = {
  listChapters: (params = {}) =>
    api.get('/grammar/chapters/', { params }),

  listTopics: (params = {}) =>
    api.get('/grammar/', { params }),

  getTopic: (slug) =>
    api.get(`/grammar/${slug}/`),

  getProgress: () =>
    api.get('/grammar/progress/'),

  getTodayReviews: () => 
    api.get('/grammar/reviews/today/'),

  getQuizQuestions: (slug) =>
    api.get(`/grammar/${slug}/quiz/questions/`), 
  
  submitQuiz: (slug, data) =>
    api.post(`/grammar/${slug}/quiz/`, data),

  getTopicExercises: (slug) =>
    api.get(`/grammar/${slug}/exercises/`),
}

export const vocabularyApi = {
  listWords: (params = {}) =>
    api.get('/vocabulary/words/', { params }),

  getWord: (id) =>
    api.get(`/vocabulary/words/${id}/`),

  addToFlashcard: (wordId) =>
    api.post('/vocabulary/flashcards/add-word/', { word_id: wordId }),
}

export function getExercise(type, id) {
  switch (type) {
    case 'listening': return exercisesApi.getListening(id)
    case 'speaking': return exercisesApi.getSpeaking(id)
    case 'reading': return exercisesApi.getReading(id)
    case 'writing': return exercisesApi.getWriting(id)
    default: throw new Error(`Unknown exercise type: ${type}`)
  }
}



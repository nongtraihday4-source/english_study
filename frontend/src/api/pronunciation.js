import apiClient from './client.js'

export const pronunciationApi = {
  /** GET /pronunciation/stages/ — all stages with per-user progress */
  getStages: () => apiClient.get('/pronunciation/stages/'),

  /** GET /pronunciation/stages/:id/lessons/ */
  getStageLessons: (stageId) => apiClient.get(`/pronunciation/stages/${stageId}/lessons/`),

  /** GET /pronunciation/lessons/:id/ — lesson with full phoneme list */
  getLessonDetail: (lessonId) => apiClient.get(`/pronunciation/lessons/${lessonId}/`),

  /** GET /pronunciation/phonemes/ — full IPA chart grouped by type */
  getPhonemeChart: () => apiClient.get('/pronunciation/phonemes/'),

  /** GET /pronunciation/minimal-pairs/ */
  getMinimalPairs: () => apiClient.get('/pronunciation/minimal-pairs/'),

  /** GET /pronunciation/minimal-pairs/:id/ */
  getMinimalPairDetail: (id) => apiClient.get(`/pronunciation/minimal-pairs/${id}/`),

  /** GET /pronunciation/lessons/by-slug/:slug/ — lesson detail (with sections) */
  getLessonBySlug: (slug) => apiClient.get(`/pronunciation/lessons/by-slug/${slug}/`),

  /** POST /pronunciation/lessons/:id/complete/ — mark lesson complete with score */
  completeLesson: (lessonId, score) => apiClient.post(`/pronunciation/lessons/${lessonId}/complete/`, { score }),

  /** POST /pronunciation/tts/ — on-demand TTS audio generation */
  generateTTS: (text, voice) => apiClient.post('/pronunciation/tts/', { text, voice }),
}

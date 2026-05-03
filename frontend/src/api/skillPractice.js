import api from './client.js'

export const skillPracticeApi = {
  // ── Topics ─────────────────────────────────────────────────────────────────
  // Returns list of topics grouped with passage count + user completion
  // params: { level: 'B1' }
  getTopics: (params = {}) => api.get('/skill-practice/topics/', { params }),

  // ── Passages ───────────────────────────────────────────────────────────────
  // params: { topic_slug, level }
  getPassages: (params = {}) => api.get('/skill-practice/passages/', { params }),
  getPassage: (id) => api.get(`/skill-practice/passages/${id}/`),

  // ── Dictation ──────────────────────────────────────────────────────────────
  // payload: { sentence_index (null=full), user_input, time_spent_seconds }
  checkDictation: (passageId, payload) =>
    api.post(`/skill-practice/passages/${passageId}/dictation/check/`, payload),

  // ── Shadowing ──────────────────────────────────────────────────────────────
  // payload: { sentence_index (null=full), self_rating (1-5), time_spent_seconds }
  completeShadowing: (passageId, payload) =>
    api.post(`/skill-practice/passages/${passageId}/shadowing/complete/`, payload),

  // ── On-demand TTS fallback ─────────────────────────────────────────────────
  // Used when sentences_json[].audio_url is null
  getSentenceTTS: (passageId, sentenceIndex) =>
    api.get(`/skill-practice/passages/${passageId}/tts/${sentenceIndex}/`),

  // ── Progress ───────────────────────────────────────────────────────────────
  getProgressSummary: () => api.get('/skill-practice/progress/summary/'),
}

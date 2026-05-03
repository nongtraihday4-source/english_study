import api from './client.js'

export const vocabularyApi = {
  // ── Words ──────────────────────────────────────────────────────────────────
  listWords: (params = {}) => api.get('/vocabulary/words/', { params }),
  getWord: (id) => api.get(`/vocabulary/words/${id}/`),

  // Returns { word_id, in_decks: [{deck_id, deck_name, flashcard_id}] }
  getWordFlashcardStatus: (wordId) =>
    api.get(`/vocabulary/words/${wordId}/flashcard-status/`),

  // ── Flashcard Decks ────────────────────────────────────────────────────────
  getDecks: (params = {}) => api.get('/vocabulary/flashcard-decks/', { params }),
  createDeck: (payload) => api.post('/vocabulary/flashcard-decks/', payload),

  // ── Add/Remove word ─────────────────────────────────────────────────────────
  // deck_id optional — omit to add to "My Words"
  addWordToDeck: (wordId, deckId = null) =>
    api.post('/vocabulary/flashcards/add-word/', {
      word_id: wordId,
      ...(deckId ? { deck_id: deckId } : {}),
    }),
  // Accepts flashcard_id OR { word_id, deck_id }
  removeWordFromDeck: (flashcardIdOrPayload) => {
    const payload = typeof flashcardIdOrPayload === 'object'
      ? flashcardIdOrPayload
      : { flashcard_id: flashcardIdOrPayload }
    return api.post('/vocabulary/flashcards/remove-word/', payload)
  },

  // ── Study Session ──────────────────────────────────────────────────────────
  getStudyCards: (deckId, params = {}) => api.get(`/vocabulary/flashcard-decks/${deckId}/study/`, { params }),
  completeSession: (deckId, data) =>
    api.post(`/vocabulary/flashcard-decks/${deckId}/session-complete/`, data),

  // Returns { deck_id, history: [{date, total_cards, avg_accuracy}] } (14 days)
  getDeckHistory: (deckId) => api.get(`/vocabulary/flashcard-decks/${deckId}/history/`),

  // ── Quiz ───────────────────────────────────────────────────────────────────
  // Single-deck quick quiz
  getDeckQuiz: (deckId, params = {}) =>
    api.get(`/vocabulary/flashcard-decks/${deckId}/quiz/`, { params }),
  // Multi-deck comprehensive quiz
  generateQuiz: (payload) => api.post('/vocabulary/quiz/generate/', payload),

  // ── SM-2 Update ────────────────────────────────────────────────────────────
  // rating: 1=Quên, 2=Khó, 4=Nhớ, 5=Dễ  (backend SM-2: >=3 = correct)
  updateSM2: (flashcardId, rating) =>
    api.post('/vocabulary/flashcards/sm2/', { flashcard_id: flashcardId, rating }),

  // ── Deck Word Browser ──────────────────────────────────────────────────────
  // status: 'all' | 'learning' | 'mastered' (default: all)
  getDeckWords: (deckId, params = {}) =>
    api.get(`/vocabulary/flashcard-decks/${deckId}/words/`, { params }),
  toggleMastered: (deckId, wordId, isMastered) =>
    api.post(`/vocabulary/flashcard-decks/${deckId}/words/toggle-mastered/`, {
      word_id: wordId,
      is_mastered: isMastered,
    }),
}


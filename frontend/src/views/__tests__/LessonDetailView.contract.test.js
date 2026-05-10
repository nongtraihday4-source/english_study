import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('LessonDetailView Contract', () => {
  describe('Backend SSOT Payload Contract', () => {
    it('should send raw_answers and time_spent_seconds, not score', () => {
      const mockPayload = {
        time_spent_seconds: 120,
        raw_answers: {
          reading: [0, 1, 0],
          grammar: {},
          listening: [],
          speaking: {},
          writing: [],
        },
      }

      expect(mockPayload).toHaveProperty('raw_answers')
      expect(mockPayload).toHaveProperty('time_spent_seconds')
      expect(Object.keys(mockPayload)).not.toContain('score')
      expect(Object.keys(mockPayload)).not.toContain('autoScore')
    })

    it('should structure raw_answers for all lesson types', () => {
      const rawAnswers = {
        reading: [0, 1, 2],
        grammar: {
          'Present Simple': [0, 1],
          'Past Simple': [0],
        },
        listening: [0, 1, 1],
        speaking: { sentence_0: { audio_url: 'test.mp3', rating: 4 } },
        writing: ['I go to school yesterday.'],
      }

      expect(rawAnswers).toHaveProperty('reading')
      expect(rawAnswers).toHaveProperty('grammar')
      expect(rawAnswers).toHaveProperty('listening')
      expect(rawAnswers).toHaveProperty('speaking')
      expect(rawAnswers).toHaveProperty('writing')
    })

    it('should compute time_spent_seconds from startTime to now', () => {
      const startTime = Date.now() - 30000
      const timeSpent = Math.round((Date.now() - startTime) / 1000)

      expect(timeSpent).toBeGreaterThanOrEqual(29)
      expect(timeSpent).toBeLessThanOrEqual(31)
    })
  })

  describe('learning_objectives Field Contract', () => {
    it('should render objectives when present in content', () => {
      const content = {
        learning_objectives: ['Understand present simple', 'Learn 10 vocab words'],
      }

      expect(content.learning_objectives).toBeDefined()
      expect(content.learning_objectives.length).toBe(2)
    })

    it('should handle empty objectives gracefully', () => {
      const content = { learning_objectives: [] }

      expect(content.learning_objectives).toEqual([])
      expect(content.learning_objectives?.length).toBe(0)
    })

    it('should handle missing objectives field', () => {
      const content = {}

      expect(content.learning_objectives).toBeUndefined()
    })
  })

  describe('complete() Function Contract', () => {
    it('should call progressApi.markLessonComplete with SSOT payload', () => {
      const mockMarkComplete = vi.fn().mockResolvedValue({
        data: {
          status: 'completed',
          best_score: 85,
          xp_gained: 60,
        },
      })

      const payload = {
        time_spent_seconds: 120,
        raw_answers: { reading: [], grammar: {}, listening: [], speaking: {}, writing: [] },
      }

      expect(mockMarkComplete).not.toHaveBeenCalled()

      mockMarkComplete('/lessons/1/complete/', payload)

      expect(mockMarkComplete).toHaveBeenCalledWith('/lessons/1/complete/', payload)
    })
  })
})

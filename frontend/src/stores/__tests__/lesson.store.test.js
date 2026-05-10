import { setActivePinia, createPinia } from 'pinia'
import { useLessonStore } from '../lesson.js'
import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('useLessonStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should collect raw answers correctly', () => {
    const store = useLessonStore()
    store.recordAnswer('reading', 0, 1)
    store.recordAnswer('grammar', 'Present Simple', [0, 1])

    expect(store.rawAnswers.reading[0]).toBe(1)
    expect(store.rawAnswers.grammar['Present Simple']).toEqual([0, 1])
  })

  it('should generate Backend SSOT payload', () => {
    const store = useLessonStore()
    store.recordAnswer('listening', 0, 2)
    const payload = store.getPayload()

    expect(payload).toHaveProperty('time_spent_seconds')
    expect(payload.raw_answers.listening[0]).toBe(2)
    expect(payload).not.toHaveProperty('score')
  })

  it('should reset state correctly', () => {
    const store = useLessonStore()
    store.recordAnswer('reading', 0, 1)
    store.reset()

    expect(store.rawAnswers.reading).toEqual([])
    expect(store.rawAnswers.grammar).toEqual({})
  })

  it('should track start time', () => {
    const store = useLessonStore()
    const before = Date.now()
    const payload = store.getPayload()
    const after = Date.now()

    expect(payload.time_spent_seconds).toBeGreaterThanOrEqual(0)
    expect(payload.time_spent_seconds).toBeLessThanOrEqual(Math.round((after - before) / 1000) + 1)
  })

  it('should record speaking and writing answers', () => {
    const store = useLessonStore()
    store.recordAnswer('speaking', 'sentence_0', { audio_url: 'test.mp3', rating: 4 })
    store.recordAnswer('writing', 0, 'I went to the store.')

    expect(store.rawAnswers.speaking['sentence_0']).toEqual({ audio_url: 'test.mp3', rating: 4 })
    expect(store.rawAnswers.writing[0]).toBe('I went to the store.')
  })

  it('should not expose score in payload', () => {
    const store = useLessonStore()
    const payload = store.getPayload()

    expect(Object.keys(payload)).not.toContain('score')
    expect(Object.keys(payload)).not.toContain('autoScore')
  })

  it('should initialize with empty arrays and objects', () => {
    const store = useLessonStore()
    expect(store.rawAnswers.reading).toEqual([])
    expect(store.rawAnswers.grammar).toEqual({})
    expect(store.rawAnswers.listening).toEqual([])
    expect(store.rawAnswers.speaking).toEqual({})
    expect(store.rawAnswers.writing).toEqual([])
  })
})

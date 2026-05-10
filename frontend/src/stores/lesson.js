import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import api from '@/api/client.js'

export const useLessonStore = defineStore('lesson', () => {
  const rawAnswers = reactive({
    reading: [],
    grammar: {},
    listening: [],
    speaking: {},
    writing: [],
  })

  const startTime = ref(Date.now())
  const srsQueue = ref([])
  const srsLoading = ref(false)

  function recordAnswer(section, key, answer) {
    if (Array.isArray(rawAnswers[section])) {
      rawAnswers[section][key] = answer
    } else {
      rawAnswers[section][key] = answer
    }
  }

  function getPayload() {
    return {
      time_spent_seconds: Math.round((Date.now() - startTime.value) / 1000),
      raw_answers: { ...rawAnswers },
    }
  }

  function reset() {
    Object.keys(rawAnswers).forEach(k => {
      rawAnswers[k] = Array.isArray(rawAnswers[k]) ? [] : {}
    })
    startTime.value = Date.now()
  }

  async function fetchSRSQueue(limit = 10) {
    srsLoading.value = true
    try {
      const res = await api.get('/vocabulary/srs/queue/', { params: { limit } })
      srsQueue.value = res.data?.results || res.data || []
    } finally {
      srsLoading.value = false
    }
  }

  return {
    rawAnswers,
    startTime,
    srsQueue,
    srsLoading,
    recordAnswer,
    getPayload,
    reset,
    fetchSRSQueue,
  }
})

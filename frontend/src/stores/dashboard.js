import { defineStore } from 'pinia'
import { ref } from 'vue'
import { progressApi } from '@/api/progress.js'

export const useDashboardStore = defineStore('dashboard', () => {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastFetched = ref(null)
  const CACHE_TTL = 60_000  // 60s cache

  async function fetch(force = false) {
    if (!force && data.value && Date.now() - lastFetched.value < CACHE_TTL) return

    loading.value = true
    error.value = null
    try {
      const res = await progressApi.getDashboard()
      // VNNumberJSONRenderer wraps: { success: true, data: <payload> }
      data.value = res.data?.data ?? res.data
      lastFetched.value = Date.now()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Không thể tải dashboard.'
    } finally {
      loading.value = false
    }
  }

  function invalidate() {
    lastFetched.value = null
  }

  // Convenience computed-like getters (return raw values from data)
  function streak() { return data.value?.streak || null }
  function cumulativeScores() { return data.value?.cumulative_scores || [] }
  function enrolledCourses() { return data.value?.enrolled_courses || [] }
  function recentResults() { return data.value?.recent_results || [] }
  function totalXP() { return data.value?.total_xp || 0 }
  function totalXPDisplay() { return data.value?.total_xp_display || '0 XP' }

  return {
    data, loading, error,
    fetch, invalidate,
    streak, cumulativeScores, enrolledCourses, recentResults, totalXP, totalXPDisplay,
  }
})

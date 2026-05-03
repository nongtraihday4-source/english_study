import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notificationsApi } from '@/api/gamification.js'

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref([])
  const loading = ref(false)

  const unreadCount = () => items.value.filter(n => !n.is_read).length

  async function fetch() {
    loading.value = true
    try {
      const res = await notificationsApi.getAll()
      // VNNumberJSONRenderer wraps: { success: true, data: [...] }
      const d = res.data?.data ?? res.data
      items.value = Array.isArray(d) ? d : []
    } catch { /* ignore */ } finally {
      loading.value = false
    }
  }

  async function markRead(id) {
    try {
      await notificationsApi.markRead(id)
      const n = items.value.find(x => x.id === id)
      if (n) n.is_read = true
    } catch { /* ignore */ }
  }

  return { items, loading, unreadCount, fetch, markRead }
})

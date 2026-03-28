<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Cài đặt hệ thống</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Cấu hình toàn hệ thống theo từng danh mục</p>
    </div>

    <!-- Category filter -->
    <div class="flex flex-wrap gap-2">
      <button v-for="cat in categories" :key="cat.value" @click="activeCategory = cat.value"
        class="px-4 py-2 text-sm rounded-lg font-medium transition-all"
        :style="activeCategory === cat.value
          ? 'background-color:var(--color-primary-500);color:#fff'
          : 'background-color:var(--color-surface-02);color:var(--color-text-muted)'">
        {{ cat.label }}
      </button>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 5" :key="n" class="h-16 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
    </div>

    <div v-else class="space-y-3">
      <div v-for="s in filteredSettings" :key="s.key"
        class="rounded-2xl p-4 flex items-start gap-4" style="background-color:var(--color-surface-02)">
        <div class="flex-1 min-w-0">
          <div class="font-mono text-sm font-medium" style="color:var(--color-text-base)">{{ s.key }}</div>
          <div class="text-xs mt-0.5" style="color:var(--color-text-muted)">{{ s.description }}</div>
          <div class="text-xs mt-1" style="color:var(--color-text-muted)">Loại: {{ s.value_type }}</div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <template v-if="editing[s.key] !== undefined">
            <input v-if="s.value_type !== 'bool'" v-model="editing[s.key]"
              :type="s.value_type === 'int' ? 'number' : 'text'"
              class="input-sm w-36" />
            <select v-else v-model="editing[s.key]" class="input-sm">
              <option value="true">true</option>
              <option value="false">false</option>
            </select>
            <button @click="saveSetting(s)" :disabled="saving[s.key]"
              class="text-xs px-3 py-1.5 rounded-lg font-medium"
              style="background-color:var(--color-primary-500);color:#fff">
              {{ saving[s.key] ? '...' : 'Lưu' }}
            </button>
            <button @click="cancelEdit(s.key)" class="text-xs px-3 py-1.5 rounded-lg"
              style="background-color:var(--color-surface-03);color:var(--color-text-base)">Huỷ</button>
          </template>
          <template v-else>
            <span class="font-mono text-sm px-3 py-1.5 rounded-lg" style="background-color:var(--color-surface-03);color:var(--color-text-base)">
              {{ s.value }}
            </span>
            <button v-if="s.is_editable" @click="startEdit(s)"
              class="text-xs px-3 py-1.5 rounded-lg"
              style="background-color:var(--color-surface-03);color:var(--color-text-base)">Sửa</button>
            <span v-else class="text-xs" style="color:var(--color-text-muted)">Chỉ đọc</span>
          </template>
        </div>
      </div>
      <div v-if="filteredSettings.length === 0" class="text-center py-10 text-sm" style="color:var(--color-text-muted)">
        Không có cài đặt nào.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { adminApi } from '@/api/admin.js'

const categories = [
  { value: '', label: 'Tất cả' },
  { value: 'general', label: 'Chung' },
  { value: 'ai_grading', label: 'AI Grading' },
  { value: 'payment', label: 'Thanh toán' },
  { value: 'email', label: 'Email' },
  { value: 'security', label: 'Bảo mật' },
  { value: 'gamification', label: 'Gamification' },
]
const activeCategory = ref('')
const settings = ref([])
const loading = ref(false)
const editing = reactive({})
const saving = reactive({})

const filteredSettings = computed(() =>
  activeCategory.value ? settings.value.filter(s => s.category === activeCategory.value) : settings.value
)

onMounted(() => loadSettings())

async function loadSettings() {
  loading.value = true
  try { const r = await adminApi.getSettings(); settings.value = r.data.results ?? r.data }
  finally { loading.value = false }
}

function startEdit(s) { editing[s.key] = s.value }
function cancelEdit(key) { delete editing[key] }

async function saveSetting(s) {
  saving[s.key] = true
  try {
    await adminApi.updateSetting(s.key, editing[s.key])
    const idx = settings.value.findIndex(x => x.key === s.key)
    if (idx !== -1) settings.value[idx].value = String(editing[s.key])
    delete editing[s.key]
  } finally { saving[s.key] = false }
}
</script>

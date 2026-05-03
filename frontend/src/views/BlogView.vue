<template>
  <section class="min-h-[70vh] flex items-center justify-center py-20" style="background-color: var(--color-surface)">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 text-center">
      <!-- Decoration -->
      <div class="w-20 h-20 rounded-3xl flex items-center justify-center text-4xl mx-auto mb-8 shadow-lg"
           style="background: linear-gradient(135deg, var(--color-primary-50), var(--color-surface-02)); border: 2px solid var(--color-surface-04)">
        ✍️
      </div>

      <p class="text-xs font-bold uppercase tracking-widest mb-4" style="color: var(--color-primary-500)">Blog</p>

      <h1 class="text-4xl md:text-5xl font-black mb-6"
          style="font-family: var(--font-heading); color: var(--color-secondary); letter-spacing:-0.02em">
        Sắp ra mắt!
      </h1>

      <p class="text-base leading-relaxed mb-10 max-w-md mx-auto" style="color: var(--color-text-muted)">
        Chúng tôi đang chuẩn bị những bài viết hay về phương pháp học tiếng Anh, tips phát âm, từ vựng theo ngữ cảnh và nhiều hơn nữa.
      </p>

      <!-- Email subscribe -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center max-w-sm mx-auto mb-6">
        <input
          v-model="email"
          type="email"
          placeholder="Email của bạn..."
          class="flex-1 px-4 py-3 rounded-xl text-sm outline-none"
          style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
        />
        <button
          @click="subscribe"
          :disabled="subscribed"
          class="px-5 py-3 rounded-xl font-semibold text-sm text-white transition hover:opacity-90 disabled:opacity-60"
          style="background-color: var(--color-primary-500); white-space: nowrap"
        >{{ subscribed ? '✓ Đã đăng ký' : 'Thông báo tôi' }}</button>
      </div>
      <p class="text-xs" style="color: var(--color-text-soft)">Đăng ký để nhận thông báo khi blog ra mắt. Không spam.</p>

      <!-- Back -->
      <div class="mt-12">
        <RouterLink to="/" class="text-sm font-semibold transition hover:opacity-80"
                    style="color: var(--color-primary-500)">← Về trang chủ</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const email = ref('')
const subscribed = ref(false)

function subscribe() {
  if (!email.value) return
  subscribed.value = true
}
</script>

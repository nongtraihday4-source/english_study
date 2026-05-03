<template>
  <!-- Hero -->
  <section class="py-20 lg:py-28 relative overflow-hidden" style="background-color: var(--color-surface)">
    <div class="blob-about pointer-events-none" aria-hidden="true"></div>
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <p class="text-xs font-bold uppercase tracking-widest mb-4" style="color: var(--color-primary-500)">Về chúng tôi</p>
      <h1 class="text-4xl md:text-5xl font-black mb-6" style="font-family: var(--font-heading); color: var(--color-secondary); letter-spacing:-0.02em">
        Sứ mệnh của<br><span style="color: var(--color-primary-500)">English Study</span>
      </h1>
      <p class="text-lg leading-relaxed max-w-2xl mx-auto" style="color: var(--color-text-muted)">
        Chúng tôi tin rằng rào cản ngôn ngữ không nên cản trở cơ hội của bất kỳ ai. English Study được xây dựng để giúp người Việt học tiếng Anh thực chiến — không chỉ để thi, mà để sống, làm việc và kết nối với thế giới.
      </p>
    </div>
  </section>

  <!-- Story -->
  <section class="py-16 lg:py-20" style="background-color: var(--color-surface-02)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 grid lg:grid-cols-2 gap-12 items-center">
      <div>
        <p class="text-xs font-bold uppercase tracking-widest mb-3" style="color: var(--color-primary-500)">Câu chuyện</p>
        <h2 class="text-3xl font-black mb-5" style="font-family: var(--font-heading); color: var(--color-secondary)">
          Tại sao chúng tôi xây dựng nền tảng này?
        </h2>
        <div class="space-y-4 text-base leading-relaxed" style="color: var(--color-text-muted)">
          <p>Hàng triệu người Việt học tiếng Anh nhiều năm nhưng vẫn không dám mở miệng nói — không phải vì thiếu kiến thức, mà vì thiếu phương pháp đúng và môi trường luyện tập thực sự.</p>
          <p>Chúng tôi đã trải qua điều đó. Và chúng tôi quyết định thay đổi nó.</p>
          <p>English Study được xây dựng từ nền tảng khoa học về ngôn ngữ học, kết hợp với AI hiện đại — để mỗi bài học không chỉ truyền đạt kiến thức, mà còn xây dựng phản xạ ngôn ngữ thực sự.</p>
        </div>
      </div>
      <div class="rounded-2xl p-8 flex flex-col items-center justify-center min-h-64"
           style="background: linear-gradient(135deg, var(--color-primary-50), var(--color-surface-03)); border: 1px solid var(--color-surface-04)">
        <span class="text-7xl mb-4">🌏</span>
        <p class="font-bold text-lg text-center" style="color: var(--color-secondary); font-family: var(--font-heading)">
          "Phá rào cản ngôn ngữ,<br>mở ra cơ hội toàn cầu"
        </p>
      </div>
    </div>
  </section>

  <!-- Values -->
  <section class="py-16 lg:py-20" style="background-color: var(--color-surface)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <p class="text-xs font-bold uppercase tracking-widest mb-3" style="color: var(--color-primary-500)">Giá trị cốt lõi</p>
        <h2 class="text-3xl font-black" style="font-family: var(--font-heading); color: var(--color-secondary)">Chúng tôi tin vào điều gì</h2>
      </div>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="v in values" :key="v.title"
             class="rounded-2xl p-6"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <span class="text-3xl mb-3 block">{{ v.icon }}</span>
          <h3 class="font-bold mb-2" style="font-family: var(--font-heading); color: var(--color-secondary)">{{ v.title }}</h3>
          <p class="text-sm leading-relaxed" style="color: var(--color-text-muted)">{{ v.desc }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Method -->
  <section class="py-16 lg:py-20" style="background-color: var(--color-surface-02)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12">
        <p class="text-xs font-bold uppercase tracking-widest mb-3" style="color: var(--color-primary-500)">Phương pháp học</p>
        <h2 class="text-3xl font-black mb-4" style="font-family: var(--font-heading); color: var(--color-secondary)">
          Khoa học đằng sau English Study
        </h2>
        <p class="max-w-2xl mx-auto text-base" style="color: var(--color-text-muted)">
          Mỗi tính năng được thiết kế dựa trên nghiên cứu về nhận thức và học ngôn ngữ thứ hai (SLA).
        </p>
      </div>
      <div class="grid md:grid-cols-3 gap-6">
        <div v-for="m in methods" :key="m.title"
             class="rounded-2xl p-6 text-center border"
             style="background-color: var(--color-surface); border-color: var(--color-surface-04)">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl mx-auto mb-4"
               style="background-color: var(--color-primary-50)">{{ m.icon }}</div>
          <h3 class="font-bold mb-2" style="font-family: var(--font-heading); color: var(--color-secondary)">{{ m.title }}</h3>
          <p class="text-sm leading-relaxed" style="color: var(--color-text-muted)">{{ m.desc }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="py-16"
           style="background: linear-gradient(135deg, var(--color-secondary), #2a5880)">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <h2 class="text-3xl font-black text-white mb-4" style="font-family: var(--font-heading)">
        Cùng chúng tôi thay đổi<br>cách người Việt học tiếng Anh
      </h2>
      <p class="mb-8 text-base" style="color: rgba(255,255,255,0.8)">Tham gia ngay hôm nay — miễn phí, không cần thẻ tín dụng.</p>
      <RouterLink
        to="/register"
        class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-base transition hover:opacity-90"
        style="background-color: var(--color-primary-500); color: #fff; font-family: var(--font-heading); box-shadow: 0 8px 24px rgba(244,124,38,0.4)"
      >🚀 Bắt đầu miễn phí ngay</RouterLink>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'

const values = [
  { icon: '🎯', title: 'Thực chiến trước tiên', desc: 'Mọi bài học đều gắn với ngữ cảnh thực tế, không học ngữ pháp rời rạc. Học để dùng được ngay.' },
  { icon: '🤖', title: 'AI hỗ trợ, không thay thế', desc: 'AI giúp phản hồi nhanh và cá nhân hoá, nhưng người học là trung tâm của mọi trải nghiệm.' },
  { icon: '📈', title: 'Tiến bộ minh bạch', desc: 'Bạn luôn biết mình đang ở đâu, cần làm gì tiếp theo và còn bao xa đến mục tiêu.' },
  { icon: '🎮', title: 'Học vui, học lâu', desc: 'Gamification không phải để giải trí mà để xây dựng thói quen học bền vững qua thời gian.' },
  { icon: '🌍', title: 'Phù hợp người Việt', desc: 'Nội dung, phoneme và từ vựng được hiệu chỉnh dành riêng cho người học tiếng Việt.' },
  { icon: '🔓', title: 'Tiếp cận công bằng', desc: 'Gói miễn phí đủ để bắt đầu thực sự — không chỉ là teaser để bán gói trả phí.' },
]

const methods = [
  { icon: '🔤', title: 'Phoneme → Context', desc: 'Học từ âm cơ bản đến từ trong ngữ cảnh, không học rote parroting. Phản xạ ngôn ngữ được xây dựng tầng tầng.' },
  { icon: '🧠', title: 'Spaced Repetition (SM-2)', desc: 'Flashcard xuất hiện đúng lúc cần ôn lại theo thuật toán khoa học, tối ưu hoá ghi nhớ dài hạn.' },
  { icon: '💬', title: 'Comprehensible Input +1', desc: 'Nội dung bài tập luôn vừa đủ khó hơn trình độ hiện tại (i+1) để não vùng thoải mái và tiếp thu tốt nhất.' },
]
</script>

<style scoped>
.blob-about {
  position: absolute;
  width: 600px; height: 400px;
  background: radial-gradient(ellipse, rgba(244,124,38,0.12) 0%, transparent 70%);
  top: -100px; right: -150px;
  border-radius: 50%;
  filter: blur(60px);
}
</style>

<template>
  <div class="max-w-6xl mx-auto">

    <!-- ── TOP BAR ────────────────────────────────────────────────────────── -->
    <div class="flex items-center justify-between mb-5 gap-3">
      <div class="flex items-center gap-2 text-sm min-w-0" style="color: var(--color-text-muted)">
        <RouterLink to="/grammar" class="transition hover:opacity-80 flex-shrink-0"
                    style="color: var(--color-text-muted)">← Ngữ pháp</RouterLink>
        <span class="flex-shrink-0">/</span>
        <span class="truncate" style="color: var(--color-text-base)">{{ topic?.title || 'Đang tải...' }}</span>
      </div>
      <div class="flex items-center gap-2 flex-shrink-0">
        <RouterLink v-if="topic?.prev_topic"
                    :to="{ name: 'grammar-detail', params: { slug: topic.prev_topic.slug } }"
                    class="hidden sm:inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted); text-decoration: none">
          ← {{ truncate(topic.prev_topic.title, 18) }}
        </RouterLink>
        <RouterLink v-if="topic?.next_topic"
                    :to="{ name: 'grammar-detail', params: { slug: topic.next_topic.slug } }"
                    class="hidden sm:inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted); text-decoration: none">
          {{ truncate(topic.next_topic.title, 18) }} →
        </RouterLink>
        <!-- Mobile sidebar toggle -->
        <button
          @click="sidebarOpen = !sidebarOpen"
          class="lg:hidden flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition"
          :style="sidebarOpen
            ? 'background-color: color-mix(in srgb, var(--color-primary-500) 15%, transparent); border-color: var(--color-primary-500); color: var(--color-primary-400)'
            : 'background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-muted)'">
          📋 Mục lục
        </button>
      </div>
    </div>

    <!-- ── TWO-COLUMN LAYOUT ──────────────────────────────────────────────── -->
    <div class="lg:flex lg:gap-5 lg:items-start">

      <!-- ─── SIDEBAR: Topic Navigator ──────────────────────────────────── -->
      <aside
        class="lg:w-64 xl:w-72 lg:flex-shrink-0 lg:sticky lg:top-0 lg:self-start mb-5 lg:mb-0 rounded-2xl overflow-hidden"
        :class="sidebarOpen ? 'block' : 'hidden lg:block'"
        style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">

        <!-- Sidebar header -->
        <div class="flex items-center justify-between px-4 py-3 border-b sticky top-0 z-10 rounded-t-2xl"
             style="background-color: var(--color-surface-02); border-color: var(--color-surface-04)">
          <div class="flex items-center gap-2 min-w-0">
            <span v-if="topic" class="px-2 py-0.5 rounded text-xs font-bold flex-shrink-0"
                  :style="levelColor(topic.level)">{{ topic.level }}</span>
            <span class="text-xs font-semibold truncate" style="color: var(--color-text-base)">Chủ điểm ngữ pháp</span>
          </div>
          <button @click="sidebarOpen = false"
                  class="lg:hidden w-6 h-6 flex items-center justify-center rounded-full text-xs border transition hover:opacity-60 flex-shrink-0"
                  style="border-color: var(--color-surface-04); color: var(--color-text-muted)">✕</button>
        </div>

        <!-- Sidebar skeleton -->
        <div v-if="sidebarLoading" class="p-3 space-y-2">
          <div v-for="i in 8" :key="i" class="flex items-center gap-2 px-1">
            <div class="w-4 h-4 rounded-full flex-shrink-0 animate-pulse" style="background-color: var(--color-surface-04)"></div>
            <div class="h-3 rounded animate-pulse" :style="`background-color: var(--color-surface-04); width: ${45 + (i * 13) % 42}%`"></div>
          </div>
        </div>

        <!-- Chapter & topic list -->
        <nav v-else class="max-h-[calc(100vh-12rem)] overflow-y-auto py-1">
          <template v-for="chapter in sidebarChapters" :key="chapter.id ?? 'no-chapter'">

            <!-- Chapter row (collapsible) -->
            <button
              class="w-full flex items-center gap-2 px-3 py-2 text-left text-xs transition-colors"
              :style="isChapterExpanded(chapter.id) ? 'background-color: var(--color-surface-03)' : ''"
              @click="toggleChapter(chapter.id)">
              <span class="text-sm leading-none flex-shrink-0">{{ chapter.icon }}</span>
              <span class="flex-1 font-semibold truncate" style="color: var(--color-text-base)">{{ chapter.name }}</span>
              <span class="flex-shrink-0 tabular-nums text-[10px]" style="color: var(--color-text-muted)">{{ chapter.topics.length }}</span>
              <svg class="w-3 h-3 flex-shrink-0 transition-transform duration-200"
                   :class="isChapterExpanded(chapter.id) ? 'rotate-90' : ''"
                   style="color: var(--color-text-muted); fill: currentColor"
                   viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
              </svg>
            </button>

            <!-- Topic rows -->
            <div v-if="isChapterExpanded(chapter.id)">
              <RouterLink
                v-for="t in chapter.topics"
                :key="t.id"
                :to="{ name: 'grammar-detail', params: { slug: t.slug } }"
                @click="sidebarOpen = false"
                class="flex items-center gap-2 pr-3 py-1.5 text-xs transition-colors"
                style="text-decoration: none"
                :style="t.slug === route.params.slug
                  ? 'background-color: color-mix(in srgb, var(--color-primary-500) 12%, transparent); border-left: 2px solid var(--color-primary-500); padding-left: 30px'
                  : 'border-left: 2px solid transparent; padding-left: 32px; color: var(--color-text-muted)'">
                <span class="flex-1 leading-snug"
                      :style="t.slug === route.params.slug
                        ? 'color: var(--color-text-base); font-weight: 600'
                        : ''">{{ t.title }}</span>
                <span v-if="t.slug === route.params.slug"
                      class="flex-shrink-0 w-1.5 h-1.5 rounded-full"
                      style="background-color: var(--color-primary-500)"></span>
              </RouterLink>
            </div>

          </template>
        </nav>

      </aside>

      <!-- ─── MAIN CONTENT ──────────────────────────────────────────────── -->
      <div class="flex-1 min-w-0">

    <!-- Loading -->
    <div v-if="loading" class="space-y-4">
      <div class="h-24 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
      <div v-for="i in 3" :key="i" class="h-40 rounded-2xl animate-pulse"
           style="background-color: var(--color-surface-02)"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-16" style="color: var(--color-text-muted)">
      <p class="text-4xl mb-3">⚠️</p>
      <p>{{ error }}</p>
      <button @click="fetchTopic"
              class="mt-4 px-4 py-2 rounded-lg text-sm transition hover:opacity-80"
              style="background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white">Thử lại</button>
    </div>

    <template v-else-if="topic">

      <!-- ── STICKY TABS ────────────────────────────────────────────────────── -->
      <div class="sticky top-0 z-20 mb-6 backdrop-blur-md border-b"
           style="background-color: color-mix(in srgb, var(--color-surface-01) 90%, transparent); border-color: var(--color-surface-04);">
        <!-- Reading Progress Bar -->
        <div v-show="activeTab === 'lesson'" class="absolute top-0 left-0 h-1 bg-[var(--color-primary-500)] transition-all duration-150" :style="{ width: readingProgress + '%' }"></div>
        
        <div class="flex items-center gap-6 px-2">
          <button @click="activeTab = 'lesson'"
                  class="py-3 text-sm font-semibold transition-colors relative"
                  :style="activeTab === 'lesson' ? 'color: var(--color-primary-500)' : 'color: var(--color-text-muted)'">
            📖 Bài học
            <div v-if="activeTab === 'lesson'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary-500)] rounded-t-full"></div>
          </button>
          <button @click="activeTab = 'practice'"
                  class="py-3 text-sm font-semibold transition-colors relative flex items-center gap-2"
                  :style="activeTab === 'practice' ? 'color: var(--color-primary-500)' : 'color: var(--color-text-muted)'">
            🧩 Bài tập
            <span class="px-1.5 py-0.5 rounded-md text-[10px] bg-[var(--color-surface-03)]"
                  :style="activeTab === 'practice' ? 'color: var(--color-primary-500); background: color-mix(in srgb, var(--color-primary-500) 15%, transparent)' : 'color: var(--color-text-muted)'">
              {{ quizQuestions.length }}
            </span>
            <div v-if="activeTab === 'practice'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary-500)] rounded-t-full"></div>
          </button>
        </div>
      </div>

      <!-- ── LESSON TAB ─────────────────────────────────────────────────────── -->
      <div v-show="activeTab === 'lesson'" class="animate-in fade-in duration-300">

      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 1: HOOK — Analogy + Description                       ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section class="rounded-2xl p-6 mb-6"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <div class="flex items-center gap-3 mb-4">
          <span class="text-3xl">{{ topic.icon || '📖' }}</span>
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="px-2 py-0.5 rounded text-xs font-bold"
                    :style="levelColor(topic.level)">{{ topic.level }}</span>
              <span v-if="topic.chapter" class="text-xs" style="color: var(--color-text-muted)">
                {{ topic.chapter?.name ?? topic.chapter }}
              </span>
            </div>
            <h1 class="text-2xl font-bold" style="color: var(--color-text-base)">
              {{ topic.title }}
            </h1>
          </div>
        </div>

        
        <!-- Metaphor & Intro -->
        <div v-if="topic.metaphor_title || topic.narrative_intro" class="mb-5">
          <div v-if="topic.concept_image_url" class="mb-4 rounded-xl overflow-hidden shadow-sm border border-[var(--color-surface-04)]">
             <img :src="topic.concept_image_url" class="w-full h-auto object-cover" alt="Concept visual" />
          </div>
          <h2 v-if="topic.metaphor_title" class="text-xl font-bold mb-2 flex items-center gap-2" style="color: var(--color-text-base)">
            ✨ {{ topic.metaphor_title }}
          </h2>
          <p v-if="topic.narrative_intro" class="text-sm leading-relaxed mb-4" style="color: var(--color-text-muted)">
            {{ topic.narrative_intro }}
          </p>
        </div>
        
        <!-- Timeline generic (Option B) -->
        <div v-if="timelineType" class="mb-6 px-4 py-6 rounded-xl border border-[var(--color-surface-04)] bg-[var(--color-surface-01)] flex flex-col items-center">
           <h3 class="text-xs uppercase font-bold tracking-widest text-[var(--color-text-muted)] mb-6">Trục thời gian</h3>
           <div class="relative w-full max-w-md h-0.5 bg-[var(--color-surface-04)] flex items-center justify-between">
              <!-- Past -->
              <div class="absolute left-0 w-3 h-3 rounded-full -ml-1.5" :style="timelineType === 'past' ? 'background: #f87171; box-shadow: 0 0 10px #f87171' : 'background: var(--color-surface-04)'"></div>
              <span class="absolute left-0 top-4 text-[10px] font-bold uppercase -ml-4" :style="timelineType === 'past' ? 'color: #f87171' : 'color: var(--color-text-muted)'">Quá khứ</span>
              
              <!-- Present -->
              <div class="absolute left-1/2 w-3 h-3 rounded-full -ml-1.5" :style="timelineType === 'present' ? 'background: #34d399; box-shadow: 0 0 10px #34d399' : 'background: var(--color-surface-04)'"></div>
              <span class="absolute left-1/2 top-4 text-[10px] font-bold uppercase -ml-4" :style="timelineType === 'present' ? 'color: #34d399' : 'color: var(--color-text-muted)'">Hiện tại</span>
              
              <!-- Future -->
              <div class="absolute right-0 w-3 h-3 rounded-full -mr-1.5" :style="timelineType === 'future' ? 'background: #60a5fa; box-shadow: 0 0 10px #60a5fa' : 'background: var(--color-surface-04)'"></div>
              <span class="absolute right-0 top-4 text-[10px] font-bold uppercase -mr-4" :style="timelineType === 'future' ? 'color: #60a5fa' : 'color: var(--color-text-muted)'">Tương lai</span>
              
              <!-- Event Indicator -->
              <div v-if="timelineType === 'present_perfect'" class="absolute left-0 right-1/2 h-0.5 bg-gradient-to-r from-[#f87171] to-[#34d399]"></div>
              <div v-if="timelineType === 'present_perfect'" class="absolute left-1/2 w-4 h-4 rounded-full -ml-2 bg-[#34d399] animate-pulse"></div>
           </div>
        </div>

        <!-- Quick Vibe -->
        <div v-if="topic.quick_vibe" class="mb-4 p-4 rounded-xl text-center shadow-sm" style="background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(124,58,237,0.1)); border: 1px solid rgba(99,102,241,0.2)">
           <p class="text-lg font-medium" style="color: var(--color-primary-600)">"{{ topic.quick_vibe }}"</p>
        </div>

        <!-- Usage-cards grid (auto-parsed from description) -->
        <template v-if="descriptionParsed">
          <p v-if="descriptionParsed.intro" class="text-sm mb-3 font-medium" style="color: var(--color-text-muted)">
            {{ descriptionParsed.intro }}:
          </p>
          <div class="grid grid-cols-2 gap-2 mb-4">
            <div v-for="(item, i) in descriptionParsed.items" :key="i"
                 class="rounded-xl p-3 border"
                 :style="`background-color:${USAGE_PALETTES[i % USAGE_PALETTES.length].bg};border-color:${USAGE_PALETTES[i % USAGE_PALETTES.length].border}`">
              <p class="text-xs font-bold uppercase tracking-wide mb-1.5"
                 :style="`color:${USAGE_PALETTES[i % USAGE_PALETTES.length].label}`">
                {{ item.label }}
              </p>
              <div class="space-y-0.5">
                <p v-for="(sent, si) in item.sentences" :key="si"
                   class="text-xs leading-relaxed italic"
                   style="color: var(--color-text-base)">
                  {{ sent }}
                </p>
              </div>
            </div>
          </div>
        </template>
        <p v-else-if="topic.description" class="text-sm mb-4 leading-relaxed" style="color: var(--color-text-muted)">
          {{ topic.description }}
        </p>

        <!-- Analogy box -->
        <div v-if="topic.analogy"
             class="rounded-xl px-4 py-3 mb-3"
             style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.25)">
          <p class="text-sm" style="color: var(--color-text-base)">
            💡 <strong>Gợi nhớ:</strong> {{ topic.analogy }}
          </p>
        </div>

        <!-- Memory hook -->
        <div v-if="topic.memory_hook"
             class="rounded-xl px-4 py-3"
             style="background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.25)">
          <p class="text-sm" style="color: #fbbf24">
            🧠 <strong>Mẹo nhớ:</strong> {{ topic.memory_hook }}
          </p>
        </div>

        <!-- Signal words -->
        <div v-if="topic.signal_words?.length" class="mt-3">
          <p class="text-xs font-semibold uppercase tracking-wide mb-2" style="color: var(--color-text-muted)">🔑 Dấu hiệu nhận biết</p>
          <div class="flex flex-wrap gap-1.5">
            <span v-for="word in topic.signal_words" :key="word"
                  class="px-2.5 py-1 rounded-full text-xs font-medium"
                  style="background:rgba(6,182,212,0.12); border:1px solid rgba(6,182,212,0.3); color:#22d3ee">
              {{ word }}
            </span>
          </div>
        </div>
      </section>

      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 2: FORMULA — Rules with formulas + examples           ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="topic.rules?.length" class="mb-6">
        <h2 class="font-bold text-lg mb-4 flex items-center gap-2" style="color: var(--color-text-base)">
          📋 Công thức & Quy tắc
          <span class="text-xs font-normal px-2 py-0.5 rounded-full"
                style="background: var(--color-surface-04); color: var(--color-text-muted)">
            {{ topic.rules.length }} quy tắc
          </span>
        </h2>

        <!-- Stepper-style rule cards -->
        <div class="space-y-4">
          <div v-for="(rule, ri) in topic.rules" :key="rule.id"
               class="rounded-2xl overflow-hidden"
               :style="rule.is_exception
                 ? 'background-color: var(--color-surface-02); border: 1px solid rgba(239,68,68,0.35)'
                 : 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)'">

            <div class="p-5">
              <!-- Step number + title -->
              <div class="flex items-start gap-3 mb-3">
                <div class="flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold flex-shrink-0"
                     :style="rule.is_exception
                       ? 'background:rgba(239,68,68,0.2); color:#f87171'
                       : 'background:rgba(99,102,241,0.15); color:#818cf8'">
                  {{ ri + 1 }}
                </div>
                <div>
                  <h3 class="font-bold text-base" style="color: var(--color-text-base)">
                    {{ rule.title }}
                    <span v-if="rule.is_exception"
                          class="ml-2 text-xs font-semibold px-2 py-0.5 rounded"
                          style="background:rgba(239,68,68,0.2); color:#f87171">⚠ Ngoại lệ</span>
                  </h3>
                </div>
              </div>

              <!-- Formula pill -->
              <div v-if="rule.formula"
                   class="inline-block px-4 py-2 rounded-xl text-sm font-mono mb-3"
                   style="background: rgba(99,102,241,0.12); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.25)">
                {{ rule.formula }}
              </div>

              <!-- Explanation -->
              <p v-if="rule.explanation" class="text-sm leading-relaxed mb-3"
                 style="color: var(--color-text-muted)">
                {{ rule.explanation }}
              </p>

              <!-- Rule memory hook -->
              <div v-if="rule.memory_hook"
                   class="text-xs px-3 py-2 rounded-xl mb-3"
                   style="background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.25); color: #fbbf24">
                🧠 {{ rule.memory_hook }}
              </div>

              <!-- Grammar table -->
              <div v-if="rule.grammar_table?.headers?.length" class="mt-3 mb-1 overflow-x-auto rounded-xl"
                   style="border: 1px solid var(--color-surface-04)">
                <table class="w-full text-sm">
                  <thead>
                    <tr style="background: var(--color-surface-03)">
                      <th v-for="(h, hi) in rule.grammar_table.headers" :key="hi"
                          class="px-4 py-2 text-left font-semibold"
                          :class="hi === 0 ? 'rounded-tl-xl' : hi === rule.grammar_table.headers.length-1 ? 'rounded-tr-xl' : ''"
                          style="color: var(--color-text-base); border-bottom: 1px solid var(--color-surface-04)">
                        {{ h }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, ri) in rule.grammar_table.rows" :key="ri"
                        :style="ri % 2 === 0 ? 'background: var(--color-surface-02)' : 'background: var(--color-surface-03)'">
                      <td v-for="(cell, ci) in row" :key="ci"
                          class="px-4 py-2"
                          :class="ci === 0 ? 'font-medium' : ''"
                          style="color: var(--color-text-base); border-top: 1px solid var(--color-surface-04)">
                        <span v-if="ci === 0" style="color: #a5b4fc" class="font-mono text-xs">{{ cell }}</span>
                        <span v-else>{{ cell }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Examples -->
            <div v-if="rule.examples?.length"
                 class="border-t" style="border-color: var(--color-surface-04)">
              <div class="divide-y" style="border-color: var(--color-surface-04)">
                <div v-for="ex in rule.examples" :key="ex.id"
                     class="flex items-start gap-3 px-5 py-3"
                     :style="!ex.is_correct ? 'background: rgba(239,68,68,0.04)' : ''">
                  <span class="flex-shrink-0 text-sm font-bold mt-0.5"
                        :style="ex.is_correct !== false ? 'color:#34d399' : 'color:#f87171'">{{ ex.is_correct !== false ? '✓' : '✗' }}</span>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <p class="text-sm flex-1"
                         :style="ex.is_correct !== false ? 'color:var(--color-text-base)' : 'color:var(--color-text-muted); text-decoration:line-through'"
                         v-html="highlightSentence(ex.sentence, ex.highlight)"></p>
                      <!-- Audio button -->
                      <button v-if="ex.audio_url" @click.prevent="playAudio(ex.audio_url)"
                              class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-full transition hover:opacity-80"
                              style="background: rgba(99,102,241,0.15); color: #818cf8"
                              title="Nghe phát âm">
                        🔊
                      </button>
                    </div>
                    <p v-if="ex.translation" class="text-xs mt-0.5" style="color: var(--color-text-muted)">
                      {{ ex.translation }}
                    </p>
                    <p v-if="ex.context" class="text-xs mt-0.5 italic" style="color: #818cf8">
                      {{ ex.context }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 2.5: COMMON MISTAKES                                  ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="topic.common_mistakes?.length" class="mb-6">
        <h2 class="font-bold text-lg mb-4 flex items-center gap-2" style="color: var(--color-text-base)">
          ⚠️ Lỗi thường gặp
          <span class="text-xs font-normal px-2 py-0.5 rounded-full"
                style="background:rgba(239,68,68,0.12); color:#f87171">
            {{ topic.common_mistakes.length }} lỗi
          </span>
        </h2>
        <div class="space-y-3">
          <div v-for="(mistake, mi) in topic.common_mistakes" :key="mi"
               class="rounded-xl overflow-hidden"
               style="border: 1px solid rgba(239,68,68,0.25)">
            <div class="flex items-start gap-3 px-4 py-3"
                 style="background: rgba(239,68,68,0.07)">
              <span class="flex-shrink-0 font-bold text-sm mt-0.5" style="color:#f87171">✗</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm" style="color:var(--color-text-muted); text-decoration:line-through through">{{ mistake.wrong }}</p>
              </div>
            </div>
            <div class="flex items-start gap-3 px-4 py-3"
                 style="background: rgba(34,197,94,0.06); border-top: 1px solid rgba(239,68,68,0.15)">
              <span class="flex-shrink-0 font-bold text-sm mt-0.5" style="color:#34d399">✓</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm" style="color: var(--color-text-base)">{{ mistake.correct }}</p>
                <p v-if="mistake.explanation" class="text-xs mt-1 leading-relaxed" style="color: var(--color-text-muted)">
                  💬 {{ mistake.explanation }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      

      
      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 2.8: COMPARISON                                       ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="topic.comparison_with?.length" class="mb-6">
        <h2 class="font-bold text-lg mb-4 flex items-center gap-2" style="color: var(--color-text-base)">
          🔀 Phân biệt dễ nhầm lẫn
        </h2>
        <div class="space-y-4">
          <div v-for="(comp, ci) in topic.comparison_with" :key="ci" class="rounded-2xl p-5" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <h3 class="font-semibold mb-3 flex items-center gap-2" style="color: var(--color-text-base)">
              <span class="px-2 py-1 rounded bg-[var(--color-surface-04)] text-xs">{{ topic.title }}</span>
              <span class="text-xs text-[var(--color-text-muted)]">vs</span>
              <span class="px-2 py-1 rounded bg-[rgba(249,115,22,0.15)] text-[rgb(234,88,12)] text-xs">{{ comp.title }}</span>
            </h3>
            <p class="text-sm mb-4" style="color: var(--color-text-muted)">{{ comp.difference }}</p>
            
            <div v-if="comp.examples?.length" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
               <div v-for="(ex, ei) in comp.examples" :key="ei" class="p-3 rounded-lg border border-[var(--color-surface-04)] bg-[var(--color-surface-01)]">
                 <p class="text-sm font-medium mb-1" style="color: var(--color-text-base)">{{ ex.sentence }}</p>
                 <p class="text-xs text-[var(--color-text-muted)]">{{ ex.explanation }}</p>
               </div>
            </div>
          </div>
        </div>
      </section>

<!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 4: REAL WORLD — Practical application                 ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="topic.real_world_use" class="mb-6">
        <div class="rounded-2xl p-5"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <h3 class="font-semibold text-sm mb-2 flex items-center gap-2" style="color: var(--color-text-base)">
            🌍 Ứng dụng thực tế
          </h3>
          <p class="text-sm leading-relaxed" style="color: var(--color-text-muted)">{{ topic.real_world_use }}</p>
        </div>
      </section>

      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 5: NOTES — Tips, warnings, info callouts              ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="topic.notes?.length" class="mb-6">
        <div class="space-y-2">
          <div v-for="(note, ni) in topic.notes" :key="ni"
               class="flex items-start gap-3 px-4 py-3 rounded-xl text-sm"
               :style="noteStyle(note.type)">
            <span class="flex-shrink-0 font-bold">{{ noteIcon(note.type) }}</span>
            <p class="leading-relaxed" style="color: var(--color-text-base)">{{ note.text }}</p>
          </div>
        </div>
      </section>

      
      </div><!-- /lesson-tab -->

      <!-- ── PRACTICE TAB ───────────────────────────────────────────────────── -->
      <div v-show="activeTab === 'practice'" class="animate-in fade-in duration-300">
        <div v-if="fetchingQuiz" class="py-12 text-center text-[var(--color-text-muted)]">
           <div class="inline-block w-6 h-6 border-2 border-[var(--color-primary-500)] border-t-transparent rounded-full animate-spin mb-3"></div>
           <p class="text-sm">Đang tải bài tập...</p>
        </div>
        <div v-else-if="!quizQuestions.length" class="py-12 text-center text-[var(--color-text-muted)] border border-dashed border-[var(--color-surface-04)] rounded-2xl">
           <p class="text-3xl mb-2">🍃</p>
           <p class="text-sm">Chưa có bài tập cho chủ điểm này.</p>
        </div>
        <div v-else>
<!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 3: PRACTICE — Quiz (3 types)                         ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="quizQuestions.length" class="mb-6">
        <h2 class="font-bold text-lg mb-4 flex items-center gap-2" style="color: var(--color-text-base)">
          🧩 Thực hành
          <span class="text-xs font-normal px-2 py-0.5 rounded-full"
                style="background: var(--color-surface-04); color: var(--color-text-muted)">
            {{ quizQuestions.length }} câu
          </span>
        </h2>

        <div class="space-y-4">
          <div v-for="(q, qi) in quizQuestions" :key="qi"
               class="rounded-2xl p-5"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">

            <!-- Question type badge -->
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :style="quizTypeBadge(q.type)">
                {{ quizTypeLabel(q.type) }}
              </span>
              <span class="text-xs" style="color: var(--color-text-muted)">
                Câu {{ qi + 1 }} / {{ quizQuestions.length }}
              </span>
            </div>

            <!-- Gap-fill question -->
            <template v-if="q.type === 'gap-fill'">
              <p class="text-sm font-medium mb-4" style="color: var(--color-text-base)"
                 v-html="q.prompt"></p>
              <div class="space-y-2">
                <button v-for="(opt, oi) in q.options" :key="oi"
                        @click="selectAnswer(qi, oi)"
                        :disabled="q.selected !== null"
                        class="w-full text-left px-4 py-3 rounded-xl text-sm transition"
                        :class="optionClass(q, oi)">
                  <span class="font-medium mr-2">{{ 'ABCD'[oi] }}.</span>{{ opt }}
                </button>
              </div>
            </template>

            <!-- Multiple choice question -->
            <template v-else-if="q.type === 'mc'">
              <p class="text-sm font-medium mb-4" style="color: var(--color-text-base)">
                {{ q.prompt }}
              </p>
              <div class="space-y-2">
                <button v-for="(opt, oi) in q.options" :key="oi"
                        @click="selectAnswer(qi, oi)"
                        :disabled="q.selected !== null"
                        class="w-full text-left px-4 py-3 rounded-xl text-sm transition"
                        :class="optionClass(q, oi)">
                  <span class="font-medium mr-2">{{ 'ABCD'[oi] }}.</span>{{ opt }}
                </button>
              </div>
            </template>

            <!-- Error correction question -->
            <template v-else-if="q.type === 'error'">
              <p class="text-sm font-medium mb-2" style="color: var(--color-text-base)">
                Tìm lỗi sai trong câu:
              </p>
              <p class="text-base font-medium mb-4 px-4 py-3 rounded-xl"
                 style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); color: var(--color-text-base)">
                "{{ q.errorSentence }}"
              </p>
              <div class="space-y-2">
                <button v-for="(opt, oi) in q.options" :key="oi"
                        @click="selectAnswer(qi, oi)"
                        :disabled="q.selected !== null"
                        class="w-full text-left px-4 py-3 rounded-xl text-sm transition"
                        :class="optionClass(q, oi)">
                  <span class="font-medium mr-2">{{ 'ABCD'[oi] }}.</span>{{ opt }}
                </button>
              </div>
            </template>

            <!-- Feedback -->
            <Transition name="fade">
              <div v-if="q.selected !== null" class="mt-3 px-4 py-2 rounded-xl text-xs"
                   :style="q.selected === q.correct
                     ? 'background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);color:#86efac'
                     : 'background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#fca5a5'">
                <span v-if="q.selected === q.correct">✓ Chính xác!</span>
                <span v-else>✗ Chưa đúng. Đáp án: <strong>{{ 'ABCD'[q.correct] }}</strong></span>
                <span v-if="q.explanation"> — {{ q.explanation }}</span>
              </div>
            </Transition>
          </div>
        </div>

        <!-- Quiz score summary -->
        <Transition name="fade">
          <div v-if="quizDone" class="mt-5 rounded-2xl p-6 text-center"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p class="text-4xl mb-2">
              {{ quizScore === quizQuestions.length ? '🎉' : quizScore >= quizQuestions.length / 2 ? '👍' : '💪' }}
            </p>
            <p class="font-bold text-xl mb-1" style="color: var(--color-text-base)">
              {{ quizScore }} / {{ quizQuestions.length }} câu đúng
            </p>
            <p class="text-sm mb-4" style="color: var(--color-text-muted)">
              {{ quizPercent }}% — {{ quizPercent >= 80 ? 'Tuyệt vời!' : quizPercent >= 50 ? 'Khá tốt, cần ôn thêm.' : 'Cần ôn lại lý thuyết.' }}
            </p>

            <!-- Save indicator -->
            <p v-if="quizSaved" class="text-xs mb-3" style="color: #34d399">✓ Đã lưu kết quả</p>
            <p v-else-if="quizSaving" class="text-xs mb-3" style="color: var(--color-text-muted)">Đang lưu...</p>

            <div class="flex items-center justify-center gap-3">
              <button @click="resetQuiz"
                      class="px-5 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                      style="background:linear-gradient(135deg,#4f46e5,#7c3aed); color:white">
                Làm lại
              </button>
              <RouterLink v-if="topic.next_topic"
                          :to="{ name: 'grammar-detail', params: { slug: topic.next_topic.slug } }"
                          class="px-5 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                          style="background-color: var(--color-surface-04); color: var(--color-text-base); text-decoration: none">
                Bài tiếp →
              </RouterLink>
            </div>
          </div>
        </Transition>
      </section>
        </div>
      </div><!-- /practice-tab -->

<!-- ── Bottom navigation ──────────────────────────────────────── -->
      <div class="flex items-center justify-between pt-4 border-t" style="border-color: var(--color-surface-04)">
        <RouterLink v-if="topic.prev_topic"
                    :to="{ name: 'grammar-detail', params: { slug: topic.prev_topic.slug } }"
                    class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm transition hover:opacity-80"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted); text-decoration: none">
          ← {{ topic.prev_topic.title }}
        </RouterLink>
        <div v-else></div>
        <RouterLink v-if="topic.next_topic"
                    :to="{ name: 'grammar-detail', params: { slug: topic.next_topic.slug } }"
                    class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm transition hover:opacity-80"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted); text-decoration: none">
          {{ topic.next_topic.title }} →
        </RouterLink>
        <div v-else></div>
      </div>

    </template>

      </div><!-- /main-content -->
    </div><!-- /flex-layout -->
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { grammarApi } from '@/api/curriculum.js'
import { useAuthStore } from '@/stores/auth.js'

const route = useRoute()
const auth = useAuthStore()
const { isLoggedIn } = storeToRefs(auth)

const activeTab = ref('lesson')
const topic = ref(null)
const readingProgress = ref(0)
const fetchingQuiz = ref(false)

const timelineType = computed(() => {
  if (!topic.value?.title) return null
  const t = topic.value.title.toLowerCase()
  if (t.includes('present perfect')) return 'present_perfect'
  if (t.includes('past')) return 'past'
  if (t.includes('future')) return 'future'
  if (t.includes('present')) return 'present'
  return null
})

// Update reading progress on scroll
onMounted(() => {
  window.addEventListener('scroll', () => {
    if (activeTab.value !== 'lesson') return
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight
    readingProgress.value = height > 0 ? (winScroll / height) * 100 : 0
  })
})

const loading = ref(false)
const error = ref('')

// ── Sidebar navigator ──────────────────────────────────────────────────────
const sidebarOpen = ref(false)
const sidebarTopics = ref([])
const sidebarLoading = ref(false)
const expandedChapterIds = ref(new Set())

const sidebarChapters = computed(() => {
  const map = new Map()
  for (const t of sidebarTopics.value) {
    const key = t.chapter?.id ?? '__no_chapter__'
    if (!map.has(key)) {
      map.set(key, {
        id: t.chapter?.id ?? null,
        name: t.chapter?.name || 'Chưa phân chương',
        icon: t.chapter?.icon || '📚',
        order: t.chapter?.order ?? 999,
        topics: [],
      })
    }
    map.get(key).topics.push(t)
  }
  return [...map.values()].sort((a, b) => a.order - b.order)
})

function isChapterExpanded(chapterId) {
  return expandedChapterIds.value.has(chapterId ?? '__no_chapter__')
}

function toggleChapter(chapterId) {
  const key = chapterId ?? '__no_chapter__'
  if (expandedChapterIds.value.has(key)) {
    expandedChapterIds.value.delete(key)
  } else {
    expandedChapterIds.value.add(key)
  }
}

async function fetchSidebarTopics(level) {
  sidebarLoading.value = true
  try {
    const { data } = await grammarApi.listTopics({ level, page_size: 200 })
    sidebarTopics.value = data.results ?? data
  } catch { /* ignore */ } finally {
    sidebarLoading.value = false
  }
}

// ── Audio player ─────────────────────────────────────────────────────────────
let _audioEl = null
function playAudio(url) {
  if (!url) return
  if (_audioEl) { _audioEl.pause(); _audioEl = null }
  _audioEl = new Audio(url)
  _audioEl.play().catch(() => {})
}

// ── Mini quiz state ──────────────────────────────────────────────────────────
const quizQuestions = ref([])
const quizSaving = ref(false)
const quizSaved = ref(false)

const quizDone = computed(() =>
  quizQuestions.value.length > 0 &&
  quizQuestions.value.every(q => q.selected !== null)
)
const quizScore = computed(() =>
  quizQuestions.value.filter(q => q.selected === q.correct).length
)
const quizPercent = computed(() =>
  quizQuestions.value.length
    ? Math.round((quizScore.value / quizQuestions.value.length) * 100)
    : 0
)

// Auto-save when quiz is done
watch(quizDone, async (done) => {
  if (!done || !isLoggedIn.value || !topic.value) return
  quizSaving.value = true
  try {
    await grammarApi.submitQuiz(route.params.slug, {
      score: quizPercent.value,
      total_questions: quizQuestions.value.length,
      correct_answers: quizScore.value,
    })
    quizSaved.value = true
  } catch {
    // silently fail — quiz still shows results
  } finally {
    quizSaving.value = false
  }
})

function selectAnswer(qi, oi) {
  if (quizQuestions.value[qi].selected !== null) return
  quizQuestions.value[qi].selected = oi
}

function optionClass(q, oi) {
  if (q.selected === null) return 'hover:bg-white/5 border border-transparent'
  if (oi === q.correct) return 'correct-opt'
  if (oi === q.selected) return 'wrong-opt'
  return 'opacity-50'
}

function resetQuiz() {
  quizQuestions.value.forEach(q => { q.selected = null })
  quizSaved.value = false
}

// ── Quiz type helpers ────────────────────────────────────────────────────────
function quizTypeLabel(type) {
  return { 'gap-fill': 'Điền khuyết', 'mc': 'Trắc nghiệm', 'error': 'Tìm lỗi sai' }[type] || type
}
function quizTypeBadge(type) {
  return {
    'gap-fill': 'background:rgba(99,102,241,0.15);color:#818cf8',
    'mc': 'background:rgba(34,197,94,0.15);color:#86efac',
    'error': 'background:rgba(239,68,68,0.15);color:#fca5a5',
  }[type] || 'background:var(--color-surface-04);color:var(--color-text-muted)'
}

// ── Build quiz (3 types) ─────────────────────────────────────────────────────
function buildQuiz(rules) {
  const questions = []
  const allExamples = []

  for (const rule of rules) {
    if (!rule.examples) continue
    for (const ex of rule.examples) {
      if (ex.sentence && ex.highlight) {
        allExamples.push({ ...ex, ruleTitle: rule.title, formula: rule.formula })
      }
    }
  }

  // Type 1: Gap-fill — replace highlight with ___
  for (const ex of allExamples) {
    if (questions.length >= 5) break
    const blank = ex.sentence.replace(
      new RegExp(ex.highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'),
      '<strong style="color:#818cf8">______</strong>'
    )
    if (blank === ex.sentence) continue // highlight not found

    // Generate wrong options from other examples' highlights
    const wrongs = allExamples
      .filter(e => e.highlight !== ex.highlight)
      .map(e => e.highlight)
      .filter((v, i, a) => a.indexOf(v) === i)
      .slice(0, 3)

    if (wrongs.length < 2) continue

    const options = shuffle([ex.highlight, ...wrongs.slice(0, 3)])
    questions.push(reactive({
      type: 'gap-fill',
      prompt: blank,
      options,
      correct: options.indexOf(ex.highlight),
      explanation: ex.translation || '',
      selected: null,
    }))
  }

  // Type 2: MC — choose correct sentence for a rule
  for (const rule of rules) {
    if (questions.length >= 7) break
    if (!rule.examples || rule.examples.length < 2) continue

    const correct = rule.examples[0]
    // Find examples from OTHER rules as wrong answers
    const wrongExamples = rules
      .filter(r => r.id !== rule.id)
      .flatMap(r => (r.examples || []))
      .filter(e => e.sentence)
      .slice(0, 3)

    if (wrongExamples.length < 2) continue

    const options = shuffle([
      correct.sentence,
      ...wrongExamples.slice(0, 3).map(e => e.sentence),
    ])
    questions.push(reactive({
      type: 'mc',
      prompt: `Câu nào đúng theo quy tắc "${rule.title}"?`,
      options,
      correct: options.indexOf(correct.sentence),
      explanation: correct.translation || '',
      selected: null,
    }))
  }

  // Type 3: Error correction — swap a word to create an error
  for (const ex of allExamples) {
    if (questions.length >= 8) break
    if (!ex.highlight || ex.highlight.split(/\s+/).length < 1) continue

    // Create a wrong version by modifying the highlighted part
    const errorVersion = createErrorSentence(ex.sentence, ex.highlight)
    if (!errorVersion) continue

    const options = shuffle([
      `Lỗi ở "${ex.highlight}" — đúng phải là: "${ex.highlight}"`,
      `Câu này đúng, không có lỗi`,
      `Lỗi ở cấu trúc câu chung`,
      `Lỗi ở dấu câu`,
    ])
    // The correct answer is always the first one (before shuffle)
    const correctAnswer = `Lỗi ở "${ex.highlight}" — đúng phải là: "${ex.highlight}"`
    questions.push(reactive({
      type: 'error',
      prompt: 'Tìm lỗi sai trong câu sau:',
      errorSentence: errorVersion,
      options,
      correct: options.indexOf(correctAnswer),
      explanation: `Câu đúng: "${ex.sentence}"`,
      selected: null,
    }))
  }

  return questions.slice(0, 8) // max 8 questions
}

function createErrorSentence(sentence, highlight) {
  if (!highlight) return null
  // Simple error: change verb form
  const errorMap = {
    'is': 'are', 'are': 'is', 'was': 'were', 'were': 'was',
    'has': 'have', 'have': 'has', 'do': 'does', 'does': 'do',
    'goes': 'go', 'go': 'goes', 'plays': 'play', 'play': 'plays',
  }
  const words = highlight.split(/\s+/)
  for (let i = 0; i < words.length; i++) {
    const lower = words[i].toLowerCase()
    if (errorMap[lower]) {
      const errorWords = [...words]
      errorWords[i] = errorMap[lower]
      return sentence.replace(highlight, errorWords.join(' '))
    }
  }
  return null
}

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// ── Usage-cards parser ───────────────────────────────────────────────────────
const USAGE_PALETTES = [
  { bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.3)',   label: '#f87171' },
  { bg: 'rgba(249,115,22,0.1)', border: 'rgba(249,115,22,0.3)', label: '#fb923c' },
  { bg: 'rgba(234,179,8,0.1)',  border: 'rgba(234,179,8,0.3)',  label: '#facc15' },
  { bg: 'rgba(34,197,94,0.1)',  border: 'rgba(34,197,94,0.3)',  label: '#4ade80' },
  { bg: 'rgba(6,182,212,0.1)',  border: 'rgba(6,182,212,0.3)',  label: '#22d3ee' },
  { bg: 'rgba(99,102,241,0.1)', border: 'rgba(99,102,241,0.3)', label: '#818cf8' },
  { bg: 'rgba(168,85,247,0.1)', border: 'rgba(168,85,247,0.3)', label: '#c084fc' },
  { bg: 'rgba(236,72,153,0.1)', border: 'rgba(236,72,153,0.3)', label: '#f472b6' },
]

function parseUsageItems(text) {
  if (!text) return null
  const normalized = text.replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim()
  const re = /([A-Z][a-zA-Z ,]{1,40}):\s*/g
  const matches = []
  let m
  while ((m = re.exec(normalized)) !== null) {
    matches.push({ label: m[1].trim(), start: m.index, end: m.index + m[0].length })
  }
  if (matches.length < 4) return null
  const sections = matches.map((match, i) => {
    const contentEnd = i + 1 < matches.length ? matches[i + 1].start : normalized.length
    const content = normalized.slice(match.end, contentEnd).trimEnd()
    const sentences = content.split(/(?<=[.!?])\s+/).map(s => s.trim()).filter(Boolean)
    return { label: match.label, content, sentences }
  })
  let intro = ''
  let items = sections
  if (sections[0] && sections[0].content.length <= 3) {
    intro = sections[0].label
    items = sections.slice(1)
  }
  items = items.filter(s => s.content.length > 3)
  if (items.length < 3) return null
  return { intro, items }
}

const descriptionParsed = computed(() => {
  if (!topic.value?.description) return null
  if (topic.value.rules?.length) return null
  return parseUsageItems(topic.value.description)
})

// ── Utilities ────────────────────────────────────────────────────────────────
function highlightSentence(sentence, highlight) {
  if (!highlight || !sentence) return sentence || ''
  const escaped = highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return sentence.replace(
    new RegExp(`(${escaped})`, 'gi'),
    '<mark style="background:rgba(99,102,241,0.25);border-radius:3px;padding:0 2px">$1</mark>'
  )
}

function levelColor(level) {
  const map = {
    A1: 'background:#d1fae5; color:#065f46',
    A2: 'background:#dbeafe; color:#1e40af',
    B1: 'background:#ede9fe; color:#4c1d95',
    B2: 'background:#fef3c7; color:#92400e',
    C1: 'background:#fee2e2; color:#991b1b',
    C2: 'background:#fce7f3; color:#831843',
  }
  return map[level] || 'background:var(--color-surface-04); color:var(--color-text-muted)'
}

function truncate(str, len) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '…' : str
}

// ── Notes / Tips helpers ──────────────────────────────────────────────────────
function noteStyle(type) {
  const map = {
    tip:     'background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.25)',
    warning: 'background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.25)',
    info:    'background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.25)',
  }
  return map[type] || map.info
}
function noteIcon(type) {
  return { tip: '💡', warning: '⚠️', info: 'ℹ️' }[type] || 'ℹ️'
}


// ── API ──────────────────────────────────────────────────────────────────────
async function fetchQuiz(slug) {
  fetchingQuiz.value = true
  try {
    const res = await grammarApi.getTopicExercises(slug)
    quizQuestions.value = res.data?.results || res.data || []
  } catch (e) {
    // Fallback to auto-generated quiz if API fails or doesn't exist yet
    quizQuestions.value = buildQuiz(topic.value?.rules || [])
  } finally {
    fetchingQuiz.value = false
  }
}

async function fetchTopic() {
  loading.value = true
  error.value = ''
  quizSaved.value = false
  try {
    const res = await grammarApi.getTopic(route.params.slug)
    const d = res.data?.data ?? res.data
    if (d?.rules) {
      d.rules = d.rules.map(r => reactive({ ...r }))
    }
    topic.value = d
    // Expand the chapter that contains the current topic in the sidebar
    expandedChapterIds.value = new Set([d?.chapter?.id ?? '__no_chapter__'])
    // Load sidebar topics when the level changes (or on first load)
    const lvl = d?.level
    if (lvl && (!sidebarTopics.value.length || sidebarTopics.value[0]?.level !== lvl)) {
      fetchSidebarTopics(lvl)
    }
    
    fetchQuiz(d.slug)

  } catch (e) {
    error.value = e?.response?.data?.detail || 'Không thể tải chủ điểm này.'
  } finally {
    loading.value = false
  }
}

// Re-fetch when route params change (prev/next navigation)
watch(() => route.params.slug, (newSlug) => {
  if (newSlug) fetchTopic()
})

onMounted(fetchTopic)
</script>

<style scoped>
.correct-opt {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #86efac;
}
.wrong-opt {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

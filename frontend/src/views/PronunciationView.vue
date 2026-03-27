<template>
  <div class="p-4 md:p-6 max-w-7xl">

    <!-- ── Header ─────────────────────────────────────────────────────────── -->
    <section
      class="rounded-3xl p-5 mb-5"
      style="background: linear-gradient(145deg, color-mix(in srgb, var(--color-primary-600) 20%, transparent), color-mix(in srgb, var(--color-surface-02) 85%, transparent)); border: 1px solid var(--color-surface-04)"
    >
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-2xl font-bold" style="color: var(--color-text-base)">Phát âm tiếng Anh</h1>
          <p class="mt-1 text-sm" style="color: var(--color-text-soft)">Bảng IPA · 4 giai đoạn · Minimal Pairs</p>
        </div>
        <div class="flex gap-2 text-xs flex-wrap">
          <div class="rounded-xl px-3 py-2" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p style="color: var(--color-text-muted)">Âm vị</p>
            <p class="font-semibold" style="color: var(--color-text-base)">45</p>
          </div>
          <div class="rounded-xl px-3 py-2" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p style="color: var(--color-text-muted)">Giai đoạn</p>
            <p class="font-semibold" style="color: var(--color-text-base)">4</p>
          </div>
          <div class="rounded-xl px-3 py-2" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p style="color: var(--color-text-muted)">Cặp tối giản</p>
            <p class="font-semibold" style="color: var(--color-text-base)">{{ minimalPairs.length }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Mode hint banner (when pronunciation mode is ON) -->
    <div
      v-if="pronunciationMode.enabled"
      class="mb-4 rounded-2xl px-4 py-2 flex items-center gap-2 text-sm"
      style="background-color: color-mix(in srgb, var(--color-primary-600) 12%, transparent); border: 1px solid color-mix(in srgb, var(--color-primary-600) 35%, transparent); color: var(--color-primary-400)"
    >
      🔊 <span>Chế độ phát âm <strong>BẬT</strong> — nhấp vào bất kỳ từ tiếng Anh nào để nghe phát âm TTS</span>
    </div>

    <!-- ── Tab bar ────────────────────────────────────────────────────────── -->
    <div class="flex gap-2 mb-5 flex-wrap">
      <button
        v-for="tab in TABS"
        :key="tab.id"
        @click="switchTab(tab.id)"
        class="rounded-full px-4 py-1.5 text-sm font-semibold transition"
        :style="activeTab === tab.id
          ? 'background-color: var(--color-primary-600); color: #fff'
          : 'background-color: var(--color-surface-02); color: var(--color-text-muted); border: 1px solid var(--color-surface-04)'"
      >{{ tab.icon }} {{ tab.label }}</button>
    </div>

    <!-- ════════════════════════════════════════════════════════════════════ -->
    <!-- TAB 1 · IPA CHART ──────────────────────────────────────────────── -->
    <!-- ════════════════════════════════════════════════════════════════════ -->
    <div v-if="activeTab === 'chart'">

      <!-- loading skeleton -->
      <div v-if="chartLoading" class="space-y-6">
        <div v-for="s in 3" :key="s">
          <div class="h-5 w-40 mb-3 rounded-lg animate-pulse" style="background-color: var(--color-surface-03)" />
          <div class="grid grid-cols-4 gap-2">
            <div v-for="i in 12" :key="i" class="rounded-2xl h-20 animate-pulse" style="background-color: var(--color-surface-02)" />
          </div>
        </div>
      </div>

      <!-- error -->
      <div v-else-if="chartError" class="text-center py-16 rounded-2xl" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <p class="text-4xl mb-3">⚠️</p>
        <p style="color: #fca5a5">{{ chartError }}</p>
        <button @click="loadChart" class="mt-4 px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80" style="background-color: var(--color-primary-600); color: #fff">Thử lại</button>
      </div>

      <template v-else>
        <!-- ── VOWELS — 4-col grid ──────────────────────────────────────── -->
        <section v-if="chart.vowel?.length" class="mb-6">
          <div class="flex items-center gap-2 mb-3">
            <span class="h-3 w-3 rounded-full" style="background-color: #60a5fa" />
            <h2 class="text-sm font-bold tracking-wide uppercase" style="color: var(--color-text-muted)">
              Nguyên âm đơn &nbsp;<span class="normal-case text-xs">(Monophthongs)</span>
            </h2>
          </div>
          <div class="grid grid-cols-4 gap-2 max-w-lg">
            <button
              v-for="p in chart.vowel"
              :key="p.id"
              class="phoneme-cell vowel-cell"
              :class="{ 'is-selected': selectedPhoneme?.id === p.id, 'is-playing': playingId === p.id }"
              @click="clickPhoneme(p)"
            >
              <span class="ipa-sym">{{ bare(p.symbol) }}</span>
              <span class="ex-word">
                <template v-if="p.example_words?.[0]?.highlight !== undefined">{{ p.example_words[0].before }}<u>{{ p.example_words[0].highlight }}</u>{{ p.example_words[0].after }}</template>
                <template v-else>{{ p.example_words?.[0]?.word }}</template>
              </span>
            </button>
          </div>
        </section>

        <!-- ── DIPHTHONGS — 3-col grid ─────────────────────────────────── -->
        <section v-if="chart.diphthong?.length" class="mb-6">
          <div class="flex items-center gap-2 mb-3">
            <span class="h-3 w-3 rounded-full" style="background-color: #fbbf24" />
            <h2 class="text-sm font-bold tracking-wide uppercase" style="color: var(--color-text-muted)">
              Nguyên âm đôi &nbsp;<span class="normal-case text-xs">(Diphthongs)</span>
            </h2>
          </div>
          <div class="grid grid-cols-3 gap-2 max-w-xs">
            <button
              v-for="p in chart.diphthong"
              :key="p.id"
              class="phoneme-cell diphthong-cell"
              :class="{ 'is-selected': selectedPhoneme?.id === p.id, 'is-playing': playingId === p.id }"
              @click="clickPhoneme(p)"
            >
              <span class="ipa-sym">{{ bare(p.symbol) }}</span>
              <span class="ex-word">
                <template v-if="p.example_words?.[0]?.highlight !== undefined">{{ p.example_words[0].before }}<u>{{ p.example_words[0].highlight }}</u>{{ p.example_words[0].after }}</template>
                <template v-else>{{ p.example_words?.[0]?.word }}</template>
              </span>
            </button>
          </div>
        </section>

        <!-- ── CONSONANTS — 8-col grid (3 rows: voiceless / voiced / son) -->
        <section v-if="chart.consonant?.length" class="mb-6">
          <div class="flex items-center gap-2 mb-3">
            <span class="h-3 w-3 rounded-full" style="background-color: #34d399" />
            <h2 class="text-sm font-bold tracking-wide uppercase" style="color: var(--color-text-muted)">
              Phụ âm &nbsp;<span class="normal-case text-xs">(Consonants)</span>
            </h2>
          </div>
          <!-- sub-labels for the 3 rows -->
          <div class="grid grid-cols-4 sm:grid-cols-8 gap-2 mb-1 max-w-2xl">
            <span v-for="lbl in consonantColLabels" :key="lbl" class="text-center text-xs" style="color: var(--color-text-muted)">{{ lbl }}</span>
          </div>
          <div class="grid grid-cols-4 sm:grid-cols-8 gap-2 max-w-2xl">
            <button
              v-for="p in chart.consonant"
              :key="p.id"
              class="phoneme-cell consonant-cell"
              :class="{ 'is-selected': selectedPhoneme?.id === p.id, 'is-playing': playingId === p.id }"
              @click="clickPhoneme(p)"
            >
              <span class="ipa-sym">{{ bare(p.symbol) }}</span>
              <span class="ex-word">
                <template v-if="p.example_words?.[0]?.highlight !== undefined">{{ p.example_words[0].before }}<u>{{ p.example_words[0].highlight }}</u>{{ p.example_words[0].after }}</template>
                <template v-else>{{ p.example_words?.[0]?.word }}</template>
              </span>
            </button>
          </div>
          <div class="flex flex-wrap gap-6 mt-3 text-xs" style="color: var(--color-text-muted)">
            <span><span class="inline-block w-2 h-2 rounded-sm mr-1" style="background: color-mix(in srgb,#60a5fa 25%,transparent); border:1px solid #60a5fa60" />Vô thanh (1–8)</span>
            <span><span class="inline-block w-2 h-2 rounded-sm mr-1" style="background: color-mix(in srgb,#f87171 25%,transparent); border:1px solid #f8717160" />Hữu thanh (9–16)</span>
            <span><span class="inline-block w-2 h-2 rounded-sm mr-1" style="background: color-mix(in srgb,#34d399 25%,transparent); border:1px solid #34d39960" />Bán âm/mũi (17–24)</span>
          </div>
        </section>
      </template>

      <!-- ── Detail panel (slides up when phoneme selected) ────────────── -->
      <Transition name="slide-up">
        <div
          v-if="selectedPhoneme"
          class="fixed inset-x-3 bottom-3 sm:inset-x-auto sm:left-1/2 sm:-translate-x-1/2 sm:w-[580px] z-40 rounded-3xl p-5 shadow-2xl"
          style="background-color: var(--color-surface-01); border: 1px solid var(--color-surface-04)"
        >
          <div class="flex items-start justify-between gap-3 mb-4">
            <div class="flex items-center gap-3">
              <span class="text-4xl font-extrabold leading-none" style="color: var(--color-primary-400)">{{ bare(selectedPhoneme.symbol) }}</span>
              <div>
                <p class="font-semibold text-sm" style="color: var(--color-text-base)">{{ selectedPhoneme.description }}</p>
                <span class="inline-block mt-0.5 text-xs px-2 py-0.5 rounded-full" :class="typeChip(selectedPhoneme.phoneme_type)">
                  {{ typeLabelVi(selectedPhoneme.phoneme_type) }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <button
                v-if="selectedPhoneme.audio_url"
                @click="playAudio(selectedPhoneme.audio_url, selectedPhoneme.id)"
                class="rounded-xl px-3 py-2 text-sm font-semibold transition hover:opacity-80 flex items-center gap-1"
                style="background-color: var(--color-primary-600); color: #fff"
              >
                <span :class="playingId === selectedPhoneme.id ? 'animate-pulse' : ''">🔊</span> Phát
              </button>
              <button @click="selectedPhoneme = null" class="rounded-xl px-3 py-2 text-sm transition hover:opacity-80" style="background-color: var(--color-surface-03); color: var(--color-text-muted)">✕</button>
            </div>
          </div>

          <div v-if="selectedPhoneme.example_words?.length" class="grid grid-cols-3 gap-2">
            <div
              v-for="ex in selectedPhoneme.example_words"
              :key="ex.word"
              class="rounded-xl p-2.5 text-center cursor-pointer transition hover:opacity-80"
              style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
              :data-tts-word="ex.word"
              @click="ex.audio_url ? playAudio(ex.audio_url) : tts.speak(ex.word)"
            >
              <p class="font-bold" style="color: var(--color-text-base)">
                <template v-if="ex.highlight !== undefined">{{ ex.before }}<u>{{ ex.highlight }}</u>{{ ex.after }}</template>
                <template v-else>{{ ex.word }}</template>
              </p>
              <p class="text-xs mt-0.5" style="color: var(--color-primary-400)">{{ ex.ipa }}</p>
              <p class="text-xs mt-0.5 truncate" style="color: var(--color-text-muted)">{{ ex.meaning }}</p>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- ════════════════════════════════════════════════════════════════════ -->
    <!-- TAB 2 · 4 STAGE PROGRESSION ───────────────────────────────────── -->
    <!-- ════════════════════════════════════════════════════════════════════ -->
    <div v-else-if="activeTab === 'stages'">
      <div v-if="stagesLoading" class="grid md:grid-cols-2 gap-4">
        <div v-for="i in 4" :key="i" class="rounded-2xl h-48 animate-pulse" style="background-color: var(--color-surface-02)" />
      </div>
      <div v-else-if="stagesError" class="text-center py-16 rounded-2xl" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <p class="text-4xl mb-3">⚠️</p><p style="color: #fca5a5">{{ stagesError }}</p>
        <button @click="loadStages" class="mt-4 px-4 py-2 rounded-xl text-sm font-semibold hover:opacity-80 transition" style="background-color: var(--color-primary-600); color: #fff">Thử lại</button>
      </div>
      <div v-else class="grid md:grid-cols-2 gap-4">
        <div v-for="stage in stages" :key="stage.id" class="rounded-2xl p-5 flex flex-col gap-4" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <div class="flex items-center gap-3">
            <span class="text-3xl">{{ stage.icon }}</span>
            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-base" style="color: var(--color-text-base)">{{ stage.title }}</h3>
              <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">{{ stage.description }}</p>
            </div>
            <span class="shrink-0 text-lg font-bold" style="color: var(--color-primary-400)">{{ stage.progress_percent }}%</span>
          </div>
          <div class="w-full h-1.5 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
            <div class="h-full rounded-full transition-all" style="background-color: var(--color-primary-500)" :style="{ width: stage.progress_percent + '%' }" />
          </div>
          <p class="text-xs" style="color: var(--color-text-muted)">{{ stage.completed_lessons }} / {{ stage.total_lessons }} bài hoàn thành</p>
          <div v-if="stage.lessons?.length" class="space-y-2">
            <div
              v-for="lesson in stage.lessons.slice(0, expandedStage === stage.id ? 999 : 4)"
              :key="lesson.id"
              class="rounded-xl overflow-hidden"
              style="background-color: var(--color-surface-01); border: 1px solid var(--color-surface-04)"
            >
              <!-- Lesson header row (clickable) -->
              <div
                class="flex items-center gap-3 p-2.5 cursor-pointer hover:opacity-80 transition"
                @click="openLesson(lesson)"
              >
                <span class="text-base shrink-0" :style="lesson.is_completed ? 'color:#86efac' : 'color:var(--color-text-muted)'">{{ lesson.is_completed ? '✅' : '⬜' }}</span>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate" style="color: var(--color-text-base)">{{ lesson.title }}</p>
                  <p class="text-xs" style="color: var(--color-text-muted)">{{ lesson.cefr_level }}</p>
                </div>
                <span class="text-xs shrink-0" style="color: var(--color-text-muted)">
                  →
                </span>
              </div>
            </div>
            <button v-if="stage.lessons.length > 4" @click="expandedStage = expandedStage === stage.id ? null : stage.id" class="w-full py-2 text-xs font-semibold hover:opacity-80 transition" style="color: var(--color-primary-400)">
              {{ expandedStage === stage.id ? '▲ Thu gọn' : `▼ Xem thêm ${stage.lessons.length - 4} bài` }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════════════════════════ -->
    <!-- TAB 3 · MINIMAL PAIRS ──────────────────────────────────────────── -->
    <!-- ════════════════════════════════════════════════════════════════════ -->
    <div v-else-if="activeTab === 'minimal-pairs'">
      <div v-if="mpLoading" class="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i" class="rounded-2xl h-48 animate-pulse" style="background-color: var(--color-surface-02)" />
      </div>
      <div v-else-if="mpError" class="text-center py-16 rounded-2xl" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <p class="text-4xl mb-3">⚠️</p><p style="color: #fca5a5">{{ mpError }}</p>
        <button @click="loadMinimalPairs" class="mt-4 px-4 py-2 rounded-xl text-sm font-semibold hover:opacity-80 transition" style="background-color: var(--color-primary-600); color: #fff">Thử lại</button>
      </div>

      <!-- Active exercise -->
      <div v-else-if="activeMpSet" class="max-w-2xl mx-auto">
        <div class="rounded-2xl p-6" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <!-- Header -->
          <div class="flex items-center justify-between mb-4">
            <div>
              <h3 class="font-bold text-lg" style="color: var(--color-text-base)">{{ activeMpSet.title }}</h3>
              <p class="text-sm" style="color: var(--color-text-muted)">{{ activeMpSet.description }}</p>
            </div>
            <button @click="activeMpSet = null; mpResult = null; mpFinished = false" class="rounded-xl px-3 py-2 text-sm hover:opacity-80 transition" style="background-color: var(--color-surface-03); color: var(--color-text-muted)">← Quay lại</button>
          </div>

          <!-- Round progress bar (hidden when finished) -->
          <div v-if="!mpFinished" class="mb-5">
            <div class="flex justify-between items-center mb-2 text-xs" style="color: var(--color-text-muted)">
              <span>Câu <strong style="color: var(--color-text-base)">{{ mpRound }}</strong> / {{ mpTotalRounds }}</span>
              <span>✅ {{ mpCorrectCount }} đúng</span>
            </div>
            <div class="w-full h-1.5 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
              <div class="h-full rounded-full transition-all" style="background-color: var(--color-primary-500)" :style="{ width: ((mpRound - 1) / mpTotalRounds * 100) + '%' }" />
            </div>
          </div>

          <!-- Final score -->
          <div v-if="mpFinished" class="text-center py-8">
            <p class="text-6xl font-black mb-2" style="color: var(--color-primary-400)">
              {{ mpCorrectCount }}<span class="text-3xl font-normal" style="color: var(--color-text-muted)">/{{ mpTotalRounds }}</span>
            </p>
            <p class="text-lg font-bold mb-6"
              :style="mpCorrectCount >= mpTotalRounds * 0.8 ? 'color:#86efac' : mpCorrectCount >= mpTotalRounds * 0.5 ? 'color:#fbbf24' : 'color:#fca5a5'">
              {{ mpCorrectCount >= mpTotalRounds * 0.8 ? '🏆 Xuất sắc!' : mpCorrectCount >= mpTotalRounds * 0.5 ? '👍 Khá tốt!' : '💪 Cần luyện thêm!' }}
            </p>
            <div class="flex gap-3 justify-center">
              <button @click="restartMpExercise" class="px-5 py-2.5 rounded-xl text-sm font-semibold hover:opacity-80 transition" style="background-color: var(--color-primary-600); color: #fff">🔄 Luyện lại</button>
              <button @click="activeMpSet = null; mpFinished = false" class="px-5 py-2.5 rounded-xl text-sm font-semibold hover:opacity-80 transition" style="background-color: var(--color-surface-03); color: var(--color-text-muted)">Chọn cặp khác</button>
            </div>
          </div>

          <!-- Question (rounds not finished) -->
          <template v-else>
            <div v-if="!mpResult" class="rounded-2xl p-5 mb-5 text-center" style="background-color: var(--color-surface-01); border: 1px solid var(--color-surface-04)">
              <p class="text-sm mb-3" style="color: var(--color-text-muted)">Nghe âm dưới đây và chọn từ đúng:</p>
              <button @click="playMpAudio" :disabled="tts.speaking || !!tts.loadingText"
                class="inline-flex items-center gap-2 px-6 py-3 rounded-2xl text-base font-semibold mb-3 hover:opacity-80 transition disabled:opacity-60"
                style="background-color: var(--color-primary-600); color: #fff">
                <span :class="tts.loadingText ? 'animate-ping' : tts.speaking ? 'animate-pulse' : ''">🎵</span>
                {{ tts.loadingText ? 'Đang tải...' : tts.speaking ? 'Đang phát...' : 'Phát lại' }}
              </button>
              <p class="text-xs" style="color: var(--color-text-muted)">Nhấn để phát lại</p>
            </div>
            <div v-if="!mpResult" class="grid grid-cols-2 gap-3 mb-4">
              <button v-for="pair in shuffledMpOptions" :key="pair.id" @click="checkMpAnswer(pair)"
                class="rounded-2xl p-4 text-center hover:opacity-90 hover:-translate-y-0.5 transition"
                style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
                <p class="text-2xl font-extrabold mb-1" style="color: var(--color-text-base)">{{ pair.word }}</p>
                <p class="text-sm" style="color: var(--color-primary-400)">{{ pair.ipa }}</p>
                <p class="text-xs mt-1" style="color: var(--color-text-muted)">{{ pair.meaning }}</p>
              </button>
            </div>
            <Transition name="fade">
              <div v-if="mpResult" class="text-center py-6">
                <p class="text-5xl mb-3">{{ mpResult.correct ? '🎉' : '❌' }}</p>
                <p class="text-xl font-bold mb-1" :style="mpResult.correct ? 'color:#86efac' : 'color:#fca5a5'">{{ mpResult.correct ? 'Chính xác!' : 'Chưa đúng rồi!' }}</p>
                <p class="text-sm mb-5" style="color: var(--color-text-muted)">Đáp án đúng: <strong style="color: var(--color-text-base)">{{ mpResult.correct_word }}</strong> — {{ mpResult.correct_ipa }}</p>
                <button @click="resetMpExercise" class="px-5 py-2.5 rounded-xl text-sm font-semibold hover:opacity-80 transition" style="background-color: var(--color-primary-600); color: #fff">
                  {{ mpRound < mpTotalRounds ? 'Câu tiếp →' : 'Xem kết quả 🏁' }}
                </button>
              </div>
            </Transition>
          </template>
        </div>
      </div>

      <!-- Pair list grid -->
      <div v-else class="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="mp in minimalPairs" :key="mp.id"
          class="rounded-2xl p-5 flex flex-col gap-3 cursor-pointer hover:-translate-y-0.5 transition"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
          @click="startMpExercise(mp)">
          <span class="text-xs px-2 py-0.5 rounded-full self-start" style="background-color: var(--color-primary-600)22; color: var(--color-primary-400)">{{ mp.cefr_level }}</span>
          <h3 class="font-bold" style="color: var(--color-text-base)">{{ mp.title }}</h3>
          <p class="text-xs" style="color: var(--color-text-muted)">{{ mp.description }}</p>
          <div class="flex gap-2 mt-auto">
            <div v-for="pair in mp.pairs" :key="pair.id" class="flex-1 rounded-xl p-2.5 text-center" style="background-color: var(--color-surface-01); border: 1px solid var(--color-surface-04)">
              <p class="font-bold" style="color: var(--color-text-base)" :data-tts-word="pair.word">{{ pair.word }}</p>
              <p class="text-xs" style="color: var(--color-primary-400)">{{ pair.ipa }}</p>
            </div>
          </div>
          <button class="mt-1 w-full py-2 rounded-xl text-sm font-semibold hover:opacity-80 transition" style="background-color: var(--color-primary-600); color: #fff">Luyện tập →</button>
        </div>
        <div v-if="minimalPairs.length === 0" class="col-span-full text-center py-16 rounded-2xl" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <p class="text-5xl mb-3">🎵</p><p class="font-semibold" style="color: var(--color-text-base)">Chưa có bài tập Minimal Pairs nào.</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, ref, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pronunciationApi } from '@/api/pronunciation.js'
import { useTTS } from '@/composables/useTTS.js'
import { usePronunciationStore } from '@/stores/pronunciation.js'

const TABS = [
  { id: 'chart',         icon: '🔠', label: 'IPA Chart' },
  { id: 'stages',        icon: '📶', label: '4 Giai đoạn' },
  { id: 'minimal-pairs', icon: '🎵', label: 'Minimal Pairs' },
]
const activeTab = ref('chart')
const router = useRouter()
const route = useRoute()

function switchTab(id) {
  activeTab.value = id
  selectedPhoneme.value = null
}

// ── helpers ────────────────────────────────────────────────────────────────
/** Strip leading/trailing slashes: /æ/ → æ */
function bare(sym) { return sym.replace(/^\/|\/$/g, '') }

function typeLabelVi(t) {
  return t === 'vowel' ? 'Nguyên âm đơn' : t === 'diphthong' ? 'Nguyên âm đôi' : 'Phụ âm'
}
function typeChip(t) {
  if (t === 'vowel')     return 'chip-vowel'
  if (t === 'diphthong') return 'chip-diphthong'
  return 'chip-consonant'
}

// Column labels for consonants (shown above 8 cols on desktop)
const consonantColLabels = ['p','f','t','θ','tʃ','s','ʃ','k']

// ── IPA Chart ─────────────────────────────────────────────────────────────
const chart        = ref({})
const chartLoading = ref(false)
const chartError   = ref('')
const selectedPhoneme = shallowRef(null)
const playingId       = ref(null)

async function loadChart() {
  chartLoading.value = true; chartError.value = ''
  try {
    const res = await pronunciationApi.getPhonemeChart()
    const d = res.data?.data ?? res.data
    chart.value = d || {}
  } catch { chartError.value = 'Không thể tải bảng IPA. Vui lòng thử lại.' }
  finally  { chartLoading.value = false }
}

const tts = useTTS()
const pronunciationMode = usePronunciationStore()

function clickPhoneme(p) {
  if (selectedPhoneme.value?.id === p.id) { selectedPhoneme.value = null; return }
  selectedPhoneme.value = p
  playAudio(p.audio_url, p.id)
}

// Keep a module-level reference so Firefox doesn't GC audio mid-fetch
let _ipaAudio = null

function playAudio(url, id = null) {
  if (!url) return
  if (_ipaAudio) { _ipaAudio.pause(); _ipaAudio = null }
  const audio = new Audio(url)
  _ipaAudio = audio
  if (id) {
    playingId.value = id
    audio.addEventListener('ended', () => { if (playingId.value === id) playingId.value = null })
    audio.addEventListener('error', () => { if (playingId.value === id) playingId.value = null })
  }
  audio.play().catch(() => { if (id && playingId.value === id) playingId.value = null })
}

// ── Stages ────────────────────────────────────────────────────────────────
const stages        = ref([])
const stagesLoading = ref(false)
const stagesError   = ref('')
const expandedStage = ref(null)

async function loadStages() {
  stagesLoading.value = true; stagesError.value = ''
  try {
    const res = await pronunciationApi.getStages()
    const d = res.data?.data ?? res.data
    stages.value = Array.isArray(d) ? d : (d?.results ?? [])
  } catch { stagesError.value = 'Không thể tải giai đoạn học. Vui lòng thử lại.' }
  finally  { stagesLoading.value = false }
}

function openLesson(lesson) {
  if (!lesson?.slug) return
  router.push({ name: 'pronunciation-lesson', params: { slug: lesson.slug } })
}

// ── Minimal Pairs ─────────────────────────────────────────────────────────
const minimalPairs  = ref([])
const mpLoading     = ref(false)
const mpError       = ref('')
const activeMpSet   = shallowRef(null)
const mpResult      = ref(null)
const mpCorrectIdx  = ref(0)
const mpRound       = ref(1)
const mpTotalRounds = ref(5)
const mpCorrectCount = ref(0)
const mpFinished    = ref(false)

const shuffledMpOptions = computed(() => {
  if (!activeMpSet.value?.pairs?.length) return []
  return [...activeMpSet.value.pairs].sort(() => Math.random() - 0.5)
})

async function loadMinimalPairs() {
  mpLoading.value = true; mpError.value = ''
  try {
    const res = await pronunciationApi.getMinimalPairs()
    const d = res.data?.data ?? res.data
    minimalPairs.value = Array.isArray(d) ? d : (d?.results ?? [])
  } catch { mpError.value = 'Không thể tải Minimal Pairs.' }
  finally  { mpLoading.value = false }
}

function startMpExercise(mp) {
  activeMpSet.value = mp
  mpResult.value = null
  mpRound.value = 1
  mpTotalRounds.value = 6
  mpCorrectCount.value = 0
  mpFinished.value = false
  mpCorrectIdx.value = Math.floor(Math.random() * (mp.pairs?.length || 1))
  // Auto-play after short delay for UX
  setTimeout(playMpAudio, 600)
}

function playMpAudio() {
  const pair = activeMpSet.value?.pairs?.[mpCorrectIdx.value]
  if (!pair) return
  tts.speak(pair.word, pronunciationMode.voice)
}

function checkMpAnswer(sel) {
  const correct = activeMpSet.value?.pairs?.[mpCorrectIdx.value]
  if (!correct) return
  const isCorrect = sel.id === correct.id
  if (isCorrect) mpCorrectCount.value++
  mpResult.value = { correct: isCorrect, correct_word: correct.word, correct_ipa: correct.ipa }
}

function resetMpExercise() {
  if (mpRound.value >= mpTotalRounds.value) {
    mpFinished.value = true
    mpResult.value = null
    return
  }
  mpRound.value++
  mpResult.value = null
  if (activeMpSet.value?.pairs?.length)
    mpCorrectIdx.value = Math.floor(Math.random() * activeMpSet.value.pairs.length)
  setTimeout(playMpAudio, 400)
}

function restartMpExercise() {
  mpFinished.value = false
  mpRound.value = 1
  mpCorrectCount.value = 0
  mpResult.value = null
  if (activeMpSet.value?.pairs?.length)
    mpCorrectIdx.value = Math.floor(Math.random() * activeMpSet.value.pairs.length)
  setTimeout(playMpAudio, 400)
}

onMounted(() => {
  const tab = route.query?.tab
  if (tab && TABS.some((x) => x.id === tab)) {
    activeTab.value = tab
  }
  loadChart()
  loadStages()
  loadMinimalPairs()
})
</script>

<style scoped>
/* ── Phoneme cells ──────────────────────────────────────────────────────── */
.phoneme-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px 4px;
  border-radius: 12px;
  cursor: pointer;
  user-select: none;
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
  border: 1.5px solid var(--color-surface-04);
  background-color: var(--color-surface-02);
}
.phoneme-cell:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.phoneme-cell:active { transform: translateY(0); }

/* type-specific subtle background tints */
.vowel-cell      { background-color: color-mix(in srgb, #3b82f6 6%, var(--color-surface-02)); }
.diphthong-cell  { background-color: color-mix(in srgb, #f59e0b 6%, var(--color-surface-02)); }
.consonant-cell  { background-color: color-mix(in srgb, #10b981 6%, var(--color-surface-02)); }

/* selected state */
.vowel-cell.is-selected      { border-color: #60a5fa; background-color: color-mix(in srgb, #3b82f6 18%, var(--color-surface-02)); }
.diphthong-cell.is-selected  { border-color: #fbbf24; background-color: color-mix(in srgb, #f59e0b 18%, var(--color-surface-02)); }
.consonant-cell.is-selected  { border-color: #34d399; background-color: color-mix(in srgb, #10b981 18%, var(--color-surface-02)); }

/* playing pulse ring */
.is-playing { animation: pulse-ring 0.6s ease infinite alternate; }
@keyframes pulse-ring {
  from { box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-primary-500) 60%, transparent); }
  to   { box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-primary-500) 0%, transparent); }
}

/* IPA symbol */
.ipa-sym {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1;
  color: var(--color-primary-400);
  font-family: 'Times New Roman', serif;
}

/* example word with underline */
.ex-word {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  text-align: center;
  line-height: 1.2;
}
.ex-word u { text-decoration-thickness: 1.5px; text-underline-offset: 2px; }

/* ── type chips ──────────────────────────────────────────────────────────── */
.chip-vowel      { background-color: color-mix(in srgb,#3b82f6 20%,transparent); color:#93c5fd; }
.chip-diphthong  { background-color: color-mix(in srgb,#f59e0b 20%,transparent); color:#fcd34d; }
.chip-consonant  { background-color: color-mix(in srgb,#10b981 20%,transparent); color:#6ee7b7; }

/* ── slide-up transition ─────────────────────────────────────────────────── */
.slide-up-enter-active { transition: transform .3s ease, opacity .3s ease; }
.slide-up-leave-active { transition: transform .2s ease, opacity .2s ease; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(32px); opacity: 0; }

/* ── fade transition ──────────────────────────────────────────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>

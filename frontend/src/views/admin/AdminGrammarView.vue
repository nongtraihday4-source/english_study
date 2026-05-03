<template>
  <div class="space-y-5">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Quản lý Ngữ pháp</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Topic → Rule → Example theo dạng cây 3 cấp</p>
    </div>

    <!-- 3-panel layout -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

      <!-- ─── PANEL 1: TOPICS ──────────────────────────────────────────────── -->
      <div class="rounded-2xl border flex flex-col" style="border-color: var(--color-surface-04); background-color: var(--color-surface-01); max-height: 80vh">
        <div class="flex items-center justify-between px-4 py-3 border-b" style="border-color: var(--color-surface-04)">
          <span class="font-semibold text-sm" style="color: var(--color-text-base)">📖 Chủ đề</span>
          <button
            class="text-xs px-3 py-1.5 rounded-lg font-semibold transition hover:opacity-90"
            style="background-color: var(--color-primary-500); color: #fff"
            @click="openTopicForm()"
          >+ Thêm</button>
        </div>

        <!-- Filters -->
        <div class="px-3 py-2 space-y-1.5 border-b" style="border-color: var(--color-surface-04)">
          <select
            v-model="topicFilter.level"
            class="w-full rounded-lg px-2 py-1.5 text-xs border outline-none"
            style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
            @change="fetchTopics"
          >
            <option value="">Tất cả cấp độ</option>
            <option v-for="l in LEVELS" :key="l" :value="l">{{ l }}</option>
          </select>
          <input
            v-model="topicFilter.search"
            type="text"
            placeholder="Tìm topic..."
            class="w-full rounded-lg px-2 py-1.5 text-xs border outline-none"
            style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
            @input="debouncedFetchTopics"
          />
        </div>

        <div class="overflow-y-auto flex-1">
          <div v-if="topicsLoading" class="p-4 text-xs text-center" style="color: var(--color-text-muted)">Đang tải...</div>
          <div v-else-if="!topics.length" class="p-4 text-xs text-center" style="color: var(--color-text-muted)">Chưa có topic.</div>
          <div
            v-for="topic in topics"
            :key="topic.id"
            class="flex items-start gap-2 px-3 py-2.5 text-xs border-b cursor-pointer transition"
            style="border-color: var(--color-surface-03)"
            :style="selectedTopic?.id === topic.id
              ? 'background-color: color-mix(in srgb, var(--color-primary-600) 15%, transparent)'
              : 'background-color: transparent'"
            @click="selectTopic(topic)"
          >
            <span class="shrink-0 mt-0.5">{{ topic.icon || '📚' }}</span>
            <div class="flex-1 min-w-0">
              <div class="font-medium truncate" style="color: var(--color-text-base)">{{ topic.title }}</div>
              <div class="flex items-center gap-1.5 mt-0.5 flex-wrap">
                <span class="px-1.5 py-0.5 rounded-full text-[10px] font-semibold"
                  style="background-color:color-mix(in srgb,var(--color-primary-600) 18%,transparent);color:var(--color-primary-400)">{{ topic.level }}</span>
                <span v-if="topic.chapter_name" class="px-1.5 py-0.5 rounded-full text-[10px]"
                  style="background-color:var(--color-surface-03);color:var(--color-text-muted)">{{ topic.chapter_name }}</span>
                <span class="text-[10px]" style="color: var(--color-text-muted)">{{ topic.rule_count }} rules</span>
                <span v-if="!topic.is_published" class="px-1.5 py-0.5 rounded-full text-[10px]"
                  style="background-color:color-mix(in srgb,#ef4444 15%,transparent);color:#f87171">Ẩn</span>
              </div>
            </div>
            <div class="flex flex-col gap-1 shrink-0" @click.stop>
              <button class="px-1.5 py-0.5 rounded text-[10px] transition hover:opacity-80"
                style="background-color:color-mix(in srgb,var(--color-primary-600) 18%,transparent);color:var(--color-primary-400)"
                @click="openTopicForm(topic)">Sửa</button>
              <button class="px-1.5 py-0.5 rounded text-[10px] transition hover:opacity-80"
                style="background-color:color-mix(in srgb,#ef4444 16%,transparent);color:#f87171"
                @click="confirmDeleteTopic(topic)">Xoá</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── PANEL 2: RULES ───────────────────────────────────────────────── -->
      <div class="rounded-2xl border flex flex-col" style="border-color: var(--color-surface-04); background-color: var(--color-surface-01); max-height: 80vh">
        <div class="flex items-center justify-between px-4 py-3 border-b" style="border-color: var(--color-surface-04)">
          <span class="font-semibold text-sm" style="color: var(--color-text-base)">
            📐 Rules
            <span v-if="selectedTopic" class="font-normal text-xs ml-1" style="color: var(--color-text-muted)">— {{ selectedTopic.title }}</span>
          </span>
          <button
            v-if="selectedTopic"
            class="text-xs px-3 py-1.5 rounded-lg font-semibold transition hover:opacity-90"
            style="background-color: var(--color-primary-500); color: #fff"
            @click="openRuleForm()"
          >+ Thêm</button>
        </div>

        <div class="overflow-y-auto flex-1">
          <div v-if="!selectedTopic" class="p-6 text-xs text-center" style="color: var(--color-text-muted)">← Chọn topic để xem rules</div>
          <div v-else-if="rulesLoading" class="p-4 text-xs text-center" style="color: var(--color-text-muted)">Đang tải...</div>
          <div v-else-if="!rules.length" class="p-4 text-xs text-center" style="color: var(--color-text-muted)">Chưa có rule nào.</div>
          <div
            v-for="rule in rules"
            :key="rule.id"
            class="flex items-start gap-2 px-3 py-2.5 text-xs border-b cursor-pointer transition"
            style="border-color: var(--color-surface-03)"
            :style="selectedRule?.id === rule.id
              ? 'background-color: color-mix(in srgb, var(--color-primary-600) 15%, transparent)'
              : 'background-color: transparent'"
            @click="selectRule(rule)"
          >
            <div class="flex-1 min-w-0">
              <div class="font-medium truncate" style="color: var(--color-text-base)">
                <span v-if="rule.is_exception" class="mr-1 text-orange-400">⚠️</span>
                {{ rule.order }}. {{ rule.title }}
              </div>
              <div v-if="rule.formula" class="mt-0.5 font-mono text-[11px] truncate" style="color: var(--color-primary-400)">{{ rule.formula }}</div>
            </div>
            <div class="flex flex-col gap-1 shrink-0" @click.stop>
              <button class="px-1.5 py-0.5 rounded text-[10px] transition hover:opacity-80"
                style="background-color:color-mix(in srgb,var(--color-primary-600) 18%,transparent);color:var(--color-primary-400)"
                @click="openRuleForm(rule)">Sửa</button>
              <button class="px-1.5 py-0.5 rounded text-[10px] transition hover:opacity-80"
                style="background-color:color-mix(in srgb,#ef4444 16%,transparent);color:#f87171"
                @click="confirmDeleteRule(rule)">Xoá</button>
            </div>
          </div>
        </div>
      </div>

      <!-- ─── PANEL 3: EXAMPLES ────────────────────────────────────────────── -->
      <div class="rounded-2xl border flex flex-col" style="border-color: var(--color-surface-04); background-color: var(--color-surface-01); max-height: 80vh">
        <div class="flex items-center justify-between px-4 py-3 border-b" style="border-color: var(--color-surface-04)">
          <span class="font-semibold text-sm" style="color: var(--color-text-base)">
            💬 Examples
            <span v-if="selectedRule" class="font-normal text-xs ml-1" style="color: var(--color-text-muted)">— {{ selectedRule.title }}</span>
          </span>
          <button
            v-if="selectedRule"
            class="text-xs px-3 py-1.5 rounded-lg font-semibold transition hover:opacity-90"
            style="background-color: var(--color-primary-500); color: #fff"
            @click="openExampleForm()"
          >+ Thêm</button>
        </div>

        <div class="overflow-y-auto flex-1">
          <div v-if="!selectedRule" class="p-6 text-xs text-center" style="color: var(--color-text-muted)">← Chọn rule để xem examples</div>
          <div v-else-if="examplesLoading" class="p-4 text-xs text-center" style="color: var(--color-text-muted)">Đang tải...</div>
          <div v-else-if="!examples.length" class="p-4 text-xs text-center" style="color: var(--color-text-muted)">Chưa có example nào.</div>
          <div
            v-for="ex in examples"
            :key="ex.id"
            class="px-3 py-2.5 text-xs border-b"
            style="border-color: var(--color-surface-03)"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1 min-w-0">
                <div class="font-medium" style="color: var(--color-text-base)">{{ ex.sentence }}</div>
                <div v-if="ex.translation" class="mt-0.5" style="color: var(--color-text-muted)">{{ ex.translation }}</div>
                <div v-if="ex.context" class="mt-0.5 italic text-[11px]" style="color: var(--color-text-muted)">{{ ex.context }}</div>
                <div v-if="ex.highlight" class="mt-0.5 px-1.5 py-0.5 rounded inline-block text-[11px]"
                  style="background-color:color-mix(in srgb,var(--color-primary-600) 15%,transparent);color:var(--color-primary-400)">
                  🔑 {{ ex.highlight }}
                </div>
              </div>
              <div class="flex flex-col gap-1 shrink-0">
                <button class="px-1.5 py-0.5 rounded text-[10px] transition hover:opacity-80"
                  style="background-color:color-mix(in srgb,var(--color-primary-600) 18%,transparent);color:var(--color-primary-400)"
                  @click="openExampleForm(ex)">Sửa</button>
                <button class="px-1.5 py-0.5 rounded text-[10px] transition hover:opacity-80"
                  style="background-color:color-mix(in srgb,#ef4444 16%,transparent);color:#f87171"
                  @click="confirmDeleteExample(ex)">Xoá</button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Error banner -->
    <div v-if="globalError" class="rounded-xl p-4 text-sm"
      style="background-color:color-mix(in srgb,#ef4444 12%,transparent);color:#f87171">
      {{ globalError }}
    </div>

    <!-- ─── TOPIC FORM MODAL ──────────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showTopicForm" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)" @click.self="showTopicForm = false">
        <div class="w-full max-w-2xl rounded-2xl p-6 space-y-4 overflow-y-auto" style="background-color: var(--color-surface-01); max-height: 90vh">
          <h3 class="text-base font-bold" style="color: var(--color-text-base)">
            {{ topicFormData.id ? 'Sửa Topic' : 'Thêm Topic mới' }}
          </h3>
          <div class="grid grid-cols-2 gap-3">
            <div class="col-span-2">
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Tiêu đề *</label>
              <input v-model="topicFormData.title" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Slug (để trống = tự generate)</label>
              <input v-model="topicFormData.slug" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none font-mono"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Cấp độ CEFR *</label>
              <select v-model="topicFormData.level" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)">
                <option v-for="l in LEVELS" :key="l" :value="l">{{ l }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Chương</label>
              <select v-model="topicFormData.chapter" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)">
                <option :value="null">— Không có chương —</option>
                <option v-for="ch in chapterOptions" :key="ch.id" :value="ch.id">{{ ch.icon ? ch.icon + ' ' : '' }}{{ ch.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Thứ tự</label>
              <input v-model.number="topicFormData.order" type="number" min="0" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Icon (emoji)</label>
              <input v-model="topicFormData.icon" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div class="col-span-2">
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Mô tả ngắn</label>
              <textarea v-model="topicFormData.description" rows="2" class="w-full rounded-xl px-3 py-2 text-sm border outline-none resize-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div class="col-span-2">
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Phép ẩn dụ (Analogy)</label>
              <textarea v-model="topicFormData.analogy" rows="2" class="w-full rounded-xl px-3 py-2 text-sm border outline-none resize-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Ứng dụng thực tế</label>
              <textarea v-model="topicFormData.real_world_use" rows="2" class="w-full rounded-xl px-3 py-2 text-sm border outline-none resize-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Mẹo nhớ tổng quát</label>
              <textarea v-model="topicFormData.memory_hook" rows="2" class="w-full rounded-xl px-3 py-2 text-sm border outline-none resize-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div class="col-span-2 flex items-center gap-4 pt-1">
              <label class="flex items-center gap-2 text-sm cursor-pointer" style="color: var(--color-text-base)">
                <input v-model="topicFormData.is_published" type="checkbox" class="rounded" />
                Hiển thị (is_published)
              </label>
            </div>
          </div>
          <div v-if="topicFormError" class="rounded-xl p-3 text-sm"
            style="background-color:color-mix(in srgb,#ef4444 12%,transparent);color:#f87171">{{ topicFormError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button class="px-4 py-2 text-sm rounded-xl transition hover:opacity-80"
              style="background-color: var(--color-surface-03); color: var(--color-text-muted)" @click="showTopicForm = false">Huỷ</button>
            <button class="px-4 py-2 text-sm rounded-xl font-semibold transition hover:opacity-90"
              style="background-color: var(--color-primary-500); color: #fff" :disabled="topicFormLoading" @click="submitTopicForm">
              {{ topicFormLoading ? 'Đang lưu...' : 'Lưu' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── TOPIC DELETE CONFIRM ─────────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="topicDeleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)" @click.self="topicDeleteTarget = null">
        <div class="w-full max-w-sm rounded-2xl p-6 space-y-4" style="background-color: var(--color-surface-01)">
          <h3 class="text-base font-bold" style="color: var(--color-text-base)">Xác nhận xoá Topic</h3>
          <p class="text-sm" style="color: var(--color-text-muted)">
            Xoá topic "<strong>{{ topicDeleteTarget.title }}</strong>"? Tất cả rules và examples sẽ bị xoá.
          </p>
          <div class="flex justify-end gap-3">
            <button class="px-4 py-2 text-sm rounded-xl" style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
              @click="topicDeleteTarget = null">Huỷ</button>
            <button class="px-4 py-2 text-sm rounded-xl font-semibold transition hover:opacity-90"
              style="background-color: #ef4444; color: #fff" :disabled="topicDeleteLoading" @click="deleteTopic">
              {{ topicDeleteLoading ? 'Đang xoá...' : 'Xoá' }}</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── RULE FORM MODAL ──────────────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showRuleForm" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)" @click.self="showRuleForm = false">
        <div class="w-full max-w-lg rounded-2xl p-6 space-y-4" style="background-color: var(--color-surface-01)">
          <h3 class="text-base font-bold" style="color: var(--color-text-base)">
            {{ ruleFormData.id ? 'Sửa Rule' : 'Thêm Rule mới' }}
          </h3>
          <div class="space-y-3">
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Tiêu đề *</label>
              <input v-model="ruleFormData.title" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Công thức (Formula)</label>
              <input v-model="ruleFormData.formula" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none font-mono"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
                placeholder="VD: S + V(s/es) + Object" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Giải thích</label>
              <textarea v-model="ruleFormData.explanation" rows="3" class="w-full rounded-xl px-3 py-2 text-sm border outline-none resize-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Mẹo nhớ</label>
              <input v-model="ruleFormData.memory_hook" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div class="flex items-center gap-4">
              <div>
                <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Thứ tự</label>
                <input v-model.number="ruleFormData.order" type="number" min="0" class="w-28 rounded-xl px-3 py-2 text-sm border outline-none"
                  style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
              </div>
              <div class="flex items-end pb-2">
                <label class="flex items-center gap-2 text-sm cursor-pointer" style="color: var(--color-text-base)">
                  <input v-model="ruleFormData.is_exception" type="checkbox" class="rounded" />
                  Ngoại lệ (⚠️)
                </label>
              </div>
            </div>
          </div>
          <div v-if="ruleFormError" class="rounded-xl p-3 text-sm"
            style="background-color:color-mix(in srgb,#ef4444 12%,transparent);color:#f87171">{{ ruleFormError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button class="px-4 py-2 text-sm rounded-xl transition hover:opacity-80"
              style="background-color: var(--color-surface-03); color: var(--color-text-muted)" @click="showRuleForm = false">Huỷ</button>
            <button class="px-4 py-2 text-sm rounded-xl font-semibold transition hover:opacity-90"
              style="background-color: var(--color-primary-500); color: #fff" :disabled="ruleFormLoading" @click="submitRuleForm">
              {{ ruleFormLoading ? 'Đang lưu...' : 'Lưu' }}</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── RULE DELETE CONFIRM ──────────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="ruleDeleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)" @click.self="ruleDeleteTarget = null">
        <div class="w-full max-w-sm rounded-2xl p-6 space-y-4" style="background-color: var(--color-surface-01)">
          <h3 class="text-base font-bold" style="color: var(--color-text-base)">Xác nhận xoá Rule</h3>
          <p class="text-sm" style="color: var(--color-text-muted)">
            Xoá rule "<strong>{{ ruleDeleteTarget.title }}</strong>"? Tất cả examples của rule này cũng bị xoá.
          </p>
          <div class="flex justify-end gap-3">
            <button class="px-4 py-2 text-sm rounded-xl" style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
              @click="ruleDeleteTarget = null">Huỷ</button>
            <button class="px-4 py-2 text-sm rounded-xl font-semibold transition hover:opacity-90"
              style="background-color: #ef4444; color: #fff" :disabled="ruleDeleteLoading" @click="deleteRule">
              {{ ruleDeleteLoading ? 'Đang xoá...' : 'Xoá' }}</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── EXAMPLE FORM MODAL ───────────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showExampleForm" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)" @click.self="showExampleForm = false">
        <div class="w-full max-w-lg rounded-2xl p-6 space-y-4" style="background-color: var(--color-surface-01)">
          <h3 class="text-base font-bold" style="color: var(--color-text-base)">
            {{ exampleFormData.id ? 'Sửa Example' : 'Thêm Example mới' }}
          </h3>
          <div class="space-y-3">
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Câu ví dụ (tiếng Anh) *</label>
              <textarea v-model="exampleFormData.sentence" rows="2" class="w-full rounded-xl px-3 py-2 text-sm border outline-none resize-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Dịch nghĩa (tiếng Việt)</label>
              <input v-model="exampleFormData.translation" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Ngữ cảnh (context)</label>
              <input v-model="exampleFormData.context" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
                placeholder="VD: Khi đang ngạc nhiên" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Từ cần tô màu (highlight)</label>
              <input v-model="exampleFormData.highlight" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
                placeholder="VD: is sleeping" />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Audio URL (S3 key hoặc CDN)</label>
              <input v-model="exampleFormData.audio_url" type="text" class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)" />
            </div>
          </div>
          <div v-if="exampleFormError" class="rounded-xl p-3 text-sm"
            style="background-color:color-mix(in srgb,#ef4444 12%,transparent);color:#f87171">{{ exampleFormError }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button class="px-4 py-2 text-sm rounded-xl transition hover:opacity-80"
              style="background-color: var(--color-surface-03); color: var(--color-text-muted)" @click="showExampleForm = false">Huỷ</button>
            <button class="px-4 py-2 text-sm rounded-xl font-semibold transition hover:opacity-90"
              style="background-color: var(--color-primary-500); color: #fff" :disabled="exampleFormLoading" @click="submitExampleForm">
              {{ exampleFormLoading ? 'Đang lưu...' : 'Lưu' }}</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── EXAMPLE DELETE CONFIRM ───────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="exampleDeleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)" @click.self="exampleDeleteTarget = null">
        <div class="w-full max-w-sm rounded-2xl p-6 space-y-4" style="background-color: var(--color-surface-01)">
          <h3 class="text-base font-bold" style="color: var(--color-text-base)">Xác nhận xoá Example</h3>
          <p class="text-sm" style="color: var(--color-text-muted)">
            Xoá example "<strong>{{ exampleDeleteTarget.sentence?.slice(0, 60) }}</strong>..."?
          </p>
          <div class="flex justify-end gap-3">
            <button class="px-4 py-2 text-sm rounded-xl" style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
              @click="exampleDeleteTarget = null">Huỷ</button>
            <button class="px-4 py-2 text-sm rounded-xl font-semibold transition hover:opacity-90"
              style="background-color: #ef4444; color: #fff" :disabled="exampleDeleteLoading" @click="deleteExample">
              {{ exampleDeleteLoading ? 'Đang xoá...' : 'Xoá' }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { adminApi } from '@/api/admin.js'

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const globalError = ref(null)

// ── Topics ─────────────────────────────────────────────────────────────────
const topics = ref([])
const topicsLoading = ref(false)
const selectedTopic = ref(null)
const topicFilter = reactive({ level: '', search: '' })

let searchTimer = null
function debouncedFetchTopics() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchTopics, 400)
}

async function fetchTopics() {
  topicsLoading.value = true
  globalError.value = null
  try {
    const params = {}
    if (topicFilter.level) params.level = topicFilter.level
    if (topicFilter.search) params.search = topicFilter.search
    const { data } = await adminApi.getGrammarTopics(params)
    topics.value = data.results ?? data
  } catch {
    globalError.value = 'Không thể tải danh sách topic.'
  } finally {
    topicsLoading.value = false
  }
}

function selectTopic(topic) {
  selectedTopic.value = topic
  selectedRule.value = null
  examples.value = []
  fetchRules(topic.id)
}

// ── Topic form ──────────────────────────────────────────────────────────────
const showTopicForm = ref(false)
const topicFormLoading = ref(false)
const topicFormError = ref(null)
const topicDeleteTarget = ref(null)
const topicDeleteLoading = ref(false)
const topicFormData = reactive({
  id: null, title: '', slug: '', level: 'A1', chapter: null, order: 0,
  icon: '📚', description: '', analogy: '', real_world_use: '', memory_hook: '',
  is_published: true,
})

const chapterOptions = ref([])
async function fetchChaptersForLevel(level) {
  chapterOptions.value = []
  if (!level) return
  try {
    const { data } = await adminApi.getGrammarChapters({ level })
    chapterOptions.value = data.results ?? data
  } catch { /* ignore */ }
}
watch(() => topicFormData.level, (lvl) => fetchChaptersForLevel(lvl))

function openTopicForm(topic = null) {
  topicFormError.value = null
  if (topic) {
    Object.assign(topicFormData, {
      id: topic.id, title: topic.title, slug: topic.slug, level: topic.level,
      chapter: topic.chapter?.id ?? null, order: topic.order, icon: topic.icon || '📚',
      description: topic.description || '', analogy: topic.analogy || '',
      real_world_use: topic.real_world_use || '', memory_hook: topic.memory_hook || '',
      is_published: topic.is_published,
    })
  } else {
    Object.assign(topicFormData, {
      id: null, title: '', slug: '', level: topicFilter.level || 'A1', chapter: null, order: 0,
      icon: '📚', description: '', analogy: '', real_world_use: '', memory_hook: '',
      is_published: true,
    })
  }
  fetchChaptersForLevel(topicFormData.level)
  showTopicForm.value = true
}

async function submitTopicForm() {
  topicFormError.value = null
  if (!topicFormData.title) { topicFormError.value = 'Vui lòng nhập tiêu đề.'; return }
  topicFormLoading.value = true
  try {
    const payload = {
      title: topicFormData.title,
      level: topicFormData.level,
      chapter: topicFormData.chapter || null,
      order: topicFormData.order,
      icon: topicFormData.icon,
      description: topicFormData.description,
      analogy: topicFormData.analogy,
      real_world_use: topicFormData.real_world_use,
      memory_hook: topicFormData.memory_hook,
      is_published: topicFormData.is_published,
    }
    if (topicFormData.slug) payload.slug = topicFormData.slug
    if (topicFormData.id) {
      await adminApi.updateGrammarTopic(topicFormData.id, payload)
    } else {
      await adminApi.createGrammarTopic(payload)
    }
    showTopicForm.value = false
    await fetchTopics()
  } catch (e) {
    topicFormError.value = e?.response?.data?.detail || JSON.stringify(e?.response?.data) || 'Không thể lưu topic.'
  } finally {
    topicFormLoading.value = false
  }
}

function confirmDeleteTopic(topic) {
  topicDeleteTarget.value = topic
}

async function deleteTopic() {
  topicDeleteLoading.value = true
  try {
    await adminApi.deleteGrammarTopic(topicDeleteTarget.value.id)
    if (selectedTopic.value?.id === topicDeleteTarget.value.id) {
      selectedTopic.value = null
      rules.value = []
      selectedRule.value = null
      examples.value = []
    }
    topicDeleteTarget.value = null
    await fetchTopics()
  } catch {
    globalError.value = 'Không thể xoá topic.'
    topicDeleteTarget.value = null
  } finally {
    topicDeleteLoading.value = false
  }
}

// ── Rules ───────────────────────────────────────────────────────────────────
const rules = ref([])
const rulesLoading = ref(false)
const selectedRule = ref(null)

async function fetchRules(topicId) {
  rulesLoading.value = true
  try {
    const { data } = await adminApi.getGrammarRules(topicId)
    rules.value = data.results ?? data
  } catch {
    globalError.value = 'Không thể tải rules.'
  } finally {
    rulesLoading.value = false
  }
}

function selectRule(rule) {
  selectedRule.value = rule
  fetchExamples(rule.id)
}

// ── Rule form ───────────────────────────────────────────────────────────────
const showRuleForm = ref(false)
const ruleFormLoading = ref(false)
const ruleFormError = ref(null)
const ruleDeleteTarget = ref(null)
const ruleDeleteLoading = ref(false)
const ruleFormData = reactive({
  id: null, title: '', formula: '', explanation: '', memory_hook: '', is_exception: false, order: 0,
})

function openRuleForm(rule = null) {
  ruleFormError.value = null
  if (rule) {
    Object.assign(ruleFormData, {
      id: rule.id, title: rule.title, formula: rule.formula || '',
      explanation: rule.explanation || '', memory_hook: rule.memory_hook || '',
      is_exception: rule.is_exception, order: rule.order,
    })
  } else {
    Object.assign(ruleFormData, {
      id: null, title: '', formula: '', explanation: '', memory_hook: '',
      is_exception: false, order: rules.value.length,
    })
  }
  showRuleForm.value = true
}

async function submitRuleForm() {
  ruleFormError.value = null
  if (!ruleFormData.title) { ruleFormError.value = 'Vui lòng nhập tiêu đề rule.'; return }
  ruleFormLoading.value = true
  try {
    const payload = {
      title: ruleFormData.title,
      formula: ruleFormData.formula,
      explanation: ruleFormData.explanation,
      memory_hook: ruleFormData.memory_hook,
      is_exception: ruleFormData.is_exception,
      order: ruleFormData.order,
    }
    if (ruleFormData.id) {
      await adminApi.updateGrammarRule(selectedTopic.value.id, ruleFormData.id, payload)
    } else {
      await adminApi.createGrammarRule(selectedTopic.value.id, payload)
    }
    showRuleForm.value = false
    await fetchRules(selectedTopic.value.id)
  } catch (e) {
    ruleFormError.value = e?.response?.data?.detail || 'Không thể lưu rule.'
  } finally {
    ruleFormLoading.value = false
  }
}

function confirmDeleteRule(rule) {
  ruleDeleteTarget.value = rule
}

async function deleteRule() {
  ruleDeleteLoading.value = true
  try {
    await adminApi.deleteGrammarRule(selectedTopic.value.id, ruleDeleteTarget.value.id)
    if (selectedRule.value?.id === ruleDeleteTarget.value.id) {
      selectedRule.value = null
      examples.value = []
    }
    ruleDeleteTarget.value = null
    await fetchRules(selectedTopic.value.id)
  } catch {
    globalError.value = 'Không thể xoá rule.'
    ruleDeleteTarget.value = null
  } finally {
    ruleDeleteLoading.value = false
  }
}

// ── Examples ────────────────────────────────────────────────────────────────
const examples = ref([])
const examplesLoading = ref(false)

async function fetchExamples(ruleId) {
  examplesLoading.value = true
  try {
    const { data } = await adminApi.getGrammarExamples(ruleId)
    examples.value = data.results ?? data
  } catch {
    globalError.value = 'Không thể tải examples.'
  } finally {
    examplesLoading.value = false
  }
}

// ── Example form ────────────────────────────────────────────────────────────
const showExampleForm = ref(false)
const exampleFormLoading = ref(false)
const exampleFormError = ref(null)
const exampleDeleteTarget = ref(null)
const exampleDeleteLoading = ref(false)
const exampleFormData = reactive({
  id: null, sentence: '', translation: '', context: '', highlight: '', audio_url: '',
})

function openExampleForm(ex = null) {
  exampleFormError.value = null
  if (ex) {
    Object.assign(exampleFormData, {
      id: ex.id, sentence: ex.sentence, translation: ex.translation || '',
      context: ex.context || '', highlight: ex.highlight || '', audio_url: ex.audio_url || '',
    })
  } else {
    Object.assign(exampleFormData, { id: null, sentence: '', translation: '', context: '', highlight: '', audio_url: '' })
  }
  showExampleForm.value = true
}

async function submitExampleForm() {
  exampleFormError.value = null
  if (!exampleFormData.sentence) { exampleFormError.value = 'Vui lòng nhập câu ví dụ.'; return }
  exampleFormLoading.value = true
  try {
    const payload = {
      sentence: exampleFormData.sentence,
      translation: exampleFormData.translation,
      context: exampleFormData.context,
      highlight: exampleFormData.highlight,
      audio_url: exampleFormData.audio_url || null,
    }
    if (exampleFormData.id) {
      await adminApi.updateGrammarExample(selectedRule.value.id, exampleFormData.id, payload)
    } else {
      await adminApi.createGrammarExample(selectedRule.value.id, payload)
    }
    showExampleForm.value = false
    await fetchExamples(selectedRule.value.id)
  } catch (e) {
    exampleFormError.value = e?.response?.data?.detail || 'Không thể lưu example.'
  } finally {
    exampleFormLoading.value = false
  }
}

function confirmDeleteExample(ex) {
  exampleDeleteTarget.value = ex
}

async function deleteExample() {
  exampleDeleteLoading.value = true
  try {
    await adminApi.deleteGrammarExample(selectedRule.value.id, exampleDeleteTarget.value.id)
    exampleDeleteTarget.value = null
    await fetchExamples(selectedRule.value.id)
  } catch {
    globalError.value = 'Không thể xoá example.'
    exampleDeleteTarget.value = null
  } finally {
    exampleDeleteLoading.value = false
  }
}

onMounted(fetchTopics)
</script>

# 🏗️ CURRICULUM APP — Hướng dẫn Integration

> Tài liệu chi tiết cách **kết nối** curriculum app với các apps khác

---

## 📑 MỤC LỤC

1. [Progress App Integration](#1-progress-app-integration)
2. [Grammar App Integration](#2-grammar-app-integration)
3. [Vocabulary App Integration](#3-vocabulary-app-integration)
4. [Exercises App Integration](#4-exercises-app-integration)
5. [Gamification App Integration](#5-gamification-app-integration)
6. [Common Patterns](#6-common-patterns)

---

## 1. PROGRESS APP INTEGRATION

### Quan hệ quan trọng

```
curriculum.Lesson ←─────→ progress.LessonProgress
     (course structure)        (user progress)
```

### Use Case 1: Student enroll course

**Flow:**
```python
1. Frontend: POST /progress/enroll/
   {
     "course_id": 1
   }

2. Backend (progress app):
   - Create UserEnrollment(user=current_user, course=1, status='active')
   - current_lesson = course.chapters.first().lessons.first()
   - Set as lesson unlocked if no prerequisites

3. Response:
   {
     "enrollment_id": 1,
     "course_id": 1,
     "status": "active",
     "current_lesson": {...}
   }
```

### Use Case 2: Display lesson lock/unlock status

**Backend (curriculum serializer):**
```python
class LessonSerializer(serializers.ModelSerializer):
    is_unlocked = serializers.SerializerMethodField()
    progress_status = serializers.SerializerMethodField()
    
    def get_is_unlocked(self, obj):
        """Check if lesson is unlocked based on prerequisites"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        
        # Get all unlock rules for this lesson
        rules = list(obj.unlock_rules.values("required_lesson_id", "min_score"))
        
        # No rules = unlocked
        if not rules:
            return True
        
        # Check if all prerequisites are met
        from apps.progress.models import LessonProgress
        
        passed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson_id__in=[r["required_lesson_id"] for r in rules],
            status="completed"
        ).values_list("lesson_id", "best_score")
        
        for rule in rules:
            req_id = rule["required_lesson_id"]
            min_score = rule["min_score"]
            
            # Check if required lesson is passed with min_score
            found = any(
                lid == req_id and (score or 0) >= min_score
                for lid, score in passed_lessons
            )
            
            if not found:
                return False
        
        return True
    
    def get_progress_status(self, obj):
        """Get current lesson progress status"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return "locked"
        
        from apps.progress.models import LessonProgress
        
        lp = LessonProgress.objects.filter(
            user=request.user,
            lesson=obj
        ).first()
        
        return lp.status if lp else "locked"
```

**Frontend (LessonDetailView.vue):**
```vue
<template>
  <div class="lesson-detail">
    <!-- Status display -->
    <span class="status-badge" :class="lesson.progress_status">
      {{ statusLabel(lesson.progress_status) }}
    </span>
    
    <!-- Lock gate -->
    <div v-if="lesson.progress_status === 'locked'" class="locked-gate">
      <p>🔒 Bài học này chưa được mở</p>
      <p>Hoàn thành các bài học trước để mở khoá</p>
      
      <!-- Show prerequisites -->
      <div v-for="rule in lesson.unlock_rules" :key="rule.id">
        <p>Yêu cầu: {{ rule.required_lesson_title }} ≥ {{ rule.min_score }}%</p>
      </div>
    </div>
    
    <!-- Content (only if unlocked) -->
    <div v-else-if="lesson.progress_status !== 'locked'">
      <!-- Lesson content here -->
    </div>
  </div>
</template>
```

### Use Case 3: Mark lesson as complete

**Flow:**
```
Frontend: POST /progress/lessons/{id}/complete/
  {
    "score": 85
  }

Backend (progress app):
  1. Update LessonProgress(lesson={id}, status='completed', best_score=85)
  2. Calculate XP
  3. Check unlock rules → auto-unlock next lessons
  4. Award badges/achievements
  5. Update UserEnrollment.progress_percent

Response:
  {
    "status": "completed",
    "best_score": 85,
    "xp_awarded": 60,
    "unlocked_lessons": [5, 6]
  }
```

### Database schema (progress app)

```python
class LessonProgress(models.Model):
    STATUS_CHOICES = [
        ("locked", "Chưa mở"),
        ("in_progress", "Đang học"),
        ("completed", "Hoàn thành"),
        ("failed", "Không đạt"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey("curriculum.Lesson", on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    best_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    attempts = models.SmallIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 2. GRAMMAR APP INTEGRATION

### Quan hệ

```
curriculum.LessonContent
    ├─ grammar_topic_id → grammar.GrammarTopic.id (soft reference)
    └─ grammar_sections[].grammar_topic_id → grammar.GrammarTopic.id
```

### Use Case 1: Link lesson to grammar topic

**Backend setup:**
```python
# In seed_grammar_lessons.py
from apps.curriculum.models import Lesson, LessonContent
from apps.grammar.models import GrammarTopic

# For each lesson
lesson = Lesson.objects.get(id=1)
content = lesson.content or LessonContent.objects.create(lesson=lesson)

# Find matching grammar topic
topic = GrammarTopic.objects.filter(title__icontains="present simple").first()

if topic:
    content.grammar_topic_id = topic.id
    content.grammar_title = topic.title
    content.grammar_note = topic.explanation
    content.save()
```

### Use Case 2: Display grammar section with exercises

**LessonContent JSON structure:**
```json
{
  "grammar_sections": [
    {
      "title": "Present Simple",
      "grammar_topic_id": 42,
      "note": "Use to describe habitual actions...",
      "examples": [
        {
          "en": "She eats rice every day.",
          "vi": "Cô ấy ăn cơm mỗi ngày.",
          "highlight": "eats"
        }
      ],
      "exercises": [
        {
          "type": "gap-fill",
          "prompt": "I ___ (eat) rice.",
          "options": ["eat", "eats", "eaten"],
          "correct": 0,
          "explanation": "Chủ ngữ là 'I' (ngôi thứ nhất số nhiều), động từ không thay đổi"
        }
      ]
    }
  ]
}
```

**Frontend (GrammarSection.vue):**
```vue
<template>
  <div class="grammar-section">
    <h3>{{ section.title }}</h3>
    
    <!-- Link to full grammar topic -->
    <RouterLink v-if="section.grammar_topic_id"
                :to="`/grammar/${section.grammar_topic_id}`"
                class="link-to-grammar">
      → Xem chuyên đề ngữ pháp đầy đủ
    </RouterLink>
    
    <p class="note">{{ section.note }}</p>
    
    <!-- Examples -->
    <div class="examples">
      <div v-for="(ex, idx) in section.examples" :key="idx" class="example-item">
        <code class="en-text">{{ ex.en }}</code>
        <code class="vi-text">{{ ex.vi }}</code>
      </div>
    </div>
    
    <!-- Exercises -->
    <div v-for="(ex, idx) in section.exercises" :key="'ex-' + idx"
         class="exercise-item">
      <p v-if="ex.type === 'gap-fill'" class="prompt">
        {{ renderGapFill(ex.prompt) }}
        <select v-model="answers[idx]">
          <option v-for="(opt, oi) in ex.options" :key="oi" :value="oi">
            {{ opt }}
          </option>
        </select>
      </p>
    </div>
    
    <button @click="checkAnswers" class="btn-primary">Kiểm tra</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  section: Object
})

const answers = ref({})

const checkAnswers = () => {
  // Calculate score
  let correct = 0
  props.section.exercises.forEach((ex, idx) => {
    if (parseInt(answers.value[idx]) === ex.correct) {
      correct++
    }
  })
  
  const percent = (correct / props.section.exercises.length) * 100
  emit('progress', { type: 'grammar', score: percent })
}
</script>
```

---

## 3. VOCABULARY APP INTEGRATION

### Quan hệ

```
curriculum.LessonContent
    ├─ vocab_items[] (inline JSON)
    └─ vocab_word_ids[] → vocabulary.Word.id
```

### Use Case 1: Populate vocab_items in lesson

**Structure:**
```json
{
  "vocab_items": [
    {
      "word": "headache",
      "id": 123,
      "pos": "noun",
      "ipa": "/ˈhed.eɪk/",
      "meaning_vi": "đau đầu",
      "definition_en": "A pain inside your head.",
      "example_en": "I have a headache.",
      "example_vi": "Tôi bị đau đầu.",
      "collocations": ["have a ~", "splitting ~"],
      "highlight_in_passage": true
    }
  ],
  "vocab_word_ids": [123, 124, 125]
}
```

### Use Case 2: SRS review

**Flow:**
```
1. When marking lesson complete:
   - Extract vocab_word_ids from LessonContent
   - Create SRS queue entries in vocabulary app
   - Schedule review for next 24h/3d/7d...

2. When accessing lesson:
   - Load vocab_items for inline display
   - Highlight in reading passage
   - Show tooltip with meaning
```

### Use Case 3: Add to flashcard

**Frontend (VocabFootnote.vue):**
```vue
<template>
  <div class="vocab-footnote">
    <span class="word">{{ word }}</span>
    <span class="ipa">{{ vocab.ipa }}</span>
    <span class="meaning">{{ vocab.meaning_vi }}</span>
    
    <button @click="addToFlashcard" class="btn-small">
      ➕ Thêm vào flashcard
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { vocabularyApi } from '@/api/curriculum'

const props = defineProps({
  vocab: Object,
  word: String
})

const addToFlashcard = async () => {
  try {
    await vocabularyApi.addToFlashcard(props.vocab.id)
    showNotification('✓ Đã thêm vào flashcard')
  } catch (err) {
    showError('Lỗi: ' + err.message)
  }
}
</script>
```

---

## 4. EXERCISES APP INTEGRATION

### Polymorphic linking

```
curriculum.Lesson
    ↓
curriculum.LessonExercise (exercise_type + exercise_id)
    ↓
exercises_listenngexercise / exercises_speakingexercise / ...
```

### Use Case: Fetch and render exercise

**Backend (LessonExercise):**
```python
class LessonExercise(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="exercises")
    exercise_type = models.CharField(max_length=15, choices=EXERCISE_TYPES)
    exercise_id = models.BigIntegerField()
    order = models.SmallIntegerField(default=1)
    passing_score = models.SmallIntegerField(default=60)
```

**Frontend API call:**
```javascript
// curriculum.js
export const exercisesApi = {
  getListening: (id) => api.get(`/exercises/listening/${id}/`),
  getSpeaking: (id) => api.get(`/exercises/speaking/${id}/`),
  getReading: (id) => api.get(`/exercises/reading/${id}/`),
  getWriting: (id) => api.get(`/exercises/writing/${id}/`),
}

export function getExercise(type, id) {
  switch (type) {
    case 'listening': return exercisesApi.getListening(id)
    case 'speaking': return exercisesApi.getSpeaking(id)
    case 'reading': return exercisesApi.getReading(id)
    case 'writing': return exercisesApi.getWriting(id)
    default: throw new Error(`Unknown exercise type: ${type}`)
  }
}
```

**Frontend component:**
```vue
<template>
  <div class="lesson-exercise">
    <div v-if="loading" class="skeleton"></div>
    
    <div v-else-if="exercise">
      <!-- Render based on exercise.type -->
      <ListeningExercise v-if="exercise.type === 'listening'"
                         :exercise="exercise" @submit="onSubmit" />
      <SpeakingExercise v-else-if="exercise.type === 'speaking'"
                        :exercise="exercise" @submit="onSubmit" />
      <!-- etc -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getExercise } from '@/api/curriculum'

const props = defineProps({
  exerciseType: String,
  exerciseId: Number
})

const exercise = ref(null)
const loading = ref(true)

onMounted(async () => {
  const res = await getExercise(props.exerciseType, props.exerciseId)
  exercise.value = res.data
  loading.value = false
})
</script>
```

---

## 5. GAMIFICATION APP INTEGRATION

### XP Award flow

```
LessonProgress.completed
    ↓
Trigger XP grant:
  - completion_xp (base)
  - +bonus_xp if score >= 80%
    ↓
Call gamification API to award XP
    ↓
Check if eligible for badge/achievement
```

### Backend (progress app marking complete):

```python
from apps.gamification.signals import xp_awarded

def mark_lesson_complete(user, lesson, score):
    progress = LessonProgress.objects.get_or_create(
        user=user, lesson=lesson
    )[0]
    
    progress.status = 'completed'
    progress.best_score = score
    progress.save()
    
    # Award XP
    content = lesson.content
    xp = content.completion_xp
    
    if score >= 80:
        xp += content.bonus_xp
    
    # Signal to gamification app
    xp_awarded.send(
        sender=LessonProgress,
        user=user,
        xp_amount=xp,
        reason=f"completed_lesson_{lesson.id}"
    )
    
    # Check achievements
    check_achievements(user)
```

### Gamification integration in frontend

```vue
<template>
  <div class="lesson-complete-modal">
    <h2>🎉 Hoàn thành bài học!</h2>
    
    <div class="score-display">
      <p class="score">{{ score }}%</p>
      
      <!-- XP display -->
      <div class="xp-award">
        <span v-if="score >= 80" class="xp-base">+{{ baseXp }} XP</span>
        <span v-if="score >= 80" class="xp-bonus">+{{ bonusXp }} XP 🌟</span>
        <span v-else class="xp-base">+{{ baseXp }} XP</span>
      </div>
      
      <!-- Badge unlock -->
      <div v-if="unlockedBadge" class="badge-unlock">
        <p>🏆 Mở khoá badge: {{ unlockedBadge.name }}</p>
      </div>
    </div>
    
    <button @click="continueToNext" class="btn-primary">
      Tiếp tục
    </button>
  </div>
</template>
```

---

## 6. COMMON PATTERNS

### Pattern 1: Lesson context throughout app

**Store lesson info in serializer context:**
```python
# In views.py
def get_serializer_context(self):
    context = super().get_serializer_context()
    context['lesson'] = self.get_object()  # For detail views
    return context
```

### Pattern 2: Nested serialization

```python
class LessonDetailSerializer(serializers.ModelSerializer):
    content = LessonContentSerializer(read_only=True)
    chapter = ChapterSerializer(read_only=True)
    unlock_rules = UnlockRuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'content', 'chapter', 'unlock_rules']
```

### Pattern 3: Computed fields in serializer

```python
class LessonSerializer(serializers.ModelSerializer):
    is_unlocked = serializers.SerializerMethodField()
    progress_status = serializers.SerializerMethodField()
    exercise_type = serializers.SerializerMethodField()
    
    def get_exercise_type(self, obj):
        """Get first exercise type for quick access"""
        exercise = obj.exercises.first()
        return exercise.exercise_type if exercise else obj.lesson_type
```

### Pattern 4: Bulk operations for performance

```python
# Get all lessons for a course with prefetch
lessons = Lesson.objects.filter(
    chapter__course=course
).prefetch_related(
    'exercises',
    'unlock_rules',
    'content'
).select_related(
    'chapter__course__level'
)
```

---

**Kết luận:** Curriculum app là **hub trung tâm** kết nối tất cả các apps khác thông qua các serializer methods, foreign keys, và polymorphic references.

# DATABASE DESIGN — ENGLISH STUDY LMS
**PostgreSQL · Django ORM · Asia/Ho_Chi_Minh · Phiên bản: 1.0 · Cập nhật: 24/03/2026**

> Tài liệu này là nguồn duy nhất về sự thật (Single Source of Truth) cho toàn bộ schema Database.
> Dùng làm đầu vào (mồi) cho AI khi viết Backend Django ở Bước 4.

---

## MỤC LỤC

1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [App: users](#2-app-users)
3. [App: curriculum](#3-app-curriculum)
4. [App: exercises](#4-app-exercises)
5. [App: progress](#5-app-progress)
6. [App: vocabulary](#6-app-vocabulary)
7. [App: pronunciation](#7-app-pronunciation)
8. [App: assessment](#8-app-assessment)
9. [App: gamification](#9-app-gamification)
10. [App: payments](#10-app-payments)
11. [App: notifications](#11-app-notifications)
12. [App: classes](#12-app-classes)
13. [App: content](#13-app-content)
14. [ERD — Quan hệ chính](#14-erd--quan-hệ-chính)
15. [Quy ước chung](#15-quy-ước-chung)

---

## 1. TỔNG QUAN KIẾN TRÚC

```
english_study_project/
├── apps/
│   ├── users/          # Auth, Profile, Subscription
│   ├── curriculum/     # Cây khóa học: Level → Course → Chapter → Lesson → Exercise
│   ├── exercises/      # Nội dung bài tập 4 kỹ năng + Question Bank
│   ├── progress/       # Tiến trình học, kết quả, AI grading jobs
│   ├── vocabulary/     # Oxford 3000/5000, Flashcard, SRS
│   ├── pronunciation/  # 4-stage phoneme curriculum, minimal pairs
│   ├── assessment/     # Bộ đề kiểm tra, thi lớp
│   ├── gamification/   # XP, Badges, Leaderboard, Certificates
│   ├── payments/       # Subscription, Coupon, Transaction
│   ├── notifications/  # In-app, Email, Push
│   ├── classes/        # Lớp học giáo viên, giao bài
│   └── content/        # Source files (S3 mapping)
```

**Tổng: 12 apps · ~58 bảng chính**

---

## 2. APP: USERS

### `users_user` *(custom AbstractUser)*
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `email` | EmailField(150) | UNIQUE, NOT NULL |
| `username` | CharField(150) | UNIQUE, NOT NULL |
| `password` | CharField(128) | NOT NULL (Argon2 hash) |
| `role` | CharField(10) | CHOICES: `admin` / `teacher` / `student` |
| `account_type` | CharField(10) | CHOICES: `demo` / `premium` |
| `current_level` | CharField(3) | CHOICES: A1/A2/B1/B2/C1/C2, default=`A1` |
| `target_level` | CharField(3) | default=`B2` |
| `is_active` | BooleanField | default=True |
| `is_deleted` | BooleanField | default=False *(Soft-Delete)* |
| `date_joined` | DateTimeField | auto_now_add=True (Asia/Ho_Chi_Minh) |
| `last_login` | DateTimeField | nullable |

**Index:** `email`, `role`, `is_deleted`

---

### `users_userprofile`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE, OneToOne |
| `avatar` | ImageField | upload_to='avatars/', nullable |
| `phone` | CharField(15) | nullable |
| `date_of_birth` | DateField | nullable |
| `gender` | CharField(10) | CHOICES: male/female/other, nullable |
| `bio` | TextField | nullable |
| `native_language` | CharField(5) | default=`vi` |
| `preferred_accent` | CharField(5) | CHOICES: `uk`/`us`, default=`uk` |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

---

### `users_usersettings`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE, OneToOne |
| `dark_mode` | BooleanField | default=False |
| `daily_goal_minutes` | IntegerField | default=20 |
| `reminder_time` | TimeField | nullable *(giờ nhắc học hàng ngày)* |
| `notify_streak` | BooleanField | default=True |
| `notify_flashcard_due` | BooleanField | default=True |
| `notify_new_lesson` | BooleanField | default=True |
| `language_ui` | CharField(5) | default=`vi` |

---

### `users_sessiontoken` *(JWT refresh token tracking — multi-device)*
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `jti` | CharField(64) | UNIQUE *(JWT ID)* |
| `device_name` | CharField(100) | nullable |
| `ip_address` | GenericIPAddressField | nullable |
| `created_at` | DateTimeField | auto_now_add=True |
| `expires_at` | DateTimeField | NOT NULL |
| `is_revoked` | BooleanField | default=False |

**Index:** `user + is_revoked`, `jti`

---

## 3. APP: CURRICULUM

### `curriculum_cefrlevel`
| Field | Type | Constraints |
|---|---|---|
| `id` | SmallAutoField | PK |
| `code` | CharField(3) | UNIQUE — A1/A2/B1/B2/C1 |
| `name` | CharField(50) | VD: "Elementary" |
| `name_vi` | CharField(50) | VD: "Sơ cấp" |
| `order` | SmallIntegerField | db_index=True |
| `description` | TextField | nullable |
| `is_active` | BooleanField | default=True |

---

### `curriculum_course`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `level` | FK → curriculum_cefrlevel | CASCADE |
| `title` | CharField(200) | NOT NULL |
| `slug` | SlugField(200) | UNIQUE |
| `description` | TextField | nullable |
| `thumbnail` | ImageField | nullable |
| `order` | SmallIntegerField | db_index=True |
| `is_premium` | BooleanField | default=True |
| `is_active` | BooleanField | default=True |
| `created_by` | FK → users_user | SET_NULL, nullable |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**Index:** `level + order`, `slug`

---

### `curriculum_chapter`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `course` | FK → curriculum_course | CASCADE |
| `title` | CharField(200) | NOT NULL |
| `order` | SmallIntegerField | db_index=True |
| `description` | TextField | nullable |
| `passing_score` | SmallIntegerField | default=60 *(0-100)* |
| `created_at` | DateTimeField | auto_now_add=True |

**Index:** `course + order`

---

### `curriculum_lesson`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `chapter` | FK → curriculum_chapter | CASCADE |
| `title` | CharField(200) | NOT NULL |
| `order` | SmallIntegerField | db_index=True |
| `lesson_type` | CharField(15) | CHOICES: `listening`/`speaking`/`reading`/`writing`/`vocabulary`/`pronunciation`/`assessment` |
| `estimated_minutes` | SmallIntegerField | default=15 |
| `is_active` | BooleanField | default=True |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**Index:** `chapter + order`, `lesson_type`

---

### `curriculum_exercise`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `lesson` | FK → curriculum_lesson | CASCADE |
| `exercise_type` | CharField(15) | CHOICES: `listening`/`speaking`/`reading`/`writing` |
| `exercise_id` | BigIntegerField | ID trong bảng exercise cụ thể |
| `order` | SmallIntegerField | default=1 |
| `passing_score` | SmallIntegerField | default=60 |

*(Polymorphic reference: exercise_type + exercise_id trỏ đến bảng tương ứng trong app exercises)*

---

### `curriculum_unlockrule`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `lesson` | FK → curriculum_lesson | CASCADE *(bài cần mở)* |
| `required_lesson` | FK → curriculum_lesson | CASCADE *(bài phải hoàn thành trước)* |
| `min_score` | SmallIntegerField | default=60 |

**Ràng buộc:** Một bài học có thể có nhiều `required_lesson` (AND logic — phải đủ hết).

---

## 4. APP: EXERCISES

### `exercises_listeningexercise`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `title` | CharField(200) | NOT NULL |
| `audio_file` | CharField(500) | S3 key của file MP3 |
| `audio_duration_seconds` | IntegerField | nullable |
| `transcript` | TextField | nullable |
| `context_hint` | TextField | nullable |
| `cefr_level` | CharField(3) | FK-like, indexed |
| `created_at` | DateTimeField | auto_now_add=True |

---

### `exercises_speakingexercise`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `title` | CharField(200) | NOT NULL |
| `scenario` | TextField | Mô tả tình huống nhập vai |
| `dialogue_json` | JSONField | Mảng `[{role, text, audio_key}]` |
| `target_sentence` | TextField | Câu học viên cần nói |
| `target_audio_key` | CharField(500) | S3 key audio mẫu |
| `karaoke_words_json` | JSONField | `[{word, start_ms, end_ms}]` |
| `cefr_level` | CharField(3) | indexed |
| `created_at` | DateTimeField | auto_now_add=True |

---

### `exercises_readingexercise`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `title` | CharField(200) | NOT NULL |
| `article_text` | TextField | Nội dung bài đọc (HTML/Markdown) |
| `vocab_tooltip_json` | JSONField | `[{word, ipa, meaning_vi}]` |
| `cefr_level` | CharField(3) | indexed |
| `created_at` | DateTimeField | auto_now_add=True |

---

### `exercises_writingexercise`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `title` | CharField(200) | NOT NULL |
| `prompt_text` | TextField | Đề bài |
| `prompt_description` | TextField | Hướng dẫn chi tiết |
| `min_words` | SmallIntegerField | default=150 |
| `max_words` | SmallIntegerField | default=300 |
| `time_limit_minutes` | SmallIntegerField | default=30 |
| `structure_tips_json` | JSONField | Mảng gợi ý cấu trúc bài |
| `cefr_level` | CharField(3) | indexed |
| `created_at` | DateTimeField | auto_now_add=True |

---

### `exercises_question`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `exercise_type` | CharField(15) | `listening`/`reading` |
| `exercise_id` | BigIntegerField | ID bài tập chứa câu hỏi |
| `question_type` | CharField(15) | CHOICES: `mc`/`gap_fill`/`drag_drop` |
| `question_text` | TextField | NOT NULL |
| `order` | SmallIntegerField | default=1 |
| `correct_answers_json` | JSONField | Mảng đáp án đúng (hỗ trợ nhiều đáp án) |
| `explanation` | TextField | nullable — giải thích đáp án |
| `points` | SmallIntegerField | default=1 |
| `is_locked_initially` | BooleanField | default=False |

---

### `exercises_questionoption` *(MC options)*
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `question` | FK → exercises_question | CASCADE |
| `option_text` | CharField(500) | NOT NULL |
| `order` | SmallIntegerField | default=1 |

---

### `exercises_examset`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `title` | CharField(200) | NOT NULL |
| `skill` | CharField(10) | CHOICES: `listening`/`reading`/`mixed` |
| `cefr_level` | CharField(3) | indexed |
| `time_limit_minutes` | SmallIntegerField | NOT NULL |
| `passing_score` | SmallIntegerField | default=60 |
| `total_questions` | SmallIntegerField | computed or manual |
| `structure_json` | JSONField | `{mc: 10, gap_fill: 5, drag_drop: 5}` |
| `is_active` | BooleanField | default=True |
| `created_by` | FK → users_user | SET_NULL |
| `created_at` | DateTimeField | auto_now_add=True |

---

## 5. APP: PROGRESS

### `progress_userenrollment`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `course` | FK → curriculum_course | CASCADE |
| `status` | CharField(15) | CHOICES: `active`/`paused`/`completed`/`dropped` |
| `progress_percent` | DecimalField(5,2) | default=0.00 |
| `current_lesson` | FK → curriculum_lesson | SET_NULL, nullable |
| `enrolled_at` | DateTimeField | auto_now_add=True |
| `completed_at` | DateTimeField | nullable |
| `last_activity_at` | DateTimeField | auto_now=True |
| `is_deleted` | BooleanField | default=False *(Soft-Delete)* |

**Index:** `user + status`, `course + status`, `user + course` UNIQUE (khi không deleted)

---

### `progress_lessonprogress`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `lesson` | FK → curriculum_lesson | CASCADE |
| `status` | CharField(15) | CHOICES: `locked`/`available`/`in_progress`/`completed` |
| `best_score` | SmallIntegerField | nullable *(0-100)* |
| `attempts_count` | SmallIntegerField | default=0 |
| `time_spent_seconds` | IntegerField | default=0 |
| `completed_at` | DateTimeField | nullable |
| `updated_at` | DateTimeField | auto_now=True |

**Index:** `user + lesson` UNIQUE, `user + status`

---

### `progress_exerciseresult`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `lesson` | FK → curriculum_lesson | nullable |
| `exercise_type` | CharField(15) | `listening`/`reading`/`speaking`/`writing` |
| `exercise_id` | BigIntegerField | ID của exercise cụ thể |
| `score` | SmallIntegerField | 0-100 |
| `passed` | BooleanField | score >= passing_score |
| `time_spent_seconds` | IntegerField | default=0 |
| `detail_json` | JSONField | Chi tiết từng câu: `[{q_id, user_ans, correct, points}]` |
| `created_at` | DateTimeField | auto_now_add=True |
| `is_deleted` | BooleanField | default=False |

**Index:** `user + exercise_type + exercise_id`, `user + created_at`

---

### `progress_speakingsubmission`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `exercise_id` | BigIntegerField | FK-like → exercises_speakingexercise |
| `lesson` | FK → curriculum_lesson | nullable |
| `audio_s3_key` | CharField(500) | S3 key file ghi âm |
| `audio_duration_seconds` | FloatField | nullable |
| `audio_size_bytes` | IntegerField | nullable |
| `status` | CharField(15) | CHOICES: `pending`/`processing`/`completed`/`failed` |
| `transcript` | TextField | nullable *(từ Whisper)* |
| `ai_score` | SmallIntegerField | nullable *(0-100)* |
| `pronunciation_score` | SmallIntegerField | nullable |
| `fluency_score` | SmallIntegerField | nullable |
| `intonation_score` | SmallIntegerField | nullable |
| `vocab_score` | SmallIntegerField | nullable |
| `error_list_json` | JSONField | `[{type, word, suggestion}]`, nullable |
| `submitted_at` | DateTimeField | auto_now_add=True |
| `graded_at` | DateTimeField | nullable |
| `is_deleted` | BooleanField | default=False |

**Index:** `user + status`, `user + exercise_id`

---

### `progress_writingsubmission`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `exercise_id` | BigIntegerField | FK-like → exercises_writingexercise |
| `lesson` | FK → curriculum_lesson | nullable |
| `content_text` | TextField | NOT NULL |
| `word_count` | SmallIntegerField | NOT NULL |
| `status` | CharField(15) | `pending`/`processing`/`completed`/`failed` |
| `ai_score` | SmallIntegerField | nullable |
| `task_achievement_score` | SmallIntegerField | nullable |
| `grammar_score` | SmallIntegerField | nullable |
| `vocabulary_score` | SmallIntegerField | nullable |
| `coherence_score` | SmallIntegerField | nullable |
| `feedback_text` | TextField | nullable *(AI tổng nhận xét)* |
| `error_list_json` | JSONField | `[{type, original, suggestion, explanation}]`, nullable |
| `vocab_cefr_json` | JSONField | `[{word, cefr_level}]` — các từ trong bài kèm CEFR, nullable |
| `submitted_at` | DateTimeField | auto_now_add=True |
| `graded_at` | DateTimeField | nullable |
| `teacher_comment` | TextField | nullable *(Teacher Override)* |
| `is_deleted` | BooleanField | default=False |

**Index:** `user + status`, `user + exercise_id`

---

### `progress_aigradingjob`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `job_type` | CharField(15) | CHOICES: `speaking`/`writing` |
| `submission_id` | BigIntegerField | ID trong SpeakingSubmission hoặc WritingSubmission |
| `celery_task_id` | CharField(128) | UNIQUE, nullable |
| `status` | CharField(15) | `queued`/`processing`/`completed`/`failed`/`retrying` |
| `retry_count` | SmallIntegerField | default=0 |
| `error_message` | TextField | nullable |
| `ai_model_used` | CharField(50) | VD: `whisper-1`, `gpt-4o` |
| `tokens_used` | IntegerField | nullable *(cost tracking)* |
| `queued_at` | DateTimeField | auto_now_add=True |
| `started_at` | DateTimeField | nullable |
| `completed_at` | DateTimeField | nullable |

**Index:** `status`, `job_type + status`, `celery_task_id`

---

### `progress_dailystreak`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE, OneToOne |
| `current_streak` | SmallIntegerField | default=0 |
| `longest_streak` | SmallIntegerField | default=0 |
| `last_activity_date` | DateField | nullable *(ngày cuối học, timezone VN)* |
| `streak_protected_until` | DateField | nullable *(streak freeze item)* |
| `updated_at` | DateTimeField | auto_now=True |

---

### `progress_cumulativescore`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `level` | FK → curriculum_cefrlevel | CASCADE |
| `listening_avg` | DecimalField(5,2) | default=0 |
| `speaking_avg` | DecimalField(5,2) | default=0 |
| `reading_avg` | DecimalField(5,2) | default=0 |
| `writing_avg` | DecimalField(5,2) | default=0 |
| `overall_avg` | DecimalField(5,2) | computed: weighted avg |
| `total_exercises_done` | IntegerField | default=0 |
| `cefr_equivalent` | CharField(3) | nullable — auto từ Section 7.4 |
| `updated_at` | DateTimeField | auto_now=True |

**Index:** `user + level` UNIQUE

---

## 6. APP: VOCABULARY

### `vocabulary_word`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `word` | CharField(100) | NOT NULL, db_index=True |
| `part_of_speech` | CharField(20) | noun/verb/adjective/adverb/... |
| `cefr_level` | CharField(3) | A1/A2/B1/B2/C1 |
| `domain` | CharField(30) | business/casual/medical/academic/travel, nullable |
| `ipa_uk` | CharField(100) | nullable |
| `ipa_us` | CharField(100) | nullable |
| `audio_uk_key` | CharField(500) | S3 key, nullable |
| `audio_us_key` | CharField(500) | S3 key, nullable |
| `meaning_vi` | TextField | NOT NULL |
| `definition_en` | TextField | nullable |
| `example_en` | TextField | nullable |
| `example_vi` | TextField | nullable |
| `collocations_json` | JSONField | `["make a decision", "take a photo"]`, nullable |
| `mnemonic` | TextField | nullable |
| `etymology` | TextField | nullable |
| `synonyms_json` | JSONField | `["choose", "pick"]`, nullable |
| `antonyms_json` | JSONField | nullable |
| `frequency_rank` | IntegerField | nullable |
| `register` | CharField(15) | formal/informal/slang/academic, nullable |
| `image_key` | CharField(500) | S3 key, nullable |
| `is_oxford_3000` | BooleanField | default=False |
| `is_oxford_5000` | BooleanField | default=False |
| `created_at` | DateTimeField | auto_now_add=True |

**Index:** `word`, `cefr_level`, `domain`, `is_oxford_3000`

---

### `vocabulary_flashcarddeck`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `name` | CharField(200) | NOT NULL |
| `description` | TextField | nullable |
| `owner` | FK → users_user | nullable *(null = system deck)* |
| `cefr_level` | CharField(3) | nullable |
| `domain` | CharField(30) | nullable |
| `is_public` | BooleanField | default=True |
| `created_at` | DateTimeField | auto_now_add=True |

---

### `vocabulary_flashcard`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `deck` | FK → vocabulary_flashcarddeck | CASCADE |
| `word` | FK → vocabulary_word | CASCADE, nullable |
| `front_text` | CharField(300) | NOT NULL |
| `back_text` | TextField | NOT NULL |
| `card_type` | CharField(20) | `word_to_def`/`def_to_word`/`audio_to_word` |
| `order` | SmallIntegerField | default=1 |

---

### `vocabulary_userflashcardprogress` *(SM-2 state per user per card)*
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `flashcard` | FK → vocabulary_flashcard | CASCADE |
| `ease_factor` | FloatField | default=2.5 *(SM-2)* |
| `interval_days` | SmallIntegerField | default=1 |
| `repetition_count` | SmallIntegerField | default=0 |
| `next_review_date` | DateField | NOT NULL |
| `last_review_date` | DateField | nullable |
| `last_quality_rating` | SmallIntegerField | nullable *(0-5)* |
| `is_graduated` | BooleanField | default=False |

**Index:** `user + next_review_date`, `user + flashcard` UNIQUE

---

### `vocabulary_studysession`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `deck` | FK → vocabulary_flashcarddeck | nullable |
| `new_cards_studied` | SmallIntegerField | default=0 |
| `review_cards_done` | SmallIntegerField | default=0 |
| `total_time_seconds` | IntegerField | default=0 |
| `accuracy_percent` | DecimalField(5,2) | nullable |
| `created_at` | DateTimeField | auto_now_add=True |

---

## 7. APP: PRONUNCIATION

### `pronunciation_curriculumstage`
| Field | Type | Constraints |
|---|---|---|
| `id` | SmallAutoField | PK |
| `name` | CharField(100) | NOT NULL |
| `name_vi` | CharField(100) | nullable |
| `description` | TextField | nullable |
| `stage_number` | SmallIntegerField | UNIQUE *(1-4)* |
| `focus_area` | CharField(200) | VD: "Mouth shape, tongue position" |
| `objectives_json` | JSONField | Mảng mục tiêu học |
| `estimated_lessons` | SmallIntegerField | nullable |
| `estimated_hours` | SmallIntegerField | nullable |
| `color_hex` | CharField(7) | default=`#5B6EFF` |
| `passing_score` | SmallIntegerField | default=70 |
| `order` | SmallIntegerField | db_index=True |
| `is_active` | BooleanField | default=True |

### `pronunciation_curriculumstage_prerequisites` *(M2M self)*
| Field | Type |
|---|---|
| `from_stage_id` | FK → pronunciation_curriculumstage |
| `to_stage_id` | FK → pronunciation_curriculumstage |

---

### `pronunciation_phonemeexercise`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `stage` | FK → pronunciation_curriculumstage | CASCADE |
| `phoneme_ipa` | CharField(10) | VD: `/æ/` |
| `phoneme_description` | CharField(200) | nullable |
| `audio_key` | CharField(500) | S3 key audio mẫu |
| `mouth_diagram_key` | CharField(500) | S3 key hình minh họa, nullable |
| `example_words_json` | JSONField | `["cat", "hat", "man"]` |
| `order` | SmallIntegerField | default=1 |

---

### `pronunciation_minimalpairset`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `stage` | FK → pronunciation_curriculumstage | CASCADE |
| `word_a` | CharField(50) | NOT NULL |
| `word_b` | CharField(50) | NOT NULL |
| `phoneme_a` | CharField(10) | IPA của word_a |
| `phoneme_b` | CharField(10) | IPA của word_b |
| `audio_a_key` | CharField(500) | NOT NULL |
| `audio_b_key` | CharField(500) | NOT NULL |
| `difficulty` | CharField(10) | easy/medium/hard |

---

### `pronunciation_userstageprogress`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `stage` | FK → pronunciation_curriculumstage | CASCADE |
| `status` | CharField(15) | `locked`/`in_progress`/`completed` |
| `best_score` | SmallIntegerField | nullable |
| `attempts` | SmallIntegerField | default=0 |
| `completed_at` | DateTimeField | nullable |

**Index:** `user + stage` UNIQUE

---

## 8. APP: ASSESSMENT

### `assessment_questionbank`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `question_text` | TextField | NOT NULL |
| `question_type` | CharField(15) | `mc`/`gap_fill`/`drag_drop` |
| `skill` | CharField(10) | `listening`/`reading`/`writing` |
| `cefr_level` | CharField(3) | indexed |
| `topic` | CharField(100) | nullable |
| `difficulty` | CharField(10) | easy/medium/hard |
| `correct_answers_json` | JSONField | NOT NULL |
| `options_json` | JSONField | nullable *(cho MC)* |
| `explanation` | TextField | nullable |
| `source_audio_key` | CharField(500) | nullable *(cho listening)* |
| `source_text` | TextField | nullable *(cho reading)* |
| `created_by` | FK → users_user | SET_NULL |
| `created_at` | DateTimeField | auto_now_add=True |

**Index:** `skill + cefr_level`, `difficulty`

---

### `assessment_classexam`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `teacher_class` | FK → classes_teacherclass | CASCADE |
| `title` | CharField(200) | NOT NULL |
| `description` | TextField | nullable |
| `questions_json` | JSONField | Mảng question_bank IDs |
| `time_limit_minutes` | SmallIntegerField | NOT NULL |
| `passing_score` | SmallIntegerField | default=60 |
| `deadline` | DateTimeField | NOT NULL |
| `allow_retake` | BooleanField | default=False |
| `is_active` | BooleanField | default=True |
| `created_at` | DateTimeField | auto_now_add=True |

---

### `assessment_examattempt`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `exam` | FK → assessment_classexam | CASCADE |
| `score` | SmallIntegerField | nullable |
| `passed` | BooleanField | nullable |
| `answers_json` | JSONField | `[{q_id, user_answer, is_correct}]` |
| `started_at` | DateTimeField | auto_now_add=True |
| `submitted_at` | DateTimeField | nullable |
| `time_taken_seconds` | IntegerField | nullable |
| `is_deleted` | BooleanField | default=False |

**Index:** `user + exam` UNIQUE *(khi allow_retake=False)*

---

## 9. APP: GAMIFICATION

### `gamification_achievement`
| Field | Type | Constraints |
|---|---|---|
| `id` | SmallAutoField | PK |
| `code` | CharField(50) | UNIQUE |
| `name` | CharField(100) | NOT NULL |
| `name_vi` | CharField(100) | NOT NULL |
| `description_vi` | TextField | nullable |
| `category` | CharField(20) | `streak`/`skill`/`speed`/`social`/`milestone` |
| `condition_type` | CharField(50) | VD: `streak_days`, `skill_score_gte`, `lessons_count` |
| `threshold_value` | IntegerField | Giá trị ngưỡng kích hoạt |
| `icon_url` | CharField(500) | nullable |
| `xp_reward` | IntegerField | default=0 |
| `is_active` | BooleanField | default=True |

---

### `gamification_userachievement`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `achievement` | FK → gamification_achievement | CASCADE |
| `earned_at` | DateTimeField | auto_now_add=True |

**Index:** `user + achievement` UNIQUE

---

### `gamification_xplog`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `amount` | SmallIntegerField | NOT NULL *(positive = gain)* |
| `reason` | CharField(50) | `exercise_complete`/`perfect_score`/`streak_bonus`/`daily_challenge`/`chapter_complete`/`achievement` |
| `reference_id` | BigIntegerField | nullable *(ID bài tập hoặc achievement)* |
| `created_at` | DateTimeField | auto_now_add=True |

**Index:** `user + created_at`

---

### `gamification_leaderboardsnapshot`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `period` | CharField(10) | `weekly`/`monthly`/`all_time` |
| `period_key` | CharField(10) | VD: `2026-W12` hoặc `2026-03`, `all` |
| `total_xp` | IntegerField | NOT NULL |
| `rank` | IntegerField | NOT NULL |
| `snapshot_at` | DateTimeField | auto_now_add=True |

**Index:** `period + period_key + rank`, `user + period + period_key` UNIQUE

---

### `gamification_certificate`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `level` | FK → curriculum_cefrlevel | CASCADE |
| `verification_code` | CharField(32) | UNIQUE |
| `cumulative_score` | DecimalField(5,2) | NOT NULL |
| `issued_at` | DateTimeField | auto_now_add=True |
| `pdf_s3_key` | CharField(500) | nullable |

---

### `gamification_dailychallenge`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `challenge_date` | DateField | UNIQUE *(ngày VN timezone)* |
| `exercise_type` | CharField(15) | NOT NULL |
| `exercise_id` | BigIntegerField | NOT NULL |
| `xp_reward` | SmallIntegerField | default=20 |

### `gamification_dailychallengeattempt`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `challenge` | FK → gamification_dailychallenge | CASCADE |
| `completed` | BooleanField | default=False |
| `score` | SmallIntegerField | nullable |
| `attempted_at` | DateTimeField | auto_now_add=True |

**Index:** `user + challenge` UNIQUE

---

## 10. APP: PAYMENTS

### `payments_subscriptionplan`
| Field | Type | Constraints |
|---|---|---|
| `id` | SmallAutoField | PK |
| `name` | CharField(50) | UNIQUE — monthly/yearly/single_course |
| `name_vi` | CharField(100) | NOT NULL |
| `price_vnd` | IntegerField | NOT NULL *(giá gốc, không dấu chấm — format ở FE)* |
| `duration_days` | SmallIntegerField | nullable *(null = vĩnh viễn cho single course)* |
| `features_json` | JSONField | Danh sách tính năng hiển thị |
| `is_active` | BooleanField | default=True |

---

### `payments_usersubscription`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE, OneToOne |
| `plan` | FK → payments_subscriptionplan | SET_NULL, nullable |
| `status` | CharField(15) | `active`/`expired`/`cancelled`/`trial` |
| `start_date` | DateTimeField | NOT NULL |
| `end_date` | DateTimeField | nullable |
| `auto_renew` | BooleanField | default=False |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

---

### `payments_coupon`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `code` | CharField(20) | UNIQUE |
| `discount_type` | CharField(10) | `percent`/`fixed_vnd` |
| `discount_value` | IntegerField | NOT NULL |
| `applicable_plan` | FK → payments_subscriptionplan | nullable *(null = áp dụng tất cả)* |
| `max_uses` | IntegerField | nullable *(null = không giới hạn)* |
| `uses_count` | IntegerField | default=0 |
| `valid_from` | DateTimeField | NOT NULL |
| `valid_until` | DateTimeField | NOT NULL |
| `is_active` | BooleanField | default=True |
| `created_by` | FK → users_user | SET_NULL |

---

### `payments_couponredemption`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `coupon` | FK → payments_coupon | CASCADE |
| `user` | FK → users_user | CASCADE |
| `redeemed_at` | DateTimeField | auto_now_add=True |

**Index:** `coupon + user` UNIQUE

---

### `payments_transaction`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `plan` | FK → payments_subscriptionplan | SET_NULL |
| `coupon` | FK → payments_coupon | SET_NULL, nullable |
| `amount_vnd` | IntegerField | NOT NULL *(số tiền thực thu)* |
| `original_amount_vnd` | IntegerField | NOT NULL *(trước giảm giá)* |
| `discount_amount_vnd` | IntegerField | default=0 |
| `status` | CharField(15) | `pending`/`completed`/`failed`/`refunded` |
| `payment_gateway` | CharField(20) | `vnpay`/`stripe`/`manual` |
| `gateway_transaction_id` | CharField(200) | nullable |
| `gateway_response_json` | JSONField | nullable *(raw webhook data)* |
| `created_at` | DateTimeField | auto_now_add=True |
| `updated_at` | DateTimeField | auto_now=True |

**Index:** `user + status`, `gateway_transaction_id`

---

## 11. APP: NOTIFICATIONS

### `notifications_notification`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE |
| `notification_type` | CharField(30) | `lesson_unlocked`/`ai_graded`/`flashcard_due`/`streak_warning`/`assignment`/`system` |
| `title` | CharField(200) | NOT NULL |
| `body` | TextField | NOT NULL |
| `action_url` | CharField(500) | nullable |
| `is_read` | BooleanField | default=False |
| `created_at` | DateTimeField | auto_now_add=True |

**Index:** `user + is_read`, `user + created_at`

---

### `notifications_notificationsetting`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | CASCADE, OneToOne |
| `enabled_types_json` | JSONField | Danh sách loại notification bật |
| `email_enabled` | BooleanField | default=True |
| `push_enabled` | BooleanField | default=True |

---

### `notifications_emailtemplate`
| Field | Type | Constraints |
|---|---|---|
| `id` | SmallAutoField | PK |
| `name` | CharField(50) | UNIQUE |
| `subject` | CharField(200) | NOT NULL |
| `html_body` | TextField | NOT NULL *(hỗ trợ `{{ var }}`)* |
| `trigger_event` | CharField(50) | `welcome`/`payment_confirmed`/`streak_lost`/`certificate`/`manual` |
| `is_active` | BooleanField | default=True |

---

### `notifications_emaillog`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `user` | FK → users_user | SET_NULL, nullable |
| `template` | FK → notifications_emailtemplate | SET_NULL |
| `to_email` | EmailField | NOT NULL |
| `subject` | CharField(200) | NOT NULL |
| `status` | CharField(15) | `sent`/`failed`/`bounced` |
| `sent_at` | DateTimeField | auto_now_add=True |
| `celery_task_id` | CharField(128) | nullable |

---

## 12. APP: CLASSES

### `classes_teacherclass`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `teacher` | FK → users_user | CASCADE |
| `name` | CharField(200) | NOT NULL |
| `description` | TextField | nullable |
| `join_code` | CharField(10) | UNIQUE *(random 6-char)* |
| `is_active` | BooleanField | default=True |
| `created_at` | DateTimeField | auto_now_add=True |

---

### `classes_classenrollment`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `student` | FK → users_user | CASCADE |
| `class_obj` | FK → classes_teacherclass | CASCADE |
| `joined_at` | DateTimeField | auto_now_add=True |
| `is_active` | BooleanField | default=True |

**Index:** `student + class_obj` UNIQUE

---

### `classes_assignedexercise`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `teacher_class` | FK → classes_teacherclass | CASCADE |
| `assigned_to` | FK → users_user | nullable *(null = cả lớp)* |
| `exercise_type` | CharField(15) | NOT NULL |
| `exercise_id` | BigIntegerField | NOT NULL |
| `due_date` | DateTimeField | nullable |
| `note` | TextField | nullable |
| `created_at` | DateTimeField | auto_now_add=True |

---

## 13. APP: CONTENT

### `content_sourcefile`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `file_type` | CharField(20) | `audio`/`grammar_doc`/`vocabulary_csv`/`image`/`pronunciation_audio` |
| `original_name` | CharField(300) | NOT NULL |
| `s3_key` | CharField(500) | UNIQUE |
| `s3_bucket` | CharField(100) | NOT NULL |
| `file_size_bytes` | BigIntegerField | nullable |
| `mime_type` | CharField(100) | nullable |
| `level` | FK → curriculum_cefrlevel | nullable |
| `course` | FK → curriculum_course | SET_NULL, nullable |
| `uploaded_by` | FK → users_user | SET_NULL |
| `created_at` | DateTimeField | auto_now_add=True |

---

### `content_lessonsource`
| Field | Type | Constraints |
|---|---|---|
| `id` | BigAutoField | PK |
| `lesson` | FK → curriculum_lesson | CASCADE |
| `source_file` | FK → content_sourcefile | CASCADE |
| `role` | CharField(30) | `main_audio`/`background`/`reference_doc`/`vocabulary` |

---

## 14. ERD — QUAN HỆ CHÍNH

```
users_user
  ├─1:1─► users_userprofile
  ├─1:1─► users_usersettings
  ├─1:1─► payments_usersubscription
  ├─1:1─► progress_dailystreak
  ├─1:1─► gamification_leaderboardsnapshot (nhiều rows per user)
  ├─1:N─► progress_userenrollment ──► curriculum_course
  ├─1:N─► progress_lessonprogress ──► curriculum_lesson
  ├─1:N─► progress_exerciseresult
  ├─1:N─► progress_speakingsubmission
  ├─1:N─► progress_writingsubmission
  ├─1:N─► progress_cumulativescore ──► curriculum_cefrlevel
  ├─1:N─► vocabulary_userflashcardprogress ──► vocabulary_flashcard
  ├─1:N─► vocabulary_studysession
  ├─1:N─► gamification_xplog
  ├─1:N─► gamification_userachievement ──► gamification_achievement
  ├─1:N─► gamification_certificate ──► curriculum_cefrlevel
  ├─1:N─► notifications_notification
  └─1:N─► payments_transaction

curriculum_cefrlevel
  └─1:N─► curriculum_course
              └─1:N─► curriculum_chapter
                          └─1:N─► curriculum_lesson
                                      └─1:N─► curriculum_exercise
                                      └─1:N─► curriculum_unlockrule

exercises_listeningexercise / speakingexercise / readingexercise / writingexercise
  └─1:N─► exercises_question ──► exercises_questionoption

progress_speakingsubmission / progress_writingsubmission
  └─1:1─► progress_aigradingjob (Celery async grading)

vocabulary_flashcarddeck
  └─1:N─► vocabulary_flashcard
              └─1:N─► vocabulary_userflashcardprogress

classes_teacherclass
  ├─1:N─► classes_classenrollment ──► users_user
  └─1:N─► classes_assignedexercise
```

---

## 15. QUY ƯỚC CHUNG

### 1. Timezone
- **Tất cả** `DateTimeField` dùng `USE_TZ=True` + `TIME_ZONE='Asia/Ho_Chi_Minh'` trong Django settings.
- Lưu UTC trong DB, Django tự convert khi đọc.
- API response serialize về ISO 8601 với offset `+07:00`.

### 2. Số tiền (VND)
- Lưu dạng **Integer (đồng)**, không có dấu chấm.
- Format ra `vi-VN` ở tầng Frontend/Serializer: `1490000` → `1.490.000 đ`

### 3. Soft-Delete
Các bảng có `is_deleted = BooleanField(default=False)`:
- `users_user`, `progress_userenrollment`, `progress_exerciseresult`
- `progress_speakingsubmission`, `progress_writingsubmission`
- `assessment_examattempt`, `payments_transaction`

Dùng custom Manager: `objects = ActiveManager()` lọc `is_deleted=False` mặc định.

### 4. Performance Indexes
Ngoài index đã ghi trong từng bảng, thêm composite index:
- `progress_exerciseresult(user, exercise_type, created_at)`
- `vocabulary_userflashcardprogress(user, next_review_date, is_graduated)`
- `notifications_notification(user, is_read, created_at)`
- `gamification_xplog(user, created_at)` *(weekly XP aggregation)*

### 5. Security
- Passwords: Django mặc định PBKDF2, khuyến nghị migrate sang **Argon2** (`django-argon2`).
- `users_sessiontoken`: verify `jti` claim trong JWT middleware để revoke token tức thì.
- `payments_transaction.gateway_response_json`: không log thông tin thẻ, chỉ lưu transaction ID.
- `content_sourcefile.s3_key`: generate signed URL (TTL 1 giờ) cho file media có kiểm soát truy cập.

### 6. Số bảng theo app
| App | Số bảng |
|---|---|
| users | 4 |
| curriculum | 6 |
| exercises | 6 |
| progress | 8 |
| vocabulary | 5 |
| pronunciation | 5 |
| assessment | 3 |
| gamification | 7 |
| payments | 5 |
| notifications | 4 |
| classes | 3 |
| content | 2 |
| **TỔNG** | **58** |

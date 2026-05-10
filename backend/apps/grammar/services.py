"""apps/grammar/services.py"""
import random
import re
import logging
from django.core.cache import cache
import uuid
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import (
    GrammarTopic,
    GrammarRule,
    GrammarQuizAttempt,
    GrammarQuizAnswer,
    GrammarQuizResult,
    GrammarExample,
    GrammarReviewSchedule, 
    ErrorPattern,
    GrammarQuizQuestion
)

logger = logging.getLogger(__name__)
QUIZ_CACHE_TTL = 60 * 60 * 24 * 7  # 7 ngày
QUIZ_CACHE_PREFIX = "grammar:quiz:"

def invalidate_quiz_cache(topic_slug: str):
    """Gọi khi admin cập nhật topic/rules/examples để cache không bị stale."""
    cache.delete(f"{QUIZ_CACHE_PREFIX}{topic_slug}")

def pregenerate_quiz(topic_slug: str, difficulty: int = None) -> list[dict]:
    """
    Sinh quiz từ GrammarExample, cache kết quả.
    Ưu tiên trả về câu hỏi Admin đã duyệt (is_verified=True).
    Nếu chưa có, tự sinh và LƯU (persist) xuống DB để Admin duyệt sau.
    """
    cache_key = f"{QUIZ_CACHE_PREFIX}{topic_slug}:{difficulty or 'all'}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.debug(f"Cache HIT: {cache_key} ({len(cached)} questions)")
        return cached

    logger.debug(f"Cache MISS: {cache_key}. Đang query DB...")
    topic = GrammarTopic.objects.filter(slug=topic_slug, is_published=True).prefetch_related(
        "rules", "rules__examples"
    ).first()
    if not topic:
        logger.warning(f"Topic not found or unpublished: {topic_slug}")
        return []

    # 1. Ưu tiên verified questions
    verified_qs = GrammarQuizQuestion.objects.filter(topic=topic, is_verified=True)
    if difficulty:
        verified_qs = verified_qs.filter(difficulty=difficulty)
    verified_qs = verified_qs.select_related("rule", "source_example").order_by("type", "id")

    logger.debug(f"Found {verified_qs.count()} verified questions for '{topic_slug}'")

    if verified_qs.exists():
        questions = [
            {
                "type": q.type, "source_id": q.source_example_id, "rule_id": q.rule_id,
                "prompt": q.prompt, "options": q.options, "correct_index": q.correct_index,
                "explanation": q.explanation, "difficulty": getattr(q, "difficulty", 2),
            }
            for q in verified_qs
        ]
        cache.set(cache_key, questions, QUIZ_CACHE_TTL)
        logger.info(f"✅ Returning {len(questions)} VERIFIED questions for '{topic_slug}'")
        return questions

    # 2. Fallback auto-generate (filter example theo difficulty nếu có)
    logger.info(f"⚠️ No verified questions. Falling back to auto-gen for '{topic_slug}'...")
    all_examples = []
    for rule in topic.rules.all():
        ex_qs = rule.examples.all()
        if difficulty:
            ex_qs = ex_qs.filter(difficulty=difficulty)
        for ex in ex_qs:
            if ex.sentence and ex.highlight:
                all_examples.append({
                    "id": ex.id, "rule_id": rule.id, "sentence": ex.sentence,
                    "translation": ex.translation or "", "highlight": ex.highlight,
                    "difficulty": getattr(ex, "difficulty", 2),
                })

    if not all_examples:
        logger.warning(f"❌ No valid examples for topic '{topic_slug}'.")
        return []

    questions = []
    target_len = len(all_examples)

    # ── TYPE 1: GAP-FILL ─────────────────────────────────────────────
    for ex in all_examples:
        if len(questions) >= min(5, target_len):
            break
        pattern = re.compile(re.escape(ex["highlight"]), re.IGNORECASE)
        if not pattern.search(ex["sentence"]):
            continue

        prompt = pattern.sub('<strong style="color:#818cf8">______</strong>', ex["sentence"], count=1)
        candidates = [e["highlight"] for e in all_examples if e["highlight"].lower() != ex["highlight"].lower()]
        hl_len = len(ex["highlight"])
        candidates = [c for c in candidates if abs(len(c) - hl_len) <= 4]
        candidates = list(dict.fromkeys(candidates))

        if len(candidates) < 2:
            continue

        distractors = random.sample(candidates, min(3, len(candidates)))
        options = distractors + [ex["highlight"]]
        random.shuffle(options)
        correct_idx = options.index(ex["highlight"])

        questions.append({
            "type": "gap-fill", "source_id": ex["id"], "rule_id": ex["rule_id"],
            "prompt": prompt, "options": options, "correct_index": correct_idx,
            "explanation": ex["translation"], "difficulty": ex.get("difficulty", 2),
        })

    # ── TYPE 2: MULTIPLE CHOICE ──────────────────────────────────────
    rules_with_ex = [r for r in topic.rules.all() if r.examples.filter(is_correct=True).exists()]
    for rule in rules_with_ex:
        if len(questions) >= min(8, target_len + 3):
            break
        correct_ex = rule.examples.filter(is_correct=True).first()
        if not correct_ex:
            continue

        wrong_sentences = list(
            GrammarExample.objects.filter(rule__topic__level=topic.level, is_correct=True)
            .exclude(rule__topic=topic).values_list("sentence", flat=True)[:3]
        )
        if len(wrong_sentences) < 2:
            continue

        options = wrong_sentences + [correct_ex.sentence]
        random.shuffle(options)
        correct_idx = options.index(correct_ex.sentence)

        questions.append({
            "type": "mc", "source_id": correct_ex.id, "rule_id": rule.id,
            "prompt": f'Câu nào minh họa đúng cho quy tắc "{rule.title}"?',
            "options": options, "correct_index": correct_idx,
            "explanation": correct_ex.translation or "",
        })

    # ── PERSIST XUỐNG DB ─────────────────────────────────────────────
    for q in questions:
        GrammarQuizQuestion.objects.get_or_create(
            topic=topic, source_example_id=q["source_id"], type=q["type"],
            defaults={
                "rule_id": q.get("rule_id"), "prompt": q["prompt"], "options": q["options"],
                "correct_index": q["correct_index"], "explanation": q.get("explanation", ""),
                "is_auto_generated": True, "needs_review": True,
            }
        )

    # Chỉ cache khi có dữ liệu để tránh giữ mảng rỗng stale trong dev
    if questions:
        cache.set(cache_key, questions, QUIZ_CACHE_TTL)
        logger.info(f"🔄 Auto-generated & persisted {len(questions)} questions for '{topic_slug}'")
    return questions

def submit_quiz_attempt(user, topic_slug: str, answers_payload: list[dict]) -> dict:
    """
    Xử lý submit quiz:
    1. Validate & chấm điểm server-side
    2. Lưu Attempt + Answer chi tiết
    3. Upsert GrammarQuizResult (giữ max score)
    4. Sync LessonProgress explicit (không dùng signal)
    5. Trả về kết quả chi tiết cho frontend
    """
    topic = GrammarTopic.objects.filter(slug=topic_slug, is_published=True).first()
    if not topic:
        raise ValueError("Chủ điểm không tồn tại hoặc chưa publish.")

    # Lấy quiz đã sinh sẵn từ cache/DB để đối chiếu đáp án
    cached_quiz = pregenerate_quiz(topic_slug)
    if not cached_quiz:
        raise ValueError("Chưa có bài tập cho chủ điểm này.")

    # Map source_id → correct data để chấm nhanh O(1)
    answer_key = {q["source_id"]: q for q in cached_quiz}

    with transaction.atomic():
        attempt = GrammarQuizAttempt.objects.create(
            user=user, topic=topic, started_at=timezone.now(), completed_at=timezone.now()
        )

        correct_count = 0
        total = len(answers_payload)

        for ans in answers_payload:
            src_id = ans["question_source_id"]
            selected = ans["selected_option"]
            correct_data = answer_key.get(src_id)

            if not correct_data:
                continue # Bỏ qua câu hỏi không hợp lệ

            is_correct = (selected == correct_data["options"][correct_data["correct_index"]])
            update_srs(user, correct_data.get("rule_id"), is_correct)
            track_error_pattern(
                user,
                correct_data.get("rule_id"),
                is_correct,
                selected,
                correct_data["options"][correct_data["correct_index"]]
            )
            if is_correct:
                correct_count += 1

            GrammarQuizAnswer.objects.create(
                attempt=attempt,
                rule_id=correct_data.get("rule_id"),
                question_source_id=src_id,
                selected_option=selected,
                is_correct=is_correct,
            )

        score = round((correct_count / total * 100), 2) if total > 0 else 0
        attempt.score = score
        attempt.save(update_fields=["score"])

        # Upsert aggregate result (giữ điểm cao nhất)
        result, created = GrammarQuizResult.objects.update_or_create(
            user=user, topic=topic,
            defaults={
                "score": score,
                "total_questions": total,
                "correct_answers": correct_count,
            }
        )
        # Nếu điểm mới cao hơn điểm cũ, cập nhật; nếu không, giữ nguyên max
        if not created and score > result.score:
            result.score = score
            result.total_questions = total
            result.correct_answers = correct_count
            result.save(update_fields=["score", "total_questions", "correct_answers", "attempted_at"])

        # Explicit Progress Sync (Phase 1.4 logic embedded)
        sync_lesson_progress(user, topic, score)

        # Tính weak_rules (rule có error count >= 2)
        weak_rules = list(
            ErrorPattern.objects.filter(user=user, count__gte=2)
            .select_related("rule")
            .values_list("rule__title", flat=True)
            .distinct()[:3]
        )
        
        # Tìm lần ôn gần nhất trong 3 ngày tới
        next_review_obj = GrammarReviewSchedule.objects.filter(
            user=user, next_review__lte=timezone.now().date() + timedelta(days=3)
        ).order_by("next_review").first()

    # Gom remedial status theo rule xuất hiện trong quiz
    remedial_map = {}
    for ans in answers_payload:
        src_id = ans["question_source_id"]
        q_data = answer_key.get(src_id)
        if q_data and q_data.get("rule_id"):
            rid = q_data["rule_id"]
            if rid not in remedial_map:
                remedial_map[rid] = get_remedial_status(user, rid)
    
    # ── Remedial Logic ─────────────────────────────────────────────────────
    remedial_map = {}
    for ans in answers_payload:
        src_id = ans["question_source_id"]
        q_data = answer_key.get(src_id)
        if q_data and q_data.get("rule_id"):
            rid = q_data["rule_id"]
            if rid not in remedial_map:
                remedial_map[rid] = get_remedial_status(user, rid)

    # Auto-clear nếu điểm lần này >= 80%
    if score >= 80:
        for rid in list(remedial_map.keys()):
            clear_remedial_lock(user, rid)
            remedial_map[rid] = get_remedial_status(user, rid)

    return {
        "attempt_id": attempt.id,
        "score": result.score,
        "current_score": score,
        "total_questions": total,
        "correct_answers": correct_count,
        "next_review_date": next_review_obj.next_review.isoformat() if next_review_obj else None,
        "weak_rules": weak_rules,
        "remedial_rules": remedial_map,
    }

def sync_lesson_progress(user, topic, score: float):
    """
    Explicit sync: Tìm LessonExercise gắn với topic này → cập nhật LessonProgress.
    Thay thế hoàn toàn signal post_save.
    """
    if score < 70:
        return # Chưa đạt ngưỡng hoàn thành

    # Tìm exercise liên kết (giả định model curriculum đã có FK grammar_topic)
    # Tạm thời bypass nếu chưa migrate LessonExercise để tránh crash Phase 1
    try:
        from apps.curriculum.models import LessonExercise, LessonProgress
        exercise = LessonExercise.objects.filter(grammar_topic=topic).first()
        if not exercise:
            return

        progress, _ = LessonProgress.objects.get_or_create(
            user=user, lesson=exercise.lesson,
            defaults={"status": "in_progress"}
        )
        if progress.status != "completed":
            progress.status = "completed"
            progress.completed_at = timezone.now()
            progress.save(update_fields=["status", "completed_at"])
    except Exception:
        pass # Fail-silent nếu curriculum chưa sẵn sàng, sẽ fix ở Phase 1.4

def update_srs(user, rule_id: int, is_correct: bool):
    """
    SM-2 biến thể cho ngữ pháp (binary feedback).
    Track theo Rule, không theo Topic.
    """
    if not rule_id:
        return
    schedule, created = GrammarReviewSchedule.objects.get_or_create(
        user=user, rule_id=rule_id,
        defaults={
            "next_review": timezone.now().date(),
            "interval_days": 1,
            "ease_factor": 2.5
        }
    )
    if is_correct:
        # Đúng: tăng interval, giữ ease_factor ổn định
        new_interval = max(1, int(schedule.interval_days * schedule.ease_factor))
        schedule.interval_days = new_interval
        schedule.ease_factor = max(1.3, min(schedule.ease_factor, 3.0))
    else:
        # Sai: reset về 1 ngày, giảm ease_factor
        schedule.interval_days = 1
        schedule.ease_factor = max(1.3, schedule.ease_factor - 0.2)

    schedule.next_review = timezone.now().date() + timedelta(days=schedule.interval_days)
    schedule.save(update_fields=["next_review", "interval_days", "ease_factor"])


def track_error_pattern(user, rule_id: int, is_correct: bool, selected: str, correct: str):
    """
    Track lỗi sai lặp lại theo Rule.
    Heuristic phân loại lỗi cơ bản (sẽ nâng cấp ở Phase 3).
    """
    if not rule_id or is_correct:
        return

    error_type = "general"
    sel_len, cor_len = len(selected), len(correct)
    if sel_len < cor_len - 2:
        error_type = "thiếu_từ"
    elif sel_len > cor_len + 2:
        error_type = "thừa_từ"
    elif selected.lower().endswith(('s', 'es')) and not correct.lower().endswith(('s', 'es')):
        error_type = "chia_sai_s_es"
    elif not selected.lower().endswith(('s', 'es')) and correct.lower().endswith(('s', 'es')):
        error_type = "quên_chia_s_es"

    pattern, created = ErrorPattern.objects.get_or_create(
        user=user, rule_id=rule_id, error_type=error_type,
        defaults={"count": 1}
    )
    if not created:
        pattern.count += 1
        pattern.last_seen = timezone.now()
        pattern.save(update_fields=["count", "last_seen"])

def get_remedial_status(user, rule_id: int) -> dict:
    """
    Trả về trạng thái remedial của 1 rule cho user.
    Nếu count >= 3 → đề xuất ôn tập & soft-lock bài nâng cao.
    """
    if not rule_id:
        return {"needs_remedial": False, "error_count": 0, "locked": False}

    pattern = ErrorPattern.objects.filter(user=user, rule_id=rule_id).order_by("-count").first()
    count = pattern.count if pattern else 0
    needs_remedial = count >= 3

    return {
        "needs_remedial": needs_remedial,
        "error_count": count,
        "locked": needs_remedial,  # Soft-lock flag
        "error_type": pattern.error_type if pattern else "general",
    }

def clear_remedial_lock(user, rule_id: int):
    """
    Gọi khi học viên vượt qua remedial quiz (score >= 80%).
    Reset error count để gỡ lock.
    """
    ErrorPattern.objects.filter(user=user, rule_id=rule_id).update(count=0, last_seen=timezone.now())

def backfill_difficulty(batch_size: int = 500):
    """
    Gán difficulty cho GrammarExample chưa được gán (hoặc default=2).
    Heuristic:
      - Độ dài câu (số từ)
      - Số mệnh đề/phức tạp (dấu phẩy, liên từ)
      - Rule có is_exception=True → +1 độ khó
    """
    qs = GrammarExample.objects.filter(difficulty=2).select_related("rule")
    total = qs.count()
    updated = 0

    for i in range(0, total, batch_size):
        batch = qs[i:i+batch_size]
        for ex in batch:
            words = ex.sentence.split()
            word_count = len(words)
            
            # Đếm mệnh đề/phức tạp
            clauses = len(re.findall(r'[;,]|\\b(and|but|because|although|if|when|while|so)\\b', ex.sentence, re.IGNORECASE))
            
            base = 2
            if word_count <= 7 and clauses == 0:
                base = 1
            elif word_count >= 14 or clauses >= 2:
                base = 3
            
            # Ngoại lệ ngữ pháp → tăng độ khó
            if ex.rule and ex.rule.is_exception:
                base = min(3, base + 1)
            
            ex.difficulty = base
            ex.save(update_fields=["difficulty"])
            updated += 1

    logger.info(f"Backfilled difficulty for {updated}/{total} examples.")
    return updated
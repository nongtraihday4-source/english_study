from apps.progress.models import LessonProgress
from apps.curriculum.models import UnlockRule

class UnlockService:
    @staticmethod
    def check_lesson_unlocked(user, lesson, rules_cache=None):
        if not user or not user.is_authenticated:
            return False
        rules = rules_cache or list(lesson.unlock_rules.values("required_lesson_id", "min_score"))
        if not rules:
            return True
        
        required_ids = [r["required_lesson_id"] for r in rules]
        passed = LessonProgress.objects.filter(
            user=user, lesson_id__in=required_ids, status="completed"
        ).values_list("lesson_id", "best_score")
        
        passed_dict = {lid: (sc or 0) for lid, sc in passed}
        return all(passed_dict.get(r["required_lesson_id"], 0) >= r["min_score"] for r in rules)

    @staticmethod
    def batch_check_unlocked(user, lessons):
        if not user or not user.is_authenticated:
            return {l.id: False for l in lessons}
        
        lesson_ids = [l.id for l in lessons]
        
        # 1 QUERY: Gom toàn bộ rules của danh sách lessons
        rules_qs = UnlockRule.objects.filter(lesson_id__in=lesson_ids).values("lesson_id", "required_lesson_id", "min_score")
        rules_map = {lid: [] for lid in lesson_ids}
        for r in rules_qs:
            rules_map[r["lesson_id"]].append(r)
            
        all_required_ids = {r["required_lesson_id"] for rules in rules_map.values() for r in rules}
        
        if not all_required_ids:
            return {l.id: True for l in lessons}
            
        # 1 QUERY: Kiểm tra progress của các bài prerequisite
        passed = LessonProgress.objects.filter(
            user=user, lesson_id__in=all_required_ids, status="completed"
        ).values_list("lesson_id", "best_score")
        passed_dict = {lid: (sc or 0) for lid, sc in passed}
        
        result = {}
        for l in lessons:
            rules = rules_map[l.id]
            result[l.id] = not rules or all(passed_dict.get(r["required_lesson_id"], 0) >= r["min_score"] for r in rules)
        return result
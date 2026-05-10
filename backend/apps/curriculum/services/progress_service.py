from apps.progress.models import LessonProgress

class ProgressService:
    @staticmethod
    def get_lesson_status(user, lesson):
        if not user or not user.is_authenticated:
            return "locked"
        lp = LessonProgress.objects.filter(user=user, lesson=lesson).first()
        return lp.status if lp else "locked"

    @staticmethod
    def batch_get_status(user, lessons):
        if not user or not user.is_authenticated:
            return {l.id: "locked" for l in lessons}
        
        lesson_ids = [l.id for l in lessons]
        # Khởi tạo mặc định locked cho tất cả
        result = {lid: "locked" for lid in lesson_ids}
        
        # Override bằng data thực tế từ DB
        progress_qs = LessonProgress.objects.filter(user=user, lesson_id__in=lesson_ids)
        for lp in progress_qs:
            result[lp.lesson_id] = lp.status
            
        return result
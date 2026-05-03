"""
apps/exercises/serializers.py
"""
from rest_framework import serializers

from .models import (
    ListeningExercise,
    SpeakingExercise,
    ReadingExercise,
    WritingExercise,
    Question,
    QuestionOption,
    ExamSet,
)


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "option_text", "order"]


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id", "question_text", "question_type", "order", "points",
            "explanation", "options", "passage_ref_start", "passage_ref_end",
        ]
        # correct_answers_json is NEVER exposed to students


class QuestionWithAnswerSerializer(QuestionSerializer):
    """Admin/teacher only — reveals correct answers for review."""
    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ["correct_answers_json"]


# ── Listening ─────────────────────────────────────────────────────────────────

class ListeningExerciseSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    time_limit = serializers.SerializerMethodField()

    class Meta:
        model = ListeningExercise
        fields = [
            "id", "title", "cefr_level", "audio_url", "context_hint",
            "audio_duration_seconds", "max_plays", "time_limit", "questions", "total_points",
        ]
        # transcript hidden from students

    def get_time_limit(self, obj):
        return obj.time_limit_seconds

    def get_audio_url(self, obj):
        """Generate S3 pre-signed URL for the audio file."""
        if not obj.audio_file:
            return None
        from django.conf import settings
        import boto3
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": obj.audio_file},
                ExpiresIn=settings.AWS_PRESIGNED_URL_EXPIRY,
            )
        except Exception:
            return None

    def get_questions(self, obj):
        qs = Question.objects.filter(
            exercise_type="listening", exercise_id=obj.id
        ).prefetch_related("options").order_by("order")
        return QuestionSerializer(qs, many=True).data

    def get_total_points(self, obj):
        return sum(
            q.points for q in
            Question.objects.filter(exercise_type="listening", exercise_id=obj.id)
        )


# ── Speaking ──────────────────────────────────────────────────────────────────

class SpeakingExerciseSerializer(serializers.ModelSerializer):
    sample_audio_url = serializers.SerializerMethodField()

    class Meta:
        model = SpeakingExercise
        fields = [
            "id", "title", "cefr_level", "scenario", "dialogue_json",
            "target_sentence", "karaoke_words_json", "time_limit_seconds",
            "sample_audio_url",
        ]

    def get_sample_audio_url(self, obj):
        if not obj.target_audio_key:
            return None
        from django.conf import settings
        import boto3
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": obj.target_audio_key},
                ExpiresIn=getattr(settings, "AWS_PRESIGNED_URL_EXPIRY", 3600),
            )
        except Exception:
            return None


# ── Reading ───────────────────────────────────────────────────────────────────

class ReadingExerciseSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    passage = serializers.CharField(source="article_text", read_only=True)
    time_limit = serializers.IntegerField(source="time_limit_seconds", read_only=True)

    class Meta:
        model = ReadingExercise
        fields = [
            "id", "title", "cefr_level", "article_text", "passage",
            "vocab_tooltip_json", "time_limit", "questions", "total_points",
        ]

    def get_questions(self, obj):
        qs = Question.objects.filter(
            exercise_type="reading", exercise_id=obj.id
        ).prefetch_related("options").order_by("order")
        return QuestionSerializer(qs, many=True).data

    def get_total_points(self, obj):
        return sum(
            q.points for q in
            Question.objects.filter(exercise_type="reading", exercise_id=obj.id)
        )


# ── Writing ───────────────────────────────────────────────────────────────────

class WritingExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingExercise
        fields = [
            "id", "title", "cefr_level", "prompt_text", "prompt_description",
            "min_words", "max_words", "time_limit_minutes", "structure_tips_json",
        ]


# ── ExamSet ───────────────────────────────────────────────────────────────────

class ExamQuestionSerializer(serializers.ModelSerializer):
    """Question serializer for exam — includes section info via exercise_type."""
    options = QuestionOptionSerializer(many=True, read_only=True)
    section = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id", "question_text", "question_type", "order", "points",
            "explanation", "options", "section",
            "passage_ref_start", "passage_ref_end",
        ]

    def get_section(self, obj):
        text = (obj.question_text or "").strip().lower()
        if text.startswith("[listening]"):
            return "listening"
        if text.startswith("[reading]"):
            return "reading"
        if text.startswith("[grammar]"):
            return "grammar"
        return "general"


class ExamSetListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = ExamSet
        fields = [
            "id", "title", "exam_type", "skill", "cefr_level",
            "time_limit_minutes", "passing_score", "total_questions",
            "question_count", "is_active",
        ]

    def get_question_count(self, obj):
        return Question.objects.filter(exercise_type="exam", exercise_id=obj.id).count()


class ExamSetDetailSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = ExamSet
        fields = [
            "id", "title", "exam_type", "skill", "cefr_level",
            "time_limit_minutes", "passing_score", "total_questions",
            "structure_json", "is_active", "questions",
        ]

    def get_questions(self, obj):
        qs = Question.objects.filter(
            exercise_type="exam", exercise_id=obj.id
        ).prefetch_related("options").order_by("order")
        return ExamQuestionSerializer(qs, many=True).data

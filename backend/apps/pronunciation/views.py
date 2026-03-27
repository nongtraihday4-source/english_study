import asyncio
import concurrent.futures

from django.http import FileResponse
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from utils.tts import TTSService, TTSVoice

from django.utils import timezone

from .models import MinimalPairSet, Phoneme, PhonemeLesson, PronunciationStage, UserPhonemeProgress
from .serializers import (
    MinimalPairSetSerializer,
    PhonemeChartSerializer,
    PhonemeLessonSerializer,
    PronunciationStageSerializer,
)


class StageListView(ListAPIView):
    """GET /pronunciation/stages/ — all active stages with per-user progress."""

    permission_classes = [IsAuthenticated]
    serializer_class = PronunciationStageSerializer
    pagination_class = None

    def get_queryset(self):
        return PronunciationStage.objects.filter(is_active=True).prefetch_related(
            "lessons__phonemes"
        )


class StageLessonsView(ListAPIView):
    """GET /pronunciation/stages/:id/lessons/ — lessons in a stage."""

    permission_classes = [IsAuthenticated]
    serializer_class = PhonemeLessonSerializer
    pagination_class = None

    def get_queryset(self):
        stage_id = self.kwargs["pk"]
        return PhonemeLesson.objects.filter(
            stage_id=stage_id, is_published=True
        ).prefetch_related("phonemes").order_by("order")


class LessonDetailView(RetrieveAPIView):
    """GET /pronunciation/lessons/:id/ — full lesson with phonemes + sections."""

    permission_classes = [IsAuthenticated]
    serializer_class = PhonemeLessonSerializer
    queryset = PhonemeLesson.objects.filter(is_published=True).prefetch_related("phonemes", "sections")


class LessonDetailBySlugView(RetrieveAPIView):
    """GET /pronunciation/lessons/by-slug/:slug/ — lookup lesson by slug."""

    permission_classes = [IsAuthenticated]
    serializer_class = PhonemeLessonSerializer
    queryset = PhonemeLesson.objects.filter(is_published=True).prefetch_related("phonemes", "sections")
    lookup_field = "slug"


class LessonCompleteView(APIView):
    """
    POST /pronunciation/lessons/:id/complete/
    Body: { score: 80 }  (integer 0-100)
    Marks lesson as completed if score >= 70, updates best score, increments attempts.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        lesson = PhonemeLesson.objects.filter(pk=pk, is_published=True).first()
        if not lesson:
            return Response({"detail": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            score = float(request.data.get("score", 0))
        except (TypeError, ValueError):
            return Response({"detail": "score must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        score = max(0.0, min(100.0, score))
        passed = score >= 70.0
        now = timezone.now()

        prog, created = UserPhonemeProgress.objects.get_or_create(
            user=request.user, lesson=lesson,
            defaults={"score": score, "attempts": 1, "last_practiced_at": now,
                      "is_completed": passed, "completed_at": now if passed else None},
        )
        if not created:
            prog.attempts += 1
            prog.last_practiced_at = now
            if score > prog.score:
                prog.score = score
            if passed and not prog.is_completed:
                prog.is_completed = True
                prog.completed_at = now
            prog.save(update_fields=["attempts", "last_practiced_at", "score", "is_completed", "completed_at"])

        return Response({
            "is_completed": prog.is_completed,
            "score": prog.score,
            "attempts": prog.attempts,
            "passed": passed,
        })


class PhonemeChartView(APIView):
    """
    GET /pronunciation/phonemes/ — full IPA chart grouped by type.
    Returns { vowels: [...], consonants: [...], diphthongs: [...] }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Phoneme.objects.all().order_by("phoneme_type", "order")
        data = PhonemeChartSerializer(qs, many=True).data

        grouped = {"vowel": [], "consonant": [], "diphthong": []}
        for phoneme in data:
            pt = phoneme.get("phoneme_type", "vowel")
            grouped.setdefault(pt, []).append(phoneme)

        return Response(grouped)


class MinimalPairSetListView(ListAPIView):
    """GET /pronunciation/minimal-pairs/ — list of minimal pair exercises."""

    permission_classes = [IsAuthenticated]
    serializer_class = MinimalPairSetSerializer
    pagination_class = None

    def get_queryset(self):
        return MinimalPairSet.objects.filter(is_published=True).prefetch_related("pairs")


class MinimalPairSetDetailView(RetrieveAPIView):
    """GET /pronunciation/minimal-pairs/:id/ — single minimal pair set."""

    permission_classes = [IsAuthenticated]
    serializer_class = MinimalPairSetSerializer
    queryset = MinimalPairSet.objects.filter(is_published=True).prefetch_related("pairs")


# ── TTS ───────────────────────────────────────────────────────────────────────

class TTSThrottle(UserRateThrottle):
    rate = "60/min"


class TTSGenerateView(APIView):
    """
    GET  /pronunciation/tts/?text=hello&voice=en-GB-SoniaNeural
         → streams audio/mpeg binary directly (no /media proxy needed)
    POST /pronunciation/tts/  { text, voice }
         → returns { audio_url } (kept for compatibility)
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [TTSThrottle]

    def _resolve(self, text, voice):
        """Generate (or return cached) audio file path. Runs in a thread."""
        if not text or not text.strip():
            return None
        if len(text) > 500:
            return None
        voice = voice if voice in TTSVoice.ALLOWED else TTSVoice.DEFAULT
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, TTSService.speak_async(text, voice=voice))
            return future.result(timeout=30)

    def get(self, request):
        """Stream mp3 directly — avoids any /media proxy or CORS issues."""
        text = (request.query_params.get("text") or "").strip()
        voice = request.query_params.get("voice") or TTSVoice.DEFAULT

        if not text:
            return Response({"detail": "text is required."}, status=status.HTTP_400_BAD_REQUEST)

        audio_url = self._resolve(text, voice)
        if not audio_url:
            return Response({"detail": "TTS generation failed."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # audio_url is like /media/tts/<voice>/<hash>.mp3 — resolve to filesystem path
        from django.conf import settings
        from pathlib import Path
        media_root = Path(settings.MEDIA_ROOT)
        # Strip leading /media/ prefix to get relative path
        rel = audio_url.lstrip("/")
        if rel.startswith("media/"):
            rel = rel[len("media/"):]
        file_path = media_root / rel

        if not file_path.exists():
            return Response({"detail": "Audio file not found."}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(open(file_path, "rb"), content_type="audio/mpeg")

    def post(self, request):
        text = (request.data.get("text") or "").strip()
        voice = request.data.get("voice") or TTSVoice.DEFAULT

        if not text:
            return Response({"detail": "text is required."}, status=status.HTTP_400_BAD_REQUEST)

        audio_url = self._resolve(text, voice)
        if audio_url is None:
            return Response({"detail": "TTS generation failed."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({"audio_url": audio_url})

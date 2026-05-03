"""
Views for skill_practice app.
All endpoints require authentication.
"""
import difflib
import re
from collections import defaultdict

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.tts import TTSService, TTSVoice

from .models import DictationAttempt, PracticePassage, UserPassageProgress
from .serializers import (
    DictationCheckSerializer,
    PracticePassageDetailSerializer,
    PracticePassageListSerializer,
    ShadowingCompleteSerializer,
)


def _word_diff(correct_text: str, user_text: str) -> tuple:
    """
    Compare user input against correct text using LCS-based alignment.
    Returns (diff_list, accuracy_percent).
    diff_list: [{word, match, correct_word}]
    """
    def normalize(t):
        t = re.sub(r"[^\w\s']", "", t.lower())
        return t.split()

    correct_words = normalize(correct_text)
    user_words = normalize(user_text)

    if not correct_words:
        return [], 100

    # Use SequenceMatcher to find best word alignment (handles insertions/deletions)
    matcher = difflib.SequenceMatcher(None, correct_words, user_words, autojunk=False)
    opcodes = matcher.get_opcodes()

    diff = []
    matched = 0

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            for cw in correct_words[i1:i2]:
                diff.append({"word": cw, "match": True, "correct_word": cw})
                matched += 1
        elif tag == 'replace':
            c_chunk = correct_words[i1:i2]
            u_chunk = user_words[j1:j2]
            for k, cw in enumerate(c_chunk):
                uw = u_chunk[k] if k < len(u_chunk) else ""
                diff.append({"word": uw if uw else f"[{cw}]", "match": False, "correct_word": cw})
            for uw in u_chunk[len(c_chunk):]:
                diff.append({"word": uw, "match": False, "correct_word": ""})
        elif tag == 'delete':
            for cw in correct_words[i1:i2]:
                diff.append({"word": f"[{cw}]", "match": False, "correct_word": cw})
        elif tag == 'insert':
            for uw in user_words[j1:j2]:
                diff.append({"word": uw, "match": False, "correct_word": ""})

    accuracy = int(matched / len(correct_words) * 100)
    return diff, accuracy


def _get_hint(correct_text: str) -> str:
    """Generate a hint: first letter + underscores for each word."""
    words = re.sub(r"[^\w\s']", "", correct_text).split()
    return " ".join(w[0] + "_" * (len(w) - 1) for w in words)


class TopicListView(APIView):
    """
    GET /skill-practice/topics/?level=B1
    Returns topics grouped by CEFR level with passage count and user progress.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        level_filter = request.query_params.get("level")

        qs = PracticePassage.objects.filter(is_published=True)
        if level_filter:
            qs = qs.filter(cefr_level=level_filter)

        stats = (
            qs.values("cefr_level", "topic", "topic_slug")
            .annotate(
                passage_count=Count("id"),
                easy_count=Count("id", filter=Q(difficulty_tag="easy")),
                medium_count=Count("id", filter=Q(difficulty_tag="medium")),
                hard_count=Count("id", filter=Q(difficulty_tag="hard")),
            )
            .order_by("cefr_level", "topic")
        )

        user_progress = UserPassageProgress.objects.filter(
            user=request.user,
            status="completed",
            passage__is_published=True,
        ).values("passage__topic_slug", "mode")

        topic_completion = defaultdict(lambda: {"dictation": 0, "shadowing": 0})
        for p in user_progress:
            slug = p["passage__topic_slug"]
            topic_completion[slug][p["mode"]] += 1

        result = []
        for s in stats:
            slug = s["topic_slug"]
            completion = topic_completion[slug]
            result.append({
                "topic": s["topic"],
                "topic_slug": slug,
                "cefr_level": s["cefr_level"],
                "passage_count": s["passage_count"],
                "easy_count": s["easy_count"],
                "medium_count": s["medium_count"],
                "hard_count": s["hard_count"],
                "dictation_completed": completion["dictation"],
                "shadowing_completed": completion["shadowing"],
            })

        return Response(result)


class PassageListView(ListAPIView):
    """
    GET /skill-practice/passages/?topic_slug=health-symptoms&level=B1
    Returns passages for a topic/level with user progress overlay.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PracticePassageListSerializer
    pagination_class = None

    def get_queryset(self):
        qs = PracticePassage.objects.filter(is_published=True)
        topic_slug = self.request.query_params.get("topic_slug")
        level = self.request.query_params.get("level")
        if topic_slug:
            qs = qs.filter(topic_slug=topic_slug)
        if level:
            qs = qs.filter(cefr_level=level)
        return qs.order_by("difficulty_tag", "id")

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        passages = list(qs)

        passage_ids = [p.id for p in passages]
        progresses = UserPassageProgress.objects.filter(
            user=request.user,
            passage_id__in=passage_ids,
        )
        progress_map = defaultdict(list)
        for prog in progresses:
            progress_map[prog.passage_id].append(prog)

        for passage in passages:
            passage._user_progresses = progress_map.get(passage.id, [])

        serializer = self.get_serializer(passages, many=True)
        return Response(serializer.data)


class PassageDetailView(RetrieveAPIView):
    """GET /skill-practice/passages/{id}/ — full passage detail."""
    permission_classes = [IsAuthenticated]
    serializer_class = PracticePassageDetailSerializer
    queryset = PracticePassage.objects.filter(is_published=True)


class DictationCheckView(APIView):
    """
    POST /skill-practice/passages/{id}/dictation/check/
    Body: {sentence_index, user_input, time_spent_seconds}
    Returns diff result + accuracy, updates progress.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        passage = PracticePassage.objects.filter(pk=pk, is_published=True).first()
        if not passage:
            return Response({"detail": "Passage not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DictationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        sentence_index = data.get("sentence_index")
        user_input = data["user_input"]
        time_spent = data.get("time_spent_seconds", 0)

        if sentence_index is not None:
            sentences = passage.sentences_json or []
            sentence = next((s for s in sentences if s.get("index") == sentence_index), None)
            if not sentence:
                return Response(
                    {"detail": f"Sentence index {sentence_index} not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            correct_text = sentence["text"]
        else:
            correct_text = passage.full_text

        diff, accuracy = _word_diff(correct_text, user_input)

        DictationAttempt.objects.create(
            user=request.user,
            passage=passage,
            sentence_index=sentence_index,
            user_input=user_input,
            accuracy_percent=accuracy,
            diff_json=diff,
        )

        progress, _ = UserPassageProgress.objects.get_or_create(
            user=request.user,
            passage=passage,
            mode="dictation",
            defaults={"status": "in_progress"},
        )
        progress.attempts += 1
        progress.time_spent_seconds += time_spent
        progress.last_practiced_at = timezone.now()

        is_correct = accuracy >= 80

        if is_correct and sentence_index is not None:
            completed = dict(progress.sentences_completed_json)
            completed[str(sentence_index)] = True
            progress.sentences_completed_json = completed

        if accuracy > progress.best_score:
            progress.best_score = accuracy

        total_sentences = len(passage.sentences_json or [])
        if total_sentences > 0:
            all_done = all(
                progress.sentences_completed_json.get(str(i))
                for i in range(total_sentences)
            )
            # Full-passage mode with passing accuracy also completes the passage
            if all_done or (sentence_index is None and is_correct):
                progress.status = "completed"
            elif progress.status == "not_started":
                progress.status = "in_progress"
        elif sentence_index is None and is_correct:
            progress.status = "completed"
        elif progress.status == "not_started":
            progress.status = "in_progress"

        progress.save()

        return Response({
            "accuracy_percent": accuracy,
            "diff": diff,
            "correct_text": correct_text,
            "is_correct": is_correct,
            "hint": _get_hint(correct_text) if not is_correct else None,
            "progress_status": progress.status,
        })


class ShadowingCompleteView(APIView):
    """
    POST /skill-practice/passages/{id}/shadowing/complete/
    Body: {sentence_index, self_rating (1-5), time_spent_seconds}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        passage = PracticePassage.objects.filter(pk=pk, is_published=True).first()
        if not passage:
            return Response({"detail": "Passage not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShadowingCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        sentence_index = data.get("sentence_index")
        self_rating = data["self_rating"]
        time_spent = data.get("time_spent_seconds", 0)

        progress, _ = UserPassageProgress.objects.get_or_create(
            user=request.user,
            passage=passage,
            mode="shadowing",
            defaults={"status": "in_progress"},
        )
        progress.attempts += 1
        progress.time_spent_seconds += time_spent
        progress.last_practiced_at = timezone.now()

        score = int((self_rating / 5) * 100)
        if score > progress.best_score:
            progress.best_score = score

        if sentence_index is not None and self_rating >= 2:
            completed = dict(progress.sentences_completed_json)
            completed[str(sentence_index)] = True
            progress.sentences_completed_json = completed

        total_sentences = len(passage.sentences_json or [])
        if total_sentences > 0:
            all_done = all(
                progress.sentences_completed_json.get(str(i))
                for i in range(total_sentences)
            )
            if all_done:
                progress.status = "completed"
            elif progress.status == "not_started":
                progress.status = "in_progress"
        elif sentence_index is None:
            if self_rating >= 3:
                progress.status = "completed"
            elif progress.status == "not_started":
                progress.status = "in_progress"

        progress.save()

        return Response({
            "recorded_score": score,
            "progress_status": progress.status,
            "sentences_completed_json": progress.sentences_completed_json,
        })


class ProgressSummaryView(APIView):
    """GET /skill-practice/progress/summary/ — user's overall skill practice stats."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        progresses = UserPassageProgress.objects.filter(
            user=request.user
        ).select_related("passage").order_by("-last_practiced_at")

        total_started = progresses.values("passage_id").distinct().count()
        dictation_completed = progresses.filter(mode="dictation", status="completed").count()
        shadowing_completed = progresses.filter(mode="shadowing", status="completed").count()
        total_time = sum(p.time_spent_seconds for p in progresses)

        seen = set()
        recent_passage_ids = []
        for p in progresses:
            if p.passage_id not in seen:
                seen.add(p.passage_id)
                recent_passage_ids.append(p.passage_id)
            if len(recent_passage_ids) >= 5:
                break

        recent_passages_qs = PracticePassage.objects.filter(
            id__in=recent_passage_ids, is_published=True
        )
        passage_map = {p.id: p for p in recent_passages_qs}
        recent_passages = [passage_map[pid] for pid in recent_passage_ids if pid in passage_map]

        prog_map = defaultdict(list)
        for pr in progresses:
            prog_map[pr.passage_id].append(pr)
        for passage in recent_passages:
            passage._user_progresses = prog_map.get(passage.id, [])

        return Response({
            "total_passages_started": total_started,
            "dictation_completed": dictation_completed,
            "shadowing_completed": shadowing_completed,
            "total_time_seconds": total_time,
            "recent_passages": PracticePassageListSerializer(
                recent_passages,
                many=True,
                context={"request": request},
            ).data,
        })


class OnDemandTTSView(APIView):
    """
    GET /skill-practice/passages/{id}/tts/{sentence_index}/
    Returns TTS audio URL for a specific sentence (on-demand fallback).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, sentence_index):
        passage = PracticePassage.objects.filter(pk=pk, is_published=True).first()
        if not passage:
            return Response({"detail": "Passage not found."}, status=status.HTTP_404_NOT_FOUND)

        sentences = passage.sentences_json or []
        sentence = next((s for s in sentences if s.get("index") == sentence_index), None)
        if not sentence:
            return Response({"detail": "Sentence not found."}, status=status.HTTP_404_NOT_FOUND)

        tts = TTSService()
        audio_url = tts.speak(sentence["text"], voice=passage.tts_voice or TTSVoice.US_FEMALE)

        if not audio_url:
            return Response(
                {"detail": "TTS generation failed."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"audio_url": audio_url})

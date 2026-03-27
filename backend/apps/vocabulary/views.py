"""
apps/vocabulary/views.py
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status as drf_status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.permissions import IsAdmin
from .models import Flashcard, FlashcardDeck, StudySession, UserFlashcardProgress, Word
from .serializers import (
    FlashcardDeckSerializer,
    FlashcardSerializer,
    FlashcardStudySerializer,
    SM2UpdateSerializer,
    UserFlashcardProgressSerializer,
    WordSerializer,
)


class WordListView(generics.ListAPIView):
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["cefr_level", "domain", "part_of_speech", "is_oxford_3000", "is_oxford_5000"]
    search_fields = ["word", "meaning_vi"]
    ordering_fields = ["word", "frequency_rank", "cefr_level"]

    def get_queryset(self):
        return Word.objects.all()


class WordDetailView(generics.RetrieveAPIView):
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Word.objects.all()


class FlashcardAddWordView(APIView):
    """
    POST /api/vocabulary/flashcards/add-word/
    Adds a word to a specified deck (deck_id) or to 'My Words' if no deck_id given.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from django.db.models import Q
        word_id = request.data.get('word_id')
        deck_id = request.data.get('deck_id')  # optional
        if not word_id:
            return Response({'error': 'word_id required'}, status=drf_status.HTTP_400_BAD_REQUEST)
        try:
            word = Word.objects.get(pk=word_id)
        except Word.DoesNotExist:
            return Response({'error': 'Word not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        if deck_id:
            try:
                deck = FlashcardDeck.objects.get(
                    Q(owner=request.user) | Q(is_public=True, owner__isnull=False), pk=deck_id
                )
                # Public system decks should not be writable by students
                if deck.owner and deck.owner != request.user:
                    return Response({'error': 'Not authorized to add to this deck'}, status=drf_status.HTTP_403_FORBIDDEN)
            except FlashcardDeck.DoesNotExist:
                return Response({'error': 'Deck not found'}, status=drf_status.HTTP_404_NOT_FOUND)
        else:
            deck, _ = FlashcardDeck.objects.get_or_create(
                owner=request.user,
                name='My Words',
                defaults={'description': 'Từ vựng đã lưu', 'is_public': False},
            )

        # Create all 3 card types for a richer study experience
        card_configs = [
            ('word_to_def',   word.word,                         word.meaning_vi, 1),
            ('def_to_word',   word.meaning_vi or word.word,      word.word,       2),
            ('audio_to_word', word.word,                         word.word,       3),
        ]
        first_card = None
        newly_created = False
        for ctype, front, back, order in card_configs:
            fc, cr = Flashcard.objects.get_or_create(
                deck=deck, word=word, card_type=ctype,
                defaults={'front_text': front, 'back_text': back, 'order': order},
            )
            if ctype == 'word_to_def':
                first_card = fc
                newly_created = cr
        return Response({
            'status': 'added' if newly_created else 'exists',
            'deck_id': deck.id,
            'deck_name': deck.name,
            'card_id': first_card.id,
        })


class FlashcardDeckListView(generics.ListCreateAPIView):
    serializer_class = FlashcardDeckSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["cefr_level", "domain"]
    search_fields = ["name"]

    def get_queryset(self):
        user = self.request.user
        from django.db.models import Q
        return FlashcardDeck.objects.filter(Q(owner=user) | Q(is_public=True))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FlashcardStudyView(generics.RetrieveAPIView):
    serializer_class = FlashcardStudySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        return FlashcardDeck.objects.filter(Q(owner=user) | Q(is_public=True))

    def retrieve(self, request, *args, **kwargs):
        from django.utils import timezone
        from itertools import chain as ichain
        deck = self.get_object()
        user = request.user
        today = timezone.localdate()
        mode = request.query_params.get('mode', 'scheduled')

        if mode == 'all':
            # Force practice: all non-mastered cards regardless of SM-2 schedule
            mastered_fc_ids = list(
                UserFlashcardProgress.objects.filter(
                    user=user, flashcard__deck=deck, is_mastered=True
                ).values_list('flashcard_id', flat=True)
            )
            study_cards = list(deck.cards.exclude(id__in=mastered_fc_ids))
            due_count = 0
            new_count = len(study_cards)
        else:
            # Normal SM-2 scheduled study
            # Cards with overdue review date (excluding mastered)
            due_ids = list(
                UserFlashcardProgress.objects.filter(
                    user=user, flashcard__deck=deck, next_review_date__lte=today, is_mastered=False
                ).values_list("flashcard_id", flat=True)
            )
            # All cards user has ever reviewed in this deck (mastered cards are among these)
            reviewed_ids = list(
                UserFlashcardProgress.objects.filter(
                    user=user, flashcard__deck=deck
                ).values_list("flashcard_id", flat=True)
            )
            due_cards = list(deck.cards.filter(id__in=due_ids))
            # New cards: never reviewed AND not mastered (mastered implies reviewed anyway)
            new_cards = list(deck.cards.exclude(id__in=reviewed_ids))
            study_cards = list(ichain(due_cards, new_cards))
            due_count = len(due_cards)
            new_count = len(new_cards)

        card_data = FlashcardSerializer(
            study_cards, many=True, context={"request": request}
        ).data
        return Response({
            "id": deck.id,
            "name": deck.name,
            "cefr_level": deck.cefr_level,
            "flashcards": card_data,
            "due_count": due_count,
            "new_count": new_count,
            "total_count": len(study_cards),
            "mode": mode,
        })


class SM2UpdateView(APIView):
    """
    POST /api/vocabulary/flashcards/sm2/
    Applies SM-2 algorithm to a flashcard rating and schedules next_review_date.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SM2UpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        flashcard_id = data["flashcard_id"]
        rating = data["rating"]  # 0-5

        progress, _ = UserFlashcardProgress.objects.get_or_create(
            user=request.user,
            flashcard_id=flashcard_id,
        )
        progress.apply_sm2(rating)  # method defined on model

        return Response(UserFlashcardProgressSerializer(progress).data)


class WordFlashcardStatusView(APIView):
    """
    GET /api/vocabulary/words/:id/flashcard-status/
    Returns the list of decks (accessible to this user) that contain the given word.
    Used by VocabularyView to show 'already in deck' state.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        from django.db.models import Q
        try:
            Word.objects.get(pk=pk)
        except Word.DoesNotExist:
            return Response({'error': 'Not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        flashcards = Flashcard.objects.filter(
            word_id=pk,
            deck__in=FlashcardDeck.objects.filter(
                Q(owner=request.user) | Q(is_public=True)
            ),
        ).select_related('deck')

        in_decks = [
            {
                'deck_id': fc.deck.id,
                'deck_name': fc.deck.name,
                'flashcard_id': fc.id,
            }
            for fc in flashcards
        ]
        return Response({'word_id': pk, 'in_decks': in_decks})


class FlashcardRemoveWordView(APIView):
    """
    POST /api/vocabulary/flashcards/remove-word/
    Removes ALL card types for a word from a user-owned deck.
    Accepts either:
      { flashcard_id }               → resolves deck + word from that card
      { word_id, deck_id }           → direct lookup
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        flashcard_id = request.data.get('flashcard_id')
        word_id = request.data.get('word_id')
        deck_id = request.data.get('deck_id')

        if flashcard_id:
            try:
                fc = Flashcard.objects.get(pk=flashcard_id, deck__owner=request.user)
            except Flashcard.DoesNotExist:
                return Response({'error': 'Not found or not authorized'}, status=drf_status.HTTP_404_NOT_FOUND)
            word_id = fc.word_id
            deck_id = fc.deck_id
        elif word_id and deck_id:
            try:
                FlashcardDeck.objects.get(pk=deck_id, owner=request.user)
            except FlashcardDeck.DoesNotExist:
                return Response({'error': 'Not authorized'}, status=drf_status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'flashcard_id or (word_id + deck_id) required'}, status=drf_status.HTTP_400_BAD_REQUEST)

        deleted, _ = Flashcard.objects.filter(deck_id=deck_id, word_id=word_id).delete()
        return Response({'status': 'removed', 'deleted_count': deleted})


class StudySessionCompleteView(APIView):
    """
    POST /api/vocabulary/flashcard-decks/:id/session-complete/
    PRD 5.8 Session Tracking — saves a completed study session.
    Payload: { new_cards, review_cards, total_reviewed, correct_count, duration_seconds }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        from django.utils import timezone
        try:
            deck = FlashcardDeck.objects.get(pk=pk)
        except FlashcardDeck.DoesNotExist:
            return Response({'error': 'Deck not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        total = request.data.get('total_reviewed', 0)
        correct = request.data.get('correct_count', 0)
        accuracy = round(correct / total * 100, 1) if total > 0 else 0.0

        session = StudySession.objects.create(
            user=request.user,
            deck=deck,
            new_cards=request.data.get('new_cards', 0),
            review_cards=request.data.get('review_cards', 0),
            total_reviewed=total,
            correct_count=correct,
            accuracy_pct=accuracy,
            duration_seconds=request.data.get('duration_seconds', 0),
            is_completed=True,
            completed_at=timezone.now(),
        )
        return Response({'session_id': session.id, 'accuracy_pct': session.accuracy_pct})


class DeckStudyHistoryView(APIView):
    """
    GET /api/vocabulary/flashcard-decks/:id/history/
    PRD 5.8 DeckStudyHistory — returns the last 14 days of study data
    aggregated from StudySession records.  Used by the frontend bar chart.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        from datetime import timedelta
        from django.db.models import Avg, Sum
        from django.utils import timezone

        try:
            FlashcardDeck.objects.get(pk=pk)
        except FlashcardDeck.DoesNotExist:
            return Response({'error': 'Not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()
        since = today - timedelta(days=13)

        sessions = (
            StudySession.objects
            .filter(user=request.user, deck_id=pk, is_completed=True, completed_at__date__gte=since)
            .values('completed_at__date')
            .annotate(total_cards=Sum('total_reviewed'), avg_accuracy=Avg('accuracy_pct'))
            .order_by('completed_at__date')
        )

        # Fill all 14 days (0 for days with no session)
        days = {}
        for i in range(14):
            d = since + timedelta(days=i)
            days[str(d)] = {'date': str(d), 'total_cards': 0, 'avg_accuracy': 0}
        for s in sessions:
            dk = str(s['completed_at__date'])
            days[dk] = {
                'date': dk,
                'total_cards': s['total_cards'] or 0,
                'avg_accuracy': round(s['avg_accuracy'] or 0, 1),
            }

        return Response({'deck_id': pk, 'history': list(days.values())})


# ── Quiz helpers ──────────────────────────────────────────────────────────────

def _presigned_url(s3_key):
    """Return a presigned S3 URL for the given key, or None."""
    if not s3_key:
        return None
    from django.conf import settings as dj_settings
    import boto3
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=dj_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=dj_settings.AWS_SECRET_ACCESS_KEY,
            region_name=dj_settings.AWS_S3_REGION_NAME,
        )
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": dj_settings.AWS_STORAGE_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=dj_settings.AWS_PRESIGNED_URL_EXPIRY,
        )
    except Exception:
        return None


def _build_quiz_questions(words, distractor_pool, count, types):
    """
    Generate MCQ questions.

    types: list of 'word_to_meaning' | 'meaning_to_word' | 'audio_to_word'
    Returns list of question dicts with correct_id embedded (educational app).
    """
    import random
    questions = []
    sample = words[:count]
    random.shuffle(sample)

    # Build a fast-lookup pool for distractors (exclude correct word each time)
    pool = list(distractor_pool)

    for i, word in enumerate(sample):
        qtype = types[i % len(types)]

        wrong_words = [w for w in pool if w.id != word.id]
        random.shuffle(wrong_words)
        distractors = wrong_words[:3]
        if len(distractors) < 3:
            continue  # not enough distinct words — skip

        if qtype == 'word_to_meaning':
            prompt = word.word
            prompt_type = 'text'
            audio_url = None
            correct = {'id': f'c_{word.id}_0', 'text': word.meaning_vi or word.word}
            wrongs = [{'id': f'c_{d.id}_{j+1}', 'text': d.meaning_vi or d.word} for j, d in enumerate(distractors)]

        elif qtype == 'meaning_to_word':
            prompt = word.meaning_vi or word.word
            prompt_type = 'text'
            audio_url = None
            correct = {'id': f'c_{word.id}_0', 'text': word.word}
            wrongs = [{'id': f'c_{d.id}_{j+1}', 'text': d.word} for j, d in enumerate(distractors)]

        else:  # audio_to_word
            prompt = word.word  # fallback label if no audio
            prompt_type = 'audio'
            audio_url = _presigned_url(word.audio_uk_s3_key) or _presigned_url(word.audio_us_s3_key)
            correct = {'id': f'c_{word.id}_0', 'text': word.word}
            wrongs = [{'id': f'c_{d.id}_{j+1}', 'text': d.word} for j, d in enumerate(distractors)]

        all_choices = [correct] + wrongs
        random.shuffle(all_choices)

        questions.append({
            'id': f'q_{i}',
            'type': qtype,
            'prompt': prompt,
            'prompt_type': prompt_type,
            'ipa': word.ipa_uk or word.ipa_us or '',
            'audio_url': audio_url,
            'choices': all_choices,
            'correct_id': correct['id'],
        })

    return questions


class FlashcardQuizView(APIView):
    """
    GET /api/vocabulary/flashcard-decks/:id/quiz/
    Generates a multiple-choice quiz from a single deck.

    Query params:
      count  — number of questions (default 10, max 30)
      types  — comma-separated: word_to_meaning,meaning_to_word,audio_to_word
               (default: word_to_meaning,meaning_to_word)
      source — 'mastered' to quiz only mastered words (default: all words)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        import random
        try:
            deck = FlashcardDeck.objects.get(pk=pk)
        except FlashcardDeck.DoesNotExist:
            return Response({'error': 'Deck not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        count = min(int(request.query_params.get('count', 10)), 30)
        raw_types = request.query_params.get('types', 'word_to_meaning,meaning_to_word')
        types = [t.strip() for t in raw_types.split(',') if t.strip()]
        source = request.query_params.get('source', 'all')

        # Words in this deck (deduplicated by word_to_def cards)
        cards_qs = Flashcard.objects.filter(deck=deck, card_type='word_to_def')
        if source == 'mastered':
            mastered_fc_ids = UserFlashcardProgress.objects.filter(
                user=request.user, flashcard__deck=deck, flashcard__card_type='word_to_def',
                is_mastered=True,
            ).values_list('flashcard_id', flat=True)
            cards_qs = cards_qs.filter(id__in=mastered_fc_ids)

        word_ids = list(cards_qs.values_list('word_id', flat=True))
        deck_words = list(Word.objects.filter(id__in=word_ids))

        if len(deck_words) < 4:
            msg = 'Chưa có đủ 4 từ đã nhớ để tạo quiz.' if source == 'mastered' else 'Cần ít nhất 4 từ trong deck để tạo quiz.'
            return Response({'error': msg}, status=drf_status.HTTP_400_BAD_REQUEST)

        # Distractor pool: deck words first, supplement from global pool
        distractor_pool = list(deck_words)
        if len(distractor_pool) < 10:
            extra = list(Word.objects.exclude(id__in=word_ids).order_by('?')[:50])
            distractor_pool.extend(extra)

        random.shuffle(deck_words)
        questions = _build_quiz_questions(deck_words, distractor_pool, count, types)

        return Response({
            'deck_id': pk,
            'deck_name': deck.name,
            'total': len(questions),
            'questions': questions,
        })


class DeckWordBrowserView(APIView):
    """
    GET /api/vocabulary/flashcard-decks/:id/words/
    Returns all words in the deck with SM-2 progress for the current user.
    Query param: ?status=all|learning|mastered (default: all)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        from django.db.models import Q
        user = request.user

        try:
            deck = FlashcardDeck.objects.get(
                Q(owner=user) | Q(is_public=True), pk=pk
            )
        except FlashcardDeck.DoesNotExist:
            return Response({'error': 'Deck not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        status_filter = request.query_params.get('status', 'all')

        # Get word IDs in deck (word_to_def cards only to avoid duplicates)
        word_ids = list(
            Flashcard.objects.filter(deck=deck, card_type='word_to_def')
            .values_list('word_id', flat=True)
        )
        words = Word.objects.filter(id__in=word_ids).order_by('word')

        # Progress for word_to_def cards in this deck for this user
        progress_map = {}
        for p in UserFlashcardProgress.objects.filter(
            user=user, flashcard__deck=deck, flashcard__card_type='word_to_def',
        ).select_related('flashcard'):
            progress_map[p.flashcard.word_id] = p

        result = []
        for word in words:
            p = progress_map.get(word.id)
            if p:
                if p.is_mastered:
                    wstatus = 'mastered'
                elif p.repetitions >= 3 and p.interval_days >= 7:
                    wstatus = 'review'
                else:
                    wstatus = 'learning'
            else:
                wstatus = 'new'

            if status_filter != 'all' and wstatus != status_filter:
                continue

            result.append({
                'word_id': word.id,
                'word': word.word,
                'meaning_vi': word.meaning_vi or '',
                'ipa_uk': word.ipa_uk or '',
                'ipa_us': word.ipa_us or '',
                'part_of_speech': word.part_of_speech or '',
                'cefr_level': word.cefr_level or '',
                'status': wstatus,
                'progress': {
                    'repetitions': p.repetitions,
                    'interval_days': p.interval_days,
                    'ease_factor': round(p.ease_factor, 2),
                    'next_review_date': str(p.next_review_date) if p.next_review_date else None,
                    'is_mastered': p.is_mastered,
                } if p else None,
            })

        mastered_count = sum(1 for r in result if r['status'] == 'mastered')
        learning_count = len(result) - mastered_count

        return Response({
            'deck_id': pk,
            'deck_name': deck.name,
            'total': len(result),
            'mastered_count': mastered_count,
            'learning_count': learning_count,
            'words': result,
        })


class ToggleMasteredView(APIView):
    """
    POST /api/vocabulary/flashcard-decks/:id/words/toggle-mastered/
    Body: { word_id: int, is_mastered: bool }
    Sets is_mastered on UserFlashcardProgress for all card types of the word.
    Creates progress records if they don't exist yet.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        word_id = request.data.get('word_id')
        is_mastered = request.data.get('is_mastered')

        if word_id is None or is_mastered is None:
            return Response(
                {'error': 'word_id and is_mastered required'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        try:
            FlashcardDeck.objects.get(pk=pk)
        except FlashcardDeck.DoesNotExist:
            return Response({'error': 'Deck not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        flashcards = Flashcard.objects.filter(deck_id=pk, word_id=word_id)
        if not flashcards.exists():
            return Response({'error': 'Word not in deck'}, status=drf_status.HTTP_404_NOT_FOUND)

        flag = bool(is_mastered)
        for fc in flashcards:
            UserFlashcardProgress.objects.update_or_create(
                user=user,
                flashcard=fc,
                defaults={'is_mastered': flag},
            )

        return Response({'word_id': word_id, 'is_mastered': flag, 'updated_cards': flashcards.count()})


class MultiDeckQuizView(APIView):
    """
    POST /api/vocabulary/quiz/generate/
    Generates a comprehensive quiz from one or more decks.

    Payload: { deck_ids: [1,2,3], count: 20, types: ['word_to_meaning','meaning_to_word','audio_to_word'] }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        import random
        from django.db.models import Q

        deck_ids = request.data.get('deck_ids', [])
        count = min(int(request.data.get('count', 20)), 50)
        types = request.data.get('types', ['word_to_meaning', 'meaning_to_word'])

        if not deck_ids:
            return Response({'error': 'deck_ids required'}, status=drf_status.HTTP_400_BAD_REQUEST)

        # Verify user can access all requested decks
        accessible = FlashcardDeck.objects.filter(
            Q(owner=request.user) | Q(is_public=True),
            pk__in=deck_ids,
        )
        if accessible.count() != len(deck_ids):
            return Response({'error': 'One or more decks not found or not accessible.'}, status=drf_status.HTTP_403_FORBIDDEN)

        word_ids = list(
            Flashcard.objects.filter(deck__in=accessible, card_type='word_to_def')
            .values_list('word_id', flat=True)
            .distinct()
        )
        all_words = list(Word.objects.filter(id__in=word_ids))

        if len(all_words) < 4:
            return Response({'error': 'Cần ít nhất 4 từ để tạo quiz.'}, status=drf_status.HTTP_400_BAD_REQUEST)

        # Supplement distractor pool from global word list if needed
        distractor_pool = list(all_words)
        if len(distractor_pool) < 10:
            extra = list(Word.objects.exclude(id__in=word_ids).order_by('?')[:50])
            distractor_pool.extend(extra)

        random.shuffle(all_words)
        questions = _build_quiz_questions(all_words, distractor_pool, count, types)
        deck_names = list(accessible.values_list('name', flat=True))

        return Response({
            'deck_ids': deck_ids,
            'deck_names': deck_names,
            'total': len(questions),
            'questions': questions,
        })

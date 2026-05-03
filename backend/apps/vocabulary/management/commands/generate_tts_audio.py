"""
Management command to pre-generate TTS audio for all vocabulary words.

Usage:
  python manage.py generate_tts_audio
  python manage.py generate_tts_audio --voice en-GB-SoniaNeural
  python manage.py generate_tts_audio --limit 500         # only first N words
  python manage.py generate_tts_audio --skip-existing     # skip cached words (default)
  python manage.py generate_tts_audio --force             # regenerate even if cached
"""

import asyncio
import time

from django.core.management.base import BaseCommand

from apps.vocabulary.models import Word
from utils.tts import TTSService, TTSVoice


class Command(BaseCommand):
    help = "Pre-generate TTS audio files for all vocabulary words."

    def add_arguments(self, parser):
        parser.add_argument(
            "--voice",
            default=TTSVoice.DEFAULT,
            choices=list(TTSVoice.ALLOWED),
            help="TTS voice to use (default: en-GB-SoniaNeural)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of words to process",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate audio even if cached file already exists",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.2,
            help="Delay in seconds between requests to avoid rate limiting (default: 0.2)",
        )

    def handle(self, *args, **options):
        voice = options["voice"]
        limit = options["limit"]
        force = options["force"]
        delay = options["delay"]

        qs = Word.objects.values_list("word", flat=True).order_by("frequency_rank", "id")
        if limit:
            qs = qs[:limit]

        words = list(qs)
        total = len(words)
        self.stdout.write(f"Processing {total} words with voice '{voice}'...")

        ok = 0
        skipped = 0
        failed = 0

        for i, word in enumerate(words, 1):
            # Check cache if not forcing
            if not force:
                cache_path = TTSService._get_cache_path(word, voice, TTSService.DEFAULT_RATE, TTSService.DEFAULT_PITCH)
                if cache_path.exists():
                    skipped += 1
                    if i % 100 == 0:
                        self.stdout.write(f"  [{i}/{total}] skipped (cached): {word}")
                    continue

            try:
                audio_url = asyncio.run(TTSService.speak_async(word, voice=voice))
                if audio_url:
                    ok += 1
                    if i % 50 == 0 or i <= 5:
                        self.stdout.write(f"  [{i}/{total}] ✓ {word}")
                else:
                    failed += 1
                    self.stdout.write(self.style.WARNING(f"  [{i}/{total}] ✗ failed: {word}"))
            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(f"  [{i}/{total}] error ({word}): {e}"))

            if delay > 0:
                time.sleep(delay)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Generated: {ok}, Skipped (cached): {skipped}, Failed: {failed}"
        ))

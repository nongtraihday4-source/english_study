"""
Management command: generate_passage_audio
Generates TTS audio for PracticePassage sentences and full passages.

Usage:
  python manage.py generate_passage_audio             # all unpublished passages without audio
  python manage.py generate_passage_audio --all       # all passages (overwrite)
  python manage.py generate_passage_audio --id 1 2 3  # specific passage IDs
"""
from django.core.management.base import BaseCommand

from apps.skill_practice.models import PracticePassage
from utils.sentence_splitter import split_to_sentence_dicts
from utils.tts import TTSService, TTSVoice


class Command(BaseCommand):
    help = "Generate TTS audio for practice passage sentences."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all", action="store_true",
            help="Regenerate audio for ALL passages (overwrites existing)",
        )
        parser.add_argument(
            "--id", nargs="+", type=int, dest="ids",
            help="Specific passage IDs to process",
        )

    def handle(self, *args, **options):
        tts = TTSService()

        qs = PracticePassage.objects.all()
        if options["ids"]:
            qs = qs.filter(id__in=options["ids"])
        elif not options["all"]:
            # Only process passages that are missing audio on any sentence
            qs = qs.filter(is_published=True)

        total = qs.count()
        self.stdout.write(f"Processing {total} passage(s)...")

        success = 0
        errors = 0

        for passage in qs.iterator():
            try:
                changed = False

                # Auto-split sentences if missing
                if not passage.sentences_json and passage.full_text:
                    passage.sentences_json = split_to_sentence_dicts(passage.full_text)
                    changed = True
                    self.stdout.write(
                        f"  [{passage.id}] Split into {len(passage.sentences_json)} sentences"
                    )

                voice = passage.tts_voice or TTSVoice.US_FEMALE

                # Generate per-sentence audio
                sentences = passage.sentences_json or []
                for s in sentences:
                    if options["all"] or not s.get("audio_url"):
                        url = tts.speak(s["text"], voice=voice)
                        if url:
                            s["audio_url"] = url
                            changed = True
                        else:
                            self.stderr.write(
                                f"  [{passage.id}] TTS failed for sentence {s['index']}: {s['text'][:50]}"
                            )

                # Generate full-passage audio
                if (options["all"] or not passage.full_audio_url) and passage.full_text:
                    url = tts.speak(passage.full_text, voice=voice)
                    if url:
                        passage.full_audio_url = url
                        changed = True

                if changed:
                    passage.save(update_fields=["sentences_json", "full_audio_url"])
                    self.stdout.write(
                        self.style.SUCCESS(f"  [{passage.id}] ✓ {passage.title}")
                    )
                    success += 1
                else:
                    self.stdout.write(f"  [{passage.id}] — already complete, skipped")

            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(f"  [{passage.id}] ERROR: {exc}")
                )
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(f"\nDone: {success} updated, {errors} errors")
        )

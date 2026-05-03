"""
Text-to-Speech Service using Edge TTS (Microsoft Neural Voices).

Provides on-demand TTS with local file caching.
Audio stored at MEDIA_ROOT/tts/<voice>/<hash>.mp3.
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge-tts not installed. Run: pip install edge-tts")


class TTSVoice:
    """Available TTS voices."""

    US_FEMALE_ARIA = "en-US-AriaNeural"
    US_MALE_GUY = "en-US-GuyNeural"
    UK_FEMALE_SONIA = "en-GB-SoniaNeural"
    UK_MALE_RYAN = "en-GB-RyanNeural"
    AU_FEMALE_NATASHA = "en-AU-NatashaNeural"

    DEFAULT = UK_FEMALE_SONIA

    ALLOWED = {
        US_FEMALE_ARIA, US_MALE_GUY,
        UK_FEMALE_SONIA, UK_MALE_RYAN,
        AU_FEMALE_NATASHA,
    }


class TTSService:
    """
    TTS service with on-demand generation and local file caching.
    """

    AUDIO_DIR = Path(settings.MEDIA_ROOT) / "tts"
    DEFAULT_VOICE = TTSVoice.DEFAULT
    DEFAULT_RATE = "+0%"
    DEFAULT_PITCH = "+0Hz"

    @classmethod
    def _get_cache_path(cls, text: str, voice: str, rate: str, pitch: str) -> Path:
        cache_key = f"{text}|{voice}|{rate}|{pitch}"
        file_hash = hashlib.sha256(cache_key.encode()).hexdigest()
        voice_dir = cls.AUDIO_DIR / voice
        voice_dir.mkdir(parents=True, exist_ok=True)
        return voice_dir / f"{file_hash}.mp3"

    @classmethod
    def _get_media_url(cls, cache_path: Path) -> str:
        rel = cache_path.relative_to(Path(settings.MEDIA_ROOT))
        return f"{settings.MEDIA_URL}{rel}"

    @classmethod
    async def speak_async(
        cls,
        text: str,
        voice: str = None,
        rate: str = None,
        pitch: str = None,
    ) -> Optional[str]:
        """Generate speech audio. Returns media-relative URL or None."""
        if not EDGE_TTS_AVAILABLE:
            logger.error("edge-tts not available")
            return None

        if not text or not text.strip():
            return None

        voice = voice if voice in TTSVoice.ALLOWED else cls.DEFAULT_VOICE
        rate = rate or cls.DEFAULT_RATE
        pitch = pitch or cls.DEFAULT_PITCH

        cache_path = cls._get_cache_path(text, voice, rate, pitch)

        if cache_path.exists():
            logger.debug("TTS cache hit: %s", text[:40])
            return cls._get_media_url(cache_path)

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch,
            )
            await communicate.save(str(cache_path))
            logger.info("TTS generated: %s → %s", text[:40], cache_path.name)
            return cls._get_media_url(cache_path)
        except Exception as e:
            logger.error("TTS generation failed: %s", e)
            return None

    @classmethod
    def speak(cls, text: str, voice: str = None) -> Optional[str]:
        """Synchronous wrapper for speak_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(
                        asyncio.run,
                        cls.speak_async(text, voice),
                    ).result()
            return loop.run_until_complete(cls.speak_async(text, voice))
        except RuntimeError:
            return asyncio.run(cls.speak_async(text, voice))

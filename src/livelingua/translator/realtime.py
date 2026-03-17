"""Real-time translator with streaming sentence detection."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Callable, Optional

from livelingua.languages.detector import LanguageDetector
from livelingua.models import MeetingSession, Segment, TranslationResult
from livelingua.translator.engine import TranslationEngine


class RealTimeTranslator:
    """Process a streaming text feed, detect sentence boundaries, and translate."""

    # Sentence-ending patterns
    _SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\u0400-\u04FF\u4e00-\u9fff])|(?<=[.!?])$")

    def __init__(
        self,
        engine: TranslationEngine | None = None,
        detector: LanguageDetector | None = None,
        source_language: Optional[str] = None,
        target_languages: Optional[list[str]] = None,
        domain: Optional[str] = None,
        on_translation: Optional[Callable[[TranslationResult], None]] = None,
    ) -> None:
        self.engine = engine or TranslationEngine()
        self.detector = detector or LanguageDetector()
        self.source_language = source_language
        self.target_languages = target_languages or ["en"]
        self.domain = domain
        self.on_translation = on_translation

        self._buffer: str = ""
        self._results: list[TranslationResult] = []

    def feed(self, chunk: str) -> list[TranslationResult]:
        """Feed a text chunk into the stream.  Returns any completed translations."""
        self._buffer += chunk
        sentences = self._extract_sentences()
        results: list[TranslationResult] = []

        for sentence in sentences:
            lang = self.source_language
            if lang is None:
                detection = self.detector.detect(sentence)
                lang = detection.language

            segment = Segment(
                text=sentence, language=lang, timestamp=datetime.now(), confidence=1.0
            )

            for target in self.target_languages:
                if target == lang:
                    continue
                result = self.engine.translate(segment, target, domain=self.domain)
                results.append(result)
                if self.on_translation:
                    self.on_translation(result)

        self._results.extend(results)
        return results

    def flush(self) -> list[TranslationResult]:
        """Flush any remaining buffered text as a final segment."""
        if not self._buffer.strip():
            return []
        remaining = self._buffer.strip()
        self._buffer = ""

        lang = self.source_language or self.detector.detect(remaining).language
        segment = Segment(text=remaining, language=lang)
        results: list[TranslationResult] = []
        for target in self.target_languages:
            if target == lang:
                continue
            result = self.engine.translate(segment, target, domain=self.domain)
            results.append(result)
        self._results.extend(results)
        return results

    def _extract_sentences(self) -> list[str]:
        """Split completed sentences from the buffer, keeping remainder buffered."""
        parts = self._SENTENCE_END.split(self._buffer)
        if len(parts) <= 1:
            return []
        # All parts except the last are complete sentences
        sentences = [s.strip() for s in parts[:-1] if s.strip()]
        self._buffer = parts[-1]
        return sentences

    def build_session(self, session_id: str = "default") -> MeetingSession:
        """Build a MeetingSession from all accumulated results."""
        return MeetingSession(
            session_id=session_id,
            source_language=self.source_language or "auto",
            target_languages=self.target_languages,
            segments=list(self._results),
            glossary_domain=self.domain,
        )

    @property
    def results(self) -> list[TranslationResult]:
        return list(self._results)

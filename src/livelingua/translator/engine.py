"""Core translation engine supporting 20+ language pairs."""

from __future__ import annotations

import time
from typing import Optional

from livelingua.languages.registry import LanguageRegistry
from livelingua.models import Segment, TranslationResult
from livelingua.translator.glossary import DomainGlossary


class TranslationEngine:
    """Translate text between supported language pairs.

    This is a rule-based / dictionary-backed engine suitable for demonstration.
    A production system would delegate to a neural MT backend.
    """

    def __init__(
        self,
        registry: LanguageRegistry | None = None,
        glossary: DomainGlossary | None = None,
    ) -> None:
        self.registry = registry or LanguageRegistry()
        self.glossary = glossary or DomainGlossary()

        # Compact bilingual word tables (English <-> other) for demo translations.
        self._word_tables: dict[tuple[str, str], dict[str, str]] = {
            ("en", "es"): {
                "hello": "hola", "world": "mundo", "meeting": "reunion",
                "please": "por favor", "thank": "gracias", "you": "usted",
                "the": "el", "is": "es", "are": "son", "good": "bueno",
                "morning": "manana", "afternoon": "tarde", "welcome": "bienvenido",
                "project": "proyecto", "team": "equipo", "time": "tiempo",
                "question": "pregunta", "answer": "respuesta", "agree": "de acuerdo",
                "next": "siguiente", "slide": "diapositiva",
            },
            ("en", "fr"): {
                "hello": "bonjour", "world": "monde", "meeting": "reunion",
                "please": "s'il vous plait", "thank": "merci", "you": "vous",
                "the": "le", "is": "est", "are": "sont", "good": "bon",
                "morning": "matin", "afternoon": "apres-midi", "welcome": "bienvenue",
                "project": "projet", "team": "equipe", "time": "temps",
                "question": "question", "answer": "reponse", "agree": "d'accord",
                "next": "suivant", "slide": "diapositive",
            },
            ("en", "de"): {
                "hello": "hallo", "world": "Welt", "meeting": "Besprechung",
                "please": "bitte", "thank": "danke", "you": "Sie",
                "the": "das", "is": "ist", "are": "sind", "good": "gut",
                "morning": "Morgen", "afternoon": "Nachmittag", "welcome": "willkommen",
                "project": "Projekt", "team": "Team", "time": "Zeit",
                "question": "Frage", "answer": "Antwort", "agree": "einverstanden",
                "next": "nachste", "slide": "Folie",
            },
            ("en", "ja"): {
                "hello": "konnichiwa", "meeting": "kaigi", "thank": "arigatou",
                "you": "anata", "good": "yoi", "morning": "asa",
                "project": "purojekuto", "team": "chiimu", "time": "jikan",
                "question": "shitsumon", "answer": "kotae", "welcome": "youkoso",
            },
            ("en", "zh"): {
                "hello": "nihao", "meeting": "huiyi", "thank": "xiexie",
                "good": "hao", "morning": "zaoshang", "project": "xiangmu",
                "team": "tuandui", "time": "shijian", "welcome": "huanying",
            },
        }
        # Build reverse tables
        for (src, tgt), table in list(self._word_tables.items()):
            reverse = {v: k for k, v in table.items()}
            self._word_tables.setdefault((tgt, src), reverse)

    def translate(
        self,
        segment: Segment,
        target_language: str,
        domain: Optional[str] = None,
    ) -> TranslationResult:
        """Translate a segment into the target language."""
        start = time.perf_counter()

        if not self.registry.is_pair_supported(segment.language, target_language):
            # Attempt pivot through English
            translated = self._pivot_translate(segment.text, segment.language, target_language)
        else:
            translated = self._direct_translate(segment.text, segment.language, target_language)

        # Apply glossary substitutions
        glossary_applied: list[str] = []
        if domain:
            translated, glossary_applied = self.glossary.apply(
                translated, target_language, domain
            )

        elapsed = (time.perf_counter() - start) * 1000

        return TranslationResult(
            source=segment,
            translated_text=translated,
            target_language=target_language,
            glossary_terms_applied=glossary_applied,
            translation_time_ms=round(elapsed, 2),
        )

    def _direct_translate(self, text: str, source: str, target: str) -> str:
        """Word-by-word lookup translation (demo quality)."""
        table = self._word_tables.get((source, target), {})
        words = text.split()
        result = []
        for word in words:
            cleaned = word.strip(".,!?;:").lower()
            translated = table.get(cleaned, word)
            # Preserve original punctuation
            if word and word[-1] in ".,!?;:":
                translated += word[-1]
            result.append(translated)
        return " ".join(result)

    def _pivot_translate(self, text: str, source: str, target: str) -> str:
        """Translate via English as a pivot language."""
        if source == "en":
            return self._direct_translate(text, "en", target)
        if target == "en":
            return self._direct_translate(text, source, "en")
        # source -> en -> target
        english = self._direct_translate(text, source, "en")
        return self._direct_translate(english, "en", target)

    def supported_pairs(self) -> list[tuple[str, str]]:
        """Return list of supported (source, target) codes."""
        return [(p.source, p.target) for p in self.registry.TRANSLATION_PAIRS]

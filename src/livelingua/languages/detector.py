"""Language detection using n-gram analysis."""

from __future__ import annotations

import re
from collections import Counter

from livelingua.models import DetectionResult


# Character n-gram frequency profiles for common languages.
# These are simplified top trigrams; a production system would use larger models.
_LANGUAGE_PROFILES: dict[str, list[str]] = {
    "en": [" th", "the", "he ", "ing", "and", " an", "nd ", "ion", "tio", " of",
           "ed ", " in", "of ", "ent", "er ", "es ", " to", " co", "ati", "on ",
           " re", "is ", " be", "ou ", " ha", "al ", "tion", " st", "or ", "en "],
    "es": [" de", "de ", " la", "os ", " en", "la ", "el ", " el", "en ", "es ",
           "as ", "on ", " co", "ion", "cion", " qu", "que", " se", "ue ", "do ",
           "re ", "ent", " lo", "nte", " un", "al ", "er ", " es", "ado", "con"],
    "fr": [" de", "de ", " le", "es ", "le ", "ent", "les", " la", "la ", " les",
           "ion", " et", "et ", "on ", "tion", " en", "en ", "ous", " co", "re ",
           "ait", " pa", "que", " qu", "ue ", "ne ", " un", "er ", "des", " des"],
    "de": [" de", "en ", "er ", "der", " di", "die", "ie ", "ein", " ei", "sch",
           "ich", "ch ", "den", " da", "nd ", "und", " un", "in ", "gen", "te ",
           " be", "ung", " au", "eit", "ine", " ge", " ve", "ber", "ren", "ier"],
    "it": [" di", "di ", " in", "la ", " la", "che", " ch", "he ", "to ", "re ",
           " de", "del", "el ", " co", "ell", "lla", " e ", "le ", "ion", "one",
           "ne ", "ent", " un", " il", "il ", "ato", "per", " pe", "ment", "con"],
    "pt": [" de", "de ", " a ", "os ", " do", "as ", "do ", " co", " da", "da ",
           "ent", " qu", "que", "ue ", " e ", "em ", " em", " no", "es ", "ao ",
           "acao", " os", "ado", "al ", " se", " pa", "re ", "er ", "ment", "com"],
    "ru": [" na", " pr", " po", " v ", " ko", " ne", "eni", " i ", "ogo", "to ",
           " za", " s ", "ost", " ob", "ani", " ra", "pro", "iye", "ova", "not"],
    "zh": [],  # Chinese uses character-based detection instead
    "ja": [],  # Japanese uses script detection
    "ko": [],  # Korean uses Hangul detection
    "ar": [],  # Arabic uses script detection
    "nl": [" de", "de ", " he", "het", "et ", "en ", "van", " va", "an ", " ee",
           "een", " in", "ver", " ve", "aar", " ge", "er ", "ing", "ij ", " be"],
    "tr": [" bi", "bir", "ir ", "lar", " ve", "ve ", " ka", "ler", "in ", "an ",
           " bu", "eri", "de ", " de", "rin", "ara", " ya", "ini", "en ", "ile"],
    "hi": [],  # Hindi uses Devanagari script detection
    "sv": [" de", " och", "och", "en ", "er ", " i ", "att", " at", " fo", "for",
           " av", "av ", "det", " en", " so", "som", "ar ", "ing", "and", " ha"],
}

# Unicode ranges for script-based detection
_SCRIPT_RANGES: dict[str, list[tuple[int, int]]] = {
    "zh": [(0x4E00, 0x9FFF), (0x3400, 0x4DBF)],
    "ja": [(0x3040, 0x309F), (0x30A0, 0x30FF)],  # Hiragana + Katakana
    "ko": [(0xAC00, 0xD7AF), (0x1100, 0x11FF)],
    "ar": [(0x0600, 0x06FF), (0x0750, 0x077F)],
    "hi": [(0x0900, 0x097F)],
    "he": [(0x0590, 0x05FF)],
    "th": [(0x0E00, 0x0E7F)],
    "bn": [(0x0980, 0x09FF)],
    "el": [(0x0370, 0x03FF)],
    "uk": [(0x0400, 0x04FF)],  # Cyrillic (shared with ru)
    "ru": [(0x0400, 0x04FF)],
}


class LanguageDetector:
    """Detect the language of text using n-gram frequency analysis and script detection."""

    def __init__(self) -> None:
        self._profiles = _LANGUAGE_PROFILES
        self._script_ranges = _SCRIPT_RANGES

    def detect(self, text: str) -> DetectionResult:
        """Detect the most likely language for the given text."""
        if not text or not text.strip():
            return DetectionResult(language="en", confidence=0.0)

        # First try script-based detection for non-Latin scripts
        script_result = self._detect_by_script(text)
        if script_result is not None:
            return script_result

        # Fall back to n-gram analysis for Latin-script languages
        scores = self._score_all(text)
        if not scores:
            return DetectionResult(language="en", confidence=0.0)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_lang, best_score = ranked[0]

        # Normalise confidence to 0-1 range
        max_possible = len(self._extract_trigrams(text))
        confidence = min(best_score / max(max_possible, 1), 1.0)

        alternatives = [(lang, min(s / max(max_possible, 1), 1.0)) for lang, s in ranked[1:4]]

        return DetectionResult(
            language=best_lang,
            confidence=round(confidence, 3),
            alternatives=alternatives,
        )

    def _detect_by_script(self, text: str) -> DetectionResult | None:
        """Detect language based on Unicode script of characters."""
        script_counts: Counter[str] = Counter()
        total_alpha = 0

        for ch in text:
            cp = ord(ch)
            for lang, ranges in self._script_ranges.items():
                for low, high in ranges:
                    if low <= cp <= high:
                        script_counts[lang] += 1
                        total_alpha += 1
                        break

        if not script_counts or total_alpha < 3:
            return None

        best_lang, best_count = script_counts.most_common(1)[0]
        ratio = best_count / max(len(text.strip()), 1)

        if ratio < 0.15:
            return None

        # Disambiguate Cyrillic between Russian and Ukrainian
        if best_lang in ("ru", "uk"):
            best_lang = self._disambiguate_cyrillic(text)

        alternatives = [
            (lang, round(c / max(len(text.strip()), 1), 3))
            for lang, c in script_counts.most_common(4)[1:]
        ]

        return DetectionResult(
            language=best_lang,
            confidence=round(min(ratio * 1.5, 1.0), 3),
            alternatives=alternatives,
        )

    @staticmethod
    def _disambiguate_cyrillic(text: str) -> str:
        """Tell Russian from Ukrainian by checking for Ukrainian-specific letters."""
        ukrainian_chars = set("\u0491\u0490\u0454\u0404\u0456\u0406\u0457\u0407")  # ghee, ye, i, yi
        count = sum(1 for ch in text if ch in ukrainian_chars)
        return "uk" if count >= 2 else "ru"

    def _score_all(self, text: str) -> dict[str, float]:
        """Score every profiled language against the text."""
        trigrams = self._extract_trigrams(text)
        if not trigrams:
            return {}

        text_profile = set(trigrams)
        scores: dict[str, float] = {}
        for lang, profile in self._profiles.items():
            if not profile:
                continue
            overlap = len(text_profile & set(profile))
            scores[lang] = overlap
        return scores

    @staticmethod
    def _extract_trigrams(text: str) -> list[str]:
        """Extract character trigrams from lowercased text."""
        text = re.sub(r"[^\w\s]", "", text.lower())
        text = re.sub(r"\s+", " ", text.strip())
        return [text[i : i + 3] for i in range(len(text) - 2)]

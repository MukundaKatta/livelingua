"""Language registry with 25+ languages and ISO codes."""

from __future__ import annotations

from livelingua.models import Language, TranslationPair


class LanguageRegistry:
    """Registry of supported languages and translation pairs."""

    LANGUAGES: dict[str, Language] = {
        "en": Language(code="en", name="English", native_name="English", script="Latin"),
        "es": Language(code="es", name="Spanish", native_name="Espanol", script="Latin"),
        "fr": Language(code="fr", name="French", native_name="Francais", script="Latin"),
        "de": Language(code="de", name="German", native_name="Deutsch", script="Latin"),
        "it": Language(code="it", name="Italian", native_name="Italiano", script="Latin"),
        "pt": Language(code="pt", name="Portuguese", native_name="Portugues", script="Latin"),
        "nl": Language(code="nl", name="Dutch", native_name="Nederlands", script="Latin"),
        "ru": Language(code="ru", name="Russian", native_name="Russkiy", script="Cyrillic"),
        "zh": Language(code="zh", name="Chinese", native_name="Zhongwen", script="Han"),
        "ja": Language(code="ja", name="Japanese", native_name="Nihongo", script="Kana/Kanji"),
        "ko": Language(code="ko", name="Korean", native_name="Hangugeo", script="Hangul"),
        "ar": Language(code="ar", name="Arabic", native_name="Al-Arabiyyah", script="Arabic", rtl=True),
        "hi": Language(code="hi", name="Hindi", native_name="Hindi", script="Devanagari"),
        "bn": Language(code="bn", name="Bengali", native_name="Bangla", script="Bengali"),
        "tr": Language(code="tr", name="Turkish", native_name="Turkce", script="Latin"),
        "pl": Language(code="pl", name="Polish", native_name="Polski", script="Latin"),
        "sv": Language(code="sv", name="Swedish", native_name="Svenska", script="Latin"),
        "da": Language(code="da", name="Danish", native_name="Dansk", script="Latin"),
        "no": Language(code="no", name="Norwegian", native_name="Norsk", script="Latin"),
        "fi": Language(code="fi", name="Finnish", native_name="Suomi", script="Latin"),
        "el": Language(code="el", name="Greek", native_name="Ellinika", script="Greek"),
        "he": Language(code="he", name="Hebrew", native_name="Ivrit", script="Hebrew", rtl=True),
        "th": Language(code="th", name="Thai", native_name="Phasa Thai", script="Thai"),
        "vi": Language(code="vi", name="Vietnamese", native_name="Tieng Viet", script="Latin"),
        "uk": Language(code="uk", name="Ukrainian", native_name="Ukrainska", script="Cyrillic"),
        "cs": Language(code="cs", name="Czech", native_name="Cestina", script="Latin"),
        "ro": Language(code="ro", name="Romanian", native_name="Romana", script="Latin"),
        "id": Language(code="id", name="Indonesian", native_name="Bahasa Indonesia", script="Latin"),
    }

    # 20+ translation pairs with quality estimates
    TRANSLATION_PAIRS: list[TranslationPair] = [
        TranslationPair(source="en", target="es", quality=0.95),
        TranslationPair(source="en", target="fr", quality=0.94),
        TranslationPair(source="en", target="de", quality=0.93),
        TranslationPair(source="en", target="it", quality=0.92),
        TranslationPair(source="en", target="pt", quality=0.92),
        TranslationPair(source="en", target="zh", quality=0.88),
        TranslationPair(source="en", target="ja", quality=0.86),
        TranslationPair(source="en", target="ko", quality=0.85),
        TranslationPair(source="en", target="ru", quality=0.90),
        TranslationPair(source="en", target="ar", quality=0.84),
        TranslationPair(source="en", target="hi", quality=0.83),
        TranslationPair(source="es", target="en", quality=0.95),
        TranslationPair(source="fr", target="en", quality=0.94),
        TranslationPair(source="de", target="en", quality=0.93),
        TranslationPair(source="zh", target="en", quality=0.87),
        TranslationPair(source="ja", target="en", quality=0.85),
        TranslationPair(source="es", target="fr", quality=0.90),
        TranslationPair(source="fr", target="de", quality=0.88),
        TranslationPair(source="de", target="es", quality=0.87),
        TranslationPair(source="pt", target="es", quality=0.93),
        TranslationPair(source="ru", target="en", quality=0.89),
        TranslationPair(source="ko", target="en", quality=0.84),
        TranslationPair(source="en", target="nl", quality=0.91),
        TranslationPair(source="en", target="tr", quality=0.82),
    ]

    def __init__(self) -> None:
        self._pair_index: dict[tuple[str, str], TranslationPair] = {
            (p.source, p.target): p for p in self.TRANSLATION_PAIRS
        }

    def get_language(self, code: str) -> Language | None:
        """Look up a language by its ISO 639-1 code."""
        return self.LANGUAGES.get(code)

    def list_languages(self) -> list[Language]:
        """Return all supported languages."""
        return list(self.LANGUAGES.values())

    def get_pair(self, source: str, target: str) -> TranslationPair | None:
        """Get translation pair info if supported."""
        return self._pair_index.get((source, target))

    def is_pair_supported(self, source: str, target: str) -> bool:
        """Check whether a source-target pair is supported."""
        return (source, target) in self._pair_index

    def pairs_for_source(self, source: str) -> list[TranslationPair]:
        """List all pairs available from a given source language."""
        return [p for p in self.TRANSLATION_PAIRS if p.source == source]

    def pairs_for_target(self, target: str) -> list[TranslationPair]:
        """List all pairs that translate into the given target language."""
        return [p for p in self.TRANSLATION_PAIRS if p.target == target]

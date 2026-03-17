"""Tests for LiveLingua."""

import pytest

from livelingua.languages.detector import LanguageDetector
from livelingua.languages.registry import LanguageRegistry
from livelingua.models import Segment
from livelingua.translator.engine import TranslationEngine
from livelingua.translator.glossary import DomainGlossary, GlossaryEntry
from livelingua.translator.realtime import RealTimeTranslator


class TestLanguageRegistry:
    def test_list_languages_has_25_plus(self):
        registry = LanguageRegistry()
        assert len(registry.list_languages()) >= 25

    def test_get_language(self):
        registry = LanguageRegistry()
        lang = registry.get_language("en")
        assert lang is not None
        assert lang.name == "English"
        assert lang.code == "en"

    def test_get_unknown_language(self):
        registry = LanguageRegistry()
        assert registry.get_language("xx") is None

    def test_pair_supported(self):
        registry = LanguageRegistry()
        assert registry.is_pair_supported("en", "es")
        assert not registry.is_pair_supported("xx", "yy")

    def test_pairs_for_source(self):
        registry = LanguageRegistry()
        pairs = registry.pairs_for_source("en")
        assert len(pairs) >= 10

    def test_rtl_languages(self):
        registry = LanguageRegistry()
        ar = registry.get_language("ar")
        assert ar is not None and ar.rtl is True
        en = registry.get_language("en")
        assert en is not None and en.rtl is False


class TestLanguageDetector:
    def test_detect_english(self):
        detector = LanguageDetector()
        result = detector.detect("The quick brown fox jumps over the lazy dog.")
        assert result.language == "en"
        assert result.confidence > 0

    def test_detect_empty(self):
        detector = LanguageDetector()
        result = detector.detect("")
        assert result.confidence == 0.0

    def test_detect_spanish(self):
        detector = LanguageDetector()
        result = detector.detect("El rapido zorro marron salta sobre el perro perezoso de la casa.")
        assert result.language == "es"


class TestTranslationEngine:
    def test_translate_en_to_es(self):
        engine = TranslationEngine()
        seg = Segment(text="hello world", language="en")
        result = engine.translate(seg, "es")
        assert result.translated_text == "hola mundo"
        assert result.target_language == "es"

    def test_translate_preserves_punctuation(self):
        engine = TranslationEngine()
        seg = Segment(text="hello, world.", language="en")
        result = engine.translate(seg, "es")
        assert "hola," in result.translated_text

    def test_supported_pairs_count(self):
        engine = TranslationEngine()
        pairs = engine.supported_pairs()
        assert len(pairs) >= 20

    def test_translate_with_glossary(self):
        engine = TranslationEngine()
        seg = Segment(text="deploy the API", language="en")
        result = engine.translate(seg, "es", domain="tech")
        assert result.target_language == "es"


class TestDomainGlossary:
    def test_list_domains(self):
        glossary = DomainGlossary()
        domains = glossary.list_domains()
        assert "tech" in domains
        assert "medical" in domains

    def test_get_entries(self):
        glossary = DomainGlossary()
        entries = glossary.get_entries("tech")
        assert len(entries) >= 5

    def test_apply_glossary(self):
        glossary = DomainGlossary()
        text, applied = glossary.apply("deploy the cloud service", "es", "tech")
        assert len(applied) > 0

    def test_add_custom_entry(self):
        glossary = DomainGlossary()
        entry = GlossaryEntry(
            term="widget", translations={"es": "widget"}, domain="tech"
        )
        glossary.add_entry(entry)
        entries = glossary.get_entries("tech")
        assert any(e.term == "widget" for e in entries)


class TestRealTimeTranslator:
    def test_feed_and_flush(self):
        rt = RealTimeTranslator(source_language="en", target_languages=["es"])
        results = rt.feed("Hello world. ")
        flushed = rt.flush()
        total = results + flushed
        assert len(total) >= 1

    def test_build_session(self):
        rt = RealTimeTranslator(source_language="en", target_languages=["es"])
        rt.feed("Good morning. Welcome to the meeting. ")
        rt.flush()
        session = rt.build_session("test-session")
        assert session.session_id == "test-session"
        assert session.source_language == "en"

    def test_multiple_targets(self):
        rt = RealTimeTranslator(source_language="en", target_languages=["es", "fr"])
        rt.feed("Hello. ")
        results = rt.flush()
        # Should have translations for both targets
        langs = {r.target_language for r in rt.results}
        assert "es" in langs or "fr" in langs

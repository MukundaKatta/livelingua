"""Data models for LiveLingua."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Language(BaseModel):
    """Represents a language with metadata."""

    code: str = Field(description="ISO 639-1 two-letter code")
    name: str = Field(description="English name of the language")
    native_name: str = Field(description="Name in the language itself")
    script: str = Field(default="Latin", description="Writing script used")
    rtl: bool = Field(default=False, description="Right-to-left script")


class TranslationPair(BaseModel):
    """A supported source-target language pair."""

    source: str = Field(description="Source language ISO code")
    target: str = Field(description="Target language ISO code")
    quality: float = Field(default=0.85, ge=0.0, le=1.0, description="Expected quality score")


class Segment(BaseModel):
    """A detected sentence/segment from a speech stream."""

    text: str
    language: str
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TranslationResult(BaseModel):
    """Result of translating a segment."""

    source: Segment
    translated_text: str
    target_language: str
    glossary_terms_applied: list[str] = Field(default_factory=list)
    translation_time_ms: float = 0.0


class GlossaryEntry(BaseModel):
    """A domain-specific glossary term."""

    term: str
    translations: dict[str, str] = Field(
        default_factory=dict, description="Language code -> translation"
    )
    domain: str = Field(default="general")
    context: Optional[str] = None


class MeetingSession(BaseModel):
    """Represents a translation session for a meeting."""

    session_id: str
    source_language: str
    target_languages: list[str]
    segments: list[TranslationResult] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    glossary_domain: Optional[str] = None


class DetectionResult(BaseModel):
    """Result of language detection."""

    language: str
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives: list[tuple[str, float]] = Field(default_factory=list)

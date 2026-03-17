"""Rich console reporting for LiveLingua."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from livelingua.languages.registry import LanguageRegistry
from livelingua.models import MeetingSession, TranslationResult


def print_translation(result: TranslationResult, console: Console | None = None) -> None:
    """Print a single translation result."""
    console = console or Console()
    console.print(
        f"[bold cyan][{result.source.language} -> {result.target_language}][/] "
        f"{result.source.text} -> [green]{result.translated_text}[/]"
    )
    if result.glossary_terms_applied:
        console.print(f"  [dim]Glossary terms: {', '.join(result.glossary_terms_applied)}[/]")


def print_session_report(session: MeetingSession, console: Console | None = None) -> None:
    """Print a full meeting session report."""
    console = console or Console()
    registry = LanguageRegistry()

    console.print()
    console.rule("[bold]LiveLingua Meeting Translation Report[/]")
    console.print(f"Session: [bold]{session.session_id}[/]")
    src = registry.get_language(session.source_language)
    console.print(f"Source language: [cyan]{src.name if src else session.source_language}[/]")
    targets = [registry.get_language(t) for t in session.target_languages]
    target_names = ", ".join(t.name if t else c for t, c in zip(targets, session.target_languages))
    console.print(f"Target languages: [cyan]{target_names}[/]")
    if session.glossary_domain:
        console.print(f"Glossary domain: [yellow]{session.glossary_domain}[/]")
    console.print(f"Total segments: {len(session.segments)}")
    console.print()

    table = Table(title="Translations")
    table.add_column("#", style="dim", width=4)
    table.add_column("Source", style="cyan")
    table.add_column("Translation", style="green")
    table.add_column("Target", width=8)
    table.add_column("Time (ms)", justify="right", width=10)

    for i, seg in enumerate(session.segments, 1):
        table.add_row(
            str(i),
            seg.source.text[:60],
            seg.translated_text[:60],
            seg.target_language,
            f"{seg.translation_time_ms:.1f}",
        )

    console.print(table)


def print_languages(console: Console | None = None) -> None:
    """Print all supported languages."""
    console = console or Console()
    registry = LanguageRegistry()

    table = Table(title="Supported Languages")
    table.add_column("Code", style="bold", width=6)
    table.add_column("Language")
    table.add_column("Native Name")
    table.add_column("Script")
    table.add_column("RTL", width=5)

    for lang in registry.list_languages():
        table.add_row(lang.code, lang.name, lang.native_name, lang.script, "Yes" if lang.rtl else "")

    console.print(table)

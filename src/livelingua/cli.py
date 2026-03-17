"""CLI interface for LiveLingua."""

from __future__ import annotations

import click
from rich.console import Console

from livelingua.languages.detector import LanguageDetector
from livelingua.languages.registry import LanguageRegistry
from livelingua.models import Segment
from livelingua.report import print_languages, print_session_report, print_translation
from livelingua.translator.engine import TranslationEngine
from livelingua.translator.glossary import DomainGlossary
from livelingua.translator.realtime import RealTimeTranslator

console = Console()


@click.group()
@click.version_option(package_name="livelingua")
def cli() -> None:
    """LiveLingua - AI Meeting Translator."""


@cli.command()
@click.argument("text")
@click.option("-s", "--source", default="en", help="Source language code")
@click.option("-t", "--target", default="es", help="Target language code")
@click.option("-d", "--domain", default=None, help="Glossary domain (tech/medical/legal/finance)")
def translate(text: str, source: str, target: str, domain: str | None) -> None:
    """Translate a piece of text."""
    engine = TranslationEngine()
    segment = Segment(text=text, language=source)
    result = engine.translate(segment, target, domain=domain)
    print_translation(result, console)


@cli.command()
@click.argument("text")
def detect(text: str) -> None:
    """Detect the language of text."""
    detector = LanguageDetector()
    result = detector.detect(text)
    registry = LanguageRegistry()
    lang = registry.get_language(result.language)
    name = lang.name if lang else result.language
    console.print(f"Detected: [bold cyan]{name}[/] ({result.language}) "
                  f"confidence={result.confidence:.1%}")
    if result.alternatives:
        for code, conf in result.alternatives:
            alt = registry.get_language(code)
            alt_name = alt.name if alt else code
            console.print(f"  Alternative: {alt_name} ({code}) {conf:.1%}")


@cli.command()
def languages() -> None:
    """List all supported languages."""
    print_languages(console)


@cli.command()
def domains() -> None:
    """List available glossary domains."""
    glossary = DomainGlossary()
    for domain in glossary.list_domains():
        entries = glossary.get_entries(domain)
        console.print(f"[bold]{domain}[/]: {len(entries)} terms")


@cli.command()
@click.option("-s", "--source", default="en", help="Source language code")
@click.option("-t", "--target", multiple=True, default=["es"], help="Target language code(s)")
@click.option("-d", "--domain", default=None, help="Glossary domain")
def session(source: str, target: tuple[str, ...], domain: str | None) -> None:
    """Start an interactive translation session (type sentences, Ctrl-D to end)."""
    rt = RealTimeTranslator(
        source_language=source,
        target_languages=list(target),
        domain=domain,
        on_translation=lambda r: print_translation(r, console),
    )
    console.print("[bold]Interactive session. Type sentences and press Enter. Ctrl-D to finish.[/]")
    try:
        while True:
            line = click.get_text_stream("stdin").readline()
            if not line:
                break
            rt.feed(line)
    except (EOFError, KeyboardInterrupt):
        pass

    rt.flush()
    meeting = rt.build_session("interactive")
    print_session_report(meeting, console)


if __name__ == "__main__":
    cli()

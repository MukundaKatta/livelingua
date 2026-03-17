"""Domain-specific glossary with technical term dictionaries."""

from __future__ import annotations

from livelingua.models import GlossaryEntry


class DomainGlossary:
    """Manage and apply domain-specific glossaries for translation post-processing."""

    # Built-in glossaries organised by domain
    BUILTIN: dict[str, list[GlossaryEntry]] = {
        "tech": [
            GlossaryEntry(term="API", translations={"es": "API", "fr": "API", "de": "API", "ja": "API"}, domain="tech"),
            GlossaryEntry(term="cloud", translations={"es": "nube", "fr": "nuage", "de": "Cloud", "ja": "kuraudo"}, domain="tech"),
            GlossaryEntry(term="deploy", translations={"es": "desplegar", "fr": "deployer", "de": "bereitstellen", "ja": "depuroi"}, domain="tech"),
            GlossaryEntry(term="sprint", translations={"es": "sprint", "fr": "sprint", "de": "Sprint", "ja": "supurinto"}, domain="tech"),
            GlossaryEntry(term="refactor", translations={"es": "refactorizar", "fr": "refactoriser", "de": "refaktorisieren"}, domain="tech"),
            GlossaryEntry(term="backend", translations={"es": "backend", "fr": "backend", "de": "Backend"}, domain="tech"),
            GlossaryEntry(term="frontend", translations={"es": "frontend", "fr": "frontend", "de": "Frontend"}, domain="tech"),
            GlossaryEntry(term="repository", translations={"es": "repositorio", "fr": "depot", "de": "Repository"}, domain="tech"),
            GlossaryEntry(term="pipeline", translations={"es": "tuberia", "fr": "pipeline", "de": "Pipeline"}, domain="tech"),
            GlossaryEntry(term="microservice", translations={"es": "microservicio", "fr": "microservice", "de": "Mikrodienst"}, domain="tech"),
        ],
        "medical": [
            GlossaryEntry(term="diagnosis", translations={"es": "diagnostico", "fr": "diagnostic", "de": "Diagnose"}, domain="medical"),
            GlossaryEntry(term="prognosis", translations={"es": "pronostico", "fr": "pronostic", "de": "Prognose"}, domain="medical"),
            GlossaryEntry(term="symptom", translations={"es": "sintoma", "fr": "symptome", "de": "Symptom"}, domain="medical"),
            GlossaryEntry(term="therapy", translations={"es": "terapia", "fr": "therapie", "de": "Therapie"}, domain="medical"),
            GlossaryEntry(term="dosage", translations={"es": "dosis", "fr": "dosage", "de": "Dosierung"}, domain="medical"),
            GlossaryEntry(term="chronic", translations={"es": "cronico", "fr": "chronique", "de": "chronisch"}, domain="medical"),
        ],
        "legal": [
            GlossaryEntry(term="plaintiff", translations={"es": "demandante", "fr": "plaignant", "de": "Klager"}, domain="legal"),
            GlossaryEntry(term="defendant", translations={"es": "demandado", "fr": "defendeur", "de": "Beklagter"}, domain="legal"),
            GlossaryEntry(term="jurisdiction", translations={"es": "jurisdiccion", "fr": "juridiction", "de": "Gerichtsbarkeit"}, domain="legal"),
            GlossaryEntry(term="statute", translations={"es": "estatuto", "fr": "statut", "de": "Gesetz"}, domain="legal"),
            GlossaryEntry(term="liability", translations={"es": "responsabilidad", "fr": "responsabilite", "de": "Haftung"}, domain="legal"),
        ],
        "finance": [
            GlossaryEntry(term="equity", translations={"es": "capital", "fr": "capitaux propres", "de": "Eigenkapital"}, domain="finance"),
            GlossaryEntry(term="dividend", translations={"es": "dividendo", "fr": "dividende", "de": "Dividende"}, domain="finance"),
            GlossaryEntry(term="portfolio", translations={"es": "cartera", "fr": "portefeuille", "de": "Portfolio"}, domain="finance"),
            GlossaryEntry(term="hedge", translations={"es": "cobertura", "fr": "couverture", "de": "Absicherung"}, domain="finance"),
            GlossaryEntry(term="leverage", translations={"es": "apalancamiento", "fr": "effet de levier", "de": "Hebelwirkung"}, domain="finance"),
        ],
    }

    def __init__(self, custom_entries: list[GlossaryEntry] | None = None) -> None:
        self._custom: list[GlossaryEntry] = custom_entries or []

    def get_entries(self, domain: str) -> list[GlossaryEntry]:
        """Return all glossary entries for a domain."""
        builtin = self.BUILTIN.get(domain, [])
        custom = [e for e in self._custom if e.domain == domain]
        return builtin + custom

    def add_entry(self, entry: GlossaryEntry) -> None:
        """Add a custom glossary entry."""
        self._custom.append(entry)

    def apply(self, text: str, target_language: str, domain: str) -> tuple[str, list[str]]:
        """Replace glossary terms in translated text. Returns (text, applied_terms)."""
        entries = self.get_entries(domain)
        applied: list[str] = []
        for entry in entries:
            if entry.term.lower() in text.lower() and target_language in entry.translations:
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(entry.term), re.IGNORECASE)
                replacement = entry.translations[target_language]
                new_text = pattern.sub(replacement, text)
                if new_text != text:
                    applied.append(entry.term)
                    text = new_text
        return text, applied

    def list_domains(self) -> list[str]:
        """List all available domains."""
        domains = set(self.BUILTIN.keys())
        domains.update(e.domain for e in self._custom)
        return sorted(domains)

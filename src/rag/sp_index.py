"""ChromaDB index over the SP 107.13330 PDF.

Two responsibilities:
1. build_index() — one-shot indexing called from `scripts/build_rag.py`
2. cite_sp_paragraph(rule_id) — retrieves the literal text of a paragraph
   referenced by a rule, used to enrich ValidationIssue.sp_citation.

If the index isn't built, cite_sp_paragraph returns None gracefully so the
graph still runs (just without dressed-up citations).
"""

from __future__ import annotations

import os
from pathlib import Path

_INDEX_DIR = Path(__file__).parent.parent.parent / "chroma_db"
_COLLECTION = "sp_107_13330"

_CITATION_MAP: dict[str, str] = {}  # rule_id -> sp_clause text


def _ensure_loaded() -> None:
    """Load rule_id -> sp_clause map from rules.yaml so we know what to retrieve."""
    if _CITATION_MAP:
        return
    import yaml

    rules_path = Path(__file__).parent.parent.parent / "data" / "rules.yaml"
    if not rules_path.exists():
        return
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))["rules"]
    for r in rules:
        _CITATION_MAP[r["rule_id"]] = r.get("sp_clause", "")


def cite_sp_paragraph(rule_id: str) -> str | None:
    """Return literal SP text for the paragraph referenced by rule_id.

    Falls back to the human-readable sp_clause label from rules.yaml when
    the Chroma index is not built. Always returns *something* useful for
    the report — never None unless the rule_id is unknown.
    """
    _ensure_loaded()
    clause = _CITATION_MAP.get(rule_id)
    if not clause:
        return None

    if not _INDEX_DIR.exists():
        return f"{clause} (полный текст СП будет добавлен после построения RAG-индекса)"

    try:
        import chromadb
    except ImportError:
        return clause

    client = chromadb.PersistentClient(path=str(_INDEX_DIR))
    try:
        collection = client.get_collection(_COLLECTION)
    except Exception:
        return clause

    results = collection.query(query_texts=[clause], n_results=1)
    docs = results.get("documents", [[]])[0]
    if not docs:
        return clause
    return f"{clause}: «{docs[0][:500]}…»"


def build_index(pdf_path: Path) -> int:
    """Build the Chroma index from a PDF. Returns chunk count."""
    import chromadb
    from chromadb.utils import embedding_functions
    from pypdf import PdfReader

    if not pdf_path.exists():
        raise FileNotFoundError(f"SP PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    pages = [p.extract_text() or "" for p in reader.pages]
    full_text = "\n".join(pages)

    # Naive paragraph splitter — good enough for an SP PDF.
    chunks = [c.strip() for c in full_text.split("\n\n") if len(c.strip()) > 80]

    _INDEX_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(_INDEX_DIR))

    # Default sentence-transformers (small, runs CPU-only). Override with
    # OPENAI_API_KEY + chromadb OpenAI embedder if quality matters.
    ef = embedding_functions.DefaultEmbeddingFunction()

    if _COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(_COLLECTION)
    collection = client.create_collection(name=_COLLECTION, embedding_function=ef)

    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )
    return len(chunks)


if __name__ == "__main__":
    pdf = Path(os.environ.get("SP_PDF", "data/sp_107.pdf"))
    n = build_index(pdf)
    print(f"Indexed {n} chunks from {pdf}")

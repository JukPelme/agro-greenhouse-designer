"""ChromaDB index over the SP 107.13330 PDF, with per-paragraph chunking.

Two responsibilities:
1. build_index() — one-shot indexing called from `scripts/build_rag.py`
2. cite_sp_paragraph(rule_id) — retrieves the literal text of a paragraph
   referenced by a rule, used to enrich ValidationIssue.sp_citation.

Chunking strategy:
- Strip running header "СП 107.13330.2012" and standalone page numbers.
- Split by paragraph numbers of the form `5.10` / `5.10.1` at line starts.
- Each chunk carries its clause id as metadata for *exact* lookup,
  with semantic search as a fallback.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

_INDEX_DIR = Path(__file__).parent.parent.parent / "chroma_db"
_COLLECTION = "sp_107_13330"

# Match clause numbers at the start of a line: "5.10 …", "5.10.1 …".
_CLAUSE_RE = re.compile(r"(?m)^\s*(\d{1,2}(?:\.\d{1,2}){1,2})\s+")
_HEADER_RE = re.compile(r"СП\s*107\.13330\.20\d{2}", re.IGNORECASE)
_PAGE_NUM_RE = re.compile(r"(?m)^\s*\d{1,3}\s*$")

_RULES_META: dict[str, dict[str, str]] = {}


def _ensure_loaded() -> None:
    if _RULES_META:
        return
    import yaml

    rules_path = Path(__file__).parent.parent.parent / "data" / "rules.yaml"
    if not rules_path.exists():
        return
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))["rules"]
    for r in rules:
        _RULES_META[r["rule_id"]] = {
            "sp_clause": r.get("sp_clause", ""),
            "summary": r.get("summary", ""),
        }


def _clause_from_rule_id(rule_id: str) -> str | None:
    """SP107.5.2 → '5.2'. SP107.10.4 → '10.4'."""
    m = re.match(r"SP107\.(.+)", rule_id)
    return m.group(1) if m else None


def cite_sp_paragraph(rule_id: str) -> str | None:
    """Return literal SP text for the paragraph referenced by rule_id.

    Lookup order:
    1. Exact match by clause_id in metadata (most accurate).
    2. Semantic search by rule summary (fallback for clauses with mismatched IDs).
    3. Just the human-readable clause label if Chroma is unavailable.
    """
    _ensure_loaded()
    meta = _RULES_META.get(rule_id)
    if not meta:
        return None

    clause = meta["sp_clause"]
    summary = meta["summary"]

    if not _INDEX_DIR.exists():
        return f"{clause} (RAG-индекс не построен — см. scripts/build_rag.py)"

    try:
        import chromadb
    except ImportError:
        return clause

    client = chromadb.PersistentClient(path=str(_INDEX_DIR))
    try:
        collection = client.get_collection(_COLLECTION)
    except Exception:
        return clause

    clause_id = _clause_from_rule_id(rule_id)

    # 1. Try exact clause-id match via metadata filter.
    if clause_id:
        try:
            exact = collection.get(where={"clause_id": clause_id})
            docs = exact.get("documents", [])
            if docs:
                return _format_citation(clause, docs[0])
        except Exception:
            pass

    # 2. Semantic search by summary.
    query = summary or clause
    results = collection.query(query_texts=[query], n_results=1)
    docs = results.get("documents", [[]])[0]
    if docs:
        return _format_citation(clause, docs[0])

    return clause


def _format_citation(clause: str, snippet: str) -> str:
    s = snippet.strip()
    if len(s) > 600:
        s = s[:600].rstrip() + "…"
    return f"{clause}:\n> «{s}»"


def _clean_text(raw: str) -> str:
    cleaned = _HEADER_RE.sub("", raw)
    cleaned = _PAGE_NUM_RE.sub("", cleaned)
    # Collapse runs of blank lines.
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def _split_by_clauses(text: str) -> list[tuple[str, str]]:
    """Yield (clause_id, body) for every numbered clause in the document."""
    matches = list(_CLAUSE_RE.finditer(text))
    chunks: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        clause_id = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if len(body) >= 40:  # skip noise
            chunks.append((clause_id, body))
    return chunks


def build_index(pdf_path: Path) -> int:
    """Build the Chroma index from a PDF. Returns chunk count."""
    import chromadb
    from chromadb.utils import embedding_functions
    from pypdf import PdfReader

    if not pdf_path.exists():
        raise FileNotFoundError(f"SP PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    full_text = "\n".join(p.extract_text() or "" for p in reader.pages)
    cleaned = _clean_text(full_text)
    clauses = _split_by_clauses(cleaned)

    _INDEX_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(_INDEX_DIR))
    ef = embedding_functions.DefaultEmbeddingFunction()

    if _COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(_COLLECTION)
    collection = client.create_collection(name=_COLLECTION, embedding_function=ef)

    collection.add(
        documents=[body for _, body in clauses],
        metadatas=[{"clause_id": cid} for cid, _ in clauses],
        ids=[f"clause_{cid}_{i}" for i, (cid, _) in enumerate(clauses)],
    )
    return len(clauses)


if __name__ == "__main__":
    pdf = Path(os.environ.get("SP_PDF", "data/sp_107.pdf"))
    n = build_index(pdf)
    print(f"Indexed {n} clauses from {pdf}")

"""Build the Chroma index from the SP 107.13330 PDF.

Usage:
    python scripts/build_rag.py [path/to/sp_107.pdf]

Defaults to data/sp_107.pdf.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.rag.sp_index import build_index


def main() -> None:
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "sp_107.pdf"
    n = build_index(pdf)
    print(f"Indexed {n} chunks from {pdf}")


if __name__ == "__main__":
    main()

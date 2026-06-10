"""Markdown → HTML → PDF via weasyprint.

Why this stack:
- python-markdown turns the Reporter's Markdown into clean HTML (with tables).
- weasyprint renders the HTML to PDF with proper Cyrillic, no headless browser
  required (unlike pdfkit/playwright which need wkhtmltopdf or Chromium).
- A small CSS file in this module styles the document.
"""

from __future__ import annotations

import os
from pathlib import Path

# Same MPL trick — weasyprint reads fonts via fontconfig, which writes a cache.
os.environ.setdefault("FONTCONFIG_PATH", "/etc/fonts")

import markdown as md  # noqa: E402
from weasyprint import HTML  # noqa: E402

_CSS = """
@page {
    size: A4;
    margin: 22mm 18mm;
    @bottom-right {
        content: "стр. " counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #888;
    }
    @bottom-left {
        content: "agro-greenhouse-designer";
        font-size: 9pt;
        color: #888;
    }
}

html { font-family: "DejaVu Sans", "Liberation Sans", sans-serif; font-size: 10.5pt; color: #222; line-height: 1.45; }

h1 { font-size: 20pt; color: #2C5F2D; border-bottom: 2px solid #2C5F2D; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 14pt; color: #2C5F2D; margin-top: 22px; border-bottom: 1px solid #d0d0d0; padding-bottom: 3px; }
h3 { font-size: 12pt; color: #3a3a3a; margin-top: 16px; }

p { margin: 6px 0; }
strong { color: #1a1a1a; }

table { border-collapse: collapse; width: 100%; margin: 8px 0 14px; font-size: 10pt; }
th, td { border: 1px solid #cccccc; padding: 5px 9px; text-align: left; }
th { background: #f3f5f1; }

ul, ol { margin: 6px 0 10px 18px; padding-left: 8px; }
li { margin: 2px 0; }

img { max-width: 100%; height: auto; display: block; margin: 8px auto; }

code { background: #f4f4f4; padding: 1px 4px; border-radius: 3px; font-family: "DejaVu Sans Mono", monospace; font-size: 9.5pt; }

blockquote {
    border-left: 3px solid #97BC62;
    background: #f9faf6;
    margin: 10px 0;
    padding: 6px 10px;
    color: #444;
    font-style: italic;
}

hr { border: none; border-top: 1px solid #d0d0d0; margin: 16px 0; }

/* Validation severity highlighting */
h3:contains("ERROR") { color: #b71c1c; }
h3:contains("WARNING") { color: #b8860b; }
"""


def markdown_to_pdf(md_text: str, base_url: Path, out_path: Path) -> Path:
    """Render Markdown to a PDF file.

    Args:
        md_text:  the Markdown source produced by Reporter
        base_url: directory used to resolve relative image paths
                  (e.g. <project>/docs so that 'charts/v1/foo.png' works)
        out_path: where to write the PDF

    Returns the written path.
    """
    html_body = md.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )
    html_doc = (
        f"<!DOCTYPE html><html lang='ru'><head><meta charset='utf-8'>"
        f"<style>{_CSS}</style></head><body>{html_body}</body></html>"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_doc, base_url=str(base_url)).write_pdf(str(out_path))
    return out_path

"""
PDF Extractor Skill

Extracts text and metadata from PDF files using pypdf.
Prints results to the terminal and saves them to a .txt file.

Install dependency:
    pip install pypdf
"""

from datetime import datetime
from pathlib import Path


OUTPUT_DIR = Path("pdf_extractions")


def run(query: str) -> str:
    """
    Extract text from a PDF file, print to screen, save to file.

    Args:
        query: Path to the PDF file

    Returns:
        Extracted content as a string (also saved to file)
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        return (
            "Error: pypdf is not installed.\n"
            "Run: pip install pypdf"
        )

    pdf_path = Path(query.strip())

    if not pdf_path.exists():
        return f"Error: File not found — {pdf_path}"

    if pdf_path.suffix.lower() != ".pdf":
        return f"Error: Not a PDF file — {pdf_path}"

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as e:
        return f"Error opening PDF: {e}"

    # --- Metadata ---
    meta = reader.metadata or {}
    num_pages = len(reader.pages)
    title = meta.get("/Title", "N/A")
    author = meta.get("/Author", "N/A")
    created = meta.get("/CreationDate", "N/A")
    encrypted = "Yes" if reader.is_encrypted else "No"

    # --- Extract text from all pages ---
    pages_text = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        pages_text.append((i, text.strip()))

    full_text = "\n\n".join(
        f"--- Page {i} ---\n{text}" if text else f"--- Page {i} --- [no text]"
        for i, text in pages_text
    )

    # --- Build report ---
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""PDF Extraction Report
{'=' * 60}
File      : {pdf_path.name}
Path      : {pdf_path}
Extracted : {timestamp}
{'=' * 60}

METADATA
--------
Title     : {title}
Author    : {author}
Created   : {created}
Pages     : {num_pages}
Encrypted : {encrypted}

CONTENT
-------
{full_text}

{'=' * 60}
"""

    # --- Print to screen ---
    print(report)

    # --- Save to file ---
    OUTPUT_DIR.mkdir(exist_ok=True)
    safe_name = pdf_path.stem.replace(" ", "_")[:50]
    out_file = OUTPUT_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_name}.txt"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"💾 Saved to: {out_file}")

    return report + f"\n💾 Saved to: {out_file}"

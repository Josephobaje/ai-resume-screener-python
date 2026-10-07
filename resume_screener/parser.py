"""Turn resume files (PDF, TXT, Markdown) into plain text."""

from __future__ import annotations

import io
import re
from pathlib import Path

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


class UnsupportedFileError(ValueError):
    """Raised when a resume file type is not supported."""


def _clean(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_bytes(data: bytes, filename: str) -> str:
    """Extract text from raw file bytes; the filename decides the parser."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return _clean("\n".join(pages))
    if suffix in {".txt", ".md"}:
        return _clean(data.decode("utf-8", errors="replace"))
    raise UnsupportedFileError(
        f"Unsupported file type '{suffix or filename}'. Use one of: "
        + ", ".join(sorted(SUPPORTED_EXTENSIONS))
    )


def extract_text(path: str | Path) -> str:
    """Extract text from a resume file on disk."""
    p = Path(path)
    return extract_text_from_bytes(p.read_bytes(), p.name)

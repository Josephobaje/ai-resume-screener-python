import pytest

from resume_screener.parser import UnsupportedFileError, extract_text, extract_text_from_bytes


def test_txt(samples):
    text = extract_text(samples / "resumes" / "amina_bello.txt")
    assert "Amina Bello" in text and "FastAPI" in text


def test_markdown(samples):
    assert "Laravel" in extract_text(samples / "resumes" / "chidi_okafor.md")


def test_pdf(samples):
    text = extract_text(samples / "resumes" / "tunde_adebayo.pdf")
    assert "Tunde Adebayo" in text
    assert "FastAPI" in text


def test_unsupported_type():
    with pytest.raises(UnsupportedFileError):
        extract_text_from_bytes(b"x", "resume.exe")


def test_whitespace_cleanup():
    assert extract_text_from_bytes(b"a   b\n\n\n\nc", "x.txt") == "a b\n\nc"

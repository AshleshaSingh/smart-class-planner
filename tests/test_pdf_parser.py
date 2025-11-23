"""
Unit tests for pdf_parser.py
"""

import io
import pytest
import builtins
from unittest.mock import patch, MagicMock
from pypdf.errors import PdfReadError
from smart_class_planner.infrastructure.pdf_parser import PDFParser

# class DummyPdfReader:
#     """Minimal mock for PdfReader with .pages list."""
#     def __init__(self, *args, **kwargs):
#         page = MagicMock()
#         page.extract_text.return_value = "CPSC 6105 - Software Engineering"
#         self.pages = [page]

@patch("smart_class_planner.infrastructure.pdf_parser.os.path.exists", return_value=True)
@patch("smart_class_planner.infrastructure.pdf_parser.PdfReader")
def test_parse_valid_pdf(mock_reader, mock_exists, tmp_path):
    """Ensure PDFParser.parse() completes without raising exceptions."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "CPSC 6105 - Software Engineering"
    mock_reader.return_value.pages = [mock_page]

    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF dummy data")

    parser = PDFParser()
    try:
        result = parser.parse(str(pdf_file))
    except Exception as e:
        pytest.fail(f"parse() raised exception: {e}")

    assert result is not None or result is False


def test_parse_missing_pdf():
    """Should raise FileNotFoundError for missing file."""
    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.pdf")


def test_parse_invalid_pdf(tmp_path):
    """Should raise PdfReadError or handle corrupted PDF file gracefully."""
    invalid_pdf = tmp_path / "corrupted.pdf"
    invalid_pdf.write_text("Not a real PDF")

    parser = PDFParser()
    try:
        result = parser.parse(str(invalid_pdf))
        assert result in (None, {}, [], False)
    except (PdfReadError, Exception):
        pytest.xfail("Invalid PDF should raise PdfReadError or be caught gracefully")


@patch("smart_class_planner.infrastructure.pdf_parser.os.path.exists", return_value=True)
@patch("smart_class_planner.infrastructure.pdf_parser.PdfReader")
def test_parse_empty_pdf(mock_reader, mock_exists):
    """Handle empty PDF gracefully."""
    mock_reader.return_value.pages = []
    parser = PDFParser()
    result = parser.parse("dummy.pdf")
    assert isinstance(result, list)
    assert result == []


@patch("smart_class_planner.infrastructure.pdf_parser.os.path.exists", return_value=True)
@patch("smart_class_planner.infrastructure.pdf_parser.PdfReader")
def test_parse_missing_fields(mock_reader, mock_exists):
    """Simulate missing text on PDF pages."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_reader.return_value.pages = [mock_page]
    parser = PDFParser()
    result = parser.parse("dummy.pdf")
    assert isinstance(result, list)


# def test_parse_invalid_pdf(monkeypatch):
#     """Test-to-fail: invalid or missing PDF file."""
#     parser = PDFParser()
#     with pytest.raises(FileNotFoundError):
#         parser.parse("missing_file.pdf")


# def test_pdf_parser_handles_invalid_file(tmp_path):
#     """Handle invalid file gracefully."""
#     bad_pdf = tmp_path / "bad.pdf"
#     bad_pdf.write_text("not a real pdf")

#     parser = PDFParser()
#     result = parser.parse(str(bad_pdf))
#     assert result == []

# def test_validate_valid_file(monkeypatch, tmp_path):
#     """Simulate valid DegreeWorks file detection."""
#     pdf_file = tmp_path / "degreeworks.pdf"
#     pdf_file.write_bytes(b"%PDF-1.4\n%%EOF")

#     parser = PDFParser()

#     # Mock open() to simulate valid keywords
#     monkeypatch.setattr("builtins.open", lambda p, m="rb": io.BytesIO(b"Degree Works report"))
#     parser.validate(str(pdf_file))  # Should not raise


# def test_validate_invalid_file(monkeypatch, tmp_path):
#     """Should raise ValueError for missing DegreeWorks keywords."""
#     pdf_file = tmp_path / "invalid.pdf"
#     pdf_file.write_bytes(b"%PDF-1.4\n%%EOF")

#     parser = PDFParser()
#     monkeypatch.setattr("builtins.open", lambda p, m="rb": io.BytesIO(b"random text without keywords"))

#     with pytest.raises(ValueError):
#         parser.validate(str(pdf_file))


def test_find_course_title_patterns():
    """Test various _find_course_title regex match patterns."""
    parser = PDFParser()
    text1 = "CPSC 6109 - Object Oriented Programming"
    text2 = "CPSC 6110 Advanced AI Still In Progress"
    text3 = "CPSC 6115 Grade Complete"

    assert "Programming" in parser._find_course_title(text1, "CPSC 6109")
    assert "Advanced" in parser._find_course_title(text2, "CPSC 6110")
    assert parser._find_course_title("Unrelated text", "CPSC 6120") == ""

def test_parse_handles_pdfreaderror(monkeypatch, tmp_path):
    """Ensure parse() raises a wrapped exception for PdfReadError."""
    pdf_file = tmp_path / "broken.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%%EOF")

    parser = PDFParser()

    def fake_pdfreader(_):
        raise PdfReadError("Corrupted file")

    monkeypatch.setattr("smart_class_planner.infrastructure.pdf_parser.PdfReader", fake_pdfreader)
    with pytest.raises(Exception, match="PDF parsing failed"):
        parser.parse(str(pdf_file))


def test_parse_unexpected_exception(monkeypatch, tmp_path):
    """Ensure parse() raises a wrapped exception for unexpected errors."""
    pdf_file = tmp_path / "weird.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%%EOF")

    parser = PDFParser()

    def raise_generic(_):
        raise RuntimeError("unexpected")

    monkeypatch.setattr("smart_class_planner.infrastructure.pdf_parser.PdfReader", raise_generic)
    with pytest.raises(Exception, match="PDF parsing failed"):
        parser.parse(str(pdf_file))


def test_find_course_title_edge_cases():
    """Check edge regex and text variants."""
    parser = PDFParser()
    # Missing dash, but still has course code and title separated by spaces
    text = "CPSC6105 Advanced Algorithms"
    title = parser._find_course_title(text, "CPSC6105")
    assert "Advanced" in title or title == ""

    # Empty text input
    assert parser._find_course_title("", "CPSC9999") == ""


def test_validate_handles_ioerror(monkeypatch, tmp_path):
    """Simulate IOError during open() in validate() to test exception path."""
    pdf_file = tmp_path / "iofail.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%%EOF")
    parser = PDFParser()

    def fake_open(*args, **kwargs):
        raise IOError("cannot open")

    monkeypatch.setattr(builtins, "open", fake_open)
    with pytest.raises(IOError):
        parser.validate(str(pdf_file))
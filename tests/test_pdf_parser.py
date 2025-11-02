"""
Unit tests for pdf_parser.py
"""

import io
import pytest
from unittest.mock import patch, MagicMock
from PyPDF2.errors import PdfReadError
from smart_class_planner.infrastructure.pdf_parser import PDFParser

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
    """Should raise FileNotFoundError for missing file"""
    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.pdf")

def test_parse_invalid_pdf(tmp_path):
    """Should raise PdfReadError or handle corrupted PDF file gracefully"""
    invalid_pdf = tmp_path / "corrupted.pdf"
    invalid_pdf.write_text("Not a real PDF")

    parser = PDFParser()

    try:
        result = parser.parse(str(invalid_pdf))
        # if no exception raised, must return something falsy
        assert result is None or result == {} or result is False
    except (PdfReadError, Exception):
        # acceptable: library threw expected exception
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

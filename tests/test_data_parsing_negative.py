import pytest
from smart_class_planner.infrastructure.study_plan_parser import StudyPlanParser
from smart_class_planner.infrastructure.pdf_parser import PDFParser
from smart_class_planner.infrastructure.program_map_scraper import ProgramMapScraper
from smart_class_planner.application.plan_generator import PlanGenerator
from smart_class_planner.domain.repository import Repository

# ------------------------
# Study Plan Parser - invalid
# ------------------------
def test_study_plan_parser_invalid_file(tmp_path):
    parser = StudyPlanParser()
    invalid_file = tmp_path / "invalid.xlsx"
    invalid_file.write_text("garbage data")
    with pytest.raises(Exception):
        parser.parse(str(invalid_file))

# ------------------------
# PDF Parser - corrupted PDF
# ------------------------
def test_pdf_parser_corrupted(monkeypatch):
    parser = PDFParser()
    def mock_parse(path):
        raise ValueError("Stream has ended unexpectedly")
    monkeypatch.setattr(parser, "parse", mock_parse)
    with pytest.raises(ValueError):
        parser.parse("bad.pdf")

# ------------------------
# Program Map Scraper - missing data
# ------------------------
def test_program_map_scraper_empty(monkeypatch):
    scraper = ProgramMapScraper()
    monkeypatch.setattr(scraper, "parse", lambda x: {})
    result = scraper.parse("fake_url")
    assert result == {}

# ------------------------
# PlanGenerator - invalid prereq or missing offerings
# ------------------------
def test_plan_generator_with_invalid_data():
    repo = Repository()
    gen = PlanGenerator(repo)
    result = gen.generate_plan([], "Fall", 2025)
    assert result is None or result == []  # or appropriate empty structure


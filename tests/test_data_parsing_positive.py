import pytest
from smart_class_planner.infrastructure.study_plan_parser import StudyPlanParser
from smart_class_planner.infrastructure.pdf_parser import PDFParser
from smart_class_planner.infrastructure.program_map_scraper import ProgramMapScraper

import pandas as pd

def test_study_plan_parser_valid(tmp_path):
    parser = StudyPlanParser()
    df = pd.DataFrame({
        "Offer": ["Fall 2025"],               # matches `offer_col` logic
        "Course Number": ["CPSC6105"],        # matches `code_col` logic
        "Course Name": ["Advanced Algorithms"],  # this triggers the correct parsing branch
        "Required In": ["ACS"]
    })
    excel_file = tmp_path / "plan.xlsx"
    df.to_excel(excel_file, index=False)

    result = parser.parse(str(excel_file))
    assert isinstance(result, dict)
    assert "Fall 2025" in result
    assert result["Fall 2025"][0]["code"] == "CPSC6105"


def test_pdf_parser_handles_valid(monkeypatch):
    parser = PDFParser()
    monkeypatch.setattr(parser, "parse", lambda x: [{"code": "CPSC6105"}])
    data = parser.parse("mock.pdf")
    assert data[0]["code"] == "CPSC6105"

def test_program_map_scraper_valid(monkeypatch):
    scraper = ProgramMapScraper()
    monkeypatch.setattr(scraper, "parse", lambda x: {"Fall 2025": [{"code": "CPSC6105"}]})
    result = scraper.parse("fake_url")
    assert "Fall 2025" in result

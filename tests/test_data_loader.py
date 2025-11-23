"""
Unit tests for DataLoader class in smart_class_planner.infrastructure.data_loader.


These tests validate how the DataLoader integrates data from multiple parsers
(DegreeWorks PDF, Study Plan Excel, Program Map, and Prerequisite Graph).


Each test uses monkeypatching to replace actual parsing logic with mocks so that
we can focus solely on verifying control flow, error handling, and summary outputs.
"""

from smart_class_planner.infrastructure.data_loader import DataLoader
from smart_class_planner.domain.repository import Repository

def test_data_loader_load_all(monkeypatch):
    """Test successful integration of all loaders using mocked parser methods."""
    repo = Repository()
    loader = DataLoader(repo)

    # Mock all loaders
    monkeypatch.setattr(loader, "load_degreeworks", lambda x: ["CPSC6105"])
    monkeypatch.setattr(loader, "load_study_plan", lambda x: 5)
    monkeypatch.setattr(loader, "load_program_map", lambda x: 3)
    monkeypatch.setattr(loader, "load_prerequisites", lambda x: 2)

    # Execute combined data loading process
    summary, remaining = loader.load_all(
        pdf_path="deg.pdf", excel_path="plan.xlsx", program_map="map", prereq_data={}
    )

    # Verify data mapping consistency
    assert summary["study_plan"] == 5
    assert summary["program_map"] == 3
    assert remaining == ["CPSC6105"]

def test_data_loader_load_all_partial(monkeypatch):
    """Test DataLoader when only a subset of inputs is available."""
    repo = Repository()
    loader = DataLoader(repo)

    # Only provide minimal valid mock data
    monkeypatch.setattr(loader, "load_degreeworks", lambda x: ["CPSC6105"])
    monkeypatch.setattr(loader, "load_study_plan", lambda x: {"Fall": []})
    monkeypatch.setattr(loader, "load_program_map", lambda x: {"FA25": []})
    monkeypatch.setattr(loader, "load_prerequisites", lambda x: 3)

    result = loader.load_all("deg.pdf", "plan.xlsx", "map.xlsx")

    # Ensure function returns a (summary, remaining) tuple
    assert isinstance(result, tuple)
    summary, remaining = result
    assert isinstance(summary, dict)
    assert isinstance(remaining, list)
    

def test_data_loader_missing_files(tmp_path):
    """Test how DataLoader behaves when files are missing or paths invalid."""
    repo = Repository()
    loader = DataLoader(repo)

    # Trigger exception paths by using missing/nonexistent files
    summary, remaining = loader.load_all("missing.pdf", "missing.xlsx", "missing.xlsx")

    expected = {
    "degreeworks": 0, # Expect count fallback instead of list
    "study_plan": {},
    "program_map": {}
    }

    # Confirm error-handling fallback behavior
    assert summary == expected
    assert remaining == []

def test_load_degreeworks_file_not_found(monkeypatch):
    """Ensure FileNotFoundError from PDF parser is handled gracefully."""
    repo = Repository()
    loader = DataLoader(repo)

    # Mock parser to simulate FileNotFoundError when parsing PDF
    monkeypatch.setattr(
        loader.pdf_parser, "parse",
        lambda x: (_ for _ in ()).throw(FileNotFoundError("missing file"))
    )

    # Expect graceful empty list fallback
    result = loader.load_degreeworks("invalid.pdf")
    assert result == []


def test_load_degreeworks_unexpected_error(monkeypatch):
    """Validate that unexpected errors in DegreeWorks parsing are caught safely."""
    repo = Repository()
    loader = DataLoader(repo)

    # Simulate unexpected ValueError during PDF parsing
    monkeypatch.setattr(
        loader.pdf_parser, "parse",
        lambda x: (_ for _ in ()).throw(ValueError("bad data"))
    )

    # Should return empty list instead of propagating exception
    result = loader.load_degreeworks("deg.pdf")
    assert result == []


def test_load_study_plan_success(monkeypatch):
    """Test that Study Plan Excel parsing correctly adds courses and offerings."""
    repo = Repository()
    loader = DataLoader(repo)

    # Mock StudyPlanParser output to simulate parsed Excel data
    mock_data = {"Fall 2025": [{"code": "CPSC6105", "title": "Adv Algo"}]}
    monkeypatch.setattr(loader.study_parser, "parse", lambda x: mock_data)

    # Execute method and verify one course added successfully
    result = loader.load_study_plan("plan.xlsx")
    assert result == 1
    assert "CPSC6105" in repo.courses


def test_load_program_map_success(monkeypatch):
    """Test that Program Map parsing correctly adds offerings from scraper output."""
    repo = Repository()
    loader = DataLoader(repo)

    # Mock scraper output to simulate parsed HTML data
    mock_map = {"Fall 2025": [{"code": "CPSC6106", "year": 2025}]}
    monkeypatch.setattr(loader.map_scraper, "parse", lambda x: mock_map)

    # Verify offering successfully added
    result = loader.load_program_map("url")
    assert result == 1


def test_load_prerequisites_success(monkeypatch):
    """Test that prerequisite relationships are correctly loaded into repository."""
    repo = Repository()
    loader = DataLoader(repo)

    # Mock graph parser output representing course dependency edges
    mock_graph = {"edges": [["CPSC6105", "CPSC6106"]]}
    monkeypatch.setattr(loader.graph_parser, "parse", lambda x: mock_graph)

    # Ensure prerequisite relation is successfully added to repository
    result = loader.load_prerequisites(mock_graph)
    assert result == 1
    assert repo.prerequisites[0].course_code == "CPSC6105"

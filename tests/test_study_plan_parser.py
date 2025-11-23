"""
Tests for study_plan_parser.py
"""

import re
import pandas as pd
import pytest
from unittest.mock import patch
from smart_class_planner.infrastructure.study_plan_parser import StudyPlanParser


@patch("os.path.exists", return_value=True)
@patch("pandas.read_excel")
def test_parse_returns_courses(mock_read_excel, mock_exists):
    """Should parse Excel and not crash when data is valid."""
    df = pd.DataFrame({
        "Course Code": ["CPSC 6105"],
        "Course Name": ["Software Design"],
        "Credits": [3]
    })
    mock_read_excel.return_value = df

    parser = StudyPlanParser()
    path = "dummy.xlsx"

    try:
        result = parser.parse(path)
    except Exception as e:
        pytest.fail(f"parse() raised exception: {e}")

    assert result is not None
    assert isinstance(result, (list, dict, bool))


@patch("os.path.exists", return_value=True)
@patch("pandas.read_excel")
def test_parse_handles_empty_excel(mock_read_excel, mock_exists):
    """Should handle empty Excel gracefully."""
    mock_read_excel.return_value = pd.DataFrame()

    parser = StudyPlanParser()
    path = "empty.xlsx"

    try:
        result = parser.parse(path)
    except Exception as e:
        pytest.fail(f"parse() raised exception: {e}")

    assert result is not None
    assert isinstance(result, (list, dict, bool))


def test_parse_valid_excel(tmp_path):
    """Test StudyPlanParser.parse() with real Excel file."""
    df = pd.DataFrame({
        "Course Code": ["CPSC 6105", "CPSC 6106"],
        "Course Title": ["Software Engg", "Advanced OS"],
        "Credits": [3, 3],
        "Term": ["Fall", "Spring"]
    })
    excel_path = tmp_path / "plan.xlsx"
    df.to_excel(excel_path, index=False)

    parser = StudyPlanParser()

    try:
        result = parser.parse(str(excel_path))
    except Exception as e:
        pytest.fail(f"parse() raised exception: {e}")

    assert result is not None
    assert isinstance(result, (list, dict, bool))

def test_parse_missing_file():
    """Should raise FileNotFoundError for non-existent file"""
    parser = StudyPlanParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("missing.xlsx")

def test_parse_invalid_excel(tmp_path):
    """Should raise ValueError or handle invalid Excel file gracefully"""
    file = tmp_path / "broken.xlsx"
    file.write_text("not an excel file")
    parser = StudyPlanParser()

    try:
        result = parser.parse(str(file))
        assert result is not None
    except ValueError:
        pytest.xfail("Invalid Excel should raise ValueError or return empty result")

@patch("smart_class_planner.infrastructure.study_plan_parser.os.path.exists", return_value=True)
@patch("smart_class_planner.infrastructure.study_plan_parser.pd.read_excel")
def test_parse_missing_columns(mock_read_excel, mock_exists):
    """Handle Excel missing columns gracefully."""
    df = pd.DataFrame({"Code": ["CPSC 6105"], "Name": ["Design"]})
    mock_read_excel.return_value = df
    parser = StudyPlanParser()
    result = parser.parse("missing_cols.xlsx")
    assert isinstance(result, (list, dict))
    assert result == {} or result == []


@patch("smart_class_planner.infrastructure.study_plan_parser.os.path.exists", return_value=True)
@patch("smart_class_planner.infrastructure.study_plan_parser.pd.read_excel")
def test_parse_duplicate_courses(mock_read_excel, mock_exists):
    """Handle duplicate courses gracefully."""
    df = pd.DataFrame({
        "Course Code": ["CPSC 6105", "CPSC 6105"],
        "Course Name": ["Software", "Software"],
        "Credits": [3, 3],
    })
    mock_read_excel.return_value = df
    parser = StudyPlanParser()
    result = parser.parse("dupes.xlsx")
    assert isinstance(result, (list, dict))
    assert result == {} or result == []

# def test_parse_missing_columns(tmp_path):
#     """Test-to-fail: Excel missing required columns."""
#     df = pd.DataFrame({"Course": ["CSU101"]})
#     file = tmp_path / "incomplete.xlsx"
#     df.to_excel(file, index=False)
#     parser = StudyPlanParser()
#     result = parser.parse(str(file))
#     assert isinstance(result, dict)

def test_study_plan_parser_invalid_structure(tmp_path):
    df = pd.DataFrame({"Something": ["random"]})
    excel_file = tmp_path / "bad.xlsx"
    df.to_excel(excel_file, index=False)

    parser = StudyPlanParser()
    result = parser.parse(str(excel_file))
    assert result == {}

def test_validate_graduate_study_plan_valid(monkeypatch, tmp_path):
    """Ensure validation passes for a well-structured study plan."""
    file_path = tmp_path / "valid_plan.xlsx"
    df = pd.DataFrame({"Course Name": ["CPSC 6105"], "Offer": ["Fall Start"], "Required In": ["ACS"]})
    df.to_excel(file_path, index=False)

    parser = StudyPlanParser()
    result = parser.validate_graduate_study_plan(str(file_path))
    assert result is True


def test_validate_graduate_study_plan_as_schedule(monkeypatch, tmp_path):
    """Detect that a schedule file is rejected as invalid study plan."""
    file_path = tmp_path / "schedule.xlsx"
    df = pd.DataFrame({"Title": ["Four-Year Schedule"], "Column2": ["Online"]})
    df.to_excel(file_path, index=False)
    parser = StudyPlanParser()

    with pytest.raises(ValueError, match=r"(Four|4)-Year"):
        parser.validate_graduate_study_plan(str(file_path))


def test_validate_graduate_study_plan_missing_headers(tmp_path):
    """Reject file with missing key terms."""
    file_path = tmp_path / "bad_plan.xlsx"
    df = pd.DataFrame({"Unknown": [1], "Something": [2]})
    df.to_excel(file_path, index=False)

    parser = StudyPlanParser()
    with pytest.raises(ValueError, match="Missing CYBR/ACS"):
        parser.validate_graduate_study_plan(str(file_path))


def test_validate_graduate_study_plan_too_many_columns(tmp_path):
    """Reject file with too many columns (>10)."""
    file_path = tmp_path / "wide.xlsx"
    df = pd.DataFrame({f"Col{i}": [i] for i in range(15)})
    df.to_excel(file_path, index=False)
    parser = StudyPlanParser()
    with pytest.raises(ValueError) as excinfo:
        parser.validate_graduate_study_plan(str(file_path))
    print("ACTUAL ERROR MESSAGE:", excinfo.value)


def test_validate_four_year_schedule_valid(tmp_path):
    """Ensure validation succeeds for legitimate schedule text."""
    file_path = tmp_path / "schedule.xlsx"
    df = pd.DataFrame({"Course Title": ["Intro"], "FA24": ["X"]})
    df.to_excel(file_path, index=False)
    parser = StudyPlanParser()
    parser.validate_four_year_schedule(str(file_path))


def test_validate_four_year_schedule_invalid(tmp_path):
    """Ensure invalid 4-year schedule raises."""
    file_path = tmp_path / "bad_schedule.xlsx"
    df = pd.DataFrame({"X": ["random text"]})
    df.to_excel(file_path, index=False)
    parser = StudyPlanParser()
    with pytest.raises(ValueError, match="Four-Year Schedule"):
        parser.validate_four_year_schedule(str(file_path))

def test_parse_graduate_study_plan_basic(monkeypatch):
    """Verify parsing produces structured output from simple DataFrame."""
    df = pd.DataFrame({
        "Course Number": ["CPSC 6105"],
        "Course Name": ["Advanced Algorithms"],
        "Offer": ["Fall 2025"],
        "Required In": ["ACS"]
    })
    parser = StudyPlanParser()
    result = parser._parse_graduate_study_plan(df)
    assert "Fall 2025" in result
    assert result["Fall 2025"][0]["code"] == "CPSC 6105"


def test_parse_graduate_study_plan_skip_invalid(monkeypatch):
    """Ensure invalid rows (no code or wrong track) are skipped."""
    df = pd.DataFrame({
        "Course Number": ["", "CPSC 9999"],
        "Course Name": ["Header", "Random"],
        "Offer": ["Fall", "Fall"],
        "Required In": ["OtherDept", ""]
    })
    parser = StudyPlanParser()
    result = parser._parse_graduate_study_plan(df)
    assert isinstance(result, dict)
    assert all("ACS" not in str(v) and "CYBR" not in str(v) for v in result.values())


def test_parse_four_year_schedule_valid(tmp_path):
    """Ensure 4-Year Schedule parsing returns structured term mapping."""
    file_path = tmp_path / "schedule.xlsx"
    df = pd.DataFrame({
        "Course": ["CPSC 6105", "CYBR 6120"],
        "Course Title": ["Adv Algo", "Cyber Ops"],
        "FA24": ["D,N,O", "D"],
        "SP25": [pd.NA, "O"]
    })
    df.to_excel(file_path, index=False)
    parser = StudyPlanParser()
    result = parser._parse_four_year_schedule(str(file_path))
    assert isinstance(result, dict)
    assert any(isinstance(v, list) for v in result.values())


def test_parse_four_year_schedule_ignore_invalid(tmp_path):
    """Ensure parser skips invalid/off-format entries."""
    file_path = tmp_path / "bad_schedule.xlsx"
    df = pd.DataFrame({
        "Course": ["HIST 1000", "CPSC 9999"],
        "Course Title": ["History", "Intro to CS"],
        "FA24": ["??", ""]
    })
    df.to_excel(file_path, index=False)
    parser = StudyPlanParser()
    result = parser._parse_four_year_schedule(str(file_path))
    assert all(isinstance(v, list) for v in result.values())


def test_parse_switch_logic(monkeypatch, tmp_path):
    """Ensure parse() correctly routes to the appropriate parser."""
    file_path = tmp_path / "plan.xlsx"
    df = pd.DataFrame({"Course Name": ["X"], "Offer": ["Y"]})
    df.to_excel(file_path, index=False)
    parser = StudyPlanParser()
    result = parser.parse(str(file_path))
    assert isinstance(result, dict) or result == {}

    # Unknown structure fallback
    df2 = pd.DataFrame({"Random": [1], "Header": [2]})
    f2 = tmp_path / "unknown.xlsx"
    df2.to_excel(f2, index=False)
    result2 = parser.parse(str(f2))
    assert result2 == {}
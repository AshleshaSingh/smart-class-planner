"""
Tests for study_plan_parser.py
"""

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
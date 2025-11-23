from smart_class_planner.presentation.excel_exporter import ExcelExporter
import pytest

def test_export_with_invalid_data(tmp_path):
    """Test-to-fail: export should handle empty dataset gracefully."""
    exporter = ExcelExporter()
    output = tmp_path / "output.xlsx"
    exporter.export_plan([], output)  # should not crash
    assert output.exists()

def test_excel_exporter_empty_plan(tmp_path):
    exp = ExcelExporter()
    output = tmp_path / "out.xlsx"
    assert exp.export_plan([], output) == False
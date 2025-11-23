""" Run with: pytest tests/test_gui.py -v --tb=short """

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, PropertyMock

# Fix import path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_wizard():
    """Create a mocked wizard instance with all Tkinter mocked."""
    with patch('smart_class_planner.presentation.setup_wizard.tk.Tk') as mock_tk, \
         patch('smart_class_planner.presentation.setup_wizard.tk.Frame') as mock_frame, \
         patch('smart_class_planner.presentation.setup_wizard.tk.Label'), \
         patch('smart_class_planner.presentation.setup_wizard.tk.Button'), \
         patch('smart_class_planner.presentation.setup_wizard.tk.Text'), \
         patch('smart_class_planner.presentation.setup_wizard.tk.Canvas'), \
         patch('smart_class_planner.presentation.setup_wizard.tk.Scrollbar'), \
         patch('smart_class_planner.presentation.setup_wizard.ttk.Notebook'), \
         patch('smart_class_planner.presentation.setup_wizard.ttk.Style'):
        
        # Configure mock root
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        # Configure mock frames to return new mocks
        mock_frame.return_value = MagicMock()
        
        from smart_class_planner.presentation.setup_wizard import SetupWizard
        
        wizard = SetupWizard()
        wizard.degreeworks_status = Mock()
        wizard.study_plan_status = Mock()
        wizard.schedule_status = Mock()
        wizard.results_text = Mock()
        wizard.notebook = Mock()
        return wizard


class TestFileUploads:
    """Test file upload handlers"""

    @patch('smart_class_planner.presentation.setup_wizard.filedialog.askopenfilename')
    @patch('smart_class_planner.presentation.setup_wizard.PDFParser')
    @patch('smart_class_planner.presentation.setup_wizard.messagebox')
    def test_upload_pdf_success(self, mock_msg, mock_parser_cls, mock_dialog, mock_wizard):
        """Test uploading DegreeWorks PDF successfully."""
        mock_dialog.return_value = "/test/file.pdf"
        mock_parser_cls.return_value.validate.return_value = None
        
        mock_wizard.browse_degreeworks()
        
        assert mock_wizard.degreeworks_pdf == "/test/file.pdf"
        mock_msg.showinfo.assert_called_once()

    @patch('smart_class_planner.presentation.setup_wizard.filedialog.askopenfilename')
    @patch('smart_class_planner.presentation.setup_wizard.PDFParser')
    @patch('smart_class_planner.presentation.setup_wizard.messagebox')
    def test_upload_pdf_invalid(self, mock_msg, mock_parser_cls, mock_dialog, mock_wizard):
        """Test uploading invalid PDF shows error."""
        mock_dialog.return_value = "/test/bad.pdf"
        mock_parser_cls.return_value.validate.side_effect = ValueError("Invalid")
        
        mock_wizard.browse_degreeworks()
        
        assert mock_wizard.degreeworks_pdf is None
        mock_msg.showerror.assert_called_once()

    @patch('smart_class_planner.presentation.setup_wizard.filedialog.askopenfilename')
    def test_upload_cancel(self, mock_dialog, mock_wizard):
        """Test canceling file dialog."""
        mock_dialog.return_value = ""
        mock_wizard.browse_degreeworks()
        assert mock_wizard.degreeworks_pdf is None

    @patch('smart_class_planner.presentation.setup_wizard.filedialog.askopenfilename')
    @patch('smart_class_planner.presentation.setup_wizard.StudyPlanParser')
    @patch('smart_class_planner.presentation.setup_wizard.messagebox')
    def test_upload_study_plan(self, mock_msg, mock_parser_cls, mock_dialog, mock_wizard):
        """Test uploading Study Plan Excel."""
        mock_dialog.return_value = "/test/plan.xlsx"
        mock_parser_cls.return_value.validate_graduate_study_plan.return_value = True
        
        mock_wizard.browse_study_plan()
        
        assert mock_wizard.study_plan_excel == "/test/plan.xlsx"

    @patch('smart_class_planner.presentation.setup_wizard.filedialog.askopenfilename')
    @patch('smart_class_planner.presentation.setup_wizard.StudyPlanParser')
    @patch('smart_class_planner.presentation.setup_wizard.messagebox')
    def test_upload_schedule(self, mock_msg, mock_parser_cls, mock_dialog, mock_wizard):
        """Test uploading Schedule Excel."""
        mock_dialog.return_value = "/test/schedule.xlsx"
        mock_parser_cls.return_value.validate_four_year_schedule.return_value = True
        
        mock_wizard.browse_schedule()
        
        assert mock_wizard.schedule_excel == "/test/schedule.xlsx"

class TestPlanGeneration:
    """Test plan generation"""

    @patch('smart_class_planner.presentation.setup_wizard.messagebox')
    def test_generate_missing_files(self, mock_msg, mock_wizard):
        """Test warning when files missing."""
        mock_wizard.generate_plan()
        mock_msg.showwarning.assert_called_once()

class TestExport:
    """Test Excel export"""

    @patch('smart_class_planner.presentation.setup_wizard.messagebox')
    def test_export_no_plan(self, mock_msg, mock_wizard):
        """Test export warning when no plan exists."""
        mock_wizard.export_to_excel()
        mock_msg.showwarning.assert_called_once()

    @patch('smart_class_planner.presentation.setup_wizard.messagebox')
    def test_export_empty_plan(self, mock_msg, mock_wizard):
        """Test export with empty plan (graduation)."""
        mock_wizard.generated_plan = []
        mock_wizard.export_to_excel()
        mock_msg.showinfo.assert_called_once()

    @patch('smart_class_planner.presentation.setup_wizard.filedialog.asksaveasfilename')
    def test_export_cancel(self, mock_dialog, mock_wizard):
        """Test canceling export dialog."""
        mock_wizard.generated_plan = [Mock()]
        mock_dialog.return_value = ""
        mock_wizard.export_to_excel()


class TestClear:
    """Test clear functionality"""

    @patch('smart_class_planner.presentation.setup_wizard.messagebox.askyesno')
    def test_clear_cancel(self, mock_yesno, mock_wizard):
        """Test canceling clear operation."""
        mock_wizard.degreeworks_pdf = "/test.pdf"
        mock_yesno.return_value = False
        
        mock_wizard.clear_all_data()
        
        assert mock_wizard.degreeworks_pdf == "/test.pdf"

    @patch('smart_class_planner.presentation.setup_wizard.messagebox.askyesno')
    @patch('smart_class_planner.presentation.setup_wizard.messagebox.showinfo')
    def test_clear_confirm(self, mock_info, mock_yesno, mock_wizard):
        """Test clearing all data."""
        mock_wizard.degreeworks_pdf = "/test.pdf"
        mock_wizard.study_plan_excel = "/plan.xlsx"
        mock_wizard.generated_plan = [Mock()]
        mock_yesno.return_value = True
        
        mock_wizard.clear_all_data()
        
        assert mock_wizard.degreeworks_pdf is None
        assert mock_wizard.study_plan_excel is None
        assert mock_wizard.generated_plan is None


class TestDisplay:
    """Test results display"""

    def test_display_empty_plan(self, mock_wizard):
        """Test displaying empty plan (graduation)."""
        mock_wizard._display_plan_results([])
        mock_wizard.results_text.insert.assert_called()

    def test_display_plan_with_courses(self, mock_wizard):
        """Test displaying plan with courses."""
        mock_course = Mock(code="CPSC 6000", title="Algorithms", credits=3)
        mock_semester = Mock(
            get_term_key=Mock(return_value="Fall 2025"),
            courses=[mock_course],
            total_credits=3
        )
        
        mock_wizard._display_plan_results([mock_semester])
        
        mock_wizard.results_text.insert.assert_called()


if __name__ == "__main__":
    # Run with shorter output
    pytest.main([__file__, "-v", "--tb=short", "--no-header"])
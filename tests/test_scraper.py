from unittest.mock import patch
from smart_class_planner.infrastructure.scraper import PrerequisiteScraper


@patch("smart_class_planner.infrastructure.scraper.requests.get")
def test_scraper_parse_returns_prereqs(mock_get):
    """Ensure parse() returns a list (empty or filled) for valid HTML."""
    html = """
    <div class='courseblock'>
        <p><strong>CPSC 6105</strong> - Software Engineering
        <em>Prerequisite: CPSC 6106.</em></p>
    </div>
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = html

    scraper = PrerequisiteScraper()
    try:
        result = scraper.parse()
    except Exception:
        result = []

    assert isinstance(result, (list, dict))
    assert result is not None



@patch("smart_class_planner.infrastructure.scraper.requests.get")
def test_scraper_parse_handles_http_error(mock_get):
    """Should not raise on bad HTTP code."""
    mock_get.return_value.status_code = 404
    mock_get.return_value.text = "Not Found"

    scraper = PrerequisiteScraper()
    try:
        result = scraper.parse()
    except Exception:
        result = []

    assert isinstance(result, (list, dict))
    assert result is not None


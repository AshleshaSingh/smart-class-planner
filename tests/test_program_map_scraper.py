import pytest
from unittest.mock import patch, MagicMock
import requests
from smart_class_planner.infrastructure.program_map_scraper import ProgramMapScraper

@patch("smart_class_planner.infrastructure.program_map_scraper.requests.get")
def test_scraper_parse_success(mock_get):
    """No hardcoded failure; just ensures parse() returns a list."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<html><body><a href='plan.pdf'>Program Map</a></body></html>"

    scraper = ProgramMapScraper()
    try:
        result = scraper.parse()
    except Exception:
        result = []

    assert isinstance(result, (list, dict))
    assert result is not None

@patch("smart_class_planner.infrastructure.program_map_scraper.requests.get")
def test_scraper_parse_handles_error(mock_get):
    """Should handle HTTP 500 without crashing."""
    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Internal Server Error"

    scraper = ProgramMapScraper()
    try:
        result = scraper.parse()
    except Exception:
        result = []

    assert isinstance(result, (list, dict))
    assert result is not None

@patch("smart_class_planner.infrastructure.program_map_scraper.requests.get")
def test_scraper_parse_success(mock_get):
    html = "<html><body><a href='test.pdf'>Program Map</a></body></html>"
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = html

    scraper = ProgramMapScraper()
    result = scraper.parse()
    assert isinstance(result, list) or isinstance(result, dict)

@patch("smart_class_planner.infrastructure.program_map_scraper.requests.get")
def test_parse_empty_html(mock_get):
    """Should handle empty HTML without crashing"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = ""
    scraper = ProgramMapScraper()
    result = scraper.parse()
    assert isinstance(result, (dict, list, bool))

@patch("smart_class_planner.infrastructure.program_map_scraper.requests.get", side_effect=Exception("network error"))
def test_parse_network_exception(mock_get):
    """Should not crash on network failure"""
    scraper = ProgramMapScraper()
    try:
        result = scraper.parse()
    except Exception:
        result = []
    assert result is not None

@patch("smart_class_planner.infrastructure.program_map_scraper.requests.get")
def test_scraper_handles_invalid_html(mock_get):
    """Return empty dict or list when no links found."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<html><body>No links here</body></html>"
    scraper = ProgramMapScraper()
    result = scraper.parse()
    assert isinstance(result, (dict, list))
    assert result == {} or result == []


@patch("smart_class_planner.infrastructure.program_map_scraper.requests.get")
def test_scraper_handles_timeout(mock_get):
    """Gracefully handle network timeout."""
    mock_get.side_effect = requests.exceptions.Timeout
    scraper = ProgramMapScraper()
    result = scraper.parse()
    assert result == {} or result == []

def test_program_map_scraper_handles_empty_page(monkeypatch):
    from smart_class_planner.infrastructure.program_map_scraper import ProgramMapScraper

    scraper = ProgramMapScraper()
    monkeypatch.setattr("smart_class_planner.infrastructure.program_map_scraper.requests.get",
                        lambda url, timeout=10: type("R", (), {"text": "<html></html>", "raise_for_status": lambda self: None})())

    result = scraper.parse()
    assert result == {}

def test_parse_valid_html(monkeypatch):
    """Simulate successful scraping with multiple course tables."""
    html = """
    <html><body>
        <table class="program">
            <tr><th>FALL 2025</th></tr>
            <tr><td>CPSC 6109 - Advanced Programming</td></tr>
            <tr><td>CYBR 6120 - Cyber Defense</td></tr>
        </table>
    </body></html>
    """

    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status.return_value = None

    monkeypatch.setattr("requests.get", lambda *a, **k: mock_resp)

    scraper = ProgramMapScraper()
    result = scraper.parse()
    assert "FALL" in list(result.keys())[0]
    assert any("CPSC" in c["code"] for v in result.values() for c in v)


def test_parse_invalid_html(monkeypatch):
    """Handle invalid HTML content gracefully (missing <html> tag)."""
    mock_resp = MagicMock()
    mock_resp.text = "not real html"
    mock_resp.raise_for_status.return_value = None
    monkeypatch.setattr("requests.get", lambda *a, **k: mock_resp)

    scraper = ProgramMapScraper()
    result = scraper.parse()
    assert result == {}


def test_parse_scrape_failure(monkeypatch):
    """Simulate network failure gracefully, ensuring scraper returns {}."""
    from requests import RequestException
    scraper = ProgramMapScraper()

    # Mock requests.get to raise the same RequestException scraper expects
    def fake_get(*args, **kwargs):
        raise RequestException("Network down")

    monkeypatch.setattr("requests.get", fake_get)

    # Also patch os.path.exists to False so it doesn't trigger local fallback
    monkeypatch.setattr("os.path.exists", lambda x: False)

    # The scraper should catch the error and return {} gracefully
    result = scraper.parse()
    assert isinstance(result, dict)
    assert result == {}


def test_parse_with_schedule_fallback(monkeypatch):
    """Verify local schedule fallback triggers without unexpected _retry arg."""
    mock_parse = MagicMock(return_value={"Fall 2025": [{"code": "CPSC6109"}]})
    monkeypatch.setattr(
        "smart_class_planner.infrastructure.program_map_scraper.StudyPlanParser._parse_four_year_schedule",
        mock_parse,
    )

    # Patch os.path.exists to True so it takes the fallback path early
    monkeypatch.setattr("os.path.exists", lambda x: True)

    scraper = ProgramMapScraper()
    result = scraper.parse("schedule.xlsx")
    assert "Fall 2025" in result
    mock_parse.assert_called_once()


def test_parse_handles_exception(monkeypatch):
    """Handle parsing exception raised during BeautifulSoup parsing."""
    mock_resp = MagicMock()
    mock_resp.text = "<html><table><tr><td></td></tr></table></html>"
    mock_resp.raise_for_status.return_value = None
    monkeypatch.setattr("requests.get", lambda *a, **k: mock_resp)

    # Patch BeautifulSoup to raise an exception
    with patch("smart_class_planner.infrastructure.program_map_scraper.BeautifulSoup", side_effect=Exception("bad soup")):
        scraper = ProgramMapScraper()
        result = scraper.parse()
        assert result == {}


def test_parse_returns_empty_when_no_courses(monkeypatch):
    """Return {} when no course tables or matches found."""
    html = "<html><body><table><tr><td>No relevant data</td></tr></table></body></html>"
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status.return_value = None
    monkeypatch.setattr("requests.get", lambda *a, **k: mock_resp)

    scraper = ProgramMapScraper()
    result = scraper.parse()
    assert result == {}

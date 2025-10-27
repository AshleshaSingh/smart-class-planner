"""
Description:
    Scrapes program map for term-specific course offerings (P4 in DFD).
    Fallback: Parses local 4-Year Schedule Excel.

Architecture Layer:
    Infrastructure Layer → feeds term offerings (D3) to Repository.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from .abstract_parser import AbstractParser
from .study_plan_parser import StudyPlanParser  # Reuse for fallback


class ProgramMapScraper(AbstractParser):
    """Scrapes CSU program map for term offerings or falls back to local Excel."""

    BASE_URL = "https://www.columbusstate.edu/academic-affairs/program-maps.php"  # Update to specific MS-ACS if available

    def parse(self, source: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrapes program map for {term: [{"code": "...", "title": "..."}, ...]} or uses fallback.

        Args:
            source: Optional URL or file_path for fallback.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Term offerings.
        """
        if source and os.path.exists(source) and "schedule" in source.lower():
            # Fallback to local 4-Year Schedule
            fallback_parser = StudyPlanParser()
            return fallback_parser._parse_four_year_schedule(source)

        # Web scrape attempt
        try:
            resp = requests.get(self.BASE_URL, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Web scrape failed, using fallback if source provided: {e}")
            if source:
                return self.parse(source)  # Recursive fallback
            return {}

        soup = BeautifulSoup(resp.text, "html.parser")
        structured: Dict[str, List[Dict[str, Any]]] = {}

        # Parse tables for terms/courses (adapt to actual HTML)
        tables = soup.find_all("table", class_=re.compile(r"program|map|schedule", re.I))
        for table in tables:
            rows = table.find_all("tr")
            current_term = None
            for row in rows:
                cells = row.find_all(["td", "th"])
                if not cells:
                    continue
                cell_text = [c.get_text(strip=True) for c in cells]
                if any(term_pat in " ".join(cell_text).upper() for term_pat in ["FALL", "SPRING", "SUMMER"]):
                    current_term = " ".join(cell_text).upper().split()[0]  # e.g., "FALL 2025"
                elif current_term and any("CPSC" in c or "CYBR" in c for c in cell_text):
                    for cell in cells:
                        text = cell.get_text()
                        code_match = re.search(r"(CPSC|CYBR)\s+\d+", text)
                        if code_match:
                            code = code_match.group(0).strip()
                            title = text.split("-", 1)[-1].strip() if "-" in text else ""
                            structured.setdefault(current_term, []).append({"code": code, "title": title})

        if not structured:
            print("No web data extracted; provide local source for fallback.")
            return {}

        print(f"Scraped {sum(len(v) for v in structured.values())} offerings across {len(structured)} terms.")
        return structured
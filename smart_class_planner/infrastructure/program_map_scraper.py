"""
program_map_scraper.py

This module defines the ProgramMapScraper class responsible for scraping and parsing
academic program map data from Columbus State University (CSU) web pages. The scraper
collects term-wise course offerings and serves as a backup mechanism for local schedule files.

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
    """Scrapes and parses program map data from CSU academic websites.

    The class retrieves HTML content from CSU’s program-map web pages, parses the table
    structures, and extracts course data organized by term. It also supports a fallback
    mode that uses a local 4-Year Schedule file when scraping is not possible.
    """

    BASE_URL = "https://www.columbusstate.edu/academic-affairs/program-maps.php"

    def parse(self, source: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape CSU program map or fallback to local schedule file.

        Attempts to scrape term-wise course data directly from the CSU program-map page.
        If scraping fails (e.g., due to network restrictions or site errors), the method
        gracefully falls back to parsing a local Excel schedule file using StudyPlanParser.

        Args:
            source (str, optional): Optional path or URL used as a fallback source.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Parsed course offerings organized by term.
                Example:
                    {
                        "FALL 2025": [
                            {"code": "CPSC 6105", "title": "Advanced Algorithms"},
                            {"code": "CYBR 5150", "title": "Information Security"}
                        ],
                        "SPRING 2026": [...]
                    }
        """
        # ---------------- Fallback handling for local schedule files ----------------
        if source and os.path.exists(source) and "schedule" in source.lower():
            # Reuse the existing Excel parser for 4-Year Schedule fallback
            fallback_parser = StudyPlanParser()
            return fallback_parser._parse_four_year_schedule(source)

        # ---------------- Attempt web scraping from CSU program map ----------------
        try:
            resp = requests.get(self.BASE_URL, timeout=10)
            resp.raise_for_status()
            html = resp.text
        except requests.RequestException as e:
            # If the request fails, attempt a fallback or return an empty structure
            print(f"Web scrape failed, using fallback if source provided: {e}")
            if source:
                return self.parse(source, _retry=True)  # Recursive fallback attempt
            return {}

        # ---------------- Validate HTML structure ----------------
        if not html or "<html" not in html.lower():
            print("[Scraper] Empty or invalid HTML content.")
            return {}

        # ---------------- Parse HTML using BeautifulSoup ----------------
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            structured: Dict[str, List[Dict[str, Any]]] = {}

            # Locate tables that may contain course data (by CSS class names)
            tables = soup.find_all("table", class_=re.compile(r"program|map|schedule", re.I))

            for table in tables:
                rows = table.find_all("tr")
                current_term = None

                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if not cells:
                        continue

                    cell_text = [c.get_text(strip=True) for c in cells]

                    # Detect term headers (e.g., FALL 2025, SPRING 2026)
                    if any(term_pat in " ".join(cell_text).upper() for term_pat in ["FALL", "SPRING", "SUMMER"]):
                        current_term = " ".join(cell_text).upper().split()[0]

                    # Extract course codes and titles under detected term
                    elif current_term and any("CPSC" in c or "CYBR" in c for c in cell_text):
                        for cell in cells:
                            text = cell.get_text()
                            code_match = re.search(r"(CPSC|CYBR)\s+\d+", text)
                            if code_match:
                                code = code_match.group(0).strip()
                                title = text.split("-", 1)[-1].strip() if "-" in text else ""
                                structured.setdefault(current_term, []).append(
                                    {"code": code, "title": title}
                                )

            # ---------------- Post-processing & validation ----------------
            if not structured:
                print("No web data extracted; provide local source for fallback.")
                return {}

            print(
                f"Scraped {sum(len(v) for v in structured.values())} offerings "
                f"across {len(structured)} terms."
            )
            return structured

        except Exception as e:
            # Handle parsing errors gracefully without halting the application
            print(f"[Scraper] Parsing error: {e}")
            return {}
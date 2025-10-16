"""
File: scraper.py
Version: 1.2
Date: 2025-10-15
Description:
    Web crawler that extracts prerequisite information from
    the CPSC/CYBR Course Descriptions website (supports P5 in DFD).

Dependencies:
    - requests
    - beautifulsoup4

Architecture Layer:
    Infrastructure Layer → Web Data Acquisition (feeds prereqs for DAG in D4).
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from .abstract_parser import AbstractParser


class PrerequisiteScraper(AbstractParser):
    """Scrapes CPSC/CYBR course prerequisites from the online catalog."""

    BASE_URLS = [
        "https://catalog.columbusstate.edu/course-descriptions/cpsc/",
        "https://catalog.columbusstate.edu/course-descriptions/cybr/"
    ]

    def parse(self, _: str = None) -> Dict[str, List[str]]:
        """
        Crawls the course descriptions and extracts prerequisites as list of codes.

        Returns:
            Dict[str, List[str]]: e.g.,
                {"CPSC 6109": ["CPSC 5157"], "CYBR 6128": ["CYBR 6126", "CPSC 6157"]}
        """
        prereqs = {}
        for url in self.BASE_URLS:
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to fetch {url}: {e}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if not (text.startswith("CPSC") or text.startswith("CYBR")):
                    continue

                # Extract course code (e.g., "CPSC 6109")
                code_match = re.match(r"(CPSC|CYBR)\s+\d+", text)
                if not code_match:
                    continue
                code = code_match.group(0).strip()

                # Extract prereq codes (CPSC/CYBR only)
                if "Prerequisite:" in text:
                    prereq_text = text.split("Prerequisite:")[-1].strip()
                    prereq_codes = re.findall(r"(CPSC|CYBR)\s+\d+", prereq_text)
                    prereq_codes = [c.strip() for c in prereq_codes]
                    prereqs[code] = list(set(prereq_codes))
                else:
                    prereqs[code] = []

        print(f"Extracted {len(prereqs)} course prerequisites.")
        return prereqs
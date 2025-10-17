"""
File: scraper.py
Author: Ashlesha Singh
Date: 2025-10-10
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
    """Scrapes CPSC/CYBR core course prerequisites from the online catalog."""

    BASE_URLS = [
        "https://catalog.columbusstate.edu/course-descriptions/cpsc/#cpsctext",
        "https://catalog.columbusstate.edu/course-descriptions/cybr/#cybrtext"
    ]

    # Verified fallback from catalog (graduate cores only; ignores electives/non-CS)
    # CPSC from https://catalog.columbusstate.edu/course-descriptions/cpsc/
    # CYBR from https://catalog.columbusstate.edu/course-descriptions/cybr/
    FALLBACK_PREREQS = {
        "CPSC 6109": [],
        "CPSC 6114": [],
        "CPSC 6119": [],
        "CPSC 6121": ["CPSC 6114"],
        "CPSC 6124": ["CPSC 6114"],
        "CPSC 6125": [],
        "CPSC 6127": [],
        "CPSC 6136": ["CPSC 6126"],
        "CPSC 6138": ["CPSC 6119"],
        "CPSC 6147": [],
        "CPSC 6155": [],
        "CPSC 6157": [],
        "CPSC 6175": [],
        "CPSC 6177": [],
        "CPSC 6179": [],
        "CPSC 6185": [],
        "CYBR 6128": ["CYBR 6126", "CPSC 6157"],
        "CYBR 6136": ["CYBR 6126"],
        "CYBR 6159": ["CYBR 6126"],
        "CYBR 6167": ["CYBR 6126"],
        "CYBR 6226": ["CPSC 6157"],
        "CYBR 6228": ["CYBR 6126"]
    }

    def parse(self, _: str = None) -> Dict[str, List[str]]:
        prereqs = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        fetch_success = False
        for url in self.BASE_URLS:
            try:
                resp = requests.get(url, timeout=10, headers=headers)
                resp.raise_for_status()
                fetch_success = True
            except requests.RequestException as e:
                print(f"Failed to fetch {url}: {e}")
                continue

            if fetch_success:
                soup = BeautifulSoup(resp.text, "html.parser")
                for p in soup.find_all("p"):
                    text = p.get_text(strip=True)
                    if not (text.startswith("CPSC ") or text.startswith("CYBR ")):
                        continue

                    # Extract course code (e.g., "CPSC 6109")
                    code_match = re.match(r"(CPSC|CYBR)\s+\d{4}", text)
                    if not code_match:
                        continue
                    code = code_match.group(0).strip()

                    # Extract prereq codes (CPSC/CYBR only; handle "Prerequisite(s):")
                    prereq_key = "Prerequisite(s):" if "Prerequisite(s):" in text else "Prerequisite:"
                    if prereq_key in text:
                        prereq_text = text.split(prereq_key)[-1].split(".")[0].strip()
                        prereq_codes = re.findall(r"(CPSC|CYBR)\s+\d{4}", prereq_text)
                        prereq_codes = [c.strip() for c in prereq_codes if len(c.split()) == 2]
                        prereqs[code] = list(set(prereq_codes))
                    else:
                        prereqs[code] = []

        if not prereqs and not fetch_success:
            print("Site blocked; using verified fallback core prereqs from catalog.")
            prereqs = self.FALLBACK_PREREQS.copy()

        print(f"Extracted {len(prereqs)} core course prerequisites.")
        return prereqs
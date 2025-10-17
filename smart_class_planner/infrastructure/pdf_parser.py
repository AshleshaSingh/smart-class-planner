"""
File: pdf_parser.py
Author: Ashlesha Singh
Date: 2025-10-08
Description:
    Parses DegreeWorks PDF reports to extract the list of
    remaining required courses for a student (P2 in DFD).

Dependencies:
    - PyPDF2

Architecture Layer:
    Infrastructure Layer → feeds remaining courses (D1) to Repository.
"""

import os
from typing import List, Dict
from PyPDF2 import PdfReader
from .abstract_parser import AbstractParser


class PDFParser(AbstractParser):
    """Parses DegreeWorks PDF reports to extract required courses."""

    def parse(self, file_path: str) -> List[Dict[str, str]]:
        """
        Extracts remaining required courses from DegreeWorks PDF.

        Args:
            file_path (str): Path to the DegreeWorks PDF file.

        Returns:
            List[Dict[str, str]]: Example:
                [{"code": "CPSC 6109", "title": "Algorithms Analysis and Design"}, ...]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DegreeWorks file not found: {file_path}")

        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        # Pattern match for course lines (e.g., "CPSC 6109 - Algorithms Analysis and Design")
        # Focus on remaining required section based on DegreeWorks structure
        courses = []
        lines = text.splitlines()
        in_remaining_section = False  # Toggle based on section headers like "Still Needed"
        for line in lines:
            line = line.strip()
            if "Still Needed" in line or "Remaining Requirements" in line:
                in_remaining_section = True
                continue
            if in_remaining_section and (line.startswith("CPSC") or "CPSC " in line):
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    code = parts[0].strip()
                    title = parts[1].strip()
                    courses.append({"code": code, "title": title})

        print(f"Extracted {len(courses)} remaining courses from DegreeWorks.")
        return courses
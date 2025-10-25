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

        # Extract courses marked as "Still needed"
        import re
        courses = []
        lines = text.splitlines()

        for line in lines:
            line = line.strip()
            # Look for lines with "Still needed:" followed by course codes
            if "Still needed:" in line:
                # Extract CPSC/CYBR course codes from this line
                course_codes = re.findall(r'(CPSC|CYBR)\s*(\d{4})', line) # Pattern: "Still needed: 1 Class in CPSC 6119" or "Still needed: 6 Credits in CPSC 6985 or..."
                for prefix, number in course_codes:
                    code = f"{prefix} {number}"
                    title = self._find_course_title(text, code) # Try to find the title from earlier in the document
                    courses.append({"code": code, "title": title})
                    # print(f"DEBUG PDF: Found still-needed course: {code}")

        # Remove duplicates
        seen = set()
        unique_courses = []
        for course in courses:
            if course['code'] not in seen:
                seen.add(course['code'])
                unique_courses.append(course)

        print(f"Extracted {len(unique_courses)} remaining courses from DegreeWorks.")
        return unique_courses

    def _find_course_title(self, text: str, course_code: str) -> str:
        """Try to find the course title in the PDF text."""
        import re
        # Look for patterns like "CPSC 6119- Object-Oriented Development"
        pattern = re.escape(course_code) + r'[-\s]*([A-Za-z][\w\s,&\-]+?)(?:\n|Still|Grade|Credits|$)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return ""
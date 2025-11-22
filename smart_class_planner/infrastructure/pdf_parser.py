"""
This module defines the PDFParser class, responsible for extracting course information
from DegreeWorks PDF files. It identifies completed and remaining courses using text
extraction and pattern recognition. The parser ensures resilience against corrupted or
malformed PDFs and includes structured error handling.

Dependencies:
    - pypdf

Architecture Layer:
    Infrastructure Layer → feeds remaining courses (D1) to Repository.
"""

import os
import re
from typing import List, Dict
from pypdf import PdfReader
from .abstract_parser import AbstractParser
from pypdf.errors import PdfStreamError


class PDFParser(AbstractParser):
    """Parses DegreeWorks PDF files to extract academic course data.

    This class scans the DegreeWorks report to find sections such as
    *Still Needed* and *Completed* courses. The parsed data is returned
    in a structured list format for repository ingestion.
    """

    def validate(self, file_path: str) -> None:
        """Validate that the file appears to be a valid DegreeWorks/Progress report.

        Reads portions of the file content and searches for known keywords such as
        'Degree Works', 'Degree Progress', or 'Degree Audit Report'. Raises an error
        if none of these are found.

        Args:
            file_path (str): Path to the PDF file for validation.

        Raises:
            ValueError: If the file does not contain expected DegreeWorks identifiers.
        """
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        text = text.lower()

        if (
            "degree works" not in text
            and "degree progress" not in text
            and "degree audit report" not in text
        ):
            raise ValueError("Invalid DegreeWorks/Degree Progress report")


    def parse(self, file_path: str) -> List[Dict[str, str]]:
        """
        Extracts remaining required courses from DegreeWorks PDF.

        The parser reads the PDF file page by page, searches for text
        patterns related to course listings, and extracts course codes
        and titles into a structured list of dictionaries.

        Args:
            file_path (str): Path to the DegreeWorks PDF file.

        Returns:
            List[Dict[str, str]]: A list of course entries, where each dictionary contains:
                - code (str): Course code (e.g., 'CPSC 6105').
                - title (str): Course title (e.g., 'Advanced Algorithms').

        Raises:
            FileNotFoundError: If the provided file path does not exist.
            ValueError: If the file content does not resemble a valid DegreeWorks report.
            Exception: For any unexpected errors during PDF parsing.
        """
        # Validate file existence before attempting to open.
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DegreeWorks file not found: {file_path}")

        try: 
            # Open and read PDF using pypdf.
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
                    # Split at "Except" to exclude courses that don't count
                    # Example: "Still needed: 6 Credits in CPSC 6985 or ... Except CPSC 6103 or ..."
                    # We only want the part BEFORE "Except"
                    if "Except" in line or "except" in line:
                        # Case-insensitive split at "Except"
                        line = re.split(r'\s+[Ee]xcept\s+', line)[0]

                    # Extract CPSC/CYBR course codes from this line
                    course_codes = re.findall(r'(CPSC|CYBR)\s*(\d{4})', line) # Pattern: "Still needed: 1 Class in CPSC 6119" or "Still needed: 6 Credits in CPSC 6985 or..."
                    for prefix, number in course_codes:
                        code = f"{prefix} {number}"
                        title = self._find_course_title(text, code) # Try to find the title from earlier in the document
                        courses.append({"code": code, "title": title})

            # Remove duplicates
            seen = set()
            unique_courses = []
            for course in courses:
                if course['code'] not in seen:
                    seen.add(course['code'])
                    unique_courses.append(course)

            print(f"Extracted {len(unique_courses)} remaining courses from DegreeWorks.")
            return unique_courses

        except PdfStreamError as e:
            print(f"[PDFParser] Invalid PDF stream: {e}")
            return []
        except FileNotFoundError:
            # Propagate specific file-not-found exception.
            raise
        except Exception as e:
            # Catch and wrap unexpected parsing issues for clarity.
            raise Exception(f"PDF parsing failed: {e}")

    def _find_course_title(self, text: str, course_code: str) -> str:
        """Find the course title corresponding to a given course code.

        This helper method searches the text around a course code to locate its title
        using flexible pattern matching. It looks for formats such as:
        'CPSC 6119- Object-Oriented Development'.

        Args:
            text (str): Extracted text from the PDF page.
            course_code (str): The specific course code to search for.

        Returns:
            str: The detected course title, or an empty string if none found.
        """
        
        # Look for patterns like "CPSC 6119- Object-Oriented Development"
        pattern = re.escape(course_code) + r'[-\s]*([A-Za-z][\w\s,&\-]+?)(?:\n|Still|Grade|Credits|$)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return ""
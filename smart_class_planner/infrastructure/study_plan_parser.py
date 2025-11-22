"""
Description:
    Robust parser for Graduate Study Plan spreadsheets (P3 in DFD).
    Handles merged cells, blank 'Offer' values, and multiple column name variants.
    Fully supports 4-Year Schedule for term offerings (fallback for P4).

Architecture Layer:
    Infrastructure Layer → feeds study sequences (D2) and term offerings (D3) to Repository.
"""

import os
import pandas as pd
from typing import Dict, List, Any
from .abstract_parser import AbstractParser


class StudyPlanParser(AbstractParser):
    """Parses Graduate Study Plan and 4-Year Schedule Excel sheets.

    This parser automatically detects whether an uploaded Excel file represents
    a Graduate Study Plan or a 4-Year Course Schedule. It extracts structured
    data in a consistent format usable by the DataLoader and Repository.
    """


    def validate_graduate_study_plan(self, file_path):
        """Validate whether a file is a Graduate Study Plan.

        Checks for common schedule indicators to ensure the wrong file
        (e.g., 4-Year Schedule) is not uploaded by mistake.

        Args:
            file_path (str): Path to the Excel file being validated.

        Raises:
            ValueError: If the file structure or content does not match a
                        Graduate Study Plan.
        """
        df = pd.read_excel(file_path, header=None)
        text = " ".join(df.fillna("").astype(str).stack().tolist()).lower()

        # 1. Check that it's NOT a 4-Year Schedule
        # The schedule file always contains these words near the top:
        schedule_keywords = ["four-year", "schedule", "course title", "day time", "night time", "online", "fixed date"]
        if any(k in text for k in schedule_keywords):
            raise ValueError("File appears to be a 4-Year Course Schedule, not a Graduate Study Plan.")

        # 2️. Must contain degree track identifiers and term headers
        has_term_headers = any(term in text for term in ["fall start", "spring start", "summer"])
        has_program_tracks = any(track in text for track in ["cybr", "acs", "software dev", "ai and data science"])

        if not has_term_headers or not has_program_tracks:
            raise ValueError("Invalid Study Plan: Missing CYBR/ACS program tracks or term start sections.")

        # 3️. Sanity check: should have few columns (3–6 typical)
        if df.shape[1] > 10:
            raise ValueError("Invalid Study Plan: Too many columns, likely not a Graduate Study Plan.")

        return True
        
    def validate_four_year_schedule(self, file_path):
        """Validate whether a file is a 4-Year Schedule.

        Ensures that the uploaded Excel file includes expected keywords
        or codes that confirm it is a CSU 4-Year schedule format.

        Args:
            file_path (str): Path to the Excel file.

        Raises:
            ValueError: If file does not appear to contain 4-Year Schedule data.
        """
        df = pd.read_excel(file_path, header=None)
        text = " ".join(df.fillna("").astype(str).stack().tolist()).lower()
        if "four-year" not in text and not any(t in text for t in ["fa24", "sp25", "su25"]):
            raise ValueError("File does not contain Four-Year Schedule data or term codes.")

    
    def parse(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Detect file type and parse accordingly.

        Args:
            file_path (str): Path to the Excel file.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Structured course data indexed by term.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_excel(file_path, header=0)
        df.columns = [str(c).strip() for c in df.columns]
        cols_lower = [c.lower() for c in df.columns]

        # Decide type
        if any("course name" in c for c in cols_lower):
            return self._parse_graduate_study_plan(df)
        elif any("four-year" in c for c in cols_lower):
            return self._parse_four_year_schedule(file_path)
        else:
            print(f"Unknown structure in {os.path.basename(file_path)}")
            print("Detected columns:", df.columns.tolist())
            return {}

    # ----------------------------------------------------------------------
    def _parse_graduate_study_plan(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """Parse Graduate Study Plan format (core courses and semesters).

        Args:
            df (pd.DataFrame): DataFrame of the Excel file.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Parsed data structured by semester.
        """
        print("Detected: Graduate Study Plan (Adaptive parsing)")
        structured: Dict[str, List[Dict[str, Any]]] = {}

        # Helper: pick best-matching column
        def find_col(candidates):
            for c in df.columns:
                if any(k.lower() in str(c).lower() for k in candidates):
                    return c
            return None

        code_col = find_col(["course number", "unnamed", "course number"])
        name_col = find_col(["course name", "title"])
        offer_col = find_col(["offer", "semester"])
        required_col = find_col(["required in"])

        # Fill forward blank semesters (for merged cells)
        if offer_col:
            df[offer_col] = df[offer_col].ffill()

        for _, row in df.iterrows():
            semester = str(row.get(offer_col, "Unknown")).strip().title()
            code = str(row.get(code_col, "")).strip()
            title = str(row.get(name_col, "")).strip()
            required = str(row.get(required_col, "")).strip()

            # Skip empty or header-like rows
            if not code or code.lower() in ("nan", "none", "prerequisite", ""):
                continue

            # Filter for core tracks only (ACS, CYBR); ignore electives/non-CS
            if required and not any(track in required for track in ["ACS", "CYBR"]):
                continue

            structured.setdefault(semester or "Unknown", []).append({
                "code": code,
                "title": title,
                "required_in": required
            })

        print(f"Extracted {sum(len(v) for v in structured.values())} core courses across {len(structured)} semesters.")
        return structured

    # ----------------------------------------------------------------------
    def _parse_four_year_schedule(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse 4-Year Schedule to extract term offerings.

        Args:
            file_path (str): Path to the 4-Year Schedule Excel file.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Course offerings by term.
        """
        print("Detected: 4-Year Schedule (Parsing term offerings)")
        df = pd.read_excel(file_path, header=2, sheet_name='Sheet1')  # Skip intro rows
        df.columns = [str(c).strip() for c in df.columns]

        # Identify term columns (exclude Course, Course Title)
        term_cols = [col for col in df.columns if col not in ['Course', 'Course Title'] and pd.notna(col) and 'unnamed' not in str(col).lower()]

        structured = {term: [] for term in term_cols}

        ignore_offerings = ['', '.', '??', 'O??', '-', '?', 'O?', 'nan']  # Common placeholders (including 'nan' string)

        for _, row in df.iterrows():
            code = str(row['Course']).strip()
            if pd.isna(row['Course']) or not code:
                continue
            # Filter for CPSC/CYBR core only
            if not (code.startswith("CPSC") or code.startswith("CYBR")):
                continue
            title = str(row['Course Title']).strip()
            for term in term_cols:
                # Check if the value is actually NaN first
                if pd.isna(row[term]):
                    continue
                offering = str(row[term]).strip()
                if offering and offering not in ignore_offerings:
                    structured[term].append({
                        "code": code,
                        "title": title,
                        "offering_type": offering  # e.g., 'D,N,O' for day/night/online
                    })

        total_offerings = sum(len(v) for v in structured.values())
        print(f"Extracted {total_offerings} core course offerings across {len(term_cols)} terms.")
        return structured
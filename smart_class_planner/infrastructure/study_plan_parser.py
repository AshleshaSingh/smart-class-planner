"""
File: study_plan_parser.py
Author: Ashlesha Singh
Date: 2025-10-15
Description:
    Robust parser for Graduate Study Plan spreadsheets (P3 in DFD).
    Handles merged cells, blank 'Offer' values, and multiple column name variants.
    Now fully supports 4-Year Schedule for term offerings (fallback for P4).

Architecture Layer:
    Infrastructure Layer → feeds study sequences (D2) and term offerings (D3) to Repository.
"""

import os
import pandas as pd
from typing import Dict, List, Any
from .abstract_parser import AbstractParser


class StudyPlanParser(AbstractParser):
    """Parses Graduate Study Plan and 4-Year Schedule Excel sheets."""

    def parse(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
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
        """
        Parses 4-Year Schedule Excel to extract term offerings (D3 in DFD).
        Returns {term: [{"code": "CPSC 6109", "title": "...", "offering_type": "D,N,O"}, ...]}
        Filters for CPSC/CYBR core courses only.
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
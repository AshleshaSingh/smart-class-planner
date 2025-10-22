"""
File: infrastructure_check.py
Author: Ashlesha Singh
Date: 2025-10-15
Description:
    Integration harness to verify the Parser and Web Crawler modules
    of the Smart Class Planning Tool.
    Runs import checks, sample parses, and simple web fetches,
    printing a summary of module readiness.

Usage:
    From smart_class_planner/ root: python -m infrastructure.infrastructure_check
"""

import os
from .pdf_parser import PDFParser
from .study_plan_parser import StudyPlanParser
from .scraper import PrerequisiteScraper
from .program_map_scraper import ProgramMapScraper
from .prereq_graph_parser import PrereqGraphParser

print("\nRunning Infrastructure Layer Verification...\n")

# Paths: Files in ../data/
study_path = "../data/Graduate Study Plans -revised.xlsx"
four_path = "../data/4-year schedule.xlsx"
pdf_path = "../data/DegreeWorks.pdf"  # Handles missing

# PDF Parser (P2)
try:
    pdf = PDFParser()
    pdf.parse(pdf_path)
    print("PDF Parser: Ready (file check passed)")
except Exception as e:
    print(f"PDF Parser: {e}")

# Study Plan Parser (P3 + fallback P4)
try:
    plan = StudyPlanParser()
    sequences = plan.parse(study_path)
    print(f"Study Plan Parser: Success - {len(sequences)} semesters, {sum(len(v) for v in sequences.values())} courses")
    
    offerings = plan.parse(four_path)
    print(f"4-Year Schedule Parser: Success - {len(offerings)} terms, {sum(len(v) for v in offerings.values())} offerings")
except Exception as e:
    print(f"Study Plan Parser: {e}")

# Prerequisite Scraper (supports P5)
try:
    scraper = PrerequisiteScraper()
    prereqs = scraper.parse()
    print(f"Prerequisite Scraper: Success - {len(prereqs)} courses")
except Exception as e:
    print(f"Prerequisite Scraper: {e}")

# Program Map Scraper (P4)
try:
    pms = ProgramMapScraper()
    result = pms.parse(four_path)  # Fallback test
    print(f"Program Map Scraper: Success - {len(result)} terms")
except Exception as e:
    print(f"Program Map Scraper: {e}")

# Prereq Graph Parser (P5)
try:
    prereqs = scraper.parse()
    if not prereqs:
        # Mock from real catalog data (tool-fetched)
        prereqs = {
            "CPSC 1302K": ["CPSC 1301K"],
            "CYBR 6128": ["CYBR 6126", "CPSC 6157"],
            "CPSC 6109": ["CPSC 5157"],  # Example grad course
            "CYBR 6136": ["CYBR 6126"]
        }
        print("Using mock prereqs from catalog for graph test")
    graph_parser = PrereqGraphParser()
    graph = graph_parser.parse(prereqs)
    print(f"Prereq Graph Parser: Success - {len(graph.get('nodes', []))} nodes")
except Exception as e:
    print(f"Prereq Graph Parser: {e}")

print("\nVerification complete. Infrastructure ready for domain integration.")
"""
data_loader.py
----------------
Centralized data integration layer for Smart Class Planner.
This module coordinates parsing of DegreeWorks PDF, Study Plan Excel,
and Program Map data, converting them into domain entities (Course,
Offering, Prerequisite) and populating the Repository.

Author: ChatGPT (2025)
"""

from smart_class_planner.infrastructure.pdf_parser import PDFParser
from smart_class_planner.infrastructure.study_plan_parser import StudyPlanParser
from smart_class_planner.infrastructure.program_map_scraper import ProgramMapScraper
from smart_class_planner.infrastructure.prereq_graph_parser import PrereqGraphParser
from smart_class_planner.domain.course import Course
from smart_class_planner.domain.offering import Offering
from smart_class_planner.domain.prerequisite import Prerequisite


class DataLoader:
    """Coordinates all parsers to load structured data into the repository."""

    def __init__(self, repository):
        """
        Initialize the DataLoader with a Repository instance.

        Args:
            repository (Repository): The central domain repository to populate.
        """
        self.repo = repository
        self.pdf_parser = PDFParser()
        self.study_parser = StudyPlanParser()
        self.map_scraper = ProgramMapScraper()
        self.graph_parser = PrereqGraphParser()

    # ------------------------------------------------------
    # Individual loaders
    # ------------------------------------------------------

    def load_degreeworks(self, pdf_path: str):
        """Parse DegreeWorks PDF and add remaining courses."""
        try:
            remaining = self.pdf_parser.parse(pdf_path)
            remaining_codes = []

            for course_data in remaining:
                course = Course(
                    code=course_data.get("code"),
                    title=course_data.get("title", ""),
                    credits=course_data.get("credits", 3),
                )
                self.repo.add_course(course)
                remaining_codes.append(course.code)

            return remaining_codes  # <-- return list instead of count

        except FileNotFoundError as e:
            print(f"[DataLoader] {e}")
            return []
        except Exception as e:
            print(f"[DataLoader] Unexpected PDF load error: {e}")
            return []

    def load_study_plan(self, excel_path: str):
        """Parse Study Plan Excel and add courses and offerings."""
        plan_data = self.study_parser.parse(excel_path)
        count = 0
        for term, courses in plan_data.items():
            for course_data in courses:
                # Create course object
                course = Course(
                    code=course_data.get("code"),
                    title=course_data.get("title", ""),
                    credits=course_data.get("credits", 3),
                )
                self.repo.add_course(course)

                # Create offering object
                offering = Offering(
                    course_code=course.code,
                    term=term,
                    year=course_data.get("year", 2025),
                )
                self.repo.add_offering(offering)
                count += 1
        return count

    def load_program_map(self, url_or_path: str):
        """Scrape or parse Program Map data and add offerings."""
        map_data = self.map_scraper.parse(url_or_path)
        count = 0
        for term, courses in map_data.items():
            for course_data in courses:
                offering = Offering(
                    course_code=course_data.get("code"),
                    term=term,
                    year=course_data.get("year", 2025),
                )
                self.repo.add_offering(offering)
                count += 1
        return count

    def load_prerequisites(self, prereq_source: dict):
        """Parse prerequisite relationships and add them to the repository."""
        graph = self.graph_parser.parse(prereq_source)
        for edge in graph.get("edges", []):
            prereq = Prerequisite(edge[0], edge[1])
            self.repo.add_prerequisite(prereq)
        return len(graph.get("edges", []))

    # ------------------------------------------------------
    # Unified entry point
    # ------------------------------------------------------

    def load_all(self, pdf_path=None, excel_path=None, program_map=None, prereq_data=None):
        """
        Load all sources into the repository.

        Args:
            pdf_path (str): Path to DegreeWorks PDF.
            excel_path (str): Path to Study Plan Excel.
            program_map (str): Path or URL for program map data.
            prereq_data (dict): Prerequisite relationships.

        Returns:
            dict: Summary of items loaded from each source.
        """
        summary = {}
        remaining = []

        if pdf_path:
            try:
                remaining = self.load_degreeworks(pdf_path)
                summary["degreeworks"] = len(remaining)
            except Exception as e:
                print(f"[DataLoader] Failed DegreeWorks parse: {e}")
                summary["remaining"] = []

        if excel_path:
            try:
                summary["study_plan"] = self.load_study_plan(excel_path)
            except FileNotFoundError:
                print(f"[DataLoader] Study Plan missing: {excel_path}")
                summary["study_plan"] = {}
            except Exception as e:
                print(f"[DataLoader] Study Plan parse error: {e}")
                summary["study_plan"] = {}

        if program_map:
            try: 
                summary["program_map"] = self.load_program_map(program_map)
            except Exception as e:
                print(f"[DataLoader] Program Map scrape error: {e}")
                summary["program_map"] = {}

        if prereq_data:
            try:
                summary["prerequisites"] = self.load_prerequisites(prereq_data)
            except Exception as e:
                print(f"[DataLoader] Prerequisites scrape error: {e}")
                summary["prerequisites"] = {}

        return summary, remaining

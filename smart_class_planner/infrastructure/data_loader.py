"""
data_loader.py
----------------
Centralized data integration layer for Smart Class Planner.
This module coordinates parsing of DegreeWorks PDF, Study Plan Excel,
and Program Map data, converting them into domain entities (Course,
Offering, Prerequisite) and populating the Repository.

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

    def __init__(self, repository: object) -> None:
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

    def load_degreeworks(self, pdf_path: str) -> list[str]:
        """Parse DegreeWorks PDF and populate remaining courses.

        Args:
            pdf_path (str): Path to the DegreeWorks PDF file.

        Returns:
            list[str]: List of remaining course codes extracted from DegreeWorks.
        """
        try:
            remaining = self.pdf_parser.parse(pdf_path)
            remaining_codes = []

            # Convert parsed data into Course domain objects
            for course_data in remaining:
                course = Course(
                    code=course_data.get("code"),
                    title=course_data.get("title", ""),
                    credits=course_data.get("credits", 3),
                )
                self.repo.add_course(course)
                remaining_codes.append(course.code)

            return remaining_codes 

        except FileNotFoundError as e:
            print(f"[DataLoader] {e}")
            return []
        except Exception as e:
            print(f"[DataLoader] Unexpected PDF load error: {e}")
            return []

    def load_study_plan(self, excel_path: str) -> int :
        """Parse Graduate Study Plan Excel and add its courses and offerings.

        Args:
            excel_path (str): Path to the Excel study plan.

        Returns:
            int: Number of course offerings added to the repository.
        """        
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

    def load_program_map(self, url_or_path: str) -> int :
        """Scrape or parse Program Map data and record offerings.

        Args:
            url_or_path (str): URL or local path for the program map source.

        Returns:
            int: Number of course offerings extracted from the program map.
        """
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

    def load_prerequisites(self, prereq_source: dict) -> int:
        """Parse prerequisite relationships and populate repository graph.

        Args:
            prereq_source (dict): Mapping of prerequisite relationships.

        Returns:
            int: Number of prerequisite edges successfully added.
        """        
        graph = self.graph_parser.parse(prereq_source)
        for edge in graph.get("edges", []):
            prereq = Prerequisite(edge[0], edge[1])
            self.repo.add_prerequisite(prereq)
        return len(graph.get("edges", []))

    # ------------------------------------------------------
    # Unified entry point
    # ------------------------------------------------------

    def load_all(
        self,
        pdf_path: str | None = None,
        excel_path: str | None = None,
        program_map: str | None = None,
        prereq_data: dict | None = None,
        ) -> tuple[dict, list]:
        """Loads all supported data sources sequentially and returns a summary.


        This method coordinates data extraction from multiple input sources — DegreeWorks,
        Graduate Study Plan, and Program Map — using dedicated parsers. It captures both
        successful extractions and failures for transparency.


        Args:
            pdf_path (str | None): Path to DegreeWorks PDF file.
            excel_path (str | None): Path to the Graduate Study Plan Excel file.
            program_map (str | None): Path or URL for program map HTML.
            prereq_data (dict | None): Optional prerequisite relationships mapping.


        Returns:
            tuple[dict, list]:
                - dict: Summary of items loaded from each data source.
                - list: Remaining courses extracted from DegreeWorks.
        """
        # Initialize empty summary and placeholder for remaining DegreeWorks courses.
        summary: dict = {}
        remaining: list = []


        # --------------------------- DEGREEWORKS PDF ---------------------------
        if pdf_path:
            try:
                # Attempt to parse DegreeWorks PDF to extract remaining course list.
                remaining = self.load_degreeworks(pdf_path)
                summary["degreeworks"] = len(remaining)
            except Exception as e:
                # Capture any file or parsing errors gracefully.
                summary["degreeworks"] = []


        # --------------------------- STUDY PLAN EXCEL ---------------------------
        if excel_path:
            try:
                # Parse Graduate Study Plan Excel for structured term-course mapping.
                summary["study_plan"] = self.load_study_plan(excel_path)
            except Exception:
                # Fall back to an empty structure if parsing fails.
                summary["study_plan"] = {}


        # --------------------------- PROGRAM MAP SCRAPER ---------------------------
        if program_map:
            try:
                # Scrape and parse CSU program map (web-based source).
                summary["program_map"] = self.load_program_map(program_map)
            except Exception:
                # Default to an empty dataset on failure.
                summary["program_map"] = {}


        # --------------------------- PREREQUISITES DATA ---------------------------
        if prereq_data:
            try:
                # Process prerequisite mapping and update repository links.
                summary["prerequisites"] = self.load_prerequisites(prereq_data)
            except Exception:
                # Record empty set if parsing or linking fails.
                summary["prerequisites"] = {}


        # Return the comprehensive loading summary and any remaining courses.
        return summary, remaining

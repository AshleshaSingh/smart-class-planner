"""
Semester Plan Generator Module

Builds semester-by-semester course schedules.
Takes into account prereqs, when courses are offered, credit limits, and study plan requirements
to figure out the best way to graduate.
"""

from typing import List, Dict, Tuple, Optional, Set
from smart_class_planner.domain.course import Course
from smart_class_planner.domain.repository import Repository


class SemesterPlan:
    """Represents a schedule for one semester"""

    def __init__(self, term: str, year: int):
        self.term = term  # Fall, Spring, or Summer
        self.year = year
        self.courses = []
        self.total_credits = 0

    def add_course(self, course: Course) -> bool:
        """Add a course to this semester

        Args:
            course: The course to add

        Returns:
            bool: True if the course was added
        """
        if course not in self.courses:
            self.courses.append(course)
            self.total_credits += course.credits
            return True
        return False

    def get_term_key(self) -> str:
        """Returns the term as a string like 'Fall 2025'"""
        return f"{self.term} {self.year}"

    def __repr__(self):
        course_list = ", ".join([c.code for c in self.courses])
        return f"{self.get_term_key()}: [{course_list}] ({self.total_credits} credits)"


class PlanGenerator:
    """
    Builds semester-by-semester plans based on required courses,
    prereqs, course offerings, and credit limits.
    """

    def __init__(self, repository: Repository):
        """
        Set up the plan generator

        Args:
            repository: Where all the course data is stored
        """
        self.repository = repository
        self.generated_plan = []

    def generate_plan(
        self,
        remaining_courses: List[str],
        start_term: str,
        start_year: int,
        max_credits_per_term: int = 9,
        track: Optional[str] = None
    ) -> List[SemesterPlan]:
        """
        Build a full semester plan with all courses scheduled

        Args:
            remaining_courses: Courses still needed
            start_term: Starting term (Fall, Spring, or Summer)
            start_year: Starting year (like 2025)
            max_credits_per_term: Max credits per semester (default is 9)
            track: Optional track filter (like 'Software Systems')

        Returns:
            List[SemesterPlan]: Full semester-by-semester plan
        """
        self.generated_plan = []
        completed_courses = set()
        courses_to_schedule = set(remaining_courses)

        current_term = start_term
        current_year = start_year

        # safety check so we don't loop forever
        max_iterations = 20
        iteration = 0

        while courses_to_schedule and iteration < max_iterations:
            iteration += 1

            # make a new semester
            semester = SemesterPlan(current_term, current_year)

            # figure out what courses can be taken this term
            schedulable = self._get_schedulable_courses(
                courses_to_schedule,
                completed_courses,
                current_term,
                current_year,
                track
            )

            # add courses up to the credit limit
            scheduled_this_term = self._schedule_courses_for_term(
                semester,
                schedulable,
                max_credits_per_term
            )

            # update what's left and what's done
            for course_code in scheduled_this_term:
                courses_to_schedule.discard(course_code)
                completed_courses.add(course_code)

            # add this semester if we scheduled anything
            if semester.courses:
                self.generated_plan.append(semester)

            # go to next semester
            current_term, current_year = self._next_term(current_term, current_year)

        return self.generated_plan

    def _get_schedulable_courses(
        self,
        remaining: Set[str],
        completed: Set[str],
        term: str,
        year: int,
        track: Optional[str]
    ) -> List[Course]:
        """
        Figure out what courses can be taken this term

        A course can be taken if:
        1. It's on the remaining list
        2. All prereqs have been completed
        3. It's offered this term
        4. It matches the track (if specified)

        Args:
            remaining: Courses still needed
            completed: Courses already taken
            term: The semester
            year: The year
            track: Optional track filter

        Returns:
            List[Course]: Available courses
        """
        schedulable = []

        for course_code in remaining:
            course = self.repository.courses.get(course_code)
            if not course:
                continue

            # check if it matches the track
            if track and course.track and course.track != track:
                continue

            # make sure prereqs have been completed
            prereqs = self.repository.get_prerequisites_for(course_code)
            if not all(prereq in completed for prereq in prereqs):
                continue

            # check if it's offered this term
            if self._is_offered(course_code, term, year):
                schedulable.append(course)

        # sort by priority (courses that unlock more stuff go first)
        schedulable.sort(key=lambda c: self._get_course_priority(c.code), reverse=True)

        return schedulable

    def _is_offered(self, course_code: str, term: str, year: int) -> bool:
        """
        Check if a course is offered in a specific term

        Args:
            course_code: Course to check
            term: The semester
            year: The year

        Returns:
            bool: True if the course is offered
        """
        # check if it's offered this specific term and year
        for offering in self.repository.offerings:
            if (offering.course_code == course_code and
                offering.term == term and
                offering.year == year):
                return True

        # if we don't have that year, just check if it's offered that term in general
        for offering in self.repository.offerings:
            if offering.course_code == course_code and offering.term == term:
                return True

        # if there's no offering data at all, assume it's available
        if not any(o.course_code == course_code for o in self.repository.offerings):
            return True

        return False

    def _get_course_priority(self, course_code: str) -> int:
        """
        Figure out how important it is to take a course early.
        Courses that unlock more courses get higher priority.

        Args:
            course_code: The course

        Returns:
            int: Priority score (higher = more important)
        """
        # count how many courses need this one as a prereq
        dependents = sum(
            1 for prereq in self.repository.prerequisites
            if prereq.prereq_course_code == course_code
        )
        return dependents

    def _schedule_courses_for_term(
        self,
        semester: SemesterPlan,
        schedulable: List[Course],
        max_credits: int
    ) -> List[str]:
        """
        Add courses to a semester without going over the credit limit

        Args:
            semester: The semester being scheduled
            schedulable: Available courses
            max_credits: Credit limit

        Returns:
            List[str]: Scheduled courses
        """
        scheduled = []

        for course in schedulable:
            if semester.total_credits + course.credits <= max_credits:
                if semester.add_course(course):
                    scheduled.append(course.code)

        return scheduled

    def _next_term(self, term: str, year: int) -> Tuple[str, int]:
        """
        Figure out what the next semester is

        Args:
            term: Current term (Fall, Spring, or Summer)
            year: Current year

        Returns:
            Tuple[str, int]: Next term and year
        """
        if term == "Fall":
            return ("Spring", year + 1)
        elif term == "Spring":
            return ("Summer", year)
        elif term == "Summer":
            return ("Fall", year)
        else:
            # fallback just in case
            return ("Fall", year + 1)

    def get_plan_summary(self) -> Dict:
        """
        Get a summary of the plan

        Returns:
            Dict: Total semesters, courses, and credits
        """
        total_credits = sum(sem.total_credits for sem in self.generated_plan)
        total_courses = sum(len(sem.courses) for sem in self.generated_plan)

        return {
            "total_semesters": len(self.generated_plan),
            "total_courses": total_courses,
            "total_credits": total_credits,
            "semesters": [
                {
                    "term": sem.get_term_key(),
                    "courses": [c.code for c in sem.courses],
                    "credits": sem.total_credits
                }
                for sem in self.generated_plan
            ]
        }

    def export_to_dict(self) -> List[Dict]:
        """
        Export the plan as a dict list (good for Excel or JSON)

        Returns:
            List[Dict]: Plan data ready to export
        """
        return [
            {
                "Term": sem.get_term_key(),
                "Courses": ", ".join([c.code for c in sem.courses]),
                "Course_Titles": ", ".join([c.title for c in sem.courses]),
                "Credits": sem.total_credits
            }
            for sem in self.generated_plan
        ]

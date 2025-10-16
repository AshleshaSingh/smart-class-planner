"""
Prerequisite Validator Module

Uses a graph (DAG) to validate the course schedule - makes sure prereqs are in order
and catches any circular dependency issues.
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, deque
from smart_class_planner.domain.repository import Repository
from smart_class_planner.application.plan_generator import SemesterPlan


class ValidationResult:
    """Holds the results of validation"""

    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def add_error(self, error: str):
        """Add an error"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add a warning"""
        self.warnings.append(warning)

    def __repr__(self):
        status = "VALID" if self.is_valid else "INVALID"
        return f"ValidationResult({status}, {len(self.errors)} errors, {len(self.warnings)} warnings)"


class PrerequisiteGraph:
    """
    Graph (DAG) of course prerequisites.
    Used for sorting courses and finding circular dependencies.
    """

    def __init__(self):
        self.graph = defaultdict(list)  # course -> courses that need it
        self.reverse_graph = defaultdict(list)  # course -> its prereqs
        self.in_degree = defaultdict(int)  # course -> number of prereqs
        self.all_courses = set()

    def add_edge(self, prerequisite: str, course: str):
        """
        Adds a prereq relationship

        Args:
            prerequisite: The prereq course
            course: The course that needs the prereq
        """
        self.graph[prerequisite].append(course)
        self.reverse_graph[course].append(prerequisite)
        self.in_degree[course] += 1
        self.all_courses.add(prerequisite)
        self.all_courses.add(course)

        # Ensure prerequisite has an entry
        if prerequisite not in self.in_degree:
            self.in_degree[prerequisite] = 0

    def detect_cycles(self) -> Tuple[bool, List[str]]:
        """
        Find any circular prereq dependencies using DFS

        Returns:
            Tuple[bool, List[str]]: (found a cycle?, the cycle path)
        """
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle_start = path.index(neighbor)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for course in self.all_courses:
            if course not in visited:
                if dfs(course):
                    return True, path

        return False, []

    def topological_sort(self) -> Optional[List[str]]:
        """
        Sort courses in prereq order (uses Kahn's algorithm)

        Returns:
            Optional[List[str]]: Sorted courses (or None if there's a cycle)
        """
        in_degree_copy = self.in_degree.copy()
        queue = deque([course for course in self.all_courses if in_degree_copy[course] == 0])
        sorted_list = []

        while queue:
            course = queue.popleft()
            sorted_list.append(course)

            for dependent in self.graph[course]:
                in_degree_copy[dependent] -= 1
                if in_degree_copy[dependent] == 0:
                    queue.append(dependent)

        # if not all courses are in sorted_list, there's a cycle
        if len(sorted_list) != len(self.all_courses):
            return None

        return sorted_list

    def get_all_prerequisites(self, course: str) -> Set[str]:
        """
        get all of a course's prereqs

        Args:
            course: The course code

        Returns:
            Set[str]: All prerequisite course codes
        """
        prerequisites = set()
        queue = deque([course])
        visited = set()

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            for prereq in self.reverse_graph[current]:
                prerequisites.add(prereq)
                queue.append(prereq)

        return prerequisites


class PlanValidator:
    """
    Checks if the course plan makes sense prereq-wise and structurally
    """

    def __init__(self, repository: Repository):
        """
        Set up the validator

        Args:
            repository: Where all the course data is
        """
        self.repository = repository
        self.prereq_graph = PrerequisiteGraph()
        self._build_prerequisite_graph()

    def _build_prerequisite_graph(self):
        """Build the prerequisite graph from repository data."""
        for prereq in self.repository.prerequisites:
            self.prereq_graph.add_edge(
                prereq.prereq_course_code,
                prereq.course_code
            )

    def validate_prerequisites_structure(self) -> ValidationResult:
        """
        Check the prereq structure for cycles and consistency

        Returns:
            ValidationResult: How it looks
        """
        result = ValidationResult(is_valid=True)

        # check for cycles
        has_cycle, cycle_path = self.prereq_graph.detect_cycles()
        if has_cycle:
            result.add_error(
                f"Circular prerequisite dependency detected: {' -> '.join(cycle_path)}"
            )

        # check for  any missing courses
        for course_code in self.prereq_graph.all_courses:
            if course_code not in self.repository.courses:
                result.add_warning(
                    f"Course {course_code} is referenced in prerequisites but not in course catalog"
                )

        return result

    def validate_plan(self, plan: List[SemesterPlan]) -> ValidationResult:
        """
        Check if your full semester plan respects all prereqs

        Args:
            plan: the semester plans

        Returns:
            ValidationResult: Validation results
        """
        result = ValidationResult(is_valid=True)
        completed_courses = set()

        for semester in plan:
            for course in semester.courses:
                # get course preqreqs
                prereqs = self.repository.get_prerequisites_for(course.code)

                # Check if all prereqs are complete
                missing_prereqs = [p for p in prereqs if p not in completed_courses]
                if missing_prereqs:
                    result.add_error(
                        f"{course.code} in {semester.get_term_key()} is missing prerequisites: "
                        f"{', '.join(missing_prereqs)}"
                    )

            # Mark all courses in this semester as completed
            for course in semester.courses:
                completed_courses.add(course.code)

        return result

    def validate_single_semester(
        self,
        semester: SemesterPlan,
        completed_courses: Set[str]
    ) -> ValidationResult:
        """
        Validate a single semester against completed courses.

        Args:
            semester: The semester plan to validate
            completed_courses: Set of course codes already completed

        Returns:
            ValidationResult: Result of semester validation
        """
        result = ValidationResult(is_valid=True)

        for course in semester.courses:
            prereqs = self.repository.get_prerequisites_for(course.code)
            missing_prereqs = [p for p in prereqs if p not in completed_courses]

            if missing_prereqs:
                result.add_error(
                    f"{course.code} requires {', '.join(missing_prereqs)} which are not completed"
                )

        return result

    def get_prerequisite_chain(self, course_code: str) -> List[List[str]]:
        """
        Get all prerequisite chains for a course (for visualization/debugging).

        Args:
            course_code: The course code

        Returns:
            List[List[str]]: List of prerequisite chains
        """
        chains = []

        def build_chains(course: str, path: List[str]):
            prereqs = self.repository.get_prerequisites_for(course)
            if not prereqs:
                chains.append(path[:])
                return

            for prereq in prereqs:
                path.append(prereq)
                build_chains(prereq, path)
                path.pop()

        build_chains(course_code, [course_code])
        return chains

    def suggest_prerequisite_order(self, courses: List[str]) -> Optional[List[str]]:
        """
        Suggest an optimal ordering for a set of courses based on prerequisites.

        Args:
            courses: List of course codes to order

        Returns:
            Optional[List[str]]: Suggested order, or None if cycle detected
        """
        # Build a subgraph with only the specified courses
        subgraph = PrerequisiteGraph()

        for course in courses:
            prereqs = self.repository.get_prerequisites_for(course)
            for prereq in prereqs:
                if prereq in courses:
                    subgraph.add_edge(prereq, course)
                else:
                    # Prerequisite not in the list, add course with no prereq
                    subgraph.all_courses.add(course)
                    if course not in subgraph.in_degree:
                        subgraph.in_degree[course] = 0

        return subgraph.topological_sort()

    def check_course_availability(
        self,
        course_code: str,
        term: str,
        year: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a course is available in a given term.

        Args:
            course_code: The course code
            term: The semester term
            year: The year

        Returns:
            Tuple[bool, Optional[str]]: (is_available, suggestion_message)
        """
        for offering in self.repository.offerings:
            if offering.course_code == course_code and offering.term == term:
                return True, None

        # Find when the course is offered
        offered_terms = set()
        for offering in self.repository.offerings:
            if offering.course_code == course_code:
                offered_terms.add(offering.term)

        if offered_terms:
            return False, f"{course_code} is typically offered in: {', '.join(offered_terms)}"
        else:
            return False, f"No offering information available for {course_code}"

    def validate_credit_distribution(
        self,
        plan: List[SemesterPlan],
        min_credits: int = 3,
        max_credits: int = 12
    ) -> ValidationResult:
        """
        Validate that credit distribution is reasonable across semesters.

        Args:
            plan: List of semester plans
            min_credits: Minimum credits per semester
            max_credits: Maximum credits per semester

        Returns:
            ValidationResult: Result of credit validation
        """
        result = ValidationResult(is_valid=True)

        for semester in plan:
            if semester.total_credits < min_credits:
                result.add_warning(
                    f"{semester.get_term_key()} has only {semester.total_credits} credits "
                    f"(minimum recommended: {min_credits})"
                )
            elif semester.total_credits > max_credits:
                result.add_error(
                    f"{semester.get_term_key()} has {semester.total_credits} credits "
                    f"(maximum allowed: {max_credits})"
                )

        return result

    def get_validation_summary(self) -> Dict:
        """
        Get a summary of the prerequisite graph structure.

        Returns:
            Dict: Summary statistics
        """
        return {
            "total_courses": len(self.prereq_graph.all_courses),
            "total_prerequisites": len(self.repository.prerequisites),
            "courses_with_no_prerequisites": sum(
                1 for course in self.prereq_graph.all_courses
                if self.prereq_graph.in_degree[course] == 0
            ),
            "max_prerequisite_depth": self._calculate_max_depth()
        }

    def _calculate_max_depth(self) -> int:
        """Calculate the max depth of the prereq chain."""
        max_depth = 0

        for course in self.prereq_graph.all_courses:
            depth = len(self.prereq_graph.get_all_prerequisites(course))
            max_depth = max(max_depth, depth)

        return max_depth

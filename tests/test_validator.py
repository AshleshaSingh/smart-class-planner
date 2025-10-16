"""
Unit tests for the Validator
"""

import pytest
from smart_class_planner.domain.course import Course
from smart_class_planner.domain.prerequisite import Prerequisite
from smart_class_planner.domain.offering import Offering
from smart_class_planner.domain.repository import Repository
from smart_class_planner.application.plan_generator import SemesterPlan
from smart_class_planner.application.validator import (
    PlanValidator,
    ValidationResult,
    PrerequisiteGraph
)


class TestValidationResult:
    """Tests for ValidationResult class"""

    def test_create_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_create_invalid_result(self):
        """Test creating an invalid result."""
        result = ValidationResult(is_valid=False, errors=["Error 1"])
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_add_error(self):
        """Test adding an error."""
        result = ValidationResult(is_valid=True)
        result.add_error("Something went wrong")
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_add_warning(self):
        """Test adding a warning."""
        result = ValidationResult(is_valid=True)
        result.add_warning("This is a warning")
        assert result.is_valid is True
        assert len(result.warnings) == 1


class TestPrerequisiteGraph:
    """Tests for PrerequisiteGraph class"""

    def test_create_graph(self):
        """Test creating an empty graph."""
        graph = PrerequisiteGraph()
        assert len(graph.all_courses) == 0

    def test_add_edge(self):
        """Test adding edges to graph."""
        graph = PrerequisiteGraph()
        graph.add_edge("CPSC 6000", "CPSC 6100")

        assert "CPSC 6000" in graph.all_courses
        assert "CPSC 6100" in graph.all_courses
        assert "CPSC 6100" in graph.graph["CPSC 6000"]
        assert "CPSC 6000" in graph.reverse_graph["CPSC 6100"]
        assert graph.in_degree["CPSC 6100"] == 1
        assert graph.in_degree["CPSC 6000"] == 0

    def test_detect_no_cycle(self):
        """Test cycle detection with no cycles."""
        graph = PrerequisiteGraph()
        graph.add_edge("CPSC 6000", "CPSC 6100")
        graph.add_edge("CPSC 6100", "CPSC 6200")

        has_cycle, path = graph.detect_cycles()
        assert has_cycle is False

    def test_detect_cycle(self):
        """Test cycle detection with a cycle."""
        graph = PrerequisiteGraph()
        graph.add_edge("CPSC 6000", "CPSC 6100")
        graph.add_edge("CPSC 6100", "CPSC 6200")
        graph.add_edge("CPSC 6200", "CPSC 6000")  # Creates cycle

        has_cycle, path = graph.detect_cycles()
        assert has_cycle is True

    def test_topological_sort_valid(self):
        """Test topological sort with valid DAG."""
        graph = PrerequisiteGraph()
        graph.add_edge("CPSC 6000", "CPSC 6100")
        graph.add_edge("CPSC 6000", "CPSC 6200")
        graph.add_edge("CPSC 6100", "CPSC 6300")

        sorted_list = graph.topological_sort()
        assert sorted_list is not None
        assert len(sorted_list) == 4

        # CPSC 6000 should come before 6100, 6200, 6300
        assert sorted_list.index("CPSC 6000") < sorted_list.index("CPSC 6100")
        assert sorted_list.index("CPSC 6000") < sorted_list.index("CPSC 6200")
        assert sorted_list.index("CPSC 6100") < sorted_list.index("CPSC 6300")

    def test_topological_sort_with_cycle(self):
        """Test topological sort returns None with cycle."""
        graph = PrerequisiteGraph()
        graph.add_edge("CPSC 6000", "CPSC 6100")
        graph.add_edge("CPSC 6100", "CPSC 6000")  # Cycle

        sorted_list = graph.topological_sort()
        assert sorted_list is None

    def test_get_all_prerequisites(self):
        """Test getting all prerequisites (transitive closure)."""
        graph = PrerequisiteGraph()
        graph.add_edge("CPSC 6000", "CPSC 6100")
        graph.add_edge("CPSC 6100", "CPSC 6200")
        graph.add_edge("CPSC 6300", "CPSC 6200")

        prereqs = graph.get_all_prerequisites("CPSC 6200")
        assert "CPSC 6000" in prereqs
        assert "CPSC 6100" in prereqs
        assert "CPSC 6300" in prereqs


class TestPlanValidator:
    """Tests for PlanValidator class"""

    @pytest.fixture
    def repository(self):
        """Set up a test repo"""
        repo = Repository()

        # Create courses
        c1 = Course("CPSC 6000", "Algorithms", 3)
        c2 = Course("CPSC 6100", "Data Structures", 3)
        c3 = Course("CPSC 6200", "Machine Learning", 3)
        c4 = Course("CPSC 6300", "Software Engineering", 3)

        repo.add_course(c1)
        repo.add_course(c2)
        repo.add_course(c3)
        repo.add_course(c4)

        # Add prerequisites
        repo.add_prerequisite(Prerequisite("CPSC 6100", "CPSC 6000"))
        repo.add_prerequisite(Prerequisite("CPSC 6200", "CPSC 6100"))

        # Add offerings
        for course_code in ["CPSC 6000", "CPSC 6100", "CPSC 6200", "CPSC 6300"]:
            repo.add_offering(Offering(course_code, "Fall", 2025))
            repo.add_offering(Offering(course_code, "Spring", 2026))

        return repo

    def test_create_validator(self, repository):
        """Test creating a validator."""
        validator = PlanValidator(repository)
        assert validator.repository == repository
        assert validator.prereq_graph is not None

    def test_validate_structure_no_cycles(self, repository):
        """Test validating structure with no cycles."""
        validator = PlanValidator(repository)
        result = validator.validate_prerequisites_structure()
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_structure_with_cycle(self):
        """Test validating structure with cycles."""
        repo = Repository()
        repo.add_course(Course("CPSC 6000", "Course A", 3))
        repo.add_course(Course("CPSC 6100", "Course B", 3))

        # Create circular dependency
        repo.add_prerequisite(Prerequisite("CPSC 6000", "CPSC 6100"))
        repo.add_prerequisite(Prerequisite("CPSC 6100", "CPSC 6000"))

        validator = PlanValidator(repo)
        result = validator.validate_prerequisites_structure()
        assert result.is_valid is False
        assert any("Circular" in err for err in result.errors)

    def test_validate_valid_plan(self, repository):
        """Test validating a valid plan."""
        validator = PlanValidator(repository)

        # Create a valid plan
        sem1 = SemesterPlan("Fall", 2025)
        sem1.add_course(repository.courses["CPSC 6000"])

        sem2 = SemesterPlan("Spring", 2026)
        sem2.add_course(repository.courses["CPSC 6100"])

        sem3 = SemesterPlan("Summer", 2026)
        sem3.add_course(repository.courses["CPSC 6200"])

        plan = [sem1, sem2, sem3]
        result = validator.validate_plan(plan)
        assert result.is_valid is True

    def test_validate_invalid_plan(self, repository):
        """Test validating a plan with prerequisite violations."""
        validator = PlanValidator(repository)

        # Create an invalid plan (schedule 6200 before 6100)
        sem1 = SemesterPlan("Fall", 2025)
        sem1.add_course(repository.courses["CPSC 6000"])

        sem2 = SemesterPlan("Spring", 2026)
        sem2.add_course(repository.courses["CPSC 6200"])  # Missing prereq 6100

        plan = [sem1, sem2]
        result = validator.validate_plan(plan)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_single_semester(self, repository):
        """Test validating a single semester."""
        validator = PlanValidator(repository)

        # Valid semester
        semester = SemesterPlan("Fall", 2025)
        semester.add_course(repository.courses["CPSC 6100"])

        completed = {"CPSC 6000"}
        result = validator.validate_single_semester(semester, completed)
        assert result.is_valid is True

        # Invalid semester
        semester2 = SemesterPlan("Spring", 2026)
        semester2.add_course(repository.courses["CPSC 6200"])

        result2 = validator.validate_single_semester(semester2, completed)
        assert result2.is_valid is False

    def test_get_prerequisite_chain(self, repository):
        """Test getting prerequisite chains."""
        validator = PlanValidator(repository)
        chains = validator.get_prerequisite_chain("CPSC 6200")

        # Should have chain: 6200 -> 6100 -> 6000
        assert len(chains) > 0
        # Check that one chain contains all three courses
        full_chain = [chain for chain in chains if len(chain) == 3]
        assert len(full_chain) > 0

    def test_suggest_prerequisite_order(self, repository):
        """Test suggesting course order."""
        validator = PlanValidator(repository)
        courses = ["CPSC 6000", "CPSC 6100", "CPSC 6200"]

        order = validator.suggest_prerequisite_order(courses)
        assert order is not None
        assert len(order) == 3

        # Verify order respects prerequisites
        assert order.index("CPSC 6000") < order.index("CPSC 6100")
        assert order.index("CPSC 6100") < order.index("CPSC 6200")

    def test_check_course_availability(self, repository):
        """Test checking course availability."""
        validator = PlanValidator(repository)

        # Course offered in Fall
        is_available, msg = validator.check_course_availability("CPSC 6000", "Fall", 2025)
        assert is_available is True

        # Course not offered in Summer (based on our test data)
        is_available, msg = validator.check_course_availability("CPSC 6000", "Summer", 2025)
        assert is_available is False
        assert msg is not None

    def test_validate_credit_distribution(self, repository):
        """Test validating credit distribution."""
        validator = PlanValidator(repository)

        # Create plan with valid credits
        sem1 = SemesterPlan("Fall", 2025)
        sem1.add_course(repository.courses["CPSC 6000"])
        sem1.add_course(repository.courses["CPSC 6300"])

        plan = [sem1]
        result = validator.validate_credit_distribution(plan, min_credits=3, max_credits=12)
        assert result.is_valid is True

        # Create plan with too many credits
        sem2 = SemesterPlan("Spring", 2026)
        for _ in range(5):
            course = Course("CPSC 9999", "Heavy Course", 3)
            sem2.add_course(course)

        plan2 = [sem2]
        result2 = validator.validate_credit_distribution(plan2, min_credits=3, max_credits=12)
        assert result2.is_valid is False

    def test_get_validation_summary(self, repository):
        """Test getting validation summary."""
        validator = PlanValidator(repository)
        summary = validator.get_validation_summary()

        assert "total_courses" in summary
        assert "total_prerequisites" in summary
        assert "courses_with_no_prerequisites" in summary
        assert summary["total_courses"] > 0


class TestValidatorIntegration:
    """Integration tests for validator with complex scenarios"""

    def test_complex_prerequisite_chain(self):
        """Test validating complex prerequisite chains."""
        repo = Repository()

        # Create a complex chain
        courses = [
            ("CPSC 6000", "Foundation", []),
            ("CPSC 6100", "Course 1", ["CPSC 6000"]),
            ("CPSC 6200", "Course 2", ["CPSC 6000"]),
            ("CPSC 6300", "Course 3", ["CPSC 6100", "CPSC 6200"]),
            ("CPSC 6400", "Advanced", ["CPSC 6300"]),
        ]

        for code, title, prereqs in courses:
            course = Course(code, title, 3)
            repo.add_course(course)

            for prereq in prereqs:
                repo.add_prerequisite(Prerequisite(code, prereq))

        validator = PlanValidator(repo)

        # Validate structure
        result = validator.validate_prerequisites_structure()
        assert result.is_valid is True

        # Check all prerequisites for 6400
        all_prereqs = validator.prereq_graph.get_all_prerequisites("CPSC 6400")
        assert "CPSC 6000" in all_prereqs
        assert "CPSC 6100" in all_prereqs
        assert "CPSC 6200" in all_prereqs
        assert "CPSC 6300" in all_prereqs

    def test_multiple_prerequisite_paths(self):
        """Test handling multiple prerequisite paths."""
        repo = Repository()

        # Create diamond dependency: A -> B, A -> C, B -> D, C -> D
        courses = [
            ("CPSC 6000", "A", []),
            ("CPSC 6100", "B", ["CPSC 6000"]),
            ("CPSC 6200", "C", ["CPSC 6000"]),
            ("CPSC 6300", "D", ["CPSC 6100", "CPSC 6200"]),
        ]

        for code, title, prereqs in courses:
            course = Course(code, title, 3)
            repo.add_course(course)

            for prereq in prereqs:
                repo.add_prerequisite(Prerequisite(code, prereq))

        validator = PlanValidator(repo)

        # Test ordering
        order = validator.suggest_prerequisite_order(
            ["CPSC 6000", "CPSC 6100", "CPSC 6200", "CPSC 6300"]
        )
        assert order is not None

        # 6000 should be first, 6300 should be last
        assert order[0] == "CPSC 6000"
        assert order[-1] == "CPSC 6300"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

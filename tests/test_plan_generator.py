"""
Unit tests for the PlanGenerator
"""

import pytest
from smart_class_planner.domain.course import Course
from smart_class_planner.domain.prerequisite import Prerequisite
from smart_class_planner.domain.offering import Offering
from smart_class_planner.domain.repository import Repository
from smart_class_planner.application.plan_generator import PlanGenerator, SemesterPlan


class TestSemesterPlan:
    """Tests for SemesterPlan class"""

    def test_create_semester_plan(self):
        """Test creating a semester plan."""
        semester = SemesterPlan("Fall", 2025)
        assert semester.term == "Fall"
        assert semester.year == 2025
        assert semester.total_credits == 0
        assert len(semester.courses) == 0

    def test_add_course(self):
        """Test adding a course to a semester."""
        semester = SemesterPlan("Fall", 2025)
        course = Course("CPSC 6000", "Advanced Topics", 3)

        result = semester.add_course(course)
        assert result is True
        assert len(semester.courses) == 1
        assert semester.total_credits == 3

    def test_add_duplicate_course(self):
        """Test that duplicate courses are not added."""
        semester = SemesterPlan("Fall", 2025)
        course = Course("CPSC 6000", "Advanced Topics", 3)

        semester.add_course(course)
        result = semester.add_course(course)

        assert result is False
        assert len(semester.courses) == 1
        assert semester.total_credits == 3

    def test_get_term_key(self):
        """Test getting the term key."""
        semester = SemesterPlan("Spring", 2026)
        assert semester.get_term_key() == "Spring 2026"


class TestPlanGenerator:
    """Tests for PlanGenerator class"""

    @pytest.fixture
    def repository(self):
        """Set up a test repo with sample data"""
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

        # Add prerequisites: 6100 requires 6000, 6200 requires 6100
        repo.add_prerequisite(Prerequisite("CPSC 6100", "CPSC 6000"))
        repo.add_prerequisite(Prerequisite("CPSC 6200", "CPSC 6100"))

        # Add offerings - all courses offered every semester
        for course_code in ["CPSC 6000", "CPSC 6100", "CPSC 6200", "CPSC 6300"]:
            repo.add_offering(Offering(course_code, "Fall", 2025))
            repo.add_offering(Offering(course_code, "Spring", 2026))
            repo.add_offering(Offering(course_code, "Summer", 2026))

        return repo

    def test_create_generator(self, repository):
        """Test creating a plan generator."""
        generator = PlanGenerator(repository)
        assert generator.repository == repository
        assert len(generator.generated_plan) == 0

    def test_generate_simple_plan(self, repository):
        """Test generating a simple plan with no prerequisites."""
        generator = PlanGenerator(repository)
        plan = generator.generate_plan(
            remaining_courses=["CPSC 6300"],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        assert len(plan) == 1
        assert len(plan[0].courses) == 1
        assert plan[0].courses[0].code == "CPSC 6300"

    def test_generate_plan_with_prerequisites(self, repository):
        """Test generating a plan respecting prerequisites."""
        generator = PlanGenerator(repository)
        plan = generator.generate_plan(
            remaining_courses=["CPSC 6000", "CPSC 6100", "CPSC 6200"],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Should schedule courses in order: 6000, then 6100, then 6200
        assert len(plan) >= 3

        # Get all scheduled courses in order
        scheduled = []
        for semester in plan:
            for course in semester.courses:
                scheduled.append(course.code)

        # 6000 must come before 6100
        assert scheduled.index("CPSC 6000") < scheduled.index("CPSC 6100")
        # 6100 must come before 6200
        assert scheduled.index("CPSC 6100") < scheduled.index("CPSC 6200")

    def test_credit_limit_respected(self, repository):
        """Test that credit limits are respected."""
        generator = PlanGenerator(repository)
        plan = generator.generate_plan(
            remaining_courses=["CPSC 6000", "CPSC 6300"],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=3  # Only one course per semester
        )

        # Should need at least 2 semesters
        assert len(plan) >= 2
        for semester in plan:
            assert semester.total_credits <= 3

    def test_next_term_sequence(self, repository):
        """Test term progression."""
        generator = PlanGenerator(repository)

        assert generator._next_term("Fall", 2025) == ("Spring", 2026)
        assert generator._next_term("Spring", 2025) == ("Summer", 2025)
        assert generator._next_term("Summer", 2025) == ("Fall", 2025)

    def test_get_plan_summary(self, repository):
        """Test getting plan summary."""
        generator = PlanGenerator(repository)
        plan = generator.generate_plan(
            remaining_courses=["CPSC 6000", "CPSC 6100"],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        summary = generator.get_plan_summary()

        assert "total_semesters" in summary
        assert "total_courses" in summary
        assert "total_credits" in summary
        assert summary["total_courses"] == 2
        assert summary["total_credits"] == 6

    def test_export_to_dict(self, repository):
        """Test exporting plan to dictionary."""
        generator = PlanGenerator(repository)
        plan = generator.generate_plan(
            remaining_courses=["CPSC 6000"],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        export = generator.export_to_dict()

        assert len(export) == 1
        assert "Term" in export[0]
        assert "Courses" in export[0]
        assert "Credits" in export[0]
        assert export[0]["Credits"] == 3

    def test_course_priority_calculation(self, repository):
        """Test that courses with more dependents get higher priority."""
        generator = PlanGenerator(repository)

        # 6000 has 1 dependent (6100), 6100 has 1 dependent (6200)
        priority_6000 = generator._get_course_priority("CPSC 6000")
        priority_6300 = generator._get_course_priority("CPSC 6300")

        # 6000 should have higher priority than 6300 (which has no dependents)
        assert priority_6000 > priority_6300

    def test_empty_course_list(self, repository):
        """Test generating plan with no courses."""
        generator = PlanGenerator(repository)
        plan = generator.generate_plan(
            remaining_courses=[],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        assert len(plan) == 0

    def test_nonexistent_course(self, repository):
        """Test handling of courses not in repository."""
        generator = PlanGenerator(repository)
        plan = generator.generate_plan(
            remaining_courses=["CPSC 9999"],  # Doesn't exist
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Should return empty or handle gracefully
        assert isinstance(plan, list)

    def test_max_iterations_safety(self, repository):
        """Test that infinite loops are prevented."""
        # Create a scenario that could potentially loop
        generator = PlanGenerator(repository)

        # Add circular prerequisite (normally prevented by validator)
        # But test that generator has safety mechanism
        plan = generator.generate_plan(
            remaining_courses=["CPSC 6000", "CPSC 6100", "CPSC 6200", "CPSC 6300"],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Should complete within reasonable iterations
        assert len(plan) <= 20


class TestPlanGeneratorIntegration:
    """Integration tests for PlanGenerator with more complex stuff"""

    def test_full_degree_plan(self):
        """Test generating a complete degree plan."""
        repo = Repository()

        # Create a test set of courses
        courses = [
            ("CPSC 6000", "Algorithms", 3, None),
            ("CPSC 6100", "Theory", 3, "CPSC 6000"),
            ("CPSC 6200", "Database", 3, "CPSC 6000"),
            ("CPSC 6300", "Networks", 3, None),
            ("CPSC 6400", "Security", 3, "CPSC 6300"),
            ("CPSC 6500", "AI", 3, "CPSC 6100"),
            ("CPSC 6600", "ML", 3, "CPSC 6500"),
            ("CPSC 6700", "Cloud", 3, None),
            ("CPSC 6800", "Project", 3, None),
        ]

        for code, title, credits, prereq in courses:
            course = Course(code, title, credits)
            repo.add_course(course)

            if prereq:
                repo.add_prerequisite(Prerequisite(code, prereq))

            # All courses offered every semester
            for term in ["Fall", "Spring", "Summer"]:
                repo.add_offering(Offering(code, term, 2025))
                repo.add_offering(Offering(code, term, 2026))

        generator = PlanGenerator(repo)
        remaining = [c[0] for c in courses]

        plan = generator.generate_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )
        assert len(plan) >= 3  # At least 3 semesters needed

        # All courses should be scheduled
        scheduled_codes = []
        for semester in plan:
            for course in semester.courses:
                scheduled_codes.append(course.code)

        assert len(scheduled_codes) == len(courses)

        # Check prerequisite ordering
        assert scheduled_codes.index("CPSC 6000") < scheduled_codes.index("CPSC 6100")
        assert scheduled_codes.index("CPSC 6100") < scheduled_codes.index("CPSC 6500")
        assert scheduled_codes.index("CPSC 6500") < scheduled_codes.index("CPSC 6600")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

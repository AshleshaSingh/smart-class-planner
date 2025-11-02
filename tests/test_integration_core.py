"""
Integration Tests (Core Modules)
--------------------------------
Validates internal integration between domain and application layers:
- Repository loading
- Plan generation
- Prerequisite validation

Does NOT test GUI or entry-point scripts.
"""

import pytest
from smart_class_planner.domain.course import Course
from smart_class_planner.domain.prerequisite import Prerequisite
from smart_class_planner.domain.offering import Offering
from smart_class_planner.domain.repository import Repository
from smart_class_planner.application.planner import IntegratedPlanner


class TestIntegratedPlanner:
    """Tests for the full planning system"""

    @pytest.fixture
    def complex_repository(self):
        """Set up a test repo that looks like a real degree program"""
        repo = Repository()

        # Define a realistic course catalog for a Master's program
        courses_data = [
            # Core courses (no prerequisites)
            ("CPSC 6000", "Foundations of Computer Science", 3, None, ["Fall", "Spring"]),
            ("CPSC 6050", "Discrete Mathematics", 3, None, ["Fall", "Spring"]),

            # Second tier (depend on core)
            ("CPSC 6100", "Algorithms and Data Structures", 3, "CPSC 6000", ["Fall", "Spring", "Summer"]),
            ("CPSC 6150", "Database Systems", 3, "CPSC 6000", ["Fall", "Spring"]),

            # Third tier
            ("CPSC 6200", "Advanced Algorithms", 3, "CPSC 6100", ["Spring"]),
            ("CPSC 6250", "Machine Learning", 3, "CPSC 6100", ["Fall", "Spring"]),
            ("CPSC 6300", "Software Engineering", 3, "CPSC 6100", ["Fall", "Spring"]),

            # Fourth tier
            ("CPSC 6350", "Deep Learning", 3, "CPSC 6250", ["Spring"]),
            ("CPSC 6400", "Cloud Computing", 3, "CPSC 6150", ["Fall"]),

            # Electives (minimal prerequisites)
            ("CPSC 6500", "Cybersecurity", 3, "CPSC 6000", ["Fall", "Spring"]),
            ("CPSC 6550", "Mobile Development", 3, None, ["Fall", "Summer"]),
        ]

        for code, title, credits, prereq, terms in courses_data:
            course = Course(code, title, credits)
            repo.add_course(course)

            if prereq:
                repo.add_prerequisite(Prerequisite(code, prereq))

            # Add offerings for multiple years
            for year in [2025, 2026, 2027]:
                for term in terms:
                    repo.add_offering(Offering(code, term, year))

        return repo

    def test_create_integrated_planner(self, complex_repository):
        """Test creating an integrated planner."""
        planner = IntegratedPlanner(complex_repository)
        assert planner.repository == complex_repository
        assert planner.generator is not None
        assert planner.validator is not None

    def test_generate_and_validate_simple_plan(self, complex_repository):
        """Test generating and validating a simple plan."""
        planner = IntegratedPlanner(complex_repository)

        remaining = ["CPSC 6000", "CPSC 6100", "CPSC 6200"]

        plan, validation = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Plan should be generated
        assert len(plan) > 0

        # Validation should pass
        assert validation.is_valid is True

        # All courses should be scheduled
        scheduled_codes = []
        for semester in plan:
            for course in semester.courses:
                scheduled_codes.append(course.code)
        assert set(scheduled_codes) == set(remaining)

    def test_full_degree_program_planning(self, complex_repository):
        """Test planning a complete degree program."""
        planner = IntegratedPlanner(complex_repository)

        # Student needs to complete all courses except the already taken core course
        remaining = [
            "CPSC 6000", "CPSC 6050", "CPSC 6100", "CPSC 6150",
            "CPSC 6200", "CPSC 6250", "CPSC 6300", "CPSC 6350",
            "CPSC 6400", "CPSC 6500"
        ]

        plan, validation = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Verify plan is generated
        assert len(plan) > 0

        # Check all courses are scheduled
        scheduled_codes = set()
        for semester in plan:
            for course in semester.courses:
                scheduled_codes.add(course.code)

        assert scheduled_codes == set(remaining)

        # Verify prerequisite ordering
        scheduled_list = []
        for semester in plan:
            for course in semester.courses:
                scheduled_list.append(course.code)

        # Core courses should come first
        assert scheduled_list.index("CPSC 6000") < scheduled_list.index("CPSC 6100")
        assert scheduled_list.index("CPSC 6100") < scheduled_list.index("CPSC 6200")
        assert scheduled_list.index("CPSC 6100") < scheduled_list.index("CPSC 6250")
        assert scheduled_list.index("CPSC 6250") < scheduled_list.index("CPSC 6350")

        # Generate comprehensive report
        report = planner.get_comprehensive_report(plan, validation)
        assert "plan_summary" in report
        assert "validation" in report
        assert report["plan_summary"]["total_courses"] == len(remaining)

    def test_optimized_plan_generation(self, complex_repository):
        """Test optimized plan generation with multiple attempts."""
        planner = IntegratedPlanner(complex_repository)

        remaining = [
            "CPSC 6000", "CPSC 6100", "CPSC 6200",
            "CPSC 6250", "CPSC 6300", "CPSC 6350"
        ]

        plan, validation = planner.create_optimized_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=6,  # Tight credit limit
            max_attempts=3
        )

        # Should produce a valid plan
        assert len(plan) > 0

        # All courses should be scheduled
        scheduled_codes = set()
        for semester in plan:
            for course in semester.courses:
                scheduled_codes.add(course.code)
        assert scheduled_codes == set(remaining)

    def test_validate_existing_plan(self, complex_repository):
        """Test validating a pre-existing plan."""
        planner = IntegratedPlanner(complex_repository)

        # First generate a valid plan
        remaining = ["CPSC 6000", "CPSC 6100"]
        plan, _ = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Validate the existing plan
        validation = planner.validate_existing_plan(plan)
        assert validation.is_valid is True

    def test_suggest_course_ordering(self, complex_repository):
        """Test suggesting optimal course ordering."""
        planner = IntegratedPlanner(complex_repository)

        courses = ["CPSC 6000", "CPSC 6100", "CPSC 6200", "CPSC 6250"]
        suggested_order = planner.suggest_course_ordering(courses)

        assert suggested_order is not None
        assert len(suggested_order) == 4

        # Verify prerequisites are respected
        assert suggested_order.index("CPSC 6000") < suggested_order.index("CPSC 6100")
        assert suggested_order.index("CPSC 6100") < suggested_order.index("CPSC 6200")

    def test_graduation_requirements_check(self, complex_repository):
        """Test checking graduation requirements."""
        planner = IntegratedPlanner(complex_repository)

        # Generate a complete plan
        remaining = ["CPSC 6000", "CPSC 6100", "CPSC 6200", "CPSC 6250"]
        plan, _ = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Check if plan meets requirements (12 credits minimum)
        meets_req, issues = planner.check_graduation_requirements(
            plan=plan,
            required_courses=remaining,
            min_total_credits=12
        )

        assert meets_req is True
        assert len(issues) == 0

    def test_incomplete_graduation_requirements(self, complex_repository):
        """Test detecting incomplete graduation requirements."""
        planner = IntegratedPlanner(complex_repository)

        # Generate a partial plan
        remaining = ["CPSC 6000", "CPSC 6100"]
        plan, _ = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Check against more requirements than scheduled
        required = ["CPSC 6000", "CPSC 6100", "CPSC 6200", "CPSC 6250"]
        meets_req, issues = planner.check_graduation_requirements(
            plan=plan,
            required_courses=required,
            min_total_credits=12
        )

        assert meets_req is False
        assert len(issues) > 0

    def test_export_with_validation_annotations(self, complex_repository):
        """Test exporting plan with validation status."""
        planner = IntegratedPlanner(complex_repository)

        remaining = ["CPSC 6000", "CPSC 6100"]
        plan, validation = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        export_data = planner.export_plan_with_validation(plan, validation)

        assert len(export_data) > 0
        assert "Status" in export_data[0]
        assert "Notes" in export_data[0]

    def test_plan_with_offering_constraints(self, complex_repository):
        """Test planning with real offering constraints."""
        planner = IntegratedPlanner(complex_repository)

        # CPSC 6350 (Deep Learning) is only offered in Spring
        # CPSC 6400 (Cloud Computing) is only offered in Fall
        remaining = ["CPSC 6100", "CPSC 6150", "CPSC 6250", "CPSC 6350", "CPSC 6400"]

        plan, validation = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Find when courses are scheduled
        course_schedule = {}
        for semester in plan:
            for course in semester.courses:
                course_schedule[course.code] = semester.get_term_key()

        # Deep Learning should be scheduled in a Spring term
        if "CPSC 6350" in course_schedule:
            assert "Spring" in course_schedule["CPSC 6350"]

        # Cloud Computing should be scheduled in a Fall term
        if "CPSC 6400" in course_schedule:
            assert "Fall" in course_schedule["CPSC 6400"]

    def test_comprehensive_report_generation(self, complex_repository):
        """Test generating comprehensive report."""
        planner = IntegratedPlanner(complex_repository)

        remaining = ["CPSC 6000", "CPSC 6100", "CPSC 6200"]
        plan, validation = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        report = planner.get_comprehensive_report(plan, validation)

        # Verify report structure
        assert "plan_summary" in report
        assert "validation" in report
        assert "prerequisite_structure" in report
        assert "recommendations" in report

        # Verify plan summary details
        assert report["plan_summary"]["total_courses"] == 3
        assert report["plan_summary"]["total_credits"] == 9

        # Verify validation details
        assert "is_valid" in report["validation"]
        assert "errors" in report["validation"]
        assert "warnings" in report["validation"]

    def test_plan_with_credit_warnings(self, complex_repository):
        """Test that credit distribution warnings are generated."""
        planner = IntegratedPlanner(complex_repository)

        # Create a plan with very low credit limit
        remaining = ["CPSC 6000", "CPSC 6100"]
        plan, validation = planner.create_validated_plan(
            remaining_courses=remaining,
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=3  # Only 1 course per term
        )

        # Should generate multiple semesters
        assert len(plan) >= 2

        # Get report with recommendations
        report = planner.get_comprehensive_report(plan, validation)

        # May have recommendations about credit distribution
        assert "recommendations" in report


class TestEdgeCases:
    """Test weird edge cases and error handling"""

    def test_empty_repository(self):
        """Test planning with empty repository."""
        repo = Repository()
        planner = IntegratedPlanner(repo)

        plan, validation = planner.create_validated_plan(
            remaining_courses=["CPSC 6000"],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        # Should handle gracefully
        assert isinstance(plan, list)
        assert isinstance(validation.is_valid, bool)

    def test_missing_prerequisites_in_catalog(self):
        """Test handling of missing prerequisite courses."""
        repo = Repository()

        # Add a course
        repo.add_course(Course("CPSC 6100", "Course", 3))

        # Add prerequisite that doesn't exist
        repo.add_prerequisite(Prerequisite("CPSC 6100", "CPSC 6000"))

        planner = IntegratedPlanner(repo)

        # Validate structure should warn about missing course
        validation = planner.validator.validate_prerequisites_structure()
        assert len(validation.warnings) > 0

    def test_circular_dependencies(self):
        """Test detection of circular dependencies."""
        repo = Repository()

        repo.add_course(Course("CPSC 6000", "Course A", 3))
        repo.add_course(Course("CPSC 6100", "Course B", 3))

        # Create circular dependency
        repo.add_prerequisite(Prerequisite("CPSC 6000", "CPSC 6100"))
        repo.add_prerequisite(Prerequisite("CPSC 6100", "CPSC 6000"))

        planner = IntegratedPlanner(repo)

        # Structure validation should fail
        plan, validation = planner.create_validated_plan(
            remaining_courses=["CPSC 6000", "CPSC 6100"],
            start_term="Fall",
            start_year=2025,
            max_credits_per_term=9
        )

        assert validation.is_valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

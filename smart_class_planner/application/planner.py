"""
Integrated Planning Module

Combines plan generation and validation into one workflow
to make sure course plans are both optimal and actually valid.
"""

from typing import List, Dict, Optional, Tuple
from smart_class_planner.domain.repository import Repository
from smart_class_planner.application.plan_generator import PlanGenerator, SemesterPlan
from smart_class_planner.application.validator import PlanValidator, ValidationResult


class IntegratedPlanner:
    """
    Handles the full workflow - generates plans and validates them.
    Makes sure plans are both optimized and actually doable.
    """

    def __init__(self, repository: Repository):
        """
        Set up the integrated planner

        Args:
            repository: Where all the course data is stored
        """
        self.repository = repository
        self.generator = PlanGenerator(repository)
        self.validator = PlanValidator(repository)

    def create_validated_plan(
        self,
        remaining_courses: List[str],
        start_term: str,
        start_year: int,
        max_credits_per_term: int = 9,
        track: Optional[str] = None,
        validate_structure: bool = True
    ) -> Tuple[List[SemesterPlan], ValidationResult]:
        """
        Generate a course plan and validate it all in one go

        Args:
            remaining_courses: Courses still needed
            start_term: Starting term (Fall, Spring, or Summer)
            start_year: Starting year
            max_credits_per_term: Max credits per semester
            track: Optional track filter
            validate_structure: Whether to check prereq structure first

        Returns:
            Tuple[List[SemesterPlan], ValidationResult]: Generated plan + validation results
        """
        # Step 1: check prereq structure (recommended)
        if validate_structure:
            structure_validation = self.validator.validate_prerequisites_structure()
            if not structure_validation.is_valid:
                # if structure is broken, return empty plan with errors
                return [], structure_validation

        # Step 2: generate the plan
        plan = self.generator.generate_plan(
            remaining_courses=remaining_courses,
            start_term=start_term,
            start_year=start_year,
            max_credits_per_term=max_credits_per_term,
            track=track
        )

        # Step 3: validate the plan
        plan_validation = self.validator.validate_plan(plan)

        # Step 4: check credit distribution
        credit_validation = self.validator.validate_credit_distribution(plan)
        for warning in credit_validation.warnings:
            plan_validation.add_warning(warning)
        for error in credit_validation.errors:
            plan_validation.add_error(error)

        return plan, plan_validation

    def create_optimized_plan(
        self,
        remaining_courses: List[str],
        start_term: str,
        start_year: int,
        max_credits_per_term: int = 9,
        track: Optional[str] = None,
        max_attempts: int = 3
    ) -> Tuple[List[SemesterPlan], ValidationResult]:
        """
        Try to generate the best plan, with multiple attempts if needed

        If validation fails, this will try different strategies like
        adjusting the schedule or reordering courses.

        Args:
            remaining_courses: Courses still needed
            start_term: Starting term
            start_year: Starting year
            max_credits_per_term: Max credits per semester
            track: Optional track filter
            max_attempts: How many times to try

        Returns:
            Tuple[List[SemesterPlan], ValidationResult]: Best plan found + validation
        """
        best_plan = None
        best_validation = None
        best_error_count = float('inf')

        # try different strategies
        for attempt in range(max_attempts):
            # adjust credit limit each attempt
            adjusted_max_credits = max_credits_per_term + (attempt * 3)

            plan, validation = self.create_validated_plan(
                remaining_courses=remaining_courses,
                start_term=start_term,
                start_year=start_year,
                max_credits_per_term=adjusted_max_credits,
                track=track,
                validate_structure=(attempt == 0)
            )

            error_count = len(validation.errors)

            # keep the best plan (fewest errors)
            if error_count < best_error_count:
                best_plan = plan
                best_validation = validation
                best_error_count = error_count

            # if we got a valid plan, we're done
            if validation.is_valid:
                break

        return best_plan, best_validation

    def suggest_course_ordering(self, courses: List[str]) -> Optional[List[str]]:
        """
        Figure out the best order to take courses based on prereqs

        Args:
            courses: Courses to order

        Returns:
            Optional[List[str]]: Suggested order (or None if there's a cycle)
        """
        return self.validator.suggest_prerequisite_order(courses)

    def validate_existing_plan(self, plan: List[SemesterPlan]) -> ValidationResult:
        """
        Validate a plan that already exists (like one loaded from a file)

        Args:
            plan: The plan to check

        Returns:
            ValidationResult: Validation results
        """
        # check prerequisites
        prereq_validation = self.validator.validate_plan(plan)

        # check credit distribution
        credit_validation = self.validator.validate_credit_distribution(plan)

        # combine both results
        combined_result = ValidationResult(
            is_valid=prereq_validation.is_valid and credit_validation.is_valid
        )
        combined_result.errors = prereq_validation.errors + credit_validation.errors
        combined_result.warnings = prereq_validation.warnings + credit_validation.warnings

        return combined_result

    def get_comprehensive_report(
        self,
        plan: List[SemesterPlan],
        validation: ValidationResult
    ) -> Dict:
        """
        Get a full report about a plan

        Args:
            plan: The course plan
            validation: The validation results

        Returns:
            Dict: Full report with all the details and validation status
        """
        plan_summary = self.generator.get_plan_summary()
        validation_summary = self.validator.get_validation_summary()

        return {
            "plan_summary": plan_summary,
            "validation": {
                "is_valid": validation.is_valid,
                "errors": validation.errors,
                "warnings": validation.warnings,
                "error_count": len(validation.errors),
                "warning_count": len(validation.warnings)
            },
            "prerequisite_structure": validation_summary,
            "recommendations": self._generate_recommendations(plan, validation)
        }

    def _generate_recommendations(
        self,
        plan: List[SemesterPlan],
        validation: ValidationResult
    ) -> List[str]:
        """
        Come up with suggestions based on a plan

        Args:
            plan: The course plan
            validation: Validation results

        Returns:
            List[str]: Recommendations
        """
        recommendations = []

        # check if credits are spread unevenly
        if plan:
            credits = [sem.total_credits for sem in plan]
            avg_credits = sum(credits) / len(credits)
            if max(credits) - min(credits) > 6:
                recommendations.append(
                    f"Try redistributing courses for a more even credit load "
                    f"(currently ranging from {min(credits)} to {max(credits)} credits per term)"
                )

        # check if it's taking forever to graduate
        if len(plan) > 6:
            recommendations.append(
                f"The plan is {len(plan)} semesters long. Maybe increase credit load "
                f"or take summer courses to graduate faster."
            )

        # suggest fixes for errors
        if not validation.is_valid:
            if any("prerequisite" in err.lower() for err in validation.errors):
                recommendations.append(
                    "There are prereq errors. Double-check the course order or make sure "
                    "all prereq data is correct."
                )

        # check if skipping summers
        summer_count = sum(1 for sem in plan if sem.term == "Summer")
        if summer_count == 0 and len(plan) > 4:
            recommendations.append(
                "Consider taking summer courses to graduate sooner."
            )

        return recommendations

    def export_plan_with_validation(
        self,
        plan: List[SemesterPlan],
        validation: ValidationResult
    ) -> List[Dict]:
        """
        Export a plan with validation notes (good for Excel)

        Args:
            plan: The course plan
            validation: Validation results

        Returns:
            List[Dict]: Plan data with status info
        """
        plan_data = self.generator.export_to_dict()

        # add validation status to each semester
        for i, sem_data in enumerate(plan_data):
            if i < len(plan):
                semester = plan[i]
                # check for errors in this semester
                semester_errors = [
                    err for err in validation.errors
                    if semester.get_term_key() in err
                ]
                sem_data["Status"] = "ERROR" if semester_errors else "OK"
                sem_data["Notes"] = "; ".join(semester_errors) if semester_errors else ""

        return plan_data

    def export_plan_to_course_list(
        self,
        plan: List[SemesterPlan],
        validation: ValidationResult
    ) -> List[Dict]:
        """
        Export a plan as a flat course list (for ExcelExporter)

        Args:
            plan: The course plan
            validation: Validation results

        Returns:
            List[Dict]: Flat list of courses with validation status
        """
        courses = []
        for semester in plan:
            # Check for errors in this semester
            semester_errors = [
                err for err in validation.errors
                if semester.get_term_key() in err
            ]
            semester_status = "ERROR" if semester_errors else "OK"

            for course in semester.courses:
                # Check for course-specific errors
                course_errors = [
                    err for err in validation.errors
                    if course.code in err and semester.get_term_key() in err
                ]
                course_status = "ERROR" if course_errors else semester_status

                courses.append({
                    'semester': semester.get_term_key(),
                    'course_code': course.code,
                    'course_name': course.title,
                    'credits': course.credits,
                    'prerequisites': ', '.join(self.repository.get_prerequisites_for(course.code)),
                    'status': course_status
                })

        return courses

    def check_graduation_requirements(
        self,
        plan: List[SemesterPlan],
        required_courses: List[str],
        min_total_credits: int = 30
    ) -> Tuple[bool, List[str]]:
        """
        Check if a plan meets graduation requirements

        Args:
            plan: The course plan
            required_courses: Required courses
            min_total_credits: Minimum total credits needed

        Returns:
            Tuple[bool, List[str]]: (does it meet requirements?, any issues?)
        """
        issues = []

        # check total credits
        total_credits = sum(sem.total_credits for sem in plan)
        if total_credits < min_total_credits:
            issues.append(
                f"Only {total_credits} credits but need at least {min_total_credits}"
            )

        # check required courses
        scheduled_courses = set()
        for semester in plan:
            for course in semester.courses:
                scheduled_courses.add(course.code)

        missing_courses = [c for c in required_courses if c not in scheduled_courses]
        if missing_courses:
            issues.append(f"Missing required courses: {', '.join(missing_courses)}")

        return len(issues) == 0, issues

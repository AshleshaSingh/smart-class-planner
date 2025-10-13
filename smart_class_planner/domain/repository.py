class Repository:
    """Central storage and retrieval interface for domain entities."""

    def __init__(self):
        self.courses = {}
        self.prerequisites = []
        self.offerings = []
        self.study_plan = None

    # Courses
    def add_course(self, course):
        """Add a course to the repository."""
        if course.code not in self.courses:
            self.courses[course.code] = course

    # Prerequisites
    def add_prerequisite(self, prerequisite):
        """Add a prerequisite relationship."""
        self.prerequisites.append(prerequisite)

    def get_prerequisites_for(self, course_code: str):
        """Return a list of prerequisite course codes for a given course."""
        return [
            p.prereq_course_code for p in self.prerequisites
            if p.course_code == course_code
        ]

    # Offerings
    def add_offering(self, offering):
        """Add a course offering."""
        self.offerings.append(offering)

    # Study Plan Sequence
    def set_study_plan(self, study_plan):
        """Set the study plan sequence."""
        self.study_plan = study_plan

    def get_courses_for_term(self, term: str):
        """Return courses for a given term from the study plan."""
        if self.study_plan:
            return self.study_plan.get_courses_for_term(term)
        return []

    # Checking if prereqs for a course are complete before a term (courses scheduled previously are considered complete)
    def prerequisites_satisfied(self, term: str, course_code: str):
        if not self.study_plan:
            return False

        prereqs = self.get_prerequisites_for(course_code)
        if not prereqs:
            return True  # no prerequisites

        completed_courses = []
        for t, courses in self.study_plan.plan.items():
            if t == term:
                break
            completed_courses.extend([c.code for c in courses])

        return all(pr in completed_courses for pr in prereqs)

    def __repr__(self):
        return (
            "Repository(\n"
            f"  Courses={len(self.courses)}, "
            f"Prerequisites={len(self.prerequisites)}, "
            f"Offerings={len(self.offerings)}, "
            f"StudyPlan={self.study_plan.name if self.study_plan else 'None'}\n)"
        )
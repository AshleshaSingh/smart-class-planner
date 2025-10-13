class StudyPlanSequence:
    """Represents a structured plan of courses for a study track."""

    def __init__(self, name: str):
        self.name = name
        self.plan = {}  # List of terms and their courses

    def add_semester(self, term: str, courses: list):
        """Add a list of courses to a given term."""
        self.plan[term] = courses

    def get_courses_for_term(self, term: str):
        """Return courses scheduled for the given term."""
        return self.plan.get(term, [])

    def __repr__(self):
        return f"StudyPlanSequence({self.name})"
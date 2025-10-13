class Offering:
    """Represents a specific term when a course is offered."""

    def __init__(self, course_code: str, term: str, year: int):
        self.course_code = course_code
        self.term = term    # 'Fall', 'Spring', 'Summer'
        self.year = year

    def __repr__(self):
        return f"{self.course_code} offered {self.term} {self.year}"
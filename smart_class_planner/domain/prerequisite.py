class Prerequisite:
    """Represents prerequisite relationships between courses."""

    def __init__(self, course_code: str, prereq_course_code: str):
        self.course_code = course_code
        self.prereq_course_code = prereq_course_code

    def __repr__(self):
        return f"{self.course_code} requires {self.prereq_course_code}"
class Course:
    """Represents an individual course with details about prerequisites and offerings."""

    def __init__(self, code: str, title: str, credits: int, track=None):
        self.code = code
        self.title = title
        self.credits = credits
        self.track = track
        self.prerequisites = []     # List of prerequisite courses
        self.offerings = []     # List of when offered

    def add_prerequisite(self, prereq):
        """Adds a prerequisite relationship."""
        self.prerequisites.append(prereq)

    def add_offering(self, offering):
        """Adds a semester offering for the course."""
        self.offerings.append(offering)

    def __repr__(self):
        return f"{self.code} ({self.credits} cr)"
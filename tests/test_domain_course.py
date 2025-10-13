from smart_class_planner.domain.course import Course

def test_domain_course():
    c = Course("CPSC 1010", "Intro to CS", 3)
    print(c)

    # Testing adding prerequisites and offerings
    c.add_prerequisite("MATH 1010")
    c.add_prerequisite("CPSC 1000")
    c.add_offering("Fall 2025")
    c.add_offering("Summer 2026")
    c.add_offering("Fall 2026")

    print("Prerequisites:", c.prerequisites)
    print("Offerings:", c.offerings)
    print(c)

if __name__ == "__main__":
    test_domain_course()
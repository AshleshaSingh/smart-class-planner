from smart_class_planner.domain.prerequisite import Prerequisite

def test_domain_prereq():
    prereq = Prerequisite("CPSC 2000", "CPSC 1000")

    prereq2 = Prerequisite("CPSC 2000", "MATH 1010")

    print(prereq)
    print(prereq2)

if __name__ == "__main__":
    test_domain_prereq()
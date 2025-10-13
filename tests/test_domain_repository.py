# imports
from smart_class_planner.domain.course import Course
from smart_class_planner.domain.prerequisite import Prerequisite
from smart_class_planner.domain.offering import Offering
from smart_class_planner.domain.studyplansequence import StudyPlanSequence
from smart_class_planner.domain.repository import Repository

# Sample courses
c1 = Course("CPSC1010", "Intro to CS", 3)
c2 = Course("CPSC2010", "Advanced CS", 3)
c3 = Course("CPSC3010", "Machine Learning", 3)
c4 = Course("MATH1000", "Calculus I", 3)
c5 = Course("MATH2000", "Calculus II", 3)

# Sample prereqs
pr1 = Prerequisite("CPSC2010", "CPSC1010")
pr2 = Prerequisite("CPSC3010", "CPSC2010")
pr3 = Prerequisite("MATH2000", "MATH1000")

# Sample offerings
off1 = Offering("CPSC1010", "Fall", 2024)
off2 = Offering("CPSC2010", "Spring", 2025)
off3 = Offering("CPSC3010", "Fall", 2025)
off4 = Offering("MATH1000", "Fall", 2024)
off5 = Offering("MATH2000", "Spring", 2025)

# Sample study plan schedule
plan = StudyPlanSequence("Software Dev Track")
plan.add_semester("Fall 2024", [c1, c4])
plan.add_semester("Spring 2025", [c2, c5])
plan.add_semester("Fall 2025", [c3])

# Sample repo populated with objects created above
repo = Repository()
for c in [c1, c2, c3, c4, c5]:
    repo.add_course(c)

for p in [pr1, pr2, pr3]:
    repo.add_prerequisite(p)

for o in [off1, off2, off3, off4, off5]:
    repo.add_offering(o)

repo.set_study_plan(plan)

# Testing output

print("Repository Details:")
print(repo)

print("-----------------------------------------------------------")

print("Courses for Fall 2024:")
print(repo.get_courses_for_term("Fall 2024"))

print("\nCourses for Spring 2025:")
print(repo.get_courses_for_term("Spring 2025"))

print("\nCourses for Fall 2025:")
print(repo.get_courses_for_term("Fall 2025"))

print("-----------------------------------------------------------")

print("Prerequisites for CPSC2010:")
print(repo.get_prerequisites_for("CPSC2010"))

print("\nPrerequisites for CPSC3010")
print(repo.get_prerequisites_for("CPSC3010"))

print("-----------------------------------------------------------")

print("Check Prerequisites Satisfied")
print(f"CPSC1010 before Fall 2024? {repo.prerequisites_satisfied('Fall 2024','CPSC1010')}")
print(f"CPSC2010 before Spring 2025? {repo.prerequisites_satisfied('Spring 2025','CPSC2010')}")
print(f"CPSC3010 before Fall 2025? {repo.prerequisites_satisfied('Fall 2025','CPSC3010')}")
print(f"MATH2000 before Spring 2025? {repo.prerequisites_satisfied('Spring 2025','MATH2000')}")
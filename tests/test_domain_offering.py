from smart_class_planner.domain.offering import Offering

def test_domain_offering():
    
    offering = Offering("CPSC 1010", "Fall", 2025)
    
    print(offering)

if __name__ == "__main__":
    test_domain_offering()
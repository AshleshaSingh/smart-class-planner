"""
Main entry point for the Smart Class Planning Tool.
"""

from smart_class_planner.presentation.setup_wizard import SetupWizard

if __name__ == "__main__":
    app = SetupWizard()
    app.run()

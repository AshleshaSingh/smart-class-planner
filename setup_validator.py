"""
File: setup_validator.py
Author: Team Smart Class Planner
Date: 2025-10-07

Description:
    Unified Setup Validation Script for Smart Class Planning Tool
    --------------------------------------------------------------
    This script performs a complete verification of your environment
    and codebase before running Smart Class Planner.

    It checks:
      • Python version (>=3.12)
      • Tkinter GUI backend availability
      • Core libraries (from requirements.txt)
      • Successful import of all project modules

Usage:
    python setup_validator.py
"""

import sys
import os
import importlib
import traceback


def check_python_version():
    print("Checking Python version...")
    version = sys.version.split()[0]
    print(f"   Detected Python {version}")
    if not version.startswith("3.12"):
        print("   Recommended: Python 3.12.x (with Tkinter support)\n")
        return False
    print("   Python version is correct.\n")
    return True


def check_tkinter():
    print("Checking Tkinter installation...")
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()  # suppress window
        print("   Tkinter is installed and GUI backend works.\n")
        return True
    except ImportError:
        print("   Tkinter not found. Please install Python 3.12 from python.org.\n")
        return False
    except Exception as e:
        print(f"   Tkinter found but failed to open window: {e}\n")
        return False


def check_dependencies():
    print("Checking dependencies (requirements.txt)...")
    req_path = "requirements.txt"
    missing = []
    if not os.path.exists(req_path):
        print("   No requirements.txt found. Skipping dependency check.\n")
        return True

    with open(req_path, "r") as req_file:
        required_libs = [
            line.strip().split("==")[0]
            for line in req_file
            if line.strip() and not line.startswith("#")
        ]

    for lib in required_libs:
        if importlib.util.find_spec(lib) is None:
            missing.append(lib)
            print(f"   Missing dependency: {lib}")
        else:
            print(f"   {lib} is installed.")

    print()
    return len(missing) == 0


def check_all_modules():
    print("Checking all project modules under smart_class_planner/...")

    failed_modules = []
    package_root = "smart_class_planner"

    for root, _, files in os.walk(package_root):
        for f in files:
            if f.endswith(".py") and not f.startswith("__"):
                mod = os.path.join(root, f).replace("/", ".").replace("\\", ".")[:-3]
                try:
                    importlib.import_module(mod)
                    print(f"   {mod} imported successfully.")
                except Exception as e:
                    failed_modules.append(mod)
                    print(f"   {mod} failed: {e}")
                    traceback.print_exc(limit=1)

    print()
    return len(failed_modules) == 0


def run_all_checks():
    print("\nSmart Class Planner – Full Setup Validator")
    print("==========================================\n")

    results = {
        "Python": check_python_version(),
        "Tkinter": check_tkinter(),
        "Dependencies": check_dependencies(),
        "Modules": check_all_modules(),
    }

    print("Validation Summary")
    print("----------------------")
    for key, value in results.items():
        status = "OK" if value else "Failed"
        print(f"{key:<15}: {status}")

    if all(results.values()):
        print("\nEnvironment and project setup look perfect! You’re ready to run Smart Class Planner.\n")
        sys.exit(0)
    else:
        print("\nSome checks failed. Please fix the issues above before proceeding.\n")
        sys.exit(1)


if __name__ == "__main__":
    run_all_checks()

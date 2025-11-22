"""
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
import importlib.util
import traceback


def check_python_version():
    """
    Checks the installed Python version for compatibility.
    Accepts Python 3.12–3.14 as valid, warns if outside this range.
    """
    import sys

    print("Checking Python version...")
    version = sys.version.split()[0]
    print(f"   Detected Python {version}")

    try:
        major, minor, *_ = map(int, version.split("."))
    except ValueError:
        print("   Unable to parse Python version.\n")
        return False

    if major == 3 and 12 <= minor <= 14:
        print("   Python version is compatible (3.12–3.14).\n")
        return True
    elif major == 3 and minor < 12:
        print("   Older Python version detected. Please upgrade to 3.12+.\n")
        return False
    else:
        print("   Newer Python version detected; should work, but not fully tested.\n")
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
    """
    Cross-checks installed packages (via pip list) against requirements.txt.
    This avoids importlib issues on Python 3.14+ and handles alias names
    and version specifiers (==, >=, etc.).
    """
    import subprocess
    import sys
    import re

    print("Checking dependencies (requirements.txt)...")

    # Use the same Python that's running this script
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=freeze"],
        capture_output=True,
        text=True,
    )
    installed_lines = result.stdout.splitlines()
    installed_pkgs = {
        line.split("==")[0].strip().lower()
        for line in installed_lines
        if "==" in line
    }

    # Regex to grab the package name at the start of the requirement line
    name_pattern = re.compile(r"^\s*([A-Za-z0-9_.\-]+)")

    missing = []
    with open("requirements.txt") as reqs:
        for raw_line in reqs:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            match = name_pattern.match(line)
            if not match:
                continue  # skip weird lines

            pkg_name = match.group(1).lower()

            # map known aliases (import name != package name)
            alias_map = {
                "beautifulsoup4": "bs4",
                "pypdf": "pypdf",
            }
            alias = alias_map.get(pkg_name, pkg_name)

            if pkg_name in installed_pkgs or alias in installed_pkgs:
                print(f"   {pkg_name} is installed.")
            else:
                print(f"   Missing dependency: {pkg_name}")
                missing.append(pkg_name)

    if not missing:
        print("All dependencies verified.\n")
        return True
    else:
        print(f"Missing {len(missing)} dependencies: {', '.join(missing)}\n")
        return False

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

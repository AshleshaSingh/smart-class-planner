"""
Environment Check Script for Smart Class Planning Tool
-------------------------------------------------------
This script verifies that your local Python environment
is properly configured for GUI, data handling, and Excel export.
"""

import sys

def check_python_version():
    print("Checking Python version...")
    version = sys.version.split()[0]
    print(f"   Python version detected: {version}")
    if not version.startswith("3.12"):
        print("   Recommended version: Python 3.12.x (with Tkinter support)")
    else:
        print("   Correct version of Python detected.\n")

def check_tkinter():
    print("Checking Tkinter installation...")
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()  # don’t show a full window
        print("   Tkinter is installed and working (GUI backend available).\n")
    except ImportError:
        print("   Tkinter not found. Please install Python 3.12 from python.org.\n")
    except Exception as e:
        print(f"   Tkinter found but failed to open window: {e}\n")

def check_pandas_openpyxl():
    print("Checking data and Excel libraries...")
    try:
        import pandas
        import openpyxl
        print(f"   pandas v{pandas.__version__}, openpyxl v{openpyxl.__version__} loaded successfully.\n")
    except ImportError as e:
        print(f"   Missing library: {e.name}. Please install with `pip install -r requirements.txt`.\n")

def check_bs4_requests():
    print("Checking web scraping libraries...")
    try:
        import requests
        from bs4 import BeautifulSoup
        print("   requests and BeautifulSoup4 are available.\n")
    except ImportError as e:
        print(f"   Missing library: {e.name}. Please install with `pip install -r requirements.txt`.\n")

def run_all_checks():
    print("\nSmart Class Planner Environment Verification\n" + "-"*55)
    check_python_version()
    check_tkinter()
    check_pandas_openpyxl()
    check_bs4_requests()
    print("Environment check complete.\n")

if __name__ == "__main__":
    run_all_checks()

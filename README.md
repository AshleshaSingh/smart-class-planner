# Smart Class Planning Tool

**A Python-based academic advising application** that automates course planning, prerequisite validation, and semester scheduling for students and faculty.

This tool generates a recommended study plan in Excel format by analyzing DegreeWorks data, graduate study plans, and 4-year course schedules.
It also validates prerequisite chains using a web crawler that extracts information from CPSC course descriptions.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Project Structure](#project-structure)
5. [Setup Instructions](#setup-instructions)
6. [Environment Verification](#environment-verification)
7. [Running the Application](#running-the-application)
8. [Team Roles](#team-roles)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [References](#references)

---

## Overview

Academic advising and degree planning often require significant manual effort from both students and faculty.
This **Smart Class Planning Tool** streamlines that process by automating:

* Course prerequisite validation
* Semester-wise plan generation
* Exporting plans to Excel
* Providing a simple, interactive GUI (Tkinter)

The software follows a **layered architecture** for modularity, scalability, and maintainability.

---

## Features

| Category                       | Description                                                            |
| ------------------------------ | ---------------------------------------------------------------------- |
| **Course Planning**         | Generates semester-wise course recommendations until graduation        |
| **Prerequisite Validation** | Detects prerequisite issues using a web crawler and course catalog     |
| **Input Parsing**          | Parses DegreeWorks reports, Graduate Study Plans, and 4-year schedules |
| **Smart Logic**             | Suggests alternatives for unavailable offerings                        |
| **GUI**                     | Simple Tkinter interface for file selection and output                 |
| **Output**                  | Exports results to Excel (`.xlsx`) format                              |
| **Architecture**            | Layered + MVC principles for maintainability                           |
| **Testing**                 | Supports `pytest`-based unit and integration tests                     |

---

## System Requirements

| Requirement       | Minimum                                                          |
| ----------------- | ---------------------------------------------------------------- |
| **OS**            | macOS, Windows, or Linux                                         |
| **Python**        | 3.12.x (recommended)                                             |
| **Pip**           | v23+                                                             |
| **Libraries**     | pandas, openpyxl, beautifulsoup4, requests, tkintertable, pytest |
| **GUI Framework** | Tkinter (included in most official Python distributions)         |

---

### Important Cross-Platform Note

> **Tkinter must be available in your Python installation to run the GUI.**
>
>  **macOS:**
>   The **Homebrew build of Python 3.13** does *not* include Tkinter.
>   Install **Python 3.12 or newer** using the official macOS installer from [python.org](https://www.python.org/downloads/macos/).
>
>  **Windows:**
>   Tkinter is included by default with all standard Python installers.
>
>  **Linux (Ubuntu/Debian):**
>   Run `sudo apt install python3-tk` to add Tkinter support.

---

##  Project Structure

```
smart-class-planner/
├── smart_class_planner/
│   ├── __init__.py
│   ├── main.py                         # Entry point
│   ├── presentation/                   # GUI Layer (Tkinter)
│   │   ├── __init__.py
│   │   └── setup_wizard.py
│   ├── application/                    # Core business logic
│   │   ├── __init__.py
│   │   ├── plan_generator.py
│   │   ├── validator.py
│   │   └── offerings_handler.py
│   ├── domain/                         # Data models & repository
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── plan_sequence.py
│   ├── infrastructure/                 # External data connectors
│   │   ├── __init__.py
│   │   ├── abstract_parser.py
│   │   ├── pdf_parser.py
│   │   ├── study_plan_parser.py
│   │   ├── scraper.py
│   │   └── excel_exporter.py
│   └── config/
│       ├── __init__.py
│       ├── constants.py
│       └── settings.json
│
├── tests/
│   ├── test_repository.py
│   ├── test_plan_generator.py
│   └── test_validator.py
│
├── check_env.py                        # Environment verification script
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Setup Instructions

### Step 1 – Clone the Repository

```bash
git clone https://github.com/<your-username>/smart-class-planner.git
cd smart-class-planner
```

---

### Step 2 – Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# OR
venv\Scripts\activate         # Windows
```

---

### Step 3 – Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 – Verify the Environment

Run the included diagnostic script:

```bash
python check_env.py
```

You should see all green checkmarks confirming:

* Python 3.12+
* Tkinter GUI works
* pandas, openpyxl, requests, and BeautifulSoup4 installed

---

## Environment Verification (Manual)

Quick manual check:

```bash
python --version
python -m tkinter
python -c "import pandas, openpyxl, bs4, requests; print('All good!')"
```

If a blank Tkinter window appears and no ImportErrors occur, you’re ready!

---

## Running the Application

Launch the GUI:

```bash
python -m smart_class_planner.main
```

The application window appears with:

* **Upload DegreeWorks PDF**
* **Generate Plan** buttons
* Recommended plan exported as an Excel file

---

## Testing

Run all unit tests:

```bash
pytest
```

Example output:

```
=================== test session starts ===================
collected 5 items
tests/test_repository.py .....
==================== 5 passed in 0.12s =====================
```

---

## Troubleshooting

| Issue                         | Likely Cause                          | Solution                                                 |
| ----------------------------- | ------------------------------------- | -------------------------------------------------------- |
| `_tkinter` module not found | Using Homebrew Python (3.13) on macOS | Install Python 3.12 from python.org                      |
| Missing packages            | venv not activated                    | `source venv/bin/activate` → reinstall deps              |
| GUI won’t appear           | Running over SSH/headless session     | Run locally with display access                          |
| VS Code import errors      | Wrong interpreter                     | Use Command Palette → **Select Interpreter** → venv path |

---

## References

* **Python Tkinter Docs:** [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
* **PEP 8 Style Guide:** [https://peps.python.org/pep-0008/](https://peps.python.org/pep-0008/)
* **pytest Documentation:** [https://docs.pytest.org/](https://docs.pytest.org/)
* **BeautifulSoup4 Docs:** [https://www.crummy.com/software/BeautifulSoup/bs4/doc/](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

## Summary

You’re fully set when:

1. `python --version` → 3.12.x
2. `python -m tkinter` opens a blank window
3. `python check_env.py` passes all checks
4. `python -m smart_class_planner.main` launches the GUI


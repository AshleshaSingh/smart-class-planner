# Smart Class Planner

A Python-based academic advising application that automates course planning, prerequisite validation, and semester scheduling.

---

## Purpose

The Smart Class Planner streamlines academic advising by automating course planning for students and faculty. The application:

- **Generates semester-by-semester course recommendations** from current progress until graduation
- **Validates prerequisite requirements** by web-crawling the university course catalog
- **Analyzes multiple data sources**: DegreeWorks reports, graduate study plans, and 4-year course schedules
- **Exports optimized study plans** to Excel format for easy review and modification
- **Provides a user-friendly GUI** for file upload, plan generation, and export

This tool eliminates manual effort in degree planning, reduces prerequisite conflicts, and helps students graduate on schedule.

---

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: Version 3.12 or newer (required)
- **Disk Space**: 500 MB minimum
- **Display**: GUI-capable environment

### Required Software

**Python 3.12+** with the following packages (auto-installed via requirements.txt):
- `pandas` - Data analysis
- `openpyxl` - Excel file generation
- `beautifulsoup4` - Web scraping
- `requests` - HTTP requests
- `PyPDF2` or `pypdf` - PDF parsing
- `tkinter` - GUI framework (included with Python)
- `pytest` - Testing framework

### Platform-Specific Notes

**Windows**: Tkinter included by default with Python from python.org

**macOS**:
- Homebrew Python 3.13 lacks Tkinter support
- Install Python 3.12+ from [python.org](https://www.python.org/downloads/macos/)
- Verify: `python -m tkinter`

**Linux (Ubuntu/Debian)**:
```bash
sudo apt install python3-tk python3-pip
```

---

## Download

### Option 1: Source Code (Developers)

**Clone from GitHub:**
```bash
git clone https://github.com/AshleshaSingh/smart-class-planner.git
cd smart-class-planner
```

**Or download ZIP:**
1. Visit [https://github.com/AshleshaSingh/smart-class-planner](https://github.com/AshleshaSingh/smart-class-planner)
2. Click "Code" → "Download ZIP"
3. Extract and navigate to folder

### Option 2: Windows Installer (End Users)

Download the pre-built installer:
- **File**: `SmartClassPlanner_Setup_1.0.0.exe`
- **Location**: `installer_output/` folder in repository or submission package
- **Includes**: Standalone executable with all dependencies bundled (no Python required)

---

## Build/Configuration/Installation/Deployment


### Installation Method A: Install via Windows Installer

**For End Users (No Python Required):**

1. Run `SmartClassPlanner_Setup_1.0.0.exe`
2. Follow installation wizard
3. Choose installation directory (default: `C:\Program Files\Smart Class Planner`)
4. Create desktop shortcut (optional)
5. Click "Install"

**Launch:** Use desktop shortcut or Start Menu → Smart Class Planner

**Uninstall:** Windows Settings → Apps → Smart Class Planner → Uninstall

---

### Installation Method B: Run from Source Code

**1. Verify Python:**
```bash
python --version  # Should be 3.12+
```

**2. Create Virtual Environment:**
```bash
python -m venv venv

# Activate:
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
```

**3. Install Dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Validate Setup:**
```bash
python setup_validator.py
# Should show: ✓ Python version, ✓ Tkinter, ✓ All packages installed
```

**5. Run Application:**
```bash
python -m smart_class_planner.main
```

---

### Installation Method C: Build Windows Installer

**Prerequisites:**
- Windows 10/11
- Python 3.12+
- [Inno Setup 6](https://jrsoftware.org/isinfo.php)

**Build Steps:**
```bash
cd smart-class-planner
build_installer.bat
```

**What happens:**
1. Creates/activates virtual environment
2. Installs dependencies
3. Runs PyInstaller to create standalone executable
4. Runs Inno Setup to create installer

**Output:**
- Executable: `dist\SmartClassPlanner\SmartClassPlanner.exe`
- Installer: `installer_output\SmartClassPlanner_Setup_1.0.0.exe`

---

## Usage

### Starting the Application

**From Source:**
```bash
# Activate virtual environment first
python -m smart_class_planner.main
```

**From Installer:**
- Double-click desktop shortcut or launch from Start Menu

### Workflow

**Step 1: Upload Files**

Click upload buttons to select:
- **DegreeWorks PDF**: Academic audit showing completed courses
- **Graduate Study Plan**: Program requirements document
- **4-Year Schedule**: Course offering schedule

**Step 2: Generate Plan**

1. Click "Generate Course Plan"
2. Application processes files and validates prerequisites
3. View generated semester-by-semester plan

**Step 3: Export to Excel**

1. Click "Export to Excel"
2. Choose save location
3. Excel file contains:
   - Semester Plan (courses by semester)
   - Course Details (prerequisites, descriptions)
   - Progress Tracker (completion status)

**Step 4: Review and Adjust**

- Review plan with advisor
- Make adjustments if needed
- Re-upload files and regenerate as needed

### GUI Buttons

- **Upload Required Files**: Select input files (DegreeWorks, Study Plan, Schedule)
- **Generate Course Plan**: Process files and create semester plan
- **Export to Excel**: Save plan to .xlsx file
- **Clear All**: Reset application and remove loaded files

### Example Output

Generated plan shows:
```
Fall 2025:    CS 530, CS 540, CS 550 (9 credits)
Spring 2026:  CS 560, CS 570 (6 credits)
Fall 2026:    CS 580, CS 590 (6 credits)
Graduation:   December 2026
```

---

## Testing

Run tests:
```bash
pytest                                              # All tests
pytest --cov=smart_class_planner --cov-report=html  # With coverage
```

---

## Project Structure

```
smart-class-planner/
├── smart_class_planner/       # Main application
│   ├── main.py               # Entry point
│   ├── presentation/         # GUI (Tkinter)
│   ├── application/          # Business logic
│   ├── domain/               # Data models
│   └── infrastructure/       # Parsers & scrapers
├── tests/                    # Test suite
├── docs/                     # Documentation
├── requirements.txt          # Dependencies
├── build_installer.bat       # Build script
├── installer.iss            # Inno Setup config
└── smart_class_planner.spec # PyInstaller config
```

---

## References

- **GitHub Repository**: [https://github.com/AshleshaSingh/smart-class-planner](https://github.com/AshleshaSingh/smart-class-planner)
- **Python Docs**: [https://docs.python.org/3/](https://docs.python.org/3/)
- **PyInstaller**: [https://pyinstaller.org/](https://pyinstaller.org/)
- **Inno Setup**: [https://jrsoftware.org/ishelp/](https://jrsoftware.org/ishelp/)

---

## Quick Start

**Developers:**
```bash
git clone https://github.com/AshleshaSingh/smart-class-planner.git
cd smart-class-planner
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python setup_validator.py
python -m smart_class_planner.main
```

**End Users (Windows):**
1. Download `SmartClassPlanner_Setup_1.0.0.exe`
2. Run installer
3. Launch from Start Menu

---

Developed by Smart Class Planner Team | CS Software Design & Development | Fall 2025

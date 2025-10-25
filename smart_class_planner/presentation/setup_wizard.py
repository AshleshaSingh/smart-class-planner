"""
Description:
    Enhanced Tkinter-based GUI for Smart Class Planning Tool
    Implements presentation layer following layered architecture
    
Features:
    - Modern tabbed interface
    - DegreeWorks PDF upload (shows completed courses)
    - Graduate Study Plan Excel upload (program requirements)
    - 4-Year Course Schedule Excel upload (when courses are offered)
    - Results display with semester-by-semester plan
    - Excel export functionality
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys


class SetupWizard:
    """Enhanced Tkinter-based GUI for Smart Class Planning Tool."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Class Planning Tool - CSU")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # File paths storage
        self.degreeworks_pdf = None  # Contains completed courses
        self.study_plan_excel = None  # Contains required courses for graduation
        self.schedule_excel = None    # Contains when courses are offered (Fall/Spring/Summer)
        
        # Generated plan data
        self.generated_plan = None
        
        # Color scheme matching academic theme
        self.bg_color = "#f0f4f8"
        self.primary_color = "#1e40af"  # CSU Blue
        self.secondary_color = "#64748b"
        self.success_color = "#059669"
        self.error_color = "#dc2626"
        self.warning_color = "#f59e0b"
        
        self.root.configure(bg=self.bg_color)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the complete UI layout."""
        self._create_header()
        self._create_main_content()
        self._create_footer()

    def _create_header(self):
        """Create application header with branding."""
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Main title
        title_label = tk.Label(
            header_frame,
            text="🎓 Smart Class Planning Tool",
            font=("Segoe UI", 26, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=(15, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Automated Course Planning • Prerequisite Validation • Semester Scheduling",
            font=("Segoe UI", 10),
            bg=self.primary_color,
            fg="#93c5fd"
        )
        subtitle_label.pack()

    def _create_main_content(self):
        """Create main content area with notebook tabs."""
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', 
                       padding=[20, 12], 
                       font=('Segoe UI', 10, 'bold'),
                       background='#e2e8f0')
        style.map('TNotebook.Tab',
                 background=[('selected', 'white')],
                 foreground=[('selected', self.primary_color)])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create tabs
        self.setup_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.results_tab = tk.Frame(self.notebook, bg=self.bg_color)
        
        self.notebook.add(self.setup_tab, text="  📁 Setup & Upload  ")
        self.notebook.add(self.results_tab, text="  📋 Course Plan  ")
        
        # Build tab content
        self._build_setup_tab()
        self._build_results_tab()

    def _build_setup_tab(self):
        """Build file upload interface."""
        # Create scrollable container
        canvas = tk.Canvas(self.setup_tab, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.setup_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        container = tk.Frame(scrollable_frame, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Instructions panel
        self._create_instructions_panel(container)
        
        # File upload section
        upload_section = tk.Frame(container, bg=self.bg_color)
        upload_section.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # 1. DegreeWorks PDF Upload
        self._create_file_upload_card(
            upload_section,
            "1 DegreeWorks Audit Report (PDF)",
            "Upload your DegreeWorks audit report showing:\n"
            "  • Courses you have already completed\n"
            "  • Courses currently in progress\n"
            "  • Remaining courses needed for graduation",
            self.browse_degreeworks,
            "degreeworks",
            required=True
        )
        
        # 2. Graduate Study Plan Excel
        self._create_file_upload_card(
            upload_section,
            "2 Graduate Study Plan (Excel)",
            "Upload the official graduate study plan containing:\n"
            "  • All required courses for your program\n"
            "  • Course codes and names\n"
            "  • Credit hours for each course\n"
            "  • Recommended semester sequence",
            self.browse_study_plan,
            "study_plan",
            required=True
        )
        
        # 3. 4-Year Course Schedule
        self._create_file_upload_card(
            upload_section,
            "3 4-Year Course Schedule (Excel)",
            "Upload the 4-year course offering schedule showing:\n"
            "  • Which courses are offered in Fall semester\n"
            "  • Which courses are offered in Spring semester\n"
            "  • Which courses are offered in Summer semester\n"
            "  • This helps avoid planning for unavailable courses",
            self.browse_schedule,
            "schedule",
            required=True
        )
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_instructions_panel(self, parent):
        """Create the instructions/info panel."""
        info_frame = tk.Frame(parent, bg="white", relief=tk.SOLID, borderwidth=2)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Header
        header_frame = tk.Frame(info_frame, bg="#eff6ff")
        header_frame.pack(fill=tk.X)
        
        header_label = tk.Label(
            header_frame,
            text="📌 How This Tool Works",
            font=("Segoe UI", 12, "bold"),
            bg="#eff6ff",
            fg=self.primary_color,
            anchor="w",
            padx=20,
            pady=12
        )
        header_label.pack(fill=tk.X)
        
        # Instructions content
        instructions_text = """
The Smart Class Planning Tool automates your course planning by:

1. Analyzing your DegreeWorks to see what courses you've completed
2. Comparing against your program's study plan to find remaining requirements
3. Checking the 4-year schedule to see when courses are offered
4. Validating prerequisites using web-scraped course descriptions
5. Generating a semester-by-semester plan until graduation

STEP 1: Upload your three required files below
STEP 2: Click "Generate Course Plan" at the bottom
STEP 3: Review your personalized plan in the "Course Plan" tab
STEP 4: Export to Excel for advising appointments
        """
        
        instructions_label = tk.Label(
            info_frame,
            text=instructions_text,
            font=("Segoe UI", 9),
            bg="white",
            fg="#334155",
            justify=tk.LEFT,
            anchor="w",
            padx=20,
            pady=15
        )
        instructions_label.pack(fill=tk.X)

    def _create_file_upload_card(self, parent, title, description, command, file_key, required=False):
        """Create a styled file upload card."""
        # Card frame
        card = tk.Frame(parent, bg="white", relief=tk.RAISED, borderwidth=2)
        card.pack(fill=tk.X, pady=10)
        
        # Content padding
        content = tk.Frame(card, bg="white")
        content.pack(fill=tk.BOTH, padx=20, pady=18)
        
        # Header section
        header_frame = tk.Frame(content, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_text = title
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#1e293b",
            anchor="w"
        )
        title_label.pack(side=tk.LEFT)
        
        if required:
            req_badge = tk.Label(
                header_frame,
                text="REQUIRED",
                font=("Segoe UI", 7, "bold"),
                bg="#fee2e2",
                fg="#991b1b",
                padx=8,
                pady=3
            )
            req_badge.pack(side=tk.LEFT, padx=10)
        
        # Description
        desc_label = tk.Label(
            content,
            text=description,
            font=("Segoe UI", 9),
            bg="white",
            fg=self.secondary_color,
            anchor="w",
            wraplength=800,
            justify=tk.LEFT
        )
        desc_label.pack(fill=tk.X, pady=(0, 12))
        
        # Separator line
        separator = tk.Frame(content, bg="#e5e7eb", height=1)
        separator.pack(fill=tk.X, pady=(0, 12))
        
        # Button and status row
        action_frame = tk.Frame(content, bg="white")
        action_frame.pack(fill=tk.X)
        
        # Browse button
        browse_btn = tk.Button(
            action_frame,
            text="📂 Browse Files",
            command=command,
            bg=self.primary_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor="hand2",
            activebackground="#1e3a8a"
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Status label
        status_label = tk.Label(
            action_frame,
            text="⭕ No file selected",
            font=("Segoe UI", 9),
            bg="white",
            fg=self.secondary_color
        )
        status_label.pack(side=tk.LEFT, padx=20)
        
        # Store reference
        setattr(self, f"{file_key}_status", status_label)

    def _build_results_tab(self):
        """Build results display interface."""
        container = tk.Frame(self.results_tab, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        header_frame = tk.Frame(container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        header_label = tk.Label(
            header_frame,
            text="📋 Your Personalized Course Plan",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg="#1e293b"
        )
        header_label.pack(side=tk.LEFT)
        
        # Results display area
        results_container = tk.Frame(container, bg="white", relief=tk.SOLID, borderwidth=2)
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(results_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        self.results_text = tk.Text(
            results_container,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            bg="white",
            fg="#1e293b",
            padx=25,
            pady=25,
            relief=tk.FLAT,
            spacing1=2,
            spacing3=2
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)
        
        # Configure text tags for styling
        self.results_text.tag_configure("header", font=("Consolas", 11, "bold"), foreground="#1e40af")
        self.results_text.tag_configure("semester", font=("Consolas", 10, "bold"), foreground="#059669")
        self.results_text.tag_configure("course", font=("Consolas", 10), foreground="#334155")
        self.results_text.tag_configure("warning", font=("Consolas", 9), foreground="#f59e0b")
        self.results_text.tag_configure("error", font=("Consolas", 9), foreground="#dc2626")
        
        # Initial message
        welcome_msg = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    SMART CLASS PLANNING TOOL                             ║
║                         Course Plan Generator                            ║
╚══════════════════════════════════════════════════════════════════════════╝

Welcome! Your personalized course plan will appear here after generation.

📚 WHAT THIS TOOL DOES:

   ✓ Parses your DegreeWorks PDF to identify completed courses
   ✓ Analyzes the graduate study plan to find remaining requirements
   ✓ Checks the 4-year schedule for course availability
   ✓ Validates prerequisites by scraping course catalog
   ✓ Detects conflicts and suggests alternatives
   ✓ Generates a semester-by-semester plan to graduation


🎯 TO GET STARTED:

   1. Go to the "Setup & Upload" tab
   2. Upload all THREE required files:
      • DegreeWorks PDF (your completed courses)
      • Graduate Study Plan Excel (program requirements)
      • 4-Year Schedule Excel (when courses are offered)
   3. Click "Generate Course Plan" button at the bottom
   4. Your plan will appear here automatically


💡 TIPS:

   • Make sure your DegreeWorks PDF is current and complete
   • Verify the study plan matches your specific program
   • Check that the schedule covers the correct academic years
   • Export your plan to Excel for easy sharing with advisors


Ready to plan your academic future? Let's get started! 🚀
        """
        self.results_text.insert("1.0", welcome_msg)
        self.results_text.config(state=tk.DISABLED)

    def _create_footer(self):
        """Create footer with action buttons."""
        footer_frame = tk.Frame(self.root, bg="white", height=90, relief=tk.RAISED, borderwidth=2)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        button_container = tk.Frame(footer_frame, bg="white")
        button_container.pack(expand=True)
        
        # Generate Plan button (primary action)
        generate_btn = tk.Button(
            button_container,
            text="🚀 Generate Course Plan",
            command=self.generate_plan,
            bg=self.success_color,
            fg="white",
            font=("Segoe UI", 13, "bold"),
            relief=tk.FLAT,
            padx=40,
            pady=15,
            cursor="hand2",
            activebackground="#047857"
        )
        generate_btn.pack(side=tk.LEFT, padx=8)
        
        # Export button
        export_btn = tk.Button(
            button_container,
            text="💾 Export to Excel",
            command=self.export_to_excel,
            bg=self.primary_color,
            fg="white",
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=28,
            pady=15,
            cursor="hand2",
            activebackground="#1e3a8a"
        )
        export_btn.pack(side=tk.LEFT, padx=8)
        
        # Clear button
        clear_btn = tk.Button(
            button_container,
            text="🗑️ Clear All",
            command=self.clear_all_data,
            bg=self.secondary_color,
            fg="white",
            font=("Segoe UI", 11),
            relief=tk.FLAT,
            padx=28,
            pady=15,
            cursor="hand2",
            activebackground="#475569"
        )
        clear_btn.pack(side=tk.LEFT, padx=8)

    # ==================== EVENT HANDLERS ====================
    
    def browse_degreeworks(self):
        """Handle DegreeWorks PDF file selection."""
        file_path = filedialog.askopenfilename(
            title="Select DegreeWorks PDF Report",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.degreeworks_pdf = file_path
            filename = Path(file_path).name
            self.degreeworks_status.config(
                text=f"✅ {filename}",
                fg=self.success_color,
                font=("Segoe UI", 9, "bold")
            )
            messagebox.showinfo(
                "File Loaded",
                f"✓ DegreeWorks PDF loaded successfully!\n\n"
                f"File: {filename}\n\n"
                f"This file will be parsed to identify your completed courses."
            )

    def browse_study_plan(self):
        """Handle Study Plan Excel file selection."""
        file_path = filedialog.askopenfilename(
            title="Select Graduate Study Plan (Excel)",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.study_plan_excel = file_path
            filename = Path(file_path).name
            self.study_plan_status.config(
                text=f"✅ {filename}",
                fg=self.success_color,
                font=("Segoe UI", 9, "bold")
            )
            messagebox.showinfo(
                "File Loaded",
                f"✓ Graduate Study Plan loaded successfully!\n\n"
                f"File: {filename}\n\n"
                f"This file contains your program's required courses."
            )

    def browse_schedule(self):
        """Handle Course Schedule Excel file selection."""
        file_path = filedialog.askopenfilename(
            title="Select 4-Year Course Schedule (Excel)",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.schedule_excel = file_path
            filename = Path(file_path).name
            self.schedule_status.config(
                text=f"✅ {filename}",
                fg=self.success_color,
                font=("Segoe UI", 9, "bold")
            )
            messagebox.showinfo(
                "File Loaded",
                f"✓ 4-Year Course Schedule loaded successfully!\n\n"
                f"File: {filename}\n\n"
                f"This file shows when courses are offered each semester."
            )

    def generate_plan(self):
        """
        Generate course plan using uploaded files.
        Integrates with application layer components.
        """
        # Validate all required files are uploaded
        missing_files = []
        if not self.degreeworks_pdf:
            missing_files.append("• DegreeWorks PDF")
        if not self.study_plan_excel:
            missing_files.append("• Graduate Study Plan Excel")
        if not self.schedule_excel:
            missing_files.append("• 4-Year Course Schedule Excel")
        
        if missing_files:
            messagebox.showwarning(
                "Missing Required Files",
                "Please upload all required files before generating a plan:\n\n" +
                "\n".join(missing_files) + "\n\n" +
                "All three files are necessary for accurate course planning."
            )
            self.notebook.select(0)  # Switch to setup tab
            return
        
        # Integrate with application layer
        from smart_class_planner.application.planner import IntegratedPlanner
        from smart_class_planner.infrastructure.pdf_parser import PDFParser
        from smart_class_planner.infrastructure.study_plan_parser import StudyPlanParser
        from smart_class_planner.domain.repository import Repository
        from smart_class_planner.domain.course import Course
        from smart_class_planner.domain.offering import Offering

        try:
            # Parse DegreeWorks PDF to get remaining courses
            pdf_parser = PDFParser()
            remaining_from_degreeworks = pdf_parser.parse(self.degreeworks_pdf)

            # Parse Study Plan to get required courses
            plan_parser = StudyPlanParser()
            required_courses_dict = plan_parser.parse(self.study_plan_excel)

            # Parse Course Schedule to get when courses are offered
            schedule_parser = StudyPlanParser()
            course_offerings_dict = schedule_parser.parse(self.schedule_excel)

            # Create Repository and populate it
            repository = Repository()

            # Add all courses from required courses (study plan)
            for semester, courses in required_courses_dict.items():
                for course_data in courses:
                    course = Course(
                        code=course_data['code'],
                        title=course_data.get('title', ''),
                        credits=3  # Default to 3 credits for graduate courses
                    )
                    repository.add_course(course)

            # Add any courses from DegreeWorks that aren't in the study plan
            for course_data in remaining_from_degreeworks:
                if course_data['code'] not in repository.courses:
                    course = Course(
                        code=course_data['code'],
                        title=course_data.get('title', ''),
                        credits=3
                    )
                    repository.add_course(course)
                    # print(f"DEBUG: Added missing course from DegreeWorks: {course_data['code']}")

            # Add course offerings from schedule
            for term, courses in course_offerings_dict.items():
                # Parse term codes like "SP20", "FA21", "SU22"
                import re
                match = re.match(r'(SP|SU|FA)(\d{2})', term)
                if match:
                    term_code = match.group(1)
                    year_suffix = match.group(2)

                    # Map term codes to full names
                    term_map = {'SP': 'Spring', 'SU': 'Summer', 'FA': 'Fall'}
                    semester = term_map.get(term_code, term)

                    # Convert 2-digit year to 4-digit (20 -> 2020, 25 -> 2025)
                    year = 2000 + int(year_suffix)
                else:
                    # Fallback for other formats
                    term_parts = term.split()
                    if len(term_parts) >= 2:
                        if term_parts[0].isdigit():
                            year = int(term_parts[0])
                            semester = term_parts[1]
                        else:
                            semester = term_parts[0]
                            year = int(term_parts[1]) if term_parts[1].isdigit() else 2025
                    else:
                        semester = term
                        year = 2025

                for course_data in courses:
                    offering = Offering(
                        course_code=course_data['code'],
                        term=semester,
                        year=year
                    )
                    repository.add_offering(offering)

            # The DegreeWorks parser returns REMAINING courses (Still Needed section)
            # we use those directly as the courses to schedule
            remaining_courses = [course['code'] for course in remaining_from_degreeworks]

            # DEBUG: Check which courses have offerings
            print("\nDEBUG: Checking offering data for remaining courses:")
            for course_code in remaining_courses:
                course_offerings = [o for o in repository.offerings if o.course_code == course_code]
                if course_offerings:
                    sample = course_offerings[:3]
                    print(f"  {course_code}: {len(course_offerings)} offerings (e.g., {[(o.term, o.year) for o in sample]})")
                else:
                    print(f"  {course_code}: NO OFFERINGS FOUND")

            # print(f"DEBUG: Repository has {len(repository.courses)} courses")
            # print(f"DEBUG: Repository has {len(repository.offerings)} offerings")
            # print(f"DEBUG: Planning for {len(remaining_courses)} remaining courses")
            # print(f"DEBUG: Remaining courses: {remaining_courses[:5]}")
            # print(f"DEBUG: Courses in repository: {list(repository.courses.keys())}")
            # missing_from_repo = [c for c in remaining_courses if c not in repository.courses]
            # print(f"DEBUG: Courses NOT in repository: {missing_from_repo}")
            # print(f"DEBUG: Sample offerings: {[(o.course_code, o.term, o.year) for o in list(repository.offerings)[:5]]}")

            # # Show debug info to user
            # courses_in_repo = ', '.join(list(repository.courses.keys())[:10])
            # courses_needed = ', '.join(remaining_courses[:10])

            # # Check which courses are NOT in repository
            # missing_from_repo = [c for c in remaining_courses if c not in repository.courses]

            # # Sample offerings
            # sample_offerings = []
            # for offering in list(repository.offerings)[:5]:
            #     sample_offerings.append(f"{offering.course_code} in {offering.term} {offering.year}")

            # debug_info = (
            #     f"Debug Information:\n\n"
            #     f"DegreeWorks: {len(remaining_from_degreeworks)} remaining courses found\n"
            #     f"Study Plan: {len(required_courses_dict)} semesters parsed\n"
            #     f"Course Schedule: {len(course_offerings_dict)} terms parsed\n\n"
            #     f"Repository:\n"
            #     f"  • {len(repository.courses)} courses\n"
            #     f"  • {len(repository.offerings)} offerings\n"
            #     f"  • Courses in repo: {courses_in_repo}\n"
            #     f"  • Courses needed: {courses_needed}\n"
            #     f"  • NOT in repo: {missing_from_repo}\n\n"
            #     f"Sample offerings:\n"
            #     f"  {chr(10).join(sample_offerings)}\n\n"
            #     f"Click OK to continue with plan generation."
            # )
            # messagebox.showinfo("Debug Information", debug_info)

            # Generate Plan using IntegratedPlanner
            # Start planning from the NEXT semester since current semester is in progress
            import datetime
            current_date = datetime.datetime.now()
            current_month = current_date.month
            current_year = current_date.year

            # Determine next semester based on current month
            # Fall: Aug-Dec (months 8-12) -> Next is Spring
            # Spring: Jan-May (months 1-5) -> Next is Summer
            # Summer: Jun-Jul (months 6-7) -> Next is Fall
            if 8 <= current_month <= 12:  # Currently Fall
                start_term = "Spring"
                start_year = current_year + 1
            elif 1 <= current_month <= 5:  # Currently Spring
                start_term = "Summer"
                start_year = current_year
            else:  # Currently Summer (6-7)
                start_term = "Fall"
                start_year = current_year

            planner = IntegratedPlanner(repository)
            self.generated_plan, validation = planner.create_validated_plan(
                remaining_courses=remaining_courses,
                start_term=start_term,
                start_year=start_year,
                max_credits_per_term=9
            )

            # Store repository reference for display
            self.repository = repository

            # Display results
            self._display_plan_results(self.generated_plan)

            # Show validation warnings/errors if any
            if not validation.is_valid:
                warning_msg = "Plan generated with some issues:\n\n"
                if validation.errors:
                    warning_msg += "Errors:\n" + "\n".join(f"• {e}" for e in validation.errors[:5])
                if validation.warnings:
                    warning_msg += "\n\nWarnings:\n" + "\n".join(f"• {w}" for w in validation.warnings[:5])
                messagebox.showwarning("Validation Issues", warning_msg)

        except Exception as e:
            import traceback
            messagebox.showerror(
                "Generation Error",
                f"Failed to generate course plan:\n\n{str(e)}\n\nDetails:\n{traceback.format_exc()}"
            )
            return
        
        # Switch to results tab
        self.notebook.select(1)
        
       
        messagebox.showinfo(
            "Plan Generated Successfully",
            "✓ Your personalized course plan has been generated!\n\n"
            "The plan shows:\n"
            "  • Semester-by-semester course sequence\n"
            "  • Prerequisite validation\n"
            "  • Course availability checking\n"
            "  • Credit hour totals\n\n"
            "Review the 'Course Plan' tab for details."
        )

    def _display_plan_results(self, plan):
        """Display the actual generated course plan in the results tab."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)

        # Handle list of SemesterPlan objects
        if isinstance(plan, list):
            # Check if the plan is empty (no remaining courses)
            if len(plan) == 0:
                congratulations_message = """
╔══════════════════════════════════════════════════════════════════════════╗
║                        CONGRATULATIONS!                                  ║
╚══════════════════════════════════════════════════════════════════════════╝

🎓 Excellent news!

You have no remaining courses after this semester!

You are on track to graduate at the end of your current semester.

Next Steps:
  • Verify with your academic advisor that all requirements are met
  • Apply for graduation through your university portal
  • Attend commencement ceremonies

Best wishes!

"""
                self.results_text.insert(tk.END, congratulations_message, "header")
                self.results_text.config(state=tk.DISABLED)
                return

            header = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    GENERATED COURSE PLAN                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

"""
            self.results_text.insert(tk.END, header, "header")

            total_credits = 0
            for semester in plan:
                # Display semester header
                if hasattr(semester, 'get_term_key'):
                    self.results_text.insert(tk.END, f"\n{semester.get_term_key()}\n", "semester")
                    self.results_text.insert(tk.END, f"{'='*40}\n", "semester")

                # Display courses
                if hasattr(semester, 'courses'):
                    for course in semester.courses:
                        # Check if this course has offering data in the repository
                        has_offerings = False
                        if hasattr(self, 'repository') and self.repository:
                            has_offerings = any(o.course_code == course.code for o in self.repository.offerings)

                        course_line = f"  • {course.code} - {course.title} ({course.credits} credits)"

                        # Add warning if no offering data exists
                        if not has_offerings:
                            course_line += " [⚠ Offering schedule not available - verify with advisor]"

                        course_line += "\n"
                        self.results_text.insert(tk.END, course_line, "course")

                    # Display semester total
                    if hasattr(semester, 'total_credits'):
                        total_credits += semester.total_credits
                        self.results_text.insert(
                            tk.END,
                            f"\n  Semester Total: {semester.total_credits} credits\n",
                            "course"
                        )

            # Display overall summary
            summary = f"""

{'─'*78}
SUMMARY
{'─'*78}
Total Semesters: {len(plan)}
Total Credits: {total_credits}
Average Credits per Semester: {total_credits/len(plan) if plan else 0:.1f}
"""
            self.results_text.insert(tk.END, summary, "header")

        elif isinstance(plan, str):
            self.results_text.insert("1.0", plan)
        elif hasattr(plan, "semesters"):
            for semester in plan.semesters:
                semester_name = semester.name if hasattr(semester, 'name') else str(semester)
                self.results_text.insert(tk.END, f"\n{semester_name}\n", "semester")
                for course in semester.courses:
                    course_name = course.name if hasattr(course, 'name') else course.title
                    self.results_text.insert(
                        tk.END,
                        f"  {course.code} - {course_name} ({course.credits} credits)\n",
                        "course",
                    )
        else:
            self.results_text.insert("1.0", str(plan))

        self.results_text.config(state=tk.DISABLED)

    def export_to_excel(self):
        """
        Export results to Excel file.
        Integrates with excel_exporter.py
        """
        # Check if results exist
        if not self.generated_plan:
            messagebox.showwarning(
                "No Plan Available",
                "Please generate a course plan before exporting.\n\n"
                "Steps:\n"
                "1. Upload all required files\n"
                "2. Click 'Generate Course Plan'\n"
                "3. Then export the results"
            )
            return

        # Check if plan is empty (no remaining courses)
        if isinstance(self.generated_plan, list) and len(self.generated_plan) == 0:
            messagebox.showinfo(
                "Congratulations!",
                "🎓 Great news!\n\n"
                "You have no remaining courses after this semester.\n\n"
                "You are on track to graduate at the end of your current semester!\n\n"
                "There is nothing to export. Please verify with your academic advisor "
                "that all requirements are met and apply for graduation."
            )
            return

        # Get save location
        initial_filename = "course_plan.xlsx"
        if self.degreeworks_pdf:
            initial_filename = f"course_plan_{Path(self.degreeworks_pdf).stem}.xlsx"

        file_path = filedialog.asksaveasfilename(
            title="Save Course Plan",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            initialfile=initial_filename
        )

        if not file_path:
            return

        try:
            from smart_class_planner.presentation.excel_exporter import ExcelExporter

            exporter = ExcelExporter()
            metadata = {
                "version": "Smart Class Planner v1.0",
                "degreeworks_file": Path(self.degreeworks_pdf).name if self.degreeworks_pdf else "N/A",
                "study_plan_file": Path(self.study_plan_excel).name if self.study_plan_excel else "N/A",
                "schedule_file": Path(self.schedule_excel).name if self.schedule_excel else "N/A"
            }

            # Export the plan (ExcelExporter now handles SemesterPlan objects)
            exporter.export_plan(self.generated_plan, file_path, metadata)

            messagebox.showinfo(
                "Export Successful",
                f"✓ Course plan exported successfully!\n\n"
                f"File: {Path(file_path).name}\n"
                f"Location: {Path(file_path).parent}\n\n"
                f"The Excel file contains:\n"
                f"  • Course Plan (detailed semester schedule)\n"
                f"  • Semester Summary (credits per term)\n"
                f"  • Program Summary (overall statistics)\n"
                f"  • Metadata (generation details)\n\n"
                f"You can now share this file with your academic advisor."
            )

        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Failed to export course plan:\n\n{str(e)}\n\n"
                f"Please ensure:\n"
                f"• You have write permissions to the selected location\n"
                f"• The file is not already open in another program\n"
                f"• Pandas and openpyxl libraries are installed"
            )

    def clear_all_data(self):
        """Clear all uploaded files and results."""
        confirm = messagebox.askyesno(
            "Confirm Clear All",
            "Are you sure you want to clear all uploaded files and results?\n\n"
            "This will remove:\n"
            "  • All uploaded files (PDF and Excel)\n"
            "  • Generated course plan\n"
            "  • All results and data\n\n"
            "This action cannot be undone."
        )
        
        if not confirm:
            return
        
        # Clear file references
        self.degreeworks_pdf = None
        self.study_plan_excel = None
        self.schedule_excel = None
        self.generated_plan = None
        
        # Reset status labels
        self.degreeworks_status.config(
            text="⭕ No file selected", 
            fg=self.secondary_color,
            font=("Segoe UI", 9)
        )
        self.study_plan_status.config(
            text="⭕ No file selected", 
            fg=self.secondary_color,
            font=("Segoe UI", 9)
        )
        self.schedule_status.config(
            text="⭕ No file selected", 
            fg=self.secondary_color,
            font=("Segoe UI", 9)
        )
        
        # Clear results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        cleared_msg = """
╔══════════════════════════════════════════════════════════════════════════╗
║                         DATA CLEARED                                     ║
╚══════════════════════════════════════════════════════════════════════════╝

All data has been cleared successfully.

✓ Uploaded files removed
✓ Generated plan cleared
✓ System reset to initial state


📋 READY FOR NEW INPUT

You can now:
  1. Upload new files in the "Setup & Upload" tab
  2. Generate a fresh course plan
  3. Export new results


Start fresh whenever you need to plan for a different student or program!
        """
        
        self.results_text.insert("1.0", cleared_msg)
        self.results_text.config(state=tk.DISABLED)
        
        # Switch to first tab
        self.notebook.select(0)
        
        messagebox.showinfo(
            "Data Cleared", 
            "✓ All data has been cleared successfully.\n\n"
            "The system is ready for new input."
        )

    def run(self):
        """Start the application main loop."""
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Start main loop
        self.root.mainloop()

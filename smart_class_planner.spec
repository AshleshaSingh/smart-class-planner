# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for Smart Class Planner.
This file defines how to bundle the application into a Windows executable.
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project root directory
project_root = Path(SPECPATH)

a = Analysis(
    ['smart_class_planner/main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include any data files if needed
        # ('path/to/data', 'destination'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'openpyxl',
        'xlsxwriter',
        'beautifulsoup4',
        'bs4',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        'PyPDF2',
        'pypdf',
        'requests',
        'networkx',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'smart_class_planner',
        'smart_class_planner.presentation',
        'smart_class_planner.presentation.setup_wizard',
        'smart_class_planner.presentation.excel_exporter',
        'smart_class_planner.application',
        'smart_class_planner.application.planner',
        'smart_class_planner.application.plan_generator',
        'smart_class_planner.application.validator',
        'smart_class_planner.domain',
        'smart_class_planner.domain.course',
        'smart_class_planner.domain.offering',
        'smart_class_planner.domain.prerequisite',
        'smart_class_planner.domain.repository',
        'smart_class_planner.domain.studyplansequence',
        'smart_class_planner.infrastructure',
        'smart_class_planner.infrastructure.abstract_parser',
        'smart_class_planner.infrastructure.pdf_parser',
        'smart_class_planner.infrastructure.study_plan_parser',
        'smart_class_planner.infrastructure.scraper',
        'smart_class_planner.infrastructure.program_map_scraper',
        'smart_class_planner.infrastructure.prereq_graph_parser',
        'smart_class_planner.config',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pytest-cov',
        'coverage',
        '_pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SmartClassPlanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: 'path/to/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SmartClassPlanner',
)

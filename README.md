# Church-finance-manager
Church Finance Manager v1.0

A lightweight desktop finance management application built with Python, PySide6, and SQLite.

Designed to help churches track income and expenses, generate reports, and securely store financial data with automatic backups.

⸻

Features
• Add and delete income & expense transactions
• Monthly and yearly filtering
• “All months” yearly view
• Automatic newest-first sorting
• Color-coded transactions
• CSV export
• PDF report export
• Automatic database backups
• Data stored safely in Windows AppData
• Standalone Windows executable build

⸻

Tech Stack
• Python 3.10+
• PySide6 (Qt for Python)
• SQLite
• ReportLab (PDF generation)
• PyInstaller (for packaging)

⸻

Data Storage

All application data is stored in:

C:\Users\<User>\AppData\Local\ChurchFinance\

This includes:
• church.db (main database)
• backups/ folder
• app.log (if logging is enabled)

This ensures:
• Data is preserved across reinstalls
• The app folder can be replaced safely
• Users do not accidentally modify internal files

⸻

Installation (Development)
1. Clone the repository
2. Create a virtual environment (recommended)
3. Install dependencies:
pip install -r requirements.txt
4. Run:
python main.py

⸻

Packaging (Windows Executable)

To build a standalone .exe:

pyinstaller --onefile --windowed main.py

The executable will appear in:

dist/

If ReportLab modules are missing during packaging:

pyinstaller --onefile --windowed --collect-all reportlab main_window.py


⸻

Backup System

The app automatically creates timestamped database backups.

Backups are stored in:

AppData\Local\ChurchFinance\backups\

This protects financial data against accidental corruption or system failure.

⸻

Version Status

This is Version 1.0.

Current focus:
• Stability
• Reliable storage
• Accurate reporting

Future improvements may include:
• Edit transaction dialog
• Dashboard summaries
• Budget tracking
• Multi-user capability
• Installer creation

⸻

Project Purpose

This project serves two purposes:
1. A practical finance tool for church administration
2. A structured learning and software engineering training project

⸻

License

Private internal use (customize as needed).

⸻

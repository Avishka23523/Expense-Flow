# ExpenseFlow — Personal Expense Tracker

A dark-themed desktop personal finance manager built with **Python, CustomTkinter, SQLite, and Matplotlib**. Track income and expenses, analyse spending, export monthly reports, and manage category budgets.

## Features

- Add, view, edit, and delete transactions
- Dashboard: total income, expenses, and balance
- Analytics: expense categories, monthly comparisons, net cash flow
- Search and filter transactions by text, type, category, and date
- Export monthly PDF and Excel reports
- Set monthly category budgets with 80% warning and over-limit alerts
- Persistent local SQLite storage

## Screenshots

Add your own application screenshots to `screenshots/`, then uncomment these lines:

<!-- ![Dashboard](screenshots/dashboard.png) -->
<!-- ![Analytics](screenshots/analytics.png) -->
<!-- ![Budgets](screenshots/budgets.png) -->

## Requirements

- Python 3.10+ (a current supported Python version recommended)
- Windows, macOS, or Linux with Tk support

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/ExpenseFlow.git
cd ExpenseFlow
python -m venv .venv
```

Activate the virtual environment:

**Windows CMD:**

```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Install dependencies and run:

```bash
python -m pip install -r requirements.txt
python main.py
```

The application creates its local SQLite database automatically.

## Project Structure

```text
ExpenseFlow/
├── main.py              # Desktop UI
├── database.py          # Transaction database operations
├── budgets.py           # Budget data and calculations
├── reports.py           # PDF and Excel export
├── requirements.txt     # Dependencies
├── .gitignore           # Excludes local/private files
├── README.md
└── screenshots/         # Add your own UI screenshots
```

## Privacy

Financial data stays in the local `expenses.db` file. **Do not commit that file to GitHub.** `.gitignore` excludes it and the virtual environment.

## Technology

Python · CustomTkinter · SQLite · Matplotlib · ReportLab · openpyxl

## Future Improvements

- Date picker and advanced filtering
- Import/export backups
- Automated tests
- Multi-currency support

## License

Add a license if you want to grant reuse rights.

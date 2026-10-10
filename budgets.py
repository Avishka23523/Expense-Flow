"""Monthly category budgets. Uses the same expenses.db as transactions."""
from datetime import date
import math
from database import connect_db

CATEGORIES = ('Food', 'Transport', 'Shopping', 'Bills', 'Salary', 'Other')

def create_budget_table():
    with connect_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            UNIQUE(year, month, category)
        )''')

def save_budget(year, month, category, amount):
    year, month = int(year), int(month)
    amount = float(amount)
    if not 1 <= month <= 12 or year < 1900 or category not in CATEGORIES or not math.isfinite(amount) or amount <= 0:
        raise ValueError('Enter a valid month, category and positive budget amount.')
    with connect_db() as conn:
        conn.execute('''INSERT INTO budgets (year,month,category,amount)
            VALUES (?,?,?,?) ON CONFLICT(year,month,category)
            DO UPDATE SET amount=excluded.amount''', (year, month, category, amount))

def remove_budget(year, month, category):
    with connect_db() as conn:
        return conn.execute('DELETE FROM budgets WHERE year=? AND month=? AND category=?',
                            (int(year), int(month), category)).rowcount

def get_budget_summary(year, month):
    """Return (category, limit, spent) rows for the selected calendar month."""
    period = f'{int(year):04d}-{int(month):02d}'
    with connect_db() as conn:
        return conn.execute('''SELECT b.category, b.amount,
                COALESCE((SELECT SUM(t.amount) FROM transactions t
                    WHERE t.type='Expense' AND t.category=b.category
                      AND substr(t.date,1,7)=?),0) AS spent
            FROM budgets b WHERE b.year=? AND b.month=? ORDER BY b.category''',
            (period, int(year), int(month))).fetchall()

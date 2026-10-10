import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'expenses.db'

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_table():
    with connect_db() as connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            date TEXT NOT NULL,
            description TEXT
        )''')

def add_transaction(transaction_type, category, amount, date, description):
    with connect_db() as connection:
        connection.execute('INSERT INTO transactions (type,category,amount,date,description) VALUES (?,?,?,?,?)',
                           (transaction_type, category, amount, date, description))

def get_transactions():
    with connect_db() as connection:
        return connection.execute('SELECT id,type,category,amount,date,description FROM transactions ORDER BY id DESC').fetchall()

def update_transaction(transaction_id, transaction_type, category, amount, date, description):
    with connect_db() as connection:
        return connection.execute('''UPDATE transactions SET type=?,category=?,amount=?,date=?,description=? WHERE id=?''',
                                  (transaction_type, category, amount, date, description, transaction_id)).rowcount

def delete_transaction(transaction_id):
    with connect_db() as connection:
        return connection.execute('DELETE FROM transactions WHERE id=?', (transaction_id,)).rowcount

if __name__ == '__main__':
    create_table()
    print('Database ready!')

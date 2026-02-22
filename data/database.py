import sqlite3
from datetime import datetime
from domain.income import Income
from domain.expense import Expense
import shutil
import os
from pathlib import Path



class Database:
    def __init__(self):
        app_dir = self.get_appdata_directory()
        db_path = os.path.join(app_dir, "Calvary_AG_finance.db")
        self.connection = sqlite3.connect(db_path)
        self._create_tables()

    def get_appdata_directory(self):
        appdata = os.getenv("LOCALAPPDATA")
        if not appdata:
            raise RuntimeError("LOCALAPPDATA environment variable not found.")
        
        app_folder = Path(appdata) / "ChurchFinance"
        app_folder.mkdir(parents=True, exist_ok=True)

        return app_folder

    def _create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                source TEXT NOT NULL,
                date TEXT NOT NULL,
                deleted INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                deleted INTEGER DEFAULT 0
            )
        """)
        self.connection.commit()


    def save_income(self, income: Income):
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO incomes (amount, source, date)
            VALUES (?, ?, ?)
        """, (
            income.amount,
            income.source,
            income.date.isoformat()
        ))

        self.connection.commit()
        return cursor.lastrowid


    def create_backup(self):
        app_dir = self.get_appdata_directory()
        db_path = os.path.join(app_dir, "Calvary_AG_finance.db")

        backup_dir = os.path.join(app_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = os.path.join(backup_dir, backup_name)

        shutil.copy(db_path, backup_path)


    def clean_old_backups(self, keep=10):
        backup_dir = self.get_appdata_directory()
        files = sorted(
            [os.path.join(backup_dir, f) for f in os.listdir(backup_dir)],
            key=os.path.getmtime,
            reverse=True
        )
        for old_file in files[keep:]:
            os.remove(old_file)


    def save_expense(self, expense: Expense):
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO expenses (amount, category, date)
            VALUES (?, ?, ?)
        """, (
            expense.amount,
            expense.category,
            expense.date.isoformat()
        ))
        self.connection.commit()
        return cursor.lastrowid


    def load_incomes(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, amount, source, date FROM incomes WHERE deleted=0")

        rows = cursor.fetchall()

        incomes = []
        for id, amount, source, date_str in rows:
            date = datetime.fromisoformat(date_str)
            incomes.append(Income(amount, source, date, id=id))

        return incomes


    def load_expenses(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, amount, category, date FROM expenses WHERE deleted=0")

        rows = cursor.fetchall()

        expenses = []
        for id, amount, source, date_str in rows:
            date = datetime.fromisoformat(date_str)
            expenses.append(Expense(amount, source, date, id=id))

        return expenses
    

    def delete_income(self, income_id: int):
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE incomes SET deleted = 1 WHERE id = ?",
            (income_id,)
        )
        self.connection.commit()


    def delete_expense(self, expense_id: int):
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE expenses SET deleted = 1 WHERE id = ?",
            (expense_id,)
        )
        self.connection.commit()
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QDialog, QLineEdit, QFormLayout, QMessageBox, QHeaderView, QAbstractItemView, QFileDialog, QComboBox, QSpinBox
from PySide6.QtCore import QDate
import sys
from domain.expense import Expense
from domain.ledger import Ledger
from data.database import Database
import csv
import shutil
import subprocess
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

class MainWindow(QMainWindow):
    def __init__(self, ledger: Ledger):
        super().__init__()

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        open_data_action = file_menu.addAction("Open Data Folder")
        open_data_action.triggered.connect(self.open_data_folder)


        self.setWindowTitle("Calvary AG Finace Manager v1.0")
        self.setGeometry(200, 200, 600, 400)

        self.ledger = ledger

        db = Database()

        db.create_backup()
        db.clean_old_backups()


        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Balance label
        self.balance_label = QLabel(f"Current Balance: GHS {self.ledger.get_balance():.2f}")
        layout.addWidget(self.balance_label)


        filter_layout = QHBoxLayout()

        self.month_selector = QComboBox()
        self.month_selector.addItem("All months")
        self.month_selector.addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.month_selector.currentIndexChanged.connect(self.refresh_table)
        self.month_selector.setCurrentIndex(0)


        self.year_selector = QSpinBox()
        self.year_selector.setRange(2000, 2100)
        self.year_selector.setValue(QDate.currentDate().year())
        self.year_selector.valueChanged.connect(self.refresh_table)

        filter_layout.addWidget(self.month_selector)
        filter_layout.addWidget(self.year_selector)

        layout.addLayout(filter_layout)


        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Source/Category", "Amount", "Date"])
        self.table.setColumnHidden(0, True)  # Hide ID column
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.viewport().installEventFilter(self)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


        layout.addWidget(self.table)

        self.refresh_table()

        # Buttons layout
        button_layout = QHBoxLayout()

        self.add_income_button = QPushButton("Add Income")
        self.add_expense_button = QPushButton("Add Expense")
        self.delete_button = QPushButton("Delete Selected")
        self.export_pdf_button = QPushButton("Export PDF")
        self.export_button = QPushButton("Export CSV")
        self.delete_button.setEnabled(False) # Disabled initially

        self.delete_button.setStyleSheet("""
            QPushButton {
            background-color: darkred;
            }
            QPushButton:hover {
                background-color: red;
            }
            QPushButton:pressed {
                background-color: darkred;
            }                             
            """)
        self.export_pdf_button.setStyleSheet("""
            QPushButton {
            background-color: green;
            }
            QPushButton:hover {
                background-color: darkgreen;
            }
            QPushButton:pressed {
                background-color: darkgreen;
            }                             
            """)
        self.export_button.setStyleSheet("""
            QPushButton {
            background-color: blue;
            }
            QPushButton:hover {
                background-color: darkblue;
            }
            QPushButton:pressed {
                background-color: darkblue;
            }                             
            """)

        button_layout.addWidget(self.add_income_button)
        button_layout.addWidget(self.add_expense_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_pdf_button)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        # Connect buttons
        self.add_income_button.clicked.connect(self.open_add_income_dialog)
        self.add_expense_button.clicked.connect(self.open_add_expense_dialog)
        self.delete_button.clicked.connect(self.delete_selected_transaction)
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.export_button.clicked.connect(self.export_to_csv)


    def open_data_folder(self):
        db = Database()
        app_dir = db.get_appdata_directory()
        subprocess.Popen(f'explorer "{app_dir}"')
    from datetime import datetime

    def get_selected_date_range(self):
        selected_index = self.month_selector.currentIndex()
        selected_year = self.year_selector.value()

        # If "All Months" selected
        if selected_index == 0:
            start_date = datetime(selected_year, 1, 1)
            end_date = datetime(selected_year + 1, 1, 1)
            return start_date, end_date

        # Otherwise specific month
        selected_month = selected_index  # because index 1 = January

        start_date = datetime(selected_year, selected_month, 1)

        if selected_month == 12:
            end_date = datetime(selected_year + 1, 1, 1)
        else:
            end_date = datetime(selected_year, selected_month + 1, 1)

        return start_date, end_date


    def on_selection_changed(self):
        selected_indexes = self.table.selectionModel().selectedRows()
        if selected_indexes:
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)


    def eventFilter(self, source, event):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QMouseEvent

        if source == self.table.viewport() and isinstance(event, QMouseEvent):
            if event.type() == event.Type.MouseButtonPress:
                index = self.table.indexAt(event.pos())
                if not index.isValid():  # Clicked empty area
                    self.table.clearSelection()
                    self.on_selection_changed()  # Update delete button state
        return super().eventFilter(source, event)





    def refresh_table(self):
        self.table.setRowCount(0)

        start_date, end_date = self.get_selected_date_range()

        transactions = []

        # Collect incomes
        for income in self.ledger.list_incomes():
            if start_date <= income.date < end_date:
                transactions.append((income.id, "Income", income.source, income.amount, income.date))

        # Collect expenses
        for expense in self.ledger.list_expenses():
            if start_date <= expense.date < end_date:
                transactions.append((expense.id, "Expense", expense.category, expense.amount, expense.date))

        # Sort by date descending (newest first)
        transactions.sort(key=lambda x: x[4], reverse=True)

        # Insert into table
        for transaction in transactions:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(str(transaction[0])))
            self.table.setItem(row_position, 1, QTableWidgetItem(transaction[1]))
            self.table.setItem(row_position, 2, QTableWidgetItem(transaction[2]))
            self.table.setItem(row_position, 3, QTableWidgetItem(f"{transaction[3]:.2f}"))
            self.table.setItem(row_position, 4, QTableWidgetItem(
                transaction[4].strftime("%Y-%m-%d %H:%M:%S")
            ))




    def open_add_income_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Income")

        form_layout = QFormLayout(dialog)

        amount_input = QLineEdit()
        source_input = QLineEdit()

        form_layout.addRow("Amount:", amount_input)
        form_layout.addRow("Source:", source_input)

        save_button = QPushButton("Save")
        form_layout.addWidget(save_button)

        def save_income():
            try:
                amount = float(amount_input.text())
                source = source_input.text().strip()

                if amount <= 0:
                    raise ValueError("Amount must be positive.")
                if not source:
                    raise ValueError("Source cannot be empty.")

                from domain.income import Income
                new_income = Income(amount, source)


                from data.database import Database
                db = Database()
                new_id = db.save_income(new_income)
                new_income.id = new_id

                self.ledger.add_income(new_income)

                self.refresh_ui()
                dialog.accept()

            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

        save_button.clicked.connect(save_income)

        dialog.exec()


    def open_add_expense_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Expense")

        form_layout = QFormLayout(dialog)

        amount_input = QLineEdit()
        category_input = QLineEdit()

        form_layout.addRow("Amount:", amount_input)
        form_layout.addRow("Category:", category_input)

        save_button = QPushButton("Save")
        form_layout.addWidget(save_button)

        def save_expense():
            try:
                amount = float(amount_input.text())
                category = category_input.text().strip()

                if amount <= 0:
                    raise ValueError("Amount must be positive.")
                if not category:
                    raise ValueError("Category cannot be empty.")

                from domain.expense import Expense
                new_expense = Expense(amount, category)


                from data.database import Database
                db = Database()
                new_id = db.save_expense(new_expense)

                new_expense.id = new_id

                self.ledger.add_expense(new_expense)

                self.refresh_ui()
                dialog.accept()

            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

        save_button.clicked.connect(save_expense)

        dialog.exec()


    from PySide6.QtWidgets import QMessageBox

    def delete_selected_transaction(self):
        from PySide6.QtWidgets import QMessageBox
        from data.database import Database  # adjust import if needed

        selected_indexes = self.table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
            return

        selected_row = selected_indexes[0].row()

        # Get the hidden ID and Type
        id_item = self.table.item(selected_row, 0)
        type_item = self.table.item(selected_row, 1)

        if id_item is None:
            QMessageBox.warning(self, "Error", "No ID found")
            return

        if not id_item or not type_item:
            QMessageBox.warning(self, "Error", "Selected row is invalid.")
            return

        id_text = id_item.text()
        type_text = type_item.text()


        try:
            transaction_id = int(id_text)
            transaction_type = type_text
        except ValueError:
            QMessageBox.warning(self, "Error", f"Invalid ID: {id_text}")
        
            transaction_id = int(id_text)
            transaction_type = type_text
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this {transaction_type}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # ✅ Instantiate Database here
        db = Database()

        try:
            if transaction_type == "Income":
                db.delete_income(transaction_id)
            else:
                db.delete_expense(transaction_id)

            # Refresh the table and totals
            self.reload_ledger()
            self.refresh_table()
            self.refresh_ui()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete transaction:\n{str(e)}")



    def export_to_pdf(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Monthly PDF Report",
            f"Calvary_AG_{self.month_selector.currentText()}_{self.year_selector.value()}_finance_report.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        start_date, end_date = self.get_selected_date_range()

        transactions = []
        total_income = 0
        total_expense = 0

        # Collect filtered transactions
        for income in self.ledger.list_incomes():
            if start_date <= income.date < end_date:
                transactions.append(("Income", income.source, income.amount, income.date))
                total_income += income.amount

        for expense in self.ledger.list_expenses():
            if start_date <= expense.date < end_date:
                transactions.append(("Expense", expense.category, expense.amount, expense.date))
                total_expense += expense.amount

        transactions.sort(key=lambda x: x[3], reverse=True)

        try:
            doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
            elements = []

            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"Calvary Assemblies of God - Odumasi Central", styles["Heading1"]))
            elements.append(Paragraph(
                f"Financial Report {self.month_selector.currentText()} {self.year_selector.value()}",
                styles["Heading2"]))
            elements.append(Paragraph(
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                styles["Normal"]
            ))
            elements.append(Spacer(1, 0.4 * inch))

            # Table data
            table_data = [["Type", "Source/Category", "Amount", "Date"]]

            for t in transactions:
                table_data.append([
                    t[0],
                    t[1],
                    f"{t[2]:.2f}",
                    t[3].strftime("%Y-%m-%d %H:%M")
                ])

            table = Table(table_data, repeatRows=1)

            elements.append(table)
            elements.append(Spacer(1, 0.4 * inch))

            net_balance = total_income - total_expense

            summary_data = [
                ["Total Income", f"{total_income:.2f}"],
                ["Total Expense", f"{total_expense:.2f}"],
                ["Net Balance", f"{net_balance:.2f}"]
            ]

            summary_table = Table(summary_data)
            if net_balance >= 0:
                color = colors.green
            else:
                color = colors.red

            summary_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("TEXTCOLOR", (1, 2), (1, 2), color)  # Net balance value
            ]))


            elements.append(summary_table)

            doc.build(elements)

            QMessageBox.information(self, "Success", "PDF report exported successfully!")

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


    def export_to_csv(self):

        selected_month = self.month_selector.currentText()
        selected_year = self.year_selector.value()

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Monthly CSV",
            f"Calvary_AG_{selected_month}_{selected_year}_finance_report_csv.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        start_date, end_date = self.get_selected_date_range()

        monthly_income_total = 0.0
        monthly_expense_total = 0.0


        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                writer.writerow(["Type", "Source/Category", "Amount", "Date"])

                # Incomes
                for income in self.ledger.list_incomes():
                    if start_date <= income.date < end_date:
                        writer.writerow([
                            "Income",
                            income.source,
                            f"{income.amount:.2f}",
                            income.date.strftime("%Y-%m-%d %H:%M:%S")
                        ])
                        monthly_income_total += income.amount

                # Expenses
                for expense in self.ledger.list_expenses():
                    if start_date <= expense.date < end_date:
                        writer.writerow([
                            "Expense",
                            expense.category,
                            f"{expense.amount:.2f}",
                            expense.date.strftime("%Y-%m-%d %H:%M:%S")
                        ])
                        monthly_expense_total += expense.amount

                # Blank line before summary
                writer.writerow([])
                writer.writerow(["SUMMARY"])
                writer.writerow(["Total Income", f"{monthly_income_total:.2f}"])
                writer.writerow(["Total Expense", f"{monthly_expense_total:.2f}"])
                writer.writerow(["Net Balance", f"{(monthly_income_total - monthly_expense_total):.2f}"])

            QMessageBox.information(self, "Success", "Monthly report exported successfully!")

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


    def reload_ledger(self):
        from domain.ledger import Ledger
        from data.database import Database

        db = Database()
        self.ledger = Ledger()

        for income in db.load_incomes():
            self.ledger.add_income(income)

        for expense in db.load_expenses():
            self.ledger.add_expense(expense)


    def refresh_ui(self):
        self.balance_label.setText(
            f"Current Balance: GHS {self.ledger.get_balance():.2f}"
        )
        self.refresh_table()




if __name__ == "__main__":
    db = Database()
    ledger = Ledger()

    # Load data from DB
    for income in db.load_incomes():
        ledger.add_income(income)

    for expense in db.load_expenses():
        ledger.add_expense(expense)

    app = QApplication(sys.argv)
    window = MainWindow(ledger)
    window.show()
    sys.exit(app.exec())

from datetime import datetime


class Expense:
    def __init__(self, amount: float, category: str, date: datetime | None = None, id: int | None = None):
        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")

        if not category or not category.strip():
            raise ValueError("Expense category cannot be empty.")

        self.amount = float(amount)
        self.category = category.strip()
        self.date = date if date else datetime.now()
        self.id = id


    def __repr__(self):
        return f"Expense(amount={self.amount}, category='{self.category}', date={self.date})"

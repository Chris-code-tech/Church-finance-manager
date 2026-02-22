from datetime import datetime


class Income:
    def __init__(self, amount: float, source: str, date: datetime | None = None, id: int | None = None):
        if amount <= 0:
            raise ValueError("Income amount must be greater than zero.")

        if not source or not source.strip():
            raise ValueError("Income source cannot be empty.")

        self.amount = float(amount)
        self.source = source.strip()
        self.date = date if date else datetime.now()
        self.id = id

    def __repr__(self):
        return f"Income(amount={self.amount}, source='{self.source}', date={self.date})"

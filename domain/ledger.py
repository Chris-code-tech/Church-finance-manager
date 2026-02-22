from typing import List
from domain.income import Income
from domain.expense import Expense


class Ledger:
    def __init__(self):
        self._incomes: List[Income] = []
        self._expenses: List[Expense] = []

    def add_income(self, income: Income) -> None:
        if not isinstance(income, Income):
            raise TypeError("Expected an Income object.")
        self._incomes.append(income)

    def add_expense(self, expense: Expense) -> None:
        if not isinstance(expense, Expense):
            raise TypeError("Expected an Expense object.")
        self._expenses.append(expense)

    def total_income(self) -> float:
        return sum(i.amount for i in self._incomes)

    def total_expense(self) -> float:
        return sum(e.amount for e in self._expenses)

    def get_balance(self) -> float:
        return self.total_income() - self.total_expense()

    def list_incomes(self) -> List[Income]:
        return list(self._incomes)

    def list_expenses(self) -> List[Expense]:
        return list(self._expenses)

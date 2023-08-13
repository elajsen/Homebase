from datetime import date, datetime
from models.budget.misc_data import INCOME_LABELS, SPENDING_LABELS, OMIT_LABELS
from models.requests.request_structure import structure_week_category
from models.budget.time_stats import TimeframeStatistics
from typing import Dict, Any


class Week(TimeframeStatistics):
    def __init__(self, start_date:date, end_date:date, movements:list, number:int):
        super().__init__(str(start_date), "week")
        self.start_date = start_date
        self.end_date = end_date
        self.weekly_movements = self._initialize_weekly_movements(movements)
        self.week_number = number
        self.weekly_budget = None

    def _initialize_weekly_movements(self, movements: list) -> list:
        return [trans for trans in movements if trans["date"].date() >= self.start_date and trans["date"].date() <= self.end_date]

    @property
    def category_sum(self) -> dict:
        category_sum = {}
        for transaction in self.weekly_movements:
            if transaction["category"] not in category_sum.keys():
                category_sum[transaction["category"]] = 0

            category_sum[transaction["category"]] += transaction["amount"]
        return structure_week_category(category_sum)

    @property
    def total_weekly_income(self) -> float:
        return sum([transaction["amount"] for transaction in self.weekly_movements if transaction["category"] in INCOME_LABELS])

    @property
    def total_weekly_spending(self) -> float:
        return sum([transaction["amount"] for transaction in self.weekly_movements if transaction["category"] in SPENDING_LABELS])

    @property
    def remaining_days(self) -> int:
        return min(max((self.end_date - datetime.today().date()).days, 0), (self.end_date - self.start_date).days)

    @property
    def request_package(self) -> Dict[str, Any]:
        return {
            "categories": self.category_sum,
            "dates": f"{str(self.start_date)}-{str(self.end_date)}",
            "remaining_days": self.remaining_days,
            "amount": self.weekly_budget,
            "week": self.week_number
        }
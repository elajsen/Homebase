from models.budget.time_stats import TimeframeStatistics
from models.budget.month import Month
from models.utils.date_utils import DateUtils

from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Any


class Year(TimeframeStatistics):
    def __init__(self, partition:str):
        super().__init__(partition, "year")
        self._intialize_months()

    def _intialize_months(self):
        self.months = [Month(str(date(self.partition.year, month, 1))) for month in range(1, 13)]

    @property
    def transactions_by_category_with_change(self) -> List[Dict[str, Any]]:
        transactions_by_category = self.transactions_by_category
        return self._add_mom_change(transactions_by_category)

    def _add_mom_change(self, trans_by_category):
        def get_previous_month(date):
            for month in self.months:
                if date == month.partition:
                    return month
            return Month(str(date))

        for month in trans_by_category:
            date = month["date"]
            prev_month_obj = get_previous_month(DateUtils.string_to_datetime(date) - relativedelta(months=1))
            for income_spending in month["income"] + month["spending"]:
                previous_amount = prev_month_obj.categories[0].get(income_spending["name"], 0)
                try:
                    income_spending["diff"] = round(((income_spending["amount"] - previous_amount) / previous_amount) * 100, 2)
                except ZeroDivisionError:
                    income_spending["diff"] = 0

        return trans_by_category
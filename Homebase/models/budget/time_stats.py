from models.mongo_handler import MongoHandler
from models.utils.date_utils import DateUtils

from models.budget.misc_data import INCOME_LABELS, SPENDING_LABELS
from models.budget.person import SALARY

from pandas import DataFrame
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Union, List, Dict, Any

mongo_handler = MongoHandler()


class TimeframeStatistics:
    def __init__(self, partition: str, timeframe: Union["year", "month", "week"]):
        self.partition = DateUtils.string_to_datetime(partition)
        self.month_start = self.partition.replace(day=1)
        self.timeframe = timeframe

    def __str__(self):
        return f"{self.__class__.__name__}({self.partition})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.partition})"

    @property
    def categories(self) -> List[Dict[str, Any]]:
        """
        This function gets the categories for the month or year, the result will
        look like this:

        :return:
        [{
            '_id': ObjectId('65fc40c165a82a2672894b0d'),
            'Efectivo y servicios bancarios': 872.25,
            'Compras': 455.29,
            'Ocio': 274.49,
            'Viajes': 238.25,
            'Hogar': 31.98,
            'Transporte': 29.29,
            'Ingreso Bizum': 203.2,
            'other income': 0.0,
            'Retentions': 38.43,
            'date': '2024-03-01',
            'data_time': '2024-03-21 15:14:25'
        }]
        """
        months = self._get_months()
        data = mongo_handler.get_categories(months)
        data = self._add_hogar(data)
        return self._remove_adjustments_from_data(data)

    @property
    def transactions_by_category(self) -> List[Dict[str, Dict[str, Any]]]:
        icons = mongo_handler.get_budget_icons()
        transactions = []
        for monthly_categories in self.categories:
            transactions.append(self._income_and_spending_from_month(monthly_categories, icons))
        if not self.categories:
            transactions.append(self._income_and_spending_from_month(None, None))

        if self.timeframe == "month":
            try:
                transactions = transactions[0]
            except IndexError:
                transactions = []
        return transactions

    def _income_and_spending_from_month(self, categories: Dict[str, Any], icons: Dict[str, str]) -> Dict[Union["income", "spending"], Dict[str, float]]:
        if categories is None and icons is None:
            return {
                "income": [],
                "spending": [],
                "date": ""
            }

        def percentage_change(current_val, previous_val):
            try:
                return round(((current_val - previous_val) / previous_val) *100 , 2)
            except ZeroDivisionError:
                return 0

        previous_categories = self.get_previous_month_categories(categories["date"])
        incomes = [{"amount": val, "name": key, "icon": icons.get(key, ""), "diff": percentage_change(val, previous_categories.get(key, 0))} for key, val in categories.items() if key in INCOME_LABELS]
        spendings = [{"amount": val, "name": key, "icon": icons.get(key, ""), "diff": percentage_change(val, previous_categories.get(key, 0))} for key, val in categories.items() if key in SPENDING_LABELS]
        return {
            "income": incomes,
            "spending": spendings,
            "date": categories["date"]
        }

    def get_previous_month_categories(self, date):
        prev_date = str(DateUtils.string_to_datetime(date) - relativedelta(months=1))
        for category in self.categories:
            if category["date"] == prev_date:
                return category
        
        return mongo_handler.get_categories_month(prev_date)

    @property
    def movements(self) -> DataFrame:
        return mongo_handler.get_current_month_budget_movements(self.partition)

    @property
    def total_income(self) -> float:
        total_income = 0
        for month in self.categories:
            total_income += round(sum(val for key, val in month.items() if key in INCOME_LABELS) ,2)
        return total_income

    @property
    def total_spending(self) -> float:
        total_spending = 0
        for month in self.categories:
            total_spending += round(sum(val for key, val in month.items() if key in SPENDING_LABELS) ,2)
        return total_spending

    @property
    def net_income(self) -> float:
        return round(SALARY + self.total_income - self.total_spending, 2)

    @property
    def net_spending(self) -> float:
        return round(self.total_spending - self.total_income, 2)

    @property
    def current_month(self) -> str:
        return str(self.month_start)[:7]

    @property
    def remaining_days(self) -> int:
        if self.timeframe == "year":
            for month in self.months:
                return sum([week.remaining_days for week in month.weeks])
        elif self.timeframe == "month":
            return sum([week.remaining_days for week in self.weeks])
        else:
            raise Warning(f"For timeframe {self.timeframe} this error should not be apearing")

    def _remove_adjustments_from_data(self, categories: List) -> List:
        adjustments = mongo_handler.get_adjustments(self._get_months())
        for adjustment in adjustments:
            for month in categories:
                if adjustment["Date"] in month["date"] and adjustment["Category"] in month.keys():
                    month[adjustment["Category"]] += adjustment["Amount"]
        return categories

    def _get_months(self) -> Union[List[date], None]:
        if self.timeframe == "year":
            return [month.partition for month in self.months]
        elif self.timeframe == "month":
            return self.month_start
        elif self.timeframe == "week":
            return None
        
    def _add_hogar(self, categories: List) -> List:
        for category in categories:
            if "Hogar" not in category.keys():
                category["Hogar"] = 0
        return categories
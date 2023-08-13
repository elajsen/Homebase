from models.utils.date_utils import DateUtils
from models.budget.week import Week
from models.mongo_handler import MongoHandler
from models.utils.singleton import Singleton
from models.budget.time_stats import TimeframeStatistics

from models.requests.request_structure import structure_bills

from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any

mongo_handler = MongoHandler()


class Month(TimeframeStatistics, Singleton):
    def __init__(self, partition:str):
        super().__init__(partition, "month")
        self.partition = DateUtils.string_to_datetime(partition)
        self.month_start = self.partition.replace(day=1)
        self._initalize_weeks()
        self._assign_weekly_budgets()

    def _initalize_weeks(self) -> None:
        weeks = DateUtils.weeks_in_month(self.partition)
        movements = mongo_handler.get_current_month_budget_movements(self.partition)

        self.weeks = []
        for number, week in enumerate(weeks):
            self.weeks.append(Week(week[0], week[1], movements, number + 1))

    @property
    def week_by_week_description(self) -> List[Dict[str, Any]]:
        return [week.request_package for week in self.weeks]

    @property
    def current_month(self) -> str:
        return str(self.month_start)[:7]

    @property
    def monthly_bills(self) -> Dict[str, Any]:
        icons = mongo_handler.get_budget_icons()
        return structure_bills(mongo_handler.get_monthly_bills(self.partition), icons)

    @property
    def average_monthly_bills(self) -> float:
        date_range = [self.month_start - relativedelta(months=x) for x in range(1, 4)]
        bills = [mongo_handler.get_categories_month(d).get("Hogar") for d in date_range]
        return round(sum(bills) / len(bills), 2)

    @property
    def get_last_update(self) -> str:
        return str(self.categories[0].get("data_time")) if self.categories else ""

    def _assign_weekly_budgets(self) -> None:
        if self.remaining_days == 0:
            net_income_per_day = 0
        else:
            net_income_per_day = round(self.net_income / self.remaining_days, 2)
        for week in self.weeks:
            week.weekly_budget = round(net_income_per_day * week.remaining_days, 2)

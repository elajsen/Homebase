from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import List, Tuple


def date_formater(func):
    def wrapper(date_param):
        if isinstance(date_param, str):
            split_date = date_param.split("-")
            date_param = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))
        res = func(date_param)
        return res
    return wrapper


class DateUtils:
    @staticmethod
    @date_formater
    def datetime_to_month(datetime) -> str:
        return str(datetime)[:7]

    @staticmethod    
    def string_to_datetime(datetime_str: str) -> date:
        split_date = datetime_str.split("-")
        return date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

    @staticmethod
    def weeks_in_month(datetime: date) -> List[Tuple[str, str]]:
        first_date = datetime.replace(day=1)
        final_date = first_date + relativedelta(months=1) - relativedelta(days=1)

        week_start = first_date
        week_end = first_date + relativedelta(days= 6 -first_date.weekday())
        weeks = [(week_start, week_end)]

        while week_end < final_date:
            week_start = week_end + relativedelta(days=1)
            week_end = min(week_start + relativedelta(days=6), final_date)
            if week_end > final_date:
                week_end = final_date
            weeks.append((week_start, week_end))

        return weeks

    @staticmethod
    def date_to_datetime(date_obj: date):
        return datetime.combine(date_obj, datetime.min.time())
    
    @staticmethod
    def months_in_year(date_obj: date) -> List[date]:
        return [date(date_obj.year, month, 1) for month in range(1, 13)]
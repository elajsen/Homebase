from models.BBVA_scraper import BBVAScraper
import pandas as pd
import re
import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class BudgetHandler:
    def __init__(self):
        self.bbva_scraper = BBVAScraper(headless=False)
        self.salary = 1733.84
        self.savings = 100

    def res_dictionary_to_df(self, res_dictionary):
        columns = ["date"]
        data = []
        for vector in res_dictionary:
            for key in vector.keys():
                if key not in columns:
                    columns.append(key)

        for vector in res_dictionary:
            temp = []
            for col in columns:
                temp.append(vector.get(col, 0))
            data.append(temp)

        df = pd.DataFrame(data, columns=columns)
        return df

    def get_current_spending(self, df, current_month):
        df_dict = df.loc[df["date"] == current_month].to_dict()
        total_spending = 0
        for key, item in df_dict.items():
            if key == "date":
                continue
            elif key in ["Ingreso Bizum", "other income"]:
                total_spending -= item.get(0)
            else:
                total_spending += item.get(0)
        return total_spending

    def get_weeks_in_month(self, month=None):
        weeks = []
        if not month:
            date = datetime.today().replace(day=1).date()
        else:
            date = datetime.today().replace(day=1).replace(month=month).date()

        start_month = date.month

        cont = True

        while cont:
            temp = []
            first_d = date - relativedelta(days=date.weekday())
            assert first_d.weekday(
            ) == 0, f"weekday of first date is not monday {first_d.weekday()}"
            if first_d.month > start_month:
                break
            last_d = first_d + relativedelta(days=6)
            assert last_d.weekday(
            ) == 6, f"weekday of first date is not monday {last_d.weekday()}"
            temp.append(first_d)
            temp.append(last_d)
            weeks.append(temp)

            date = last_d + relativedelta(days=1)

            if last_d.month > start_month:
                cont = False

        return weeks

    def get_remaining_months(self, weeks_in_month):
        current_date = datetime.today().date()

        remaining_weeks = []

        for week in weeks_in_month:
            if week[-1] < current_date:
                continue
            elif week[0] < current_date:
                remaining_weeks.append([current_date, week[-1]])
            else:
                remaining_weeks.append(week)

        return remaining_weeks

    def get_weekly_budget(self, net_salary, remaining_weeks):
        remaining_days = []
        for week in remaining_weeks:
            remaining_days.append((week[-1] - week[0]).days + 1)

        total_days = sum(remaining_days)
        weekly_budget = [round(days * (net_salary / total_days), 2)
                         for days in remaining_days]
        return weekly_budget

    def get_monthly_budget(self):
        print("Get Monthly Budget")
        res_dictionary = self.bbva_scraper.get_backlog_month_categories()

        df = self.res_dictionary_to_df(res_dictionary)

        current_month = "2023-06-01"

        total_spending = self.get_current_spending(df, current_month)

        net_salary = round(self.salary - total_spending, 2) - self.savings

        weeks_in_month = self.get_weeks_in_month()

        remaining_weeks = self.get_remaining_months(weeks_in_month)

        budget_amounts = self.get_weekly_budget(net_salary, remaining_weeks)

        structured_weeks = [[str(x[0]), str(x[1])] for x in remaining_weeks]

        final_dict = {}
        for index, (dates, budget) in enumerate(zip(structured_weeks, budget_amounts)):
            final_dict[str(index + 1)] = {
                "dates": dates,
                "amount": budget
            }
        return final_dict

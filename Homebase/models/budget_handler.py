from models.BBVA_scraper import BBVAScraper
from models.mongo_handler import MongoHandler
import pandas as pd
import re
import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class BudgetHandler:
    def __init__(self):
        self.bbva_scraper = BBVAScraper(headless=False)
        self.mongo_handler = MongoHandler()
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

    def get_current_month_from_history_df(self, df, date, icon_dict):
        current_month = df.loc[df["date"] == str(date)].to_dict()
        final_list = []
        for key, vector in current_month.items():
            if key == "_id" or key == "date" or list(vector.values())[0] == 0:
                continue
            final_list.append({"name": key,
                               "amount": list(vector.values())[0],
                               "icon": icon_dict.get(key, "")})

        return final_list

    def get_current_spending(self, df, current_month):
        df_dict = df.loc[df["date"] == str(current_month)].to_dict()
        total_spending = 0
        for key, item in df_dict.items():
            if key in ["date", "_id", "data_time"]:
                continue
            elif key in ["Ingreso Bizum", "other income"]:
                total_spending -= list(item.values())[0]
            else:
                total_spending += list(item.values())[0]
        return round(total_spending, 2)

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

    def get_remaining_weeks(self, weeks_in_month):
        current_date = datetime.today().date()

        remaining_weeks = []

        for week in weeks_in_month:
            if current_date < week[0]:
                remaining_days = 7
            elif current_date > week[-1]:
                remaining_days = 0
            else:
                remaining_days = (week[-1] - current_date).days

            remaining_weeks.append({
                "dates": week,
                "remaining_days": remaining_days
            })
        return remaining_weeks

    def get_weekly_budget(self, net_salary, remaining_weeks):
        total_days = sum([x_sub.get("remaining_days")
                         for x_sub in remaining_weeks])

        for week in remaining_weeks:
            week["amount"] = round(
                (net_salary / total_days) * week.get("remaining_days"), 2)

        return remaining_weeks

    def update_backlog(self):
        res_dictionary = self.bbva_scraper.get_backlog_month_categories()

        self.mongo_handler.update_budget_history(res_dictionary)

    def update_monthly_budget(self):

        current_month_date = datetime.today().date().replace(day=1)

        new_current_month = self.bbva_scraper.get_current_month_categories()
        new_current_month["date"] = str(current_month_date)

        old_current_month_object = list(self.mongo_handler.search_collection(
            self.mongo_handler.db_name,
            self.mongo_handler.budget_history_collection,
            {"date": str(current_month_date)}
        ))

        if len(old_current_month_object) > 0:
            self.mongo_handler.delete_values(
                self.mongo_handler.db_name,
                self.mongo_handler.budget_history_collection,
                {"_id": old_current_month_object[0].get("_id")}
            )

        self.mongo_handler.insert_value(
            self.mongo_handler.db_name,
            self.mongo_handler.budget_history_collection,
            [new_current_month]
        )

    def divide_spending_and_income(self, month_dict):
        spending = []
        income = []
        for vector in month_dict:
            if vector.get("name") in ["_id", "data_time"]:
                continue
            elif vector.get("name") in ["Ingreso Bizum",
                                        "Pendiente de categorizar ingresos",
                                        "other income"]:
                income.append(vector)
            else:
                spending.append(vector)
        return {
            "income": income,
            "spending": spending
        }

    def get_monthly_budget(self):
        print("Get Monthly Budget")
        res = self.mongo_handler.get_budget_history()
        df = self.res_dictionary_to_df(res)

        current_month_date = str(datetime.today().date().replace(day=1))

        icon_images = self.mongo_handler.get_budget_icons()

        current_month = self.get_current_month_from_history_df(
            df, current_month_date, icon_images)

        data_time = [item.get("amount") for item in current_month if item.get(
            "name") == "data_time"][0]

        spending_and_income = self.divide_spending_and_income(current_month)

        total_spending = self.get_current_spending(df, current_month_date)

        net_salary = round(self.salary - total_spending, 2) - self.savings

        weeks_in_month = self.get_weeks_in_month()
        remaining_weeks = self.get_remaining_weeks(weeks_in_month)

        budget_amounts = self.get_weekly_budget(net_salary, remaining_weeks)

        week_dict = []
        for index, vector in enumerate(budget_amounts):
            structured_date_range = str(vector.get(
                "dates")[0]) + "-" + str(vector.get("dates")[1])
            week_dict.append({
                "dates": structured_date_range,
                "amount": vector.get("amount"),
                "remaining_days": vector.get("remaining_days"),
                "week": str(index + 1)
            })

        # print(f"{week_dict}\n{total_spending}\n{spending_and_income}\n{current_month}")
        print(data_time)
        return {
            "week_dict": week_dict,
            "total_spending": total_spending,
            "current_month_categories": spending_and_income,
            "data_time": data_time
        }

from models.BBVA_scraper import BBVAScraper
from models.mongo_handler import MongoHandler
import pandas as pd
import re
import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint


class BudgetHandler:
    def __init__(self):
        self.bbva_scraper = BBVAScraper(headless=True)
        self.mongo_handler = MongoHandler()
        self.salary = 1733.84
        self.savings = 200

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

        if len(current_month.get("date")) == 0:
            return []

        final_list = []
        for key, vector in current_month.items():
            if key == "_id" or key == "date" or list(vector.values())[0] == 0:
                continue
            final_list.append({"name": key,
                               "amount": list(vector.values())[0],
                               "icon": icon_dict.get(key, "")})

        return final_list

    def get_current_spending(self, df, current_month, spending_and_income):
        df_dict = df.loc[df["date"] == str(current_month)].to_dict()
        total_spending = 0
        for key, item in df_dict.items():
            if key in ["date", "_id", "data_time"]:
                continue
            elif key in ["Ingreso Bizum", "other income"]:
                if key == "other income":
                    other_income = [item.get("amount") for item in spending_and_income.get(
                        "income") if item.get("name") == "other income"]
                    if len(other_income) == 0:
                        print("NO OTHER INCOME SKIPPING")
                        continue
                print(f"{key}: income: {list(item.values())[0]}")
                total_spending -= list(item.values())[0]
            else:
                print(f"{key}: spending: {list(item.values())[0]}")
                total_spending += list(item.values())[0]
        print(f"Total spending {total_spending}")
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
        last_day_next_month = current_date\
            .replace(month=current_date.month + 1)\
            .replace(day=1)

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

        # Remaining days for the final week
        final_week_start_date = weeks_in_month[-1][0]
        remaining_weeks[-1]["remaining_days"] = (
            last_day_next_month - final_week_start_date).days

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
        def check_other_income(income):
            names = [vector.get("name") for vector in income]
            if "other income" not in names:
                return income

            total_income = 0
            for vector in income:
                if vector.get("name") == "other income":
                    other_amt = vector.get("amount")
                    other_amt_index = income.index(vector)
                else:
                    total_income += vector.get("amount")

            if other_amt == total_income:
                income.pop(other_amt_index)

            return income

        spending = []
        income = []
        for vector in month_dict:
            if vector.get("name") in ["_id", "data_time"]:
                continue
            elif vector.get("name") in ["Ingreso Bizum",
                                        "Pendiente de categorizar ingresos",
                                        "other income",
                                        "Nómina"]:
                income.append(vector)
            else:
                spending.append(vector)

        income = check_other_income(income)

        return {
            "income": income,
            "spending": spending
        }

    def get_current_month_amounts_and_icons(self, budget_history_df, current_month_first_date):
        icon_images = self.mongo_handler.get_budget_icons()

        current_month = self.get_current_month_from_history_df(
            budget_history_df, current_month_first_date, icon_images)
        return current_month, budget_history_df

    def get_week_by_week_amounts(self, net_salary):
        weeks_in_month = self.get_weeks_in_month()
        remaining_weeks = self.get_remaining_weeks(weeks_in_month)

        budget_amounts = self.get_weekly_budget(net_salary, remaining_weeks)
        return budget_amounts

    def get_last_month_bills(self, history_df, current_month_date):
        last_month_date = current_month_date - relativedelta(months=1)

        last_month_df = history_df.loc[history_df["date"] == str(
            last_month_date)].to_dict()

        return list(last_month_df.get("Hogar").values())[0]

    def get_monthly_budget(self):
        print("Get Monthly Budget")

        current_month_date = datetime.today().date().replace(day=1)
        current_month_date_string = str(current_month_date)
        res = self.mongo_handler.get_budget_history()
        budget_history_df = self.res_dictionary_to_df(res)

        current_month_amounts_and_icons, category_df = self\
            .get_current_month_amounts_and_icons(budget_history_df,
                                                 current_month_date_string)

        last_month_bills = self.get_last_month_bills(budget_history_df,
                                                     current_month_date)

        if len(current_month_amounts_and_icons) == 0:
            return {}

        data_time = [item.get("amount") for item in current_month_amounts_and_icons if item.get(
            "name") == "data_time"][0]

        spending_and_income = self.divide_spending_and_income(
            current_month_amounts_and_icons)

        total_spending_amount = self.get_current_spending(
            category_df, current_month_date_string, spending_and_income)

        net_salary = round(
            self.salary - total_spending_amount, 2) - self.savings

        week_by_week_budget_amounts = self.get_week_by_week_amounts(net_salary)

        week_dict = []
        for index, vector in enumerate(week_by_week_budget_amounts):
            structured_date_range = str(vector.get(
                "dates")[0]) + "-" + str(vector.get("dates")[1])
            week_dict.append({
                "dates": structured_date_range,
                "amount": vector.get("amount"),
                "remaining_days": vector.get("remaining_days"),
                "week": str(index + 1)
            })

        return {
            "week_dict": week_dict,
            "total_spending": total_spending_amount,
            "current_month_categories": spending_and_income,
            "data_time": data_time,
            "last_month_bills": last_month_bills
        }

    def divide_monthly_income_and_spending(self, monthly_expenses_dict):

        income_and_spending = []
        for month in monthly_expenses_dict:
            formated_month = [
                {"name": name, "amount": month.get(name)} for name in month]

            income_and_spending.append(
                self.divide_spending_and_income(formated_month))

        return income_and_spending

    def get_net_profit_and_totals_from_months(self, monthly_expenses_dict):
        for month in monthly_expenses_dict:
            total_income = sum([item.get("amount")
                               for item in month.get("income")])
            total_expenses = sum([item.get("amount") for item in month.get(
                "spending") if item.get("name") != "date"])
            net_profit = total_income - total_expenses
            month["summary"] = [
                {"name": "total_income", "amount": round(total_income, 2)},
                {"name": "total_expenses", "amount": round(total_expenses, 2)},
                {"name": "net_profit", "amount": round(net_profit, 2)}
            ]

        return monthly_expenses_dict

    def get_month_before(self, month, monthly_expenses_with_profit_and_totals):
        date_str = [item.get("amount") for item in month.get(
            "spending") if item.get("name") == "date"][0]
        date = datetime.strptime(date_str, "%Y-%m-%d")

        date_1 = (date - relativedelta(months=1)).date()
        month_d_1 = None
        for month in monthly_expenses_with_profit_and_totals:
            proposed_date = [item.get("amount")
                             for item in month.get("spending") if item.get("name") == "date"][0]

            if str(proposed_date) == str(date_1):
                month_d_1 = month
                break
            else:
                continue

        if month_d_1 is None:
            return None
        return month_d_1

    def get_difference_between_months(self, monthly_expenses_with_profit_and_totals):
        for month_d in monthly_expenses_with_profit_and_totals:
            month_d_1 = self.get_month_before(
                month_d, monthly_expenses_with_profit_and_totals)

            if not month_d_1:
                continue

            for category in month_d:
                item_list_d = month_d.get(category)
                item_list_d_1 = month_d_1.get(category)

                for item_d in item_list_d:
                    if isinstance(item_d, str) or item_d.get("name") == "date":
                        continue
                    amount_d = item_d.get("amount")

                    item_d_1 = next(iter([item for item in item_list_d_1 if item.get(
                        "name") == item_d.get("name")]), None)

                    if not item_d_1:
                        item_d["diff"] = None
                        continue

                    amount_d_1 = item_d_1.get("amount")

                    item_d["diff"] = round(
                        ((amount_d - amount_d_1) / abs(amount_d))*100, 2)

            # pprint(month_d)
        return monthly_expenses_with_profit_and_totals

    def structure_output_monthly_recap(self, monthly_recap):
        final_output = {}
        for month in monthly_recap:
            date_item = [item for item in month.get(
                "spending") if item.get("name") == "date"][0]
            date = date_item.get("amount")
            month.get("spending").remove(date_item)
            final_output[date] = month

        return final_output

    def get_monthly_recap_graphs(self, monthly_recap_dict):
        pprint(monthly_recap_dict)
        res_dict = {}
        for month, month_dict in monthly_recap_dict.items():
            flattened_dict = month_dict.get(
                "income") + month_dict.get("spending") + month_dict.get("summary")
            for item in flattened_dict:
                if item.get("name") not in res_dict.keys():
                    res_dict[item.get("name")] = {
                        "data": [], "label": [], "diff": []}

                res_dict[item.get("name")].get(
                    "data").append(item.get("amount"))
                res_dict[item.get("name")].get(
                    "label").append(month)
                diff = item.get("diff") if item.get("diff") is not None else 0
                res_dict[item.get("name")].get(
                    "diff").append(diff)

        formatted_res = []
        for name, data in res_dict.items():
            formatted_res.append(
                {"name": name, "formated_name": name.replace(" ", "_"), "data": data})

        return formatted_res

    def get_monthly_recap(self):
        monthly_expenses_dict = self.mongo_handler.get_budget_history()

        divided_income_and_spending = self.divide_monthly_income_and_spending(
            monthly_expenses_dict)

        monthly_expenses_with_profit_and_totals = self\
            .get_net_profit_and_totals_from_months(divided_income_and_spending)

        monthly_expenses_with_percentage_diff = self\
            .get_difference_between_months(monthly_expenses_with_profit_and_totals)

        structured_monthly_recap = self\
            .structure_output_monthly_recap(monthly_expenses_with_percentage_diff)

        myKeys = sorted(list(structured_monthly_recap.keys()), reverse=True)
        sorted_dict = {i: structured_monthly_recap[i] for i in myKeys}
        reversed_structured_monthly_recap = sorted_dict

        return reversed_structured_monthly_recap

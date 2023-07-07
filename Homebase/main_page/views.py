from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Models
from models.budget_handler import BudgetHandler
from models.mongo_handler import MongoHandler
from models.bill_handler import BillHandler

# Create your views here.
from django.shortcuts import render
from pprint import pprint


def home(request):
    context = {}
    return render(request, "main_page/home.html", context)


def budget(request):
    print("budget")
    budget_handler = BudgetHandler()
    bill_handler = BillHandler()

    if request.method == "POST":
        print("Post request")
        data = request.POST

        if data.get("type") == "update_budget_history":
            budget_handler.update_backlog()
        elif data.get("type") == "update_monthly_budget":
            budget_handler.update_monthly_budget()

        current_budget = budget_handler.get_monthly_budget()
        monthly_bills = bill_handler.get_dates()

        context = {
            "budget": current_budget.get("week_dict"),
            "total_spending": current_budget.get("total_spending"),
            "current_month_spending": current_budget.get("current_month_categories"),
            "salary": budget_handler.salary,
            "savings": budget_handler.savings,
            "bills": monthly_bills,
            "data_time": current_budget.get("data_time")
        }

        return JsonResponse(context)

    elif request.method == "GET":
        print("Get request")
        # current_budget = list(mongo_handler.get_budget_current_week())
        current_budget = budget_handler.get_monthly_budget()
        monthly_bills = bill_handler.get_dates()
        if request.GET.get("type", None) == "app":
            print("APP ACCESSING")
            context = {
                "budget": current_budget.get("week_dict"),
                "total_spending": current_budget.get("total_spending"),
                "current_month_spending": current_budget.get("current_month_categories"),
                "salary": budget_handler.salary,
                "savings": budget_handler.savings,
                "bills": monthly_bills,
                "data_time": current_budget.get("data_time")
            }
            return JsonResponse(context)

    context = {
        "budget": current_budget.get("week_dict"),
        "total_spending": current_budget.get("total_spending"),
        "current_month_spending": current_budget.get("current_month_categories"),
        "salary": budget_handler.salary,
        "savings": budget_handler.savings,
        "bills": monthly_bills,
        "data_time": current_budget.get("data_time")
    }
    print(current_budget.get("current_month_categories"))
    return render(request, "main_page/budget.html", context)


def monthly_recap(request):

    budget_handler = BudgetHandler()

    if request.method == "GET":
        monthly_recap = budget_handler.get_monthly_recap()

    context = {
        "monthly_recap": monthly_recap
    }
    pprint(context)
    return render(request, "main_page/monthly_recap.html", context)

from django.shortcuts import render
from django.http import HttpResponse

# Models
from models.budget_handler import BudgetHandler
from models.mongo_handler import MongoHandler

# Create your views here.
from django.shortcuts import render


def index(request):
    context = {}
    return render(request, "main_page/index.html", context)


def budget(request):
    print("budget")
    budget_handler = BudgetHandler()
    mongo_handler = MongoHandler()

    if request.method == "POST":
        print("Post request")
        data = request.POST

        if data.get("type") == "update_budget_history":
            budget_handler.update_backlog()
        elif data.get("type") == "update_monthly_budget":
            budget_handler.update_monthly_budget()

        current_budget = list(mongo_handler.get_budget_current_week())

    elif request.method == "GET":
        print("Get request")
        # current_budget = list(mongo_handler.get_budget_current_week())
        current_budget = budget_handler.get_monthly_budget()

    print(current_budget)
    context = {
        "budget": current_budget.get("week_dict"),
        "salary": budget_handler.salary,
        "savings": budget_handler.savings,
        "total_spending": current_budget.get("total_spending")
    }
    return render(request, "main_page/budget.html", context)

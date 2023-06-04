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

        if data.get("type") == "update_budget":
            budget = budget_handler.get_monthly_budget()
            mongo_handler.update_budget_current_week(budget)

    elif request.method == "GET":
        print("Get request")
        history = list(mongo_handler.get_budget_current_week())
        print(history)

    context = {
        "budget": history,
        "salary": budget_handler.salary,
        "savings": budget_handler.savings,
        "test_objects": [
            {"value": 1},
            {"value": 2},
            {"value": 3},
            {"value": 4},
        ]
    }
    return render(request, "main_page/budget.html", context)

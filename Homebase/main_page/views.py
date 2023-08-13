from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse

# Models
from models.budget_handler import BudgetHandler
from models.bill_handler import BillHandler

from models.budget.month import Month
from models.budget.year import Year
from models.budget.person import Person
from models.requests.request_utils import get_request

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

    m = Month(str(datetime.today().date()))
    p = Person()

    if request.method == "POST":
        print("Post request")
        data = request.POST

        if data.get("type") == "update_budget_history":
            budget_handler.update_backlog()
        elif data.get("type") == "update_monthly_budget":
            budget_handler.update_monthly_budget()
            budget_handler.update_current_month_movements()
        elif data.get("type") == "update_bills":
            print("Update bills")
            bill_handler.update_dates()

        res = get_request("budget", request.method, m, p)

        return JsonResponse(res)

    elif request.method == "GET":
        print("Get request")

    res = get_request("budget", request.method, m, p)
    pprint(res)
    return render(request, "main_page/budget.html", res)


def monthly_recap(request):

    budget_handler = BudgetHandler()
    y = Year(str(datetime.now().date()))

    if request.method == "POST":
        if request.POST.get("type") == "update monthly recap":
            print("Updating Backlog")
            budget_handler.update_backlog()
        return JsonResponse({})

    if request.method == "GET":
        monthly_recap = budget_handler.get_monthly_recap()
        graph_data = budget_handler.get_monthly_recap_graphs(monthly_recap)

    from pprint import pprint
    pprint(monthly_recap)

    context = {
        "monthly_recap": monthly_recap,
        "graph_data": graph_data
    }
    return render(request, "main_page/monthly_recap.html", context)

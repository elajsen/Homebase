from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from models.Account.user_handler import UserHandler
# Create your views here.


def account_page(request):
    user_handler = UserHandler()
    print("We made it")

    username = "elias_test"
    password = "password"
    data_dict = {"username": username,
                 "password": password}

    if request.method == "POST":
        type = request.POST.get("type")

        if type == "create_account":
            print("create_account")
            res = user_handler.create_user(**data_dict)
            print(res)
        elif type == "delete_account":
            print("delete_account")
            res = user_handler.delete_user(**data_dict)
            print(res)
        elif type == "login_user":
            print("login_user")
            res = user_handler.login_user(request, **data_dict)
            print(res)
        elif type == "logout_user":
            print("logout_user")
            res = user_handler.logout_user(request)
            print(res)

    context = {
        "return": 1
    }

    return render(request, "account_handler/index.html", context)

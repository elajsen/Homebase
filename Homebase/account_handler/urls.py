from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.account_page, name="home"),
    path("", include("allauth.urls"))
]

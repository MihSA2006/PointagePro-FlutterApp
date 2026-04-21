from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.admin_dashboard, name="index"),
    path("login/", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    path("employee/add/", views.add_employee, name="add_employee"),
]

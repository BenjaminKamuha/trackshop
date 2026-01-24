from django.urls import path
from . import views

app_name = "Account"

urlpatterns = [
    path('', views.index, name='index'),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/create-shop", views.create_shop, name="create-shop"),
    path("switch-shop/", views.switch_shop, name="switch_shop"),
    path("settings/", views.settings, name="setting"),
]
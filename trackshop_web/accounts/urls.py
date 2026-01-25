from django.urls import path
from . import views

app_name = "Account"

urlpatterns = [
    path('', views.index, name='index'),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/create-shop", views.create_shop, name="create-shop"),
    path("switch-shop/", views.switch_shop, name="switch-shop"),
    path("settings/", views.settings, name="setting"),
    path("settings/edit_profil/<int:user_id>/", views.edit_account, name="edit-profile"),
    path("settings/edit_shop/<int:shop_pk>/", views.edit_shop, name='edit-shop'),
]
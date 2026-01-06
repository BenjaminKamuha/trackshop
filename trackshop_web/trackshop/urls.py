from django.urls import path
from . import views

app_name = "TrackShop"

urlpatterns = [
	path('', views.index, name='index'),
	path('dashboard', views.dashboard, name='dashboard'),
	path('new_stock/', views.new_stock, name='new_stock'),
	path('new_client/', views.new_client, name='new_client'),
	path('client/', views.client, name="client"),
	path('client/<int:client_pk>', views.load_client_sub_menu, name="client_sub_menu"),
	path('client/<int:client_pk>/general', views.client_general_info, name="client_general_info"),
	path('client/<int:client_pk>/commercial', views.client_commercial_info, name="client_commercial_info"),
	path('client/<int:client_pk>/sales', views.client_sales_info, name="client_sales_info"),
	path('client/<int:client_pk>/financial', views.client_financial_info, name="client_financial_info"),
	path('client/<int:client_pk>/statistics', views.client_statistics, name="client_statistics"),
	path('client/<int:client_pk>/fallow', views.fallow_client, name="fallow_client"),
	path('client/<int:client_pk>/sales_history', views.sales_history, name="sales_history"),
	path('stock/', views.stock, name="stock"),
	path('stock/load_product/<int:stock_pk>', views.load_stock_product, name="load_stock_product"),
	path('stock/new_product/<int:stock_pk>', views.new_product, name="new_product"),
	path('stock/product/details/<int:product_pk>', views.product_detail, name="product_details"),
	path('sale/', views.sale, name="sale"),
	path('cash_book/', views.cash_book, name="cash_book"),
	path('debt/', views.debt, name="debt"),
	path('setting/', views.setting, name='setting'),
]
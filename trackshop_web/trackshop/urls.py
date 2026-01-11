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
	path('cash_book/', views.cash_book, name="cash_book"),
	path('history/', views.history, name="history"),
	path('setting/', views.setting, name='setting'),
	path('sale/new/', views.sale_create, name='sale-create'),
	path('sale/save/', views.sale_save, name='sale-save'),
	path('sale/add-row/', views.sale_add_row, name='sale-add-row'),
	path('sale/<int:sale_id>/invoice/', views.sale_invoice, name='sale-invoice'),
	path('sale/<int:sale_id>/invoice/pdf/', views.sale_invoice_pdf, name="sale-invoice-pdf"),
	path('sale/search_client/', views.search_client, name="search-client"),
	path('sale/search_product/', views.search_product, name="search-product"),
	path('sale/results/select_product/<int:product_pk>/', views.select_product, name="select-product"),
	path('sale/add_payment/<int:sale_id>', views.add_payment, name="add-payment"),
]
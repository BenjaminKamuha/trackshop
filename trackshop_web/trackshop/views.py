from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.http import HttpResponse
from .forms import StockForm, ProductForm, ClientForm
from .models import (
	Stock, 
	Client, 
	ClientDebt, 
	Spending, 
	Sale,
	Product,
	)

# Create your views here.
def index(request):
	return render(request, "trackshop/index.html")


def dashboard(request):
	# nombre de stock
	today = timezone.now().date()
	stocks = Stock.objects.all()
	clients = Client.objects.all()
	debts = ClientDebt.objects.all()
	todaySales = Sale.objects.filter(date=today)
	todaySpending = Spending.objects.filter(date=today)
	
	return render(request, "trackshop/dashboard.html", context={
		"stocks": stocks,
		"clients": clients,
		"debts": debts,
		"todaySales": todaySales,
		"todaySpending": todaySpending,
		})

def new_stock(request):
	if request.method == "POST":
		stock_form = StockForm(request.POST)
		if stock_form.is_valid():
			stock = stock_form.save(commit=False)
			stock.last_access_date = timezone.now()
			stock.save()
			return redirect("TrackShop:stock")
		else:
			return render(request, "trackshop/dashboard.html", context={"stock_form": stock_form})
		
	stock_form = StockForm()
	return render(request, "trackshop/new_stock.html", context={"stock_form": stock_form})


def new_client(request):
	if request.method == "POST":
		client_form = ClientForm(request.POST)
		if client_form.is_valid():
			client_form.save()
			return redirect("TrackShop:dashboard")
		else:
			return render(request, "trackshop/new_client.html", context={"client_form": client_form})

	client_form = ClientForm()
	return render(request, "trackshop/new_client.html", context={"client_form": client_form})

def client(request):

	return render(request, "trackshop/client.html", context={})

def stock(request):
	stocks = Stock.objects.all()
	last_access_stock = Stock.objects.order_by("-last_access_date").first()
	return render(request, "trackshop/stock.html", context={"stocks": stocks, "stock": last_access_stock})

def load_stock_product(request, stock_pk):
	stock = Stock.objects.get(pk=stock_pk)
	stock.last_access_date = timezone.now()
	stock.save()
	products = Product.objects.filter(stock=stock_pk)
	try:
		product = Product.objects.get(pk=stock.last_access_product_id)
		print(product)
		return render(request, "trackshop/partials/partial_product.html", context={"products": products, "product": product, "stock": stock})

	except:
		pass
	
	return render(request, "trackshop/partials/partial_product.html", context={"products": products, "stock": stock})

def new_product(request, stock_pk):
	stock = get_object_or_404(Stock, pk=stock_pk)
	if request.method == 'POST':
		product_form = ProductForm(request.POST)
		if product_form.is_valid():
			product = product_form.save(commit=False)
			product.stock = stock
			product_form.save()
			return redirect("TrackShop:stock")
		else:
			return render(request, "trackshop/new_product.html", context={"product_form": product_form, "stock": stock})
			
	product_form = ProductForm()
	return render(request, "trackshop/new_product.html", context={"product_form": product_form, "stock": stock})

def product_detail(request, product_pk):
	product = get_object_or_404(Product, pk=product_pk)
	stock = product.stock 
	stock.last_access_product_id = product_pk
	stock.save()
	return render(request, "trackshop/partials/partial_product_detail.html", context={"product": product})


def sale(request):
	return render(request, "trackshop/sale.html")


def cash_book(request):
	return render(request, "trackshop/cashbook.html", context={})

def setting(request):
	return render(request, "trackshop/setting.html", context={})

def debt(request):
	return render(request, "trackshop/debt.html", context={})
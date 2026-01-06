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
from django.db.models import Sum 

now = timezone.now()

def index(request):
	return render(request, "trackshop/index.html")


def dashboard(request):
	# nombre de stock
	today = timezone.now().date()
	stocks = Stock.objects.all()
	clients = Client.objects.all()
	debts = ClientDebt.objects.all()
	todaySales = Sale.objects.filter(sale_date=today)
	todaySpending = Spending.objects.filter(date=today)
	
	return render(request, "trackshop/dashboard.html", context={
		"stocks": stocks,
		"clients": clients,
		"debts": debts,
		"todaySales": todaySales,
		"todaySpending": todaySpending,
		})

def new_stock(request):
	source = request.GET.get("from")
	if request.method == "POST":
		source = request.POST.get("from")
		print(source)

		stock_form = StockForm(request.POST)
		if stock_form.is_valid():
			stock = stock_form.save(commit=False)
			stock.last_access_date = timezone.now()
			stock.save()
			if source == "dashboard":
				return redirect("TrackShop:dashboard")
			else:
				return redirect("TrackShop:stock")
		else:
			return render(request, "trackshop/dashboard.html", context={"stock_form": stock_form})
		
	stock_form = StockForm()
	return render(request, "trackshop/new_stock.html", context={"stock_form": stock_form, "source": source})


def new_client(request):
	source = request.GET.get("from")
	if request.method == "POST":
		source = request.POST.get("from")
		print(f'from {source}')
		client_form = ClientForm(request.POST)
		if client_form.is_valid():
			client_form.save()
			if source == "dashboard":
				return redirect("TrackShop:dashboard")
			else:
				return redirect("TrackShop:client")
		else:
			return render(request, "trackshop/new_client.html", context={"client_form": client_form})

	client_form = ClientForm()
	return render(request, "trackshop/new_client.html", context={"client_form": client_form, "source": source})

def client(request):
	clients = Client.objects.all()
	return render(request, "trackshop/client.html", context={"clients": clients})

def load_client_sub_menu(request, client_pk):
	client = get_object_or_404(Client, pk=client_pk)
	return render(request, "trackshop/partials/client/load_client_sub_menu.html", context={
		"client": client,
	})


def client_general_info(request, client_pk):
	client = get_object_or_404(Client, pk=client_pk)

	return render(request, "trackshop/partials/client/client_general_info.html", context={
		"client": client,
	})


def client_commercial_info(request, client_pk):

	return render(request, "trackshop/partials/client/commercial_info.html", context={})

def sales_history(request, client_pk):
	client = get_object_or_404(Client, pk=client_pk)
	client_sales = Sale.objects.filter(client=client)
	revenue = Sale.objects.filter(client=client).aggregate(total=Sum('payedAmount'))['total'] or 0
	top_product = (Sale.objects.filter(client=client).values('product__id', 'product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity').first())
		
	return render(request, "trackshop/partials/client/sales_history.html", context={"client_sales": client_sales, "client":client, "revenue": revenue, "top_product": top_product})

def client_sales_info(request, client_pk):

	return render(request, "trackshop/partials/client/sales_info.html", context={})

def client_financial_info(request, client_pk):

	return render(request, "trackshop/partials/client/financial_info.html", context={})

def client_statistics(request, client_pk):

	return render(request, "trackshop/partials/client/statistics.html", context={})

def fallow_client(request, client_pk):

	return render(request, "trackshop/partials/client/fallow.html", context={})

	

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
		return render(request, "trackshop/partials/product/partial_product.html", context={"products": products, "product": product, "stock": stock})

	except:
		pass
	
	return render(request, "trackshop/partials/product/partial_product.html", context={"products": products, "stock": stock})

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
	evaliable_quantity = product.quantity - product.sales.count()
	sales_this_month = Sale.objects.filter(
		product=product,
		sale_date__year= now.year,
		sale_date__month=now.month
	).count()

	total_revenue = product.quantity * product.price 
	sales_revenue = product.sales.count() * product.price
	stock = product.stock 
	stock.last_access_product_id = product_pk
	stock.save()
	return render(request, "trackshop/partials/product/partial_product_detail.html", context={
		"product": product, 
		"sales_this_month": sales_this_month,
		"evaliable_quantity": evaliable_quantity,
		"sales_revenue": sales_revenue,
		"total_revenue": total_revenue,
		})


def sale(request):
	return render(request, "trackshop/sale.html")


def cash_book(request):
	return render(request, "trackshop/cashbook.html", context={})

def setting(request):
	return render(request, "trackshop/setting.html", context={})

def debt(request):
	return render(request, "trackshop/debt.html", context={})
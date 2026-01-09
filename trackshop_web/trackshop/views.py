from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import transaction
from django.db.models import Sum
from .forms import StockForm, ProductForm, ClientForm
from .models import (
	Stock, 
	Client, 
	ClientDebt, 
	Spending, 
	Sale,
	Product,
	SaleItem,
	)

from django.template.loader import render_to_string
from weasyprint import HTML
from decimal import Decimal
from random import choice

@transaction.atomic
def add_payment(sale, amount, method):
	Payment.objects.create(
		sale=sale,
		amount=amount,
		payment_method=method
	)
	total_paid = sale.payments.aggregate(
		total=Sum('amount'))['total'] or 0
	
	sale.paid_amount = total_paid
	sale.is_credit = total_paid < sale.total_amount
	sale.save()


now = timezone.now()

def index(request):
	return render(request, "trackshop/index.html")


def dashboard(request):
	# nombre de stock
	today = timezone.now().date()
	stocks = Stock.objects.all()
	clients = Client.objects.all()
	debts = ClientDebt.objects.all()
	todaySales = Sale.objects.filter(created_at=today)
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
	revenue = 0
	# Calcule du chiffre d'affaire du client
	total_revenu = Sale.objects.filter(client=client).aggregate(total=Sum('total_price'))['total'] or 0
		
	return render(request, "trackshop/partials/client/sales_history.html", context={"client_sales": client_sales, "client":client})

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
	evaliable_quantity = product.quantity - product.items.count()
	sales_this_month = SaleItem.objects.filter(
		product=product,
	).count()

	total_revenue = product.quantity * product.price 
	stock = product.stock 
	stock.last_access_product_id = product_pk
	stock.save()
	return render(request, "trackshop/partials/product/partial_product_detail.html", context={
		"product": product, 
		"sales_this_month": sales_this_month,
		"evaliable_quantity": evaliable_quantity,
		"total_revenue": total_revenue,
		})


def sale(request):
		
	return render(request, "trackshop/sale.html", context={})


def cash_book(request):
	return render(request, "trackshop/cashbook.html", context={})

def setting(request):
	return render(request, "trackshop/setting.html", context={})

def debt(request):
	return render(request, "trackshop/debt.html", context={})


def add_payment_view(request, sale_id):
	sale = get_object_or_404(Sale, pk=sale_id)

	amount = Decimal(request.POST['amount'])
	method = request.POST['payement_method']

	add_payment(sale, amount, method)

	return render(request, "partials/sale/sale_summary.html", {"sale": sale})


def sale_invoice(request, sale_id):
	sale = Sale.objects.get(pk=sale_id)
	return render(request, "trackshop/sale_invoice.html", {"sale": sale})


def sale_invoice_pdf(request, sale_id):
	sale = get_object_or_404(Sale, pk=sale_id)
	html_string = render_to_string(
		"trackshop/sale_invoice.html",
		{"sale": sale}
	)

	pdf = HTML(string=html_string).write_pdf()
	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename="facture_{sale.id}.pdf"'
	return response

def sale_create(request):
	random_product = choice(Product.objects.all())
	return render(request, "trackshop/sale_form.html", {
		"clients": Client.objects.all(),
		"products": Product.objects.all(),
		"random_product": random_product,
	})

def sale_add_row(request):
	selected_ids = request.GET.getlist('product_id[]')
	products = Product.objects.exclude(id__in=selected_ids)
	print(selected_ids)

	return render(request, "trackshop/partials/sale/sale_row.html", {
		"products": products
	})

@transaction.atomic
def sale_save(request):
	product_ids = request.POST.getlist("product_id[]")
	print(product_ids)
	if len(product_ids) != len(set(product_ids)):
		return HttpResponseBadRequest("Produit dupliqué")

	quantities = request.POST.getlist("quantity[]")
	print(quantities)

	client_id = request.POST.get("client_id")


	client = Client.objects.get(id=client_id)
	print(client)
	sale = Sale.objects.create(
		client=client,
		total_amount=0
	)

	total = Decimal("0")
	for product_id, qty in zip(product_ids, quantities):
		product = Product.objects.get(id=product_id)
		qty = int(qty)

		line_total = product.price * qty 
		SaleItem.objects.create(
			sale=sale,
			product=product,
			quantity=qty,
			unit_price=product.price,
			total_price=line_total
		)

		product.quantity -= qty
		product.save()

		total += line_total 

	
	sale.total_amount = total 
	sale.save()

	return redirect("TrackShop:sale-invoice", sale_id=sale.id)
	



def search_client(request):
	search_input = request.GET.get('client_search', '')
	clients = Client.objects.filter(complete_name__icontains=search_input)[:10]

	return render(request, 'trackshop/partials/sale/client_result.html', {
		'clients': clients
	})

def search_product(request):
    q = request.GET.get("product_search", "")
    products = Product.objects.filter(name__icontains=q, stock__gt=0)
    return render(request, "trackshop/partials/sale/product_results.html", {
        "products": products
    })

def select_product(request, product_pk):
	selected_ids = request.POST.getlist("prod_selected[]")
	print(selected_ids)
	product = Product.objects.get(pk=product_pk)

	excluded_ids = [int(pid) for pid in selected_ids if pid.isdigit()]

	return render(request, "trackshop/partials/sale/sale_row_selected.html", {
        "product": product,
		"nb_product": len(excluded_ids),
    })
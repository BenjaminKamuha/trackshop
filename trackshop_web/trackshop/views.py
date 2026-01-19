from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, F, DecimalField
from .forms import StockForm, ProductForm, ClientForm
from .models import (
	Stock, 
	Client, 
	ClientDebt, 
	Spending, 
	Sale,
	Product,
	SaleItem,
	Payment,
	ProductReturn,
	Inventory,
	InventoryItem,
	InventorySummary,
	Currency,
	ExchangeRate,
	Provider,
	Purchase,
	PurchaseItem,
	ProviderPayment,

	)

from django.template.loader import render_to_string
from weasyprint import HTML
from decimal import Decimal
from random import choice

now = timezone.now()

def index(request):
	return render(request, "trackshop/index.html")

def set_exchange_rate(request):

	last_rate = ExchangeRate.objects.all().last()
	
	if request.method == "POST":
		from_code = request.POST['from_currency']
		to_code = request.POST['to_currency']
		rate = request.POST['rate']

		ExchangeRate.objects.update_or_create(
			from_currency=Currency.objects.get(code=from_code),
			to_currency=Currency.objects.get(code=to_code),
			date=now.date(),
			defaults={"rate": rate}
		)
		print("Taux enregistré")
		return redirect ("TrackShop:dashboard")

	return render(request, "trackshop/set_exchange_rate.html", {'last_rate': last_rate })

def get_today_rate(from_currency, to_currency):
	try:
		return ExchangeRate.objects.get(
			from_currency=from_currency,
			to_currency=to_currency,
			date=now.date()
		).rate 

	except ExchangeRate.DoesNotExist:
		raise ValidationError("Taux du jour non défini")

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
	evaliable_quantity = product.quantity
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

@transaction.atomic
def create_inventory(start_date, end_date, inv_type):
	# Création de l'objet inventaire
	inventory = Inventory.objects.create(
		start_date=start_date,
		end_date=end_date,
		inventory_type=inv_type
	)

	# Génération des lignes
	for product in Product.objects.all():
		InventoryItem.objects.create(
			inventory=inventory,
			product=product,
			system_quantity=product.quantity,
			physical_quantity=product.quantity,
			difference=0
		)

	# Calcul des ventes
	total_sales = (
		SaleItem.objects.filter(
			sale__created_at__range=[inventory.start_date, inventory.end_date]
		).aggregate(
			total=Sum(F('quantity') * F('unit_price'))
		)['total'] or Decimal('0')
	)

	# Calcul des retours
	total_returns = (
		ProductReturn.objects.filter(
			date__range=[inventory.start_date, inventory.end_date]
		).aggregate(
			total=Sum(F('quantity') * F('sale_item__unit_price'))
		)['total'] or Decimal('0')
	)
	# Calcul des paiements
	total_paid = (
		Payment.objects.filter(
			created_at__range=[inventory.start_date, inventory.end_date]
		).aggregate(
			total=Sum('amount')
			)['total'] or Decimal('0')
	)

	# Calcul du crédit
	total_credit = (
		Sale.objects.filter(                                    
			created_at__lte=inventory.end_date, 
			is_credit=True
		).aggregate(
			total=Sum(
				F('total_amount') - F('paid_amount'),
				output_field=DecimalField()
			)
		)['total'] or Decimal('0')
	)

	# Résumé final
	InventorySummary.objects.create(
		inventory=inventory,
		total_sales=total_sales,
		total_returns=total_returns,
		net_revenue=total_sales - total_returns,
		total_paid=total_paid,
		total_credit=total_credit
	)

	# Cloture de l'inventair
	inventory.closed = True 
	inventory.save() 


def inventory(request):
	inventories = Inventory.objects.all()
	last_created = Inventory.objects.all().last()
	return render(request, "trackshop/inventory.html", context={"last_created": last_created, "inventories": inventories})

def new_inventory_view(request):
	if request.method == "POST":
		start_date = request.POST['start_date']
		end_date = request.POST['end_date']
		inventory_type = request.POST['inventory_type']

		# Création de l'inventaire
		create_inventory(start_date, end_date, inventory_type)
		return redirect('TrackShop:inventory')

	return render(request, "trackshop/partials/inventory/inventory_form.html", {})

def load_inventory(request, inv_pk):
	inventory = get_object_or_404(Inventory, pk=inv_pk)
	return render(request, "trackshop/partials/inventory/inventory_view.html", {'inventory':inventory})
			
		
def history(request):
	sales = Sale.objects.all().order_by("-created_at")
	return render(request, "trackshop/history.html", context={"sales": sales})


def add_payment(request, sale_id):
	sale = get_object_or_404(Sale, pk=sale_id)
	if request.method == 'POST':
		currency_code = request.POST.get("currency")
		amount = Decimal(request.POST['amount'])
		
		currency = Currency.objects.get(code=currency_code)
		base_currency = Currency.objects.get(code="USD")

		rate = (
			ExchangeRate.objects.filter(from_currency=currency, to_currency=base_currency).latest('date').rate
		)

		sale.add_payment(Decimal(amount, currency, rate)) 

		return render(request, "trackshop/partials/sale/payment_succes.html",  {"sale": sale} )

	return render(request, "trackshop/add_payment.html", {"sale": sale})


def add_provider_payment(purchase, amount, currency):
	if currency.code != purchase.currency.code:
		amount = amount / purchase.exchange_rate 

	purchase.paid_amount += amount
	purchase.save()

def provider_payment(request, purchase_pk):
	
	purchase = get_object_or_404(Purchase, pk=purchase_pk)
	if request.method == "POST":
		amount = request.POST['amount']
		currency_code = request.POST['currency_code']

		currency = Currency.objects.get(code=currency_code)
		
		add_provider_payment(purchase, Decimal(amount), currency)

		return redirect("TrackShop:payment-success")
	return render(request, "trackshop/provider_payment.html", {'purchase':purchase})

def payment_succes(request):
	return render(request, "trackshop/payment_success.html")


def sale_invoice(request, sale_id):
	sale = Sale.objects.get(pk=sale_id)
	return render(request, "trackshop/sale_invoice.html", {"sale": sale})


def sale_invoice_pdf(request, sale_id):
	sale = get_object_or_404(Sale, pk=sale_id)
	is_cdf = sale.currency.code == 'CDF'
	html_string = render_to_string(
		"trackshop/sale_invoice.html",
		{"sale": sale, 'is_cdf': is_cdf}
	)

	pdf = HTML(string=html_string).write_pdf()
	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename="facture_{sale.id}.pdf"'
	return response

def sale_create(request, message=None):
	
	rate = get_today_rate(
		from_currency=Currency.objects.get(code="CDF"),
		to_currency=Currency.objects.get(code="USD")
	)
	
	return render(request, "trackshop/sale_form.html", {
		"clients": Client.objects.all(),
		"products": Product.objects.all(),
		'rate': rate,
		"message": message,
	})

def sale_add_row(request):
	selected_ids = request.GET.getlist('product_id[]')
	products = Product.objects.exclude(id__in=selected_ids)
	print(selected_ids)

	return render(request, "trackshop/partials/sale/sale_row.html", {
		"products": products
	})  

@transaction.atomic
def create_purchase(request):

	rate = get_today_rate(
		from_currency=Currency.objects.get(code="CDF"),
		to_currency=Currency.objects.get(code="USD")
	)

	if request.method == "POST":
		provider = Provider.objects.get(id=request.POST["provider_id"])
		#exchange_rate =  Decimal(request.POST["exchange_rate"])

		currency_code = request.POST.get("currency") # Récuprération ddu code de la devise de la vente
		currency = Currency.objects.get(code=currency_code) # Obtenir la dévide
		base_currency = Currency.objects.get(code="USD")

		rate = (
			ExchangeRate.objects.filter(from_currency=currency, to_currency=base_currency).latest('date').rate
		)

		purchase = Purchase.objects.create(
			provider=provider,
			currency=currency,
			exchange_rate=rate,
			total_amount=0,
			paid_amount=0
		)

		total = Decimal(0)
		total_paid_amount = Decimal(0)

		product_ids = request.POST.getlist("product_id[]")
		quantities = request.POST.getlist("quantity[]")
		unit_costs = request.POST.getlist("unit_cost[]")
		paid_amounts = request.POST.getlist("paidAmount[]")	# Récupération des différentes montants payés


		for pid, qty, cost, amount in zip(product_ids, quantities, unit_costs, paid_amounts):
			product = Product.objects.get(id=pid)
			qty = int(qty)
			cost = Decimal(cost)
			line_total = qty * cost 

			PurchaseItem.objects.create(
				purchase=purchase,
				product=product,
				quantity=qty,
				unit_cost=cost,
				total_cost=line_total
			)



			# Autgmenter le stock
			product.quantity += qty
			product.save()
			total += line_total                       
			total_paid_amount += Decimal(amount)

		purchase.total_amount = total
		purchase.paid_amount = total_paid_amount / rate
		purchase.save()

		# Paiement
		paid_amount = request.POST.get("paid_amount")
		if paid_amount:
			payment_currency = Currency.objeccts.get(code=request.POST["payment_currency"])
			amount = Decimal(paid_amount)

			if payment_currency.code == "CDF":
				amount = amount / rate

			ProviderPayment.objects.create(
				purchase=purchase,
				currency=payment_currency,
				amount=Decimal(paid_amount)
			)

			purchase.paid_amount += amount 
			purchase.save()
		
		return redirect("TrackShop:purchase-detail", purchase.id) 

	return render(request, "trackshop/purchase_form.html", {
		'rate': rate,
		'providers': Provider.objects.all(),
		'products': Product.objects.all(),
	
	})


def purchase_detail(request, purchase_pk):

	purchase = get_object_or_404(Purchase, pk=purchase_pk)
	return render(request, "trackshop/purchase_detail.html", {"purchase": purchase})


@transaction.atomic
def sale_save(request):

	currency_code = request.POST.get("currency") # Récuprération ddu code de la devise de la vente

	currency = Currency.objects.get(code=currency_code) # Obtenir la dévide
	base_currency = Currency.objects.get(code="USD")

	rate = (
		ExchangeRate.objects.filter(from_currency=currency, to_currency=base_currency).latest('date').rate
	)

	product_ids = request.POST.getlist("product_id[]") 	# Récupération des ids des produits séléctionnée
	if len(product_ids) != len(set(product_ids)): 		
		return HttpResponseBadRequest("Produit dupliqué")

	quantities = request.POST.getlist("quantity[]")		# Récupération des différentes quantités

	paid_amounts = request.POST.getlist("paidAmount[]")	# Récupération des différentes montants payés

	client_id = request.POST.get("client_id")			# Récupération de l'id du client qui achète
	if client_id:
		client = Client.objects.get(id=client_id)
	else:
		return render(request, "trackshop/sale_form.html", {
		"clients": Client.objects.all(),
		"products": Product.objects.all(),
		"message": "Erreur! vous dévez séléctionner un client d'abord",
	})
	
	# Création de la vente
	sale = Sale.objects.create(
		client=client,
		currency=currency,
		exchange_rate=rate, 
		total_amount=0,
		total_amount_base=0
	)

	total = Decimal("0")
	total_paid_amount = Decimal("0")

	for product_id, qty, paid_amount in zip(product_ids, quantities, paid_amounts):

		# Récupération du produit et du quantité d'un produit
		product = Product.objects.get(id=product_id)
		qty = int(qty)
		paid_amount = Decimal(paid_amount)

		line_total = product.price * qty   # Prix à payer pour le produit en cours

		# Création de la premiere ligne (Une ligne = un produit "item")
		SaleItem.objects.create(
			sale=sale,
			product=product,
			quantity=qty,
			unit_price=product.price,
			total_price=line_total,
			paid_amount=paid_amount/rate if currency_code=="CDF" else paid_amount
		)

		# On diminue la quantité acheté du produit
		product.quantity -= qty
		product.save()


		total += line_total * rate
		total_paid_amount += paid_amount  


	# test

	# verifier si c'est une vente en crédit
	if (total_paid_amount < total):
		sale.is_credit = True

	sale.total_amount = total 
	sale.total_amount_base = total / rate 
	sale.paid_amount = total_paid_amount
	sale.paid_amount_base = total_paid_amount / rate
	
	sale.save() # Enregistrement de la vente

	return redirect("TrackShop:sale-invoice-pdf", sale_id=sale.id)


@transaction.atomic
def return_product(sale_item, qty):
	if qty > sale_item.quantity:
		raise ValidationError("Retour invalide")
	
	product = sale_item.product 
	product.quantity += qty 
	product.is_active = True
	product.save()

	ProductReturn.objects.create(
		sale_item = sale_item,
		quantity = qty
	)


def save_return(request, item_pk):
	item = get_object_or_404(SaleItem, pk=item_pk)
	if request.method == "POST":
		qty = int(request.POST['quantity'])
		return_product(item, qty)
		return redirect("TrackShop:history")

	return render(request, "trackshop/partials/sale/product_return.html", {"item": item})


def search_client(request):
	search_input = request.GET.get('client_search', '')
	clients = Client.objects.filter(complete_name__icontains=search_input)[:10]

	return render(request, 'trackshop/partials/sale/client_result.html', {
		'clients': clients,
	})

def search_product(request):
    q = request.GET.get("product_search", "")
    products = Product.objects.filter(name__icontains=q, stock__gt=0)
    return render(request, "trackshop/partials/sale/product_results.html", {
        "products": products,
    })

def search_provider(request):
	search_input = request.GET.get('provider_search')
	providers = Provider.objects.filter(name__icontains=search_input)[:10]
	return render(request, "trackshop/partials/purchase/provider_results.html", {
		"providers": providers,
	})

def select_product(request, product_pk):
	selected_ids = request.POST.getlist("prod_selected[]")
	from_request = request.POST.get('from_request')
	print(selected_ids)
	product = Product.objects.get(pk=product_pk)

	excluded_ids = [int(pid) for pid in selected_ids if pid.isdigit()]

	if from_request == "sale_form":
		return render(request, "trackshop/partials/sale/sale_row_selected.html", {
        	"product": product,
			"nb_product": len(excluded_ids),
    	})
	elif from_request == "purchase_form":

		return render(request, "trackshop/partials/purchase/purchase_row_selected.html", {
			"product": product,
			"nb_product": len(excluded_ids)
		})
	
	return HttpResponse("Error")


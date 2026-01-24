from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField
from .forms import StockForm, ProductForm, ClientForm, SwitchShopForm
from django.template.loader import render_to_string
from weasyprint import HTML
from decimal import Decimal
from random import choice
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
	CashBook,
	StockMovement,

	)


now = timezone.now()

def set_exchange_rate(request):

	last_rate = ExchangeRate.objects.filter(shop=request.active_shop).last()
	if request.method == "POST":
		from_code = request.POST['from_currency']
		to_code = request.POST['to_currency']
		rate = request.POST['rate']

		ExchangeRate.objects.update_or_create(
			shop=request.active_shop,
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
		
		
@login_required
def dashboard(request):
	# nombre de stock
	active_shop = request.active_shop
	today = timezone.now().date()
	stocks = Stock.objects.filter(shop=request.active_shop)
	products = Product.objects.filter(shop=request.active_shop)
	clients = Client.objects.filter(shop=request.active_shop)
	todaySales = Sale.objects.filter(shop=request.active_shop, created_at=today)
	providers = Provider.objects.filter(shop=request.active_shop)

	return render(request, "trackshop/dashboard.html", context={
		"stocks": stocks,
		"products": products,
		"clients": clients,
		"todaySales": todaySales,
		"providers": providers,
		"user": request.user,
		"active_shop": active_shop,
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
			stock.shop = request.active_shop
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
		if source == "sale":
			Client.objects.create(
				shop=request.active_shop,
				complete_name=request.POST.get('client_name')
			)
			return redirect("TrackShop:sale-create")

		client_form = ClientForm(request.POST)
		if client_form.is_valid():
			print(request.POST)
			
			client = client_form.save(commit=False)
			client.shop = request.active_shop
			client.save()

			if source == "dashboard":
				return redirect("TrackShop:dashboard")
			else:
				return redirect("TrackShop:client")
		else:
			return render(request, "trackshop/new_client.html", context={"client_form": client_form})

	client_form = ClientForm()
	return render(request, "trackshop/new_client.html", context={"client_form": client_form, "source": source})

def new_provider(request):
	if request.method == "POST":	
		name = request.POST.get('provider_name')
		from_request = request.POST.get('from')
		Provider.objects.create(
			shop=request.active_shop,
			name=name
		)

		if from_request == "purchase":
			return redirect('TrackShop:create-purchase')
		else:
			return redirect('TrackShop:dashboard')
		
	return render(request, 'trackshop/partials/purchase/new_provider.html')
	

def client(request):
	clients = Client.objects.filter(shop=request.active_shop)
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
	stocks = Stock.objects.filter(shop=request.active_shop)
	last_access_stock = Stock.objects.filter(shop=request.active_shop).order_by("-last_access_date").first()
	return render(request, "trackshop/stock.html", context={"stocks": stocks, "stock": last_access_stock})

def load_stock_product(request, stock_pk):
	stock = Stock.objects.get(pk=stock_pk)
	stock.last_access_date = timezone.now()
	stock.save()
	products = Product.objects.filter(stock=stock_pk)
	try:
		product = Product.objects.get(pk=stock.last_access_product_id)
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
			product.shop = request.active_shop
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

	# Rapport dette produit
	credit_sales = Sale.objects.filter(
		is_credit=True, items__product=product
	).distinct()

	# Calcule de la dette client pour ce produit
	product_debt = 0

	for sale in credit_sales:
		sale_total = sale.total_amount_base 
		sale_balance = sale.balance

		items = sale.items.filter(product=product)

		product_total = items.aggregate(
			total=Sum('total_price')
		)['total'] or 0

		if sale_total > 0:
			product_debt += (product_total / sale_total * sale_balance) 

	# Rapport dette fournisseur pour ce produit
	credit_purchases = Purchase.objects.filter(
		is_credit=True,
		items__product=product
	).distinct()

	product_provider_debt = 0

	for purchase in credit_purchases:
		purchase_total = purchase.total_amount_base 
		purchase_balance = purchase.balance

		product_subtotal = purchase.items.filter(
			product=product
		).aggregate(
			total=Sum('total_cost')
		)['total'] or 0

		if purchase_total > 0:
			product_provider_debt += (
				product_subtotal / purchase_total
			) * purchase_balance

	return render(request, "trackshop/partials/product/partial_product_detail.html", context={
		"product": product, 
		"sales_this_month": sales_this_month,
		"evaliable_quantity": evaliable_quantity,
		"total_revenue": total_revenue,
		"product_debt": product_debt,
		"product_provider_debt": product_provider_debt
		})


def sale(request):
	return render(request, "trackshop/sale.html", context={})


def cash_book(request):
	if request.method == "POST":
		currency_code = request.POST.get('currency')
		date = request.POST.get('date')
		currency = Currency.objects.get(code=currency_code)
		print(request.active_shop)
		entries = CashBook.objects.filter(
			shop=request.active_shop, 
			currency=currency, 
			date=date
		).order_by('date')

		balance = 0
		rows = []

		for entry in entries:
			balance += entry.income - entry.expense

			rows.append({
				"date": entry.date,
				"description": entry.description,
				"income": entry.income,
				"expense": entry.expense,
				"balance": balance
			})

		return render(request, "trackshop/partials/cash_book/cashbook.html", context={
			"rows": rows,
			"currency": currency,
			"date": date,
		})
	return render(request, "trackshop/cashbook.html", {})

def cash_book_pdf(request, currency_code, date):
	currency = Currency.objects.get(code=currency_code)
	entries = CashBook.objects.filter(
		currency=currency, date=date
	).order_by('date')


	balance = 0
	rows = []

	for entry in entries:
		balance += entry.income - entry.expense
		rows.append({
			"date": entry.date,
			"description": entry.description,
			"income": entry.income,
			"expense": entry.expense,
			"balance": balance
		})
	
	html_string = render_to_string(
		"trackshop/cash_book_pdf.html",context={
			"rows": rows,
			"currency": currency,
			"date":date
		}
	)

	pdf = HTML(string=html_string).write_pdf()
	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename="Livre_de_caisse_{currency_code}_du_{date}.pdf"'
	return response
	

@transaction.atomic
def create_inventory(request, start_date, end_date, inv_type):
	# Création de l'objet inventaire
	inventory = Inventory.objects.create(
		shop=request.active_shop,
		start_date=start_date,
		end_date=end_date,
		inventory_type=inv_type,
	)

	# Génération des lignes
	for product in Product.objects.filter(shop=request.active_shop):
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
	inventories = Inventory.objects.filter(shop=request.active_shop)
	last_access__inventory = Inventory.objects.filter(shop=request.active_shop).order_by("-last_access_date").first()
	return render(request, "trackshop/inventory.html", context={"inventory": last_access__inventory, "inventories": inventories})

def new_inventory_view(request):
	if request.method == "POST":
		start_date = request.POST['start_date']
		end_date = request.POST['end_date']
		inventory_type = request.POST['inventory_type']

		# Création de l'inventaire
		create_inventory(request, start_date, end_date, inventory_type)
		
		return redirect('TrackShop:inventory')

	return render(request, "trackshop/partials/inventory/inventory_form.html", {})

def load_inventory(request, inv_pk):
	inventory = get_object_or_404(Inventory, pk=inv_pk)
	return render(request, "trackshop/partials/inventory/inventory_view.html", {'inventory':inventory})

def inventory_detail(request, inventory_pk):
	inventory = get_object_or_404(Inventory, pk=inventory_pk)
	inventory.last_access_date = now
	inventory.save()

	if inventory.closed:
		messages.error(request, "Inventaire déjà clôturé")
		return redirect("TrackShop:inventory")

	if request.method == "POST":
		with transaction.atomic():
			for item in inventory.items.select_related("product", "product__stock"):
				product = item.product
				stock = product.stock

				StockMovement.objects.create(
					stock=stock,
					product=product,
					movement_type='adjust',
					quantity=item.physical_quantity,
					reference=f"Inventaire {inventory.pk}"
				).apply()
			
			inventory.closed = True
			inventory.save()

		messages.success(request, "Inventaire appliqué avec succès")				
		return redirect("TrackShop:inventory")

	return render(request, "trackshop/partials/inventory/inventory_detail.html", {
		"inventory": inventory
	})

def inventory_detail_pdf(request, inventory_pk):

	inventory = get_object_or_404(Inventory, pk=inventory_pk)
	
	html_string = render_to_string(
		"trackshop/inventory_detail_pdf.html",context={
			"date":now.date(),
			"inventory":inventory
		}
	)

	pdf = HTML(string=html_string).write_pdf()
	response = HttpResponse(pdf, content_type='application/pdf')
	response['Content-Disposition'] = f'inline; filename="Inventaire_du_{inventory.start_date}_au_{inventory.end_date}.pdf"'
	return response

	
	
def history(request):
	sales = Sale.objects.filter(shop=request.active_shop).order_by("-created_at")
	return render(request, "trackshop/history.html", context={"sales": sales})

def purchase_history(request):
	purchases = Purchase.objects.filter(shop=request.active_shop).order_by("-created_at")
	return render(request, "trackshop/purchase_history.html", {
		"purchases":purchases
	})


def add_payment(request, sale_id):
	sale = get_object_or_404(Sale, pk=sale_id)
	rate = get_today_rate(
		from_currency=Currency.objects.get(code="CDF"),
		to_currency=Currency.objects.get(code="USD")
	)

	if request.method == 'POST':
		currency_code = request.POST.get("currency")
		amount = Decimal(request.POST['amount'])
		
		currency = Currency.objects.get(code=currency_code)
		base_currency = Currency.objects.get(code="USD")

		rate = (
			ExchangeRate.objects.filter(from_currency=currency, to_currency=base_currency).latest('date').rate
		)

		amount = Decimal(amount)

		sale.add_payment(amount, currency, rate) 

		return render(request, "trackshop/partials/sale/payment_succes.html",  {"sale": sale} )

	return render(request, "trackshop/add_payment.html", {
		"sale": sale,
		"rate": rate
	})


def provider_payment(request, purchase_pk):
	purchase = get_object_or_404(Purchase, pk=purchase_pk)
	
	rate = get_today_rate(
		from_currency=Currency.objects.get(code="CDF"),
		to_currency=Currency.objects.get(code="USD")
		)
		
	if request.method == "POST":
		amount = request.POST.get('amount')
		currency_code = request.POST.get('currency')
		currency = Currency.objects.get(code=currency_code)
		base_currency = Currency.objects.get(code="USD")

		rate = (
			ExchangeRate.objects.filter(from_currency=currency, to_currency=base_currency).latest('date').rate
		)

		amount = Decimal(amount)
		purchase.add_provider_payment(amount, currency, rate)
		return redirect("TrackShop:purchase-history")
	return render(request, "trackshop/provider_payment.html", {
		'purchase':purchase,
		'rate': rate	
	})

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
		"clients": Client.objects.filter(shop=request.active_shop),
		"products": Product.objects.filter(shop=request.active_shop),
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
			shop=request.active_shop,
			provider=provider,
			currency=currency,
			exchange_rate=rate,
			total_amount=0,
			total_amount_base=0,
			paid_amount=0,
			paid_amount_base=0,
		)

		total = Decimal(0)
		total_paid_amount = Decimal(0)

		product_ids = request.POST.getlist("product_id[]")
		quantities = request.POST.getlist("quantity[]")
		unit_costs = request.POST.getlist("unit_cost[]")
		sale_prices = request.POST.getlist("sale_price[]")
		paid_amounts = request.POST.getlist("paidAmount[]")	# Récupération des différentes montants payés


		for pid, qty, cost, amount, sp in zip(product_ids, quantities, unit_costs, paid_amounts, sale_prices):
			product = Product.objects.get(id=pid)
			qty = int(qty)
			cost = Decimal(cost)
			sp = Decimal(sp)
			line_total = qty * cost

			PurchaseItem.objects.create(
				purchase=purchase,
				product=product,
				quantity=qty,
				unit_cost=cost,
				total_cost=line_total
			)

			# Autgmenter le stock
			#product.quantity += qty
			
			StockMovement.objects.create(
				stock=product.stock,
				product=product,
				movement_type='in',
				quantity=qty,
				reference=f"Achat fournisseur #{purchase.provider.name}"
			).apply()
			
			
			product.sale_price = sp
			product.purchase_price = cost
			product.save()
			total += line_total                       
			total_paid_amount += Decimal(amount)

		purchase.total_amount = total
		purchase.total_amount_base = total / rate
		purchase.paid_amount = total_paid_amount
		purchase.paid_amount_base = total_paid_amount / rate
		purchase.is_credit = total_paid_amount < total
		purchase.save()

		# Enregistrement du livre de caisse
		CashBook.objects.create(
			shop=request.active_shop,
			date=now,
			description=f"Achat produit #{purchase.pk}",
			currency=currency,
			income=0,
			expense=total_paid_amount,
			reference_type="Purchase",
			reference_id = purchase.pk
		)	

		return redirect("TrackShop:purchase-detail", purchase.id) 

	return render(request, "trackshop/purchase_form.html", {
		'rate': rate,
		'providers': Provider.objects.filter(shop=request.active_shop),
		'products': Product.objects.filter(shop=request.active_shop),
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
		"clients": Client.objects.filter(shop=request.active_shop),
		"products": Product.objects.filter(shop=request.active_shop),
		"message": "Erreur! vous dévez séléctionner un client d'abord",
	})
	
	# Création de la vente
	sale = Sale.objects.create(
		shop=request.active_shop,
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
		#product.quantity -= qty
		StockMovement.objects.create(
			stock=product.stock,
			product=product,
			movement_type='out',
			quantity=qty,
			reference=f"Vente #{sale.pk}"
		).apply()
		
		
		product.save()


		total += line_total * rate
		total_paid_amount += paid_amount  

	# verifier si c'est une vente en crédit
	if (total_paid_amount < total):
		sale.is_credit = True

	sale.total_amount = total 
	sale.total_amount_base = total / rate 
	sale.paid_amount = total_paid_amount
	sale.paid_amount_base = total_paid_amount / rate
	
	sale.save() # Enregistrement de la vente

	# Enregistrement livre de caisse
	CashBook.objects.create(
		shop=request.active_shop,
		date=now,
		description=f"Vente #{sale.pk}",
		currency=currency,
		income=total_paid_amount,
		expense=0,
		reference_type="Sale",
		reference_id = sale.pk
	)
	return redirect("TrackShop:sale-invoice-pdf", sale_id=sale.pk)


@transaction.atomic
def return_product(sale_item, qty):
	if qty > sale_item.quantity:
		raise ValidationError("Retour invalide")
	
	product = sale_item.product 
	#product.quantity += qty 

	StockMovement.objects.create(
		stock=product.stock,
		product=product,
		movement_type='in',
		quantity=qty,
		reference=f"Retour vente #{sale_item.pk}"
	).apply()
	
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
	request_from = request.GET.get('from')
	search_input = request.GET.get('client_search', '')
	clients = Client.objects.filter(shop=request.active_shop, complete_name__icontains=search_input)[:10]
	from_client = False
	if request_from == "from_client":
		from_client = True


	return render(request, 'trackshop/partials/sale/client_result.html', {
		'clients': clients,
		'search_input': search_input,
		'from_client': from_client,
	})

def search_product(request):
    q = request.GET.get("product_search", "")
    products = Product.objects.filter(shop=request.active_shop, name__icontains=q, stock__gt=0)
    return render(request, "trackshop/partials/sale/product_results.html", {
        "products": products,
    })

def search_provider(request):
	search_input = request.GET.get('provider_search')
	providers = Provider.objects.filter(shop=request.active_shop, name__icontains=search_input)[:10]
	return render(request, "trackshop/partials/purchase/provider_results.html", {
		"providers": providers,
		"search_input": search_input,
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

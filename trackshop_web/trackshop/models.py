from django.db import models


CLIENT_TYPE_CHOICE = [
	("Particulier", "particulier"),
	("Grossiste", "Grossiste"),
	("Revendeur", "Revendeur"),
	("Entreprise", "Entreprise"),
]

CLIENT_CATEGORY = [
	("Client regulier", "client regulier"),
	("client VIP", "Client vIP"),
	("client occasionnel", "client occasionnel"),

]

class Client(models.Model):
	complete_name = models.CharField(max_length=20, null=True, blank=True, verbose_name="Nom complet")
	phoneNumber = models.CharField(max_length=15, null=True, blank=True, verbose_name="Numéro de téléphone")
	email = models.CharField(max_length=20, null=True, blank=True)
	adresse = models.CharField(max_length=50, null=True, blank=True)
	client_type = models.CharField(max_length=20, null=True, blank=True, choices=CLIENT_TYPE_CHOICE)
	def __str__(self):
		return f'{self.complete_name}'

class Stock(models.Model):
	stockName = models.CharField(max_length=20, verbose_name="Nom du stock")
	dateDebut = models.DateTimeField(auto_now=True)
	dateFin = models.DateTimeField(null=True, blank=True)
	last_access_date = models.DateTimeField(auto_now=True)
	last_access_product_id = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return self.stockName
 
CURRENCY_CHOICES = [
	("USD", "DOLLARS"),
	("CDF", "FRANC")
]

class Currency(models.Model):
	code = models.CharField(max_length=3, unique=True)
	name = models.CharField(max_length=50)
	symbol = models.CharField(max_length=3)

	def __str__(self):
		return self.code

class ExchangeRate(models.Model):
	from_currency = models.ForeignKey(Currency, related_name='rates_from', on_delete=models.CASCADE)
	to_currency = models.ForeignKey(Currency, related_name='+', on_delete=models.CASCADE)
	rate = models.DecimalField(max_digits=15, decimal_places=6)
	date = models.DateField()

	class Meta:
		unique_together = ('from_currency', 'to_currency', 'date')


class Product(models.Model):
	stock = models.ForeignKey(Stock, verbose_name="Stock", related_name="products", on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	price = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Prix Produit")
	quantity = models.PositiveIntegerField()
	date_added = models.DateTimeField(auto_now=True)
	is_active = models.BooleanField(default=True)
	
	def __str__(self):
		return self.name

# La tables du fournisseur
class Provider(models.Model):
	name = models.CharField(max_length=20)
	
	def __str__(self):
		return self.name

# Table de gestion des achat (arrivage)
class Purchase(models.Model):
	provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
	currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
	exchange_rate = models.DecimalField(max_digits=15, decimal_places=6, verbose_name="CDF pour 1 USD")
	total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	@property
	def balance(self):
		return self.total_amount - self.paid_amount

# Les items de l'arrivage
class PurchaseItem(models.Model):
	purchase = models.ForeignKey(Purchase, related_name="items", on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	quantity = models.DecimalField(max_digits=12, decimal_places=2)
	total_cost = models.DecimalField(max_digits=12, decimal_places=2)

# Suivi des payments du fournisseur
class ProviderPayment(models.Model):
	purchase = models.ForeignKey(Purchase, related_name="payments", on_delete=models.CASCADE)
	currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)

class CashBook(models.Model):
	income = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="recette")
	spending = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="depense")
	solde = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="solde")
	date = models.DateField(verbose_name="date")

class Sale(models.Model):
	client = models.ForeignKey(Client, on_delete=models.CASCADE)
	currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
	exchange_rate = models.DecimalField(max_digits=15, decimal_places=6)
	total_amount = models.DecimalField(max_digits=12, decimal_places=2)
	total_amount_base = models.DecimalField(max_digits=12, decimal_places=2)
	paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	paid_amount_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	is_credit = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	@property
	def total_cdf(self):
		return self.total_amount_base * self.exchange_rate
	
	@property
	def paid_cdf(self):
		return self.paid_amount_base * self.exchange_rate
	
	@property
	def balance(self):
		return self.total_amount - self.paid_amount

	@property 
	def balance_cdf(self):
		return (self.total_amount_base - self.paid_amount_base) * self.exchange_rate 

	def add_payment(self, amount, currency, rate):
		Payment.objects.create(
			sale=self, 
			currency=currency,
			exchange_rate=rate,
			amount=amount,
			amount_base=amount * rate
		)
		self.paid_amount += amount
		self.paid_amount_base += amount * rate
		self.is_credit = self.balance > 0
		self.save()


class SaleItem(models.Model):
	sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name="items", on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField()
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	total_price = models.DecimalField(max_digits=10, decimal_places=2)
	paid_amount = models.DecimalField(max_digits=10, decimal_places=2)

	@property
	def unit_price_cdf(self):
		return self.unit_price * self.sale.exchange_rate
	
	@property
	def total_price_cdf(self):
		return self.total_price * self.sale.exchange_rate

	@property
	def paid_amount_cdf(self):
		return self.paid_amount * self.sale.exchange_rate

class Payment(models.Model):
	sale = models.ForeignKey(Sale, related_name='payments', on_delete=models.CASCADE)
	currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
	exchange_rate = models.DecimalField(max_digits=15, decimal_places=6)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	amount_base = models.DecimalField(max_digits=12, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)           


class ProductReturn(models.Model):
	sale_item = models.ForeignKey(SaleItem, related_name='returns', on_delete=models.PROTECT)
	quantity = models.PositiveIntegerField()
	reason = models.TextField(blank=True)
	date = models.DateTimeField(auto_now_add=True)

class Invoice(models.Model):
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	nbProduct = models.PositiveIntegerField(verbose_name="Nombre de produit")
	totalPrice = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Prix total")
	totalPaid = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Total payé")


class ClientDebt(models.Model):
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
	totalAmount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Total à payé")
	PaidAmount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Montant")

class InternalDebt():
	provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	paidAmount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="montant payé")
	paid = models.BooleanField(default=False)
   

class Spending(models.Model):
	amount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Montant")
	description = models.TextField(null=True, blank=True)
	date = models.DateTimeField(auto_now=True)


class Inventory(models.Model):
	INVENTORY_TYPE = {
		('monthly', 'Mensuel'),
		('yearly', 'Annuel'),
	}

	start_date = models.DateField()
	end_date = models.DateField()
	inventory_type = models.CharField(max_length=10, choices=INVENTORY_TYPE)
	closed = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Inventaire du {self.start_date} au {self.end_date}'

class InventoryItem(models.Model):
	inventory = models.ForeignKey(Inventory, related_name="items", on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	system_quantity = models.IntegerField()
	physical_quantity = models.IntegerField()
	difference = models.IntegerField()


class InventorySummary(models.Model):
	inventory = models.OneToOneField(Inventory, related_name="summary", on_delete=models.CASCADE)
	total_sales = models.DecimalField(max_digits=12, decimal_places=2)
	total_returns = models.DecimalField(max_digits=12, decimal_places=2)
	net_revenue = models.DecimalField(max_digits=12, decimal_places=2)
	total_paid = models.DecimalField(max_digits=12, decimal_places=2)
	total_credit = models.DecimalField(max_digits=12, decimal_places=2)
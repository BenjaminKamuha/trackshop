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

class Product(models.Model):
	stock = models.ForeignKey(Stock, verbose_name="Stock", related_name="products", on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	price = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Prix Produit")
	currency = models.CharField(max_length=5, verbose_name="Dévise", choices=CURRENCY_CHOICES, null=True, blank=True)
	quantity = models.PositiveIntegerField()
	dateAdded = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.name

class CashBook(models.Model):
	income = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="recette")
	spending = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="depense")
	solde = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="solde")
	date = models.DateField(verbose_name="date")

class Sale(models.Model):
	client = models.ForeignKey(Client, on_delete=models.CASCADE)
	total_amount = models.DecimalField(max_digits=12, decimal_places=2)
	paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	is_credit = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	@property
	def balance(self):
		return self.total_amount - self.paid_amount
	
	#product = models.ForeignKey(Product, verbose_name="Produit", related_name="sales", on_delete=models.CASCADE)
	#client = models.ForeignKey(Client, verbose_name="Client", on_delete=models.CASCADE)
	#quantity = models.IntegerField(verbose_name="Quantité")
	#payedAmount = models.FloatField(verbose_name="Montant payé")
	#sale_date = models.DateField(verbose_name="Date livre")
	#reduction = models.FloatField(verbose_name="Montant reduction")

class SaleItem(models.Model):
	sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name="items", on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField()
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	total_price = models.DecimalField(max_digits=10, decimal_places=2)

class Payment(models.Model):
	sale = models.ForeignKey(Sale, related_name='payments', on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	payment_method = models.CharField(
		max_length=20,
		choices=[
			('cash', 'Cash'),
			('mobile', 'Mobile Money'),
			('bank', 'Virement'),
		]
	)
	created_at = models.DateTimeField(auto_now_add=True)

class Invoice(models.Model):
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	nbProduct = models.PositiveIntegerField(verbose_name="Nombre de produit")
	totalPrice = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Prix total")
	totalPaid = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Total payé")


class Provider(models.Model):
	name = models.CharField(max_length=20)

class ClientDebt(models.Model):
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
	totalAmount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Total à payé")
	PaidAmount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Montant")

class InternalDebt():
	provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.DecimalField(max_digits=12, decimal_places=2,)
	paidAmount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="montant payé")
	paid = models.BooleanField(default=False)


class Spending(models.Model):
	amount = models.DecimalField(max_digits=12, decimal_places=2,verbose_name="Montant")
	description = models.TextField(null=True, blank=True)
	date = models.DateTimeField(auto_now=True)



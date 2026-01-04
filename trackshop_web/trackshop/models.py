from django.db import models

class Client(models.Model):
	name = models.CharField(max_length=20, null=True, blank=True, verbose_name="Nom")
	lastName = models.CharField(max_length=20, null=True, blank=True, verbose_name="Post nom")
	phoneNumber = models.CharField(max_length=15, null=True, blank=True, verbose_name="Numéro de téléphone")

	def __str__(self):
		return f'{self.name} {lastName}'

class Stock(models.Model):
	stockName = models.CharField(max_length=20, verbose_name="Nom du stock")
	dateDebut = models.DateTimeField(auto_now=True)
	dateFin = models.DateTimeField(null=True, blank=True)
	last_access_date = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.stockName

class Product(models.Model):
	stock = models.ForeignKey(Stock, verbose_name="Stock", related_name="products", on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	price = models.FloatField(verbose_name="Prix Produit")
	quantity = models.IntegerField()
	dateAdded = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

class CashBook(models.Model):
	income = models.FloatField(verbose_name="recette")
	spending = models.FloatField(verbose_name="depense")
	solde = models.FloatField(verbose_name="solde")
	date = models.DateField(verbose_name="date")

class Sale(models.Model):
	product = models.ForeignKey(Product, verbose_name="Produit", on_delete=models.CASCADE)
	client = models.ForeignKey(Client, verbose_name="Client", on_delete=models.CASCADE)
	quantity = models.IntegerField(verbose_name="Quantité")
	payedAmount = models.FloatField(verbose_name="Montant payé")
	date = models.DateField(verbose_name="Date livre")
	reduction = models.FloatField(verbose_name="Montant reduction")

class Invoice(models.Model):
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	nbProduct = models.IntegerField(verbose_name="Nombre de produit")
	totalPrice = models.FloatField(verbose_name="Prix total")
	totalPaid = models.FloatField(verbose_name="Total payé")


class Provider(models.Model):
	name = models.CharField(max_length=20)

class ClientDebt(models.Model):
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
	totalAmount = models.FloatField(verbose_name="Total à payé")
	PaidAmount = models.FloatField(verbose_name="Montant")

class InternalDebt():
	provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.FloatField()
	paidAmount = models.FloatField(verbose_name="montant payé")
	paid = models.BooleanField(default=False)


class Spending(models.Model):
	amount = models.FloatField(verbose_name="Montant")
	description = models.TextField(null=True, blank=True)
	date = models.DateTimeField(auto_now=True)



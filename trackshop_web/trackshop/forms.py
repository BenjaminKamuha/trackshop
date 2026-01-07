from django import forms
from .models import Stock, Client, Product, Sale

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ["stockName"]
        widgets = {
        }
    

    def clean(self):
        cleaned_data = super().clean()
        stock_name = cleaned_data.get('stockName')
        if len(stock_name) < 3:
            raise forms.ValidationError("Le nom est trop court")

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client 
        fields = ["complete_name", "email", "phoneNumber"]

    def clean(self):
        cleaned_data = super().clean()
        complete_name = cleaned_data.get("complete_name")
        phoneNumber = cleaned_data.get("phoneNumber")
        email = cleaned_data.get("email")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product 
        fields = ["name", "price", "quantity"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        price = cleaned_data.get("price")
        quantity = cleaned_data.get("quantity")

        if len(name) < 3:
            raise forms.ValidationError("Le nom est trop court")

        elif price < 0:
            raise forms.ValidationError("Le prix est invalide")

        elif quantity < 0: 
            raise forms.ValidationError("La quantité est invalide")


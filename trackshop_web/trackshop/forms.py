from django import forms
from .models import Stock, Client, Product

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
        fields = ["name", "lastName", "phoneNumber"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        lastName = cleaned_data.get("LastName")
        phoneNumber = cleaned_data.get("phoneNumber")

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
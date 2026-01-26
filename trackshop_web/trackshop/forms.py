from django import forms
from .models import Stock, Client, Product, Sale





def include_tailwind_classes(fields):
    TAILWIND_CLASSES = (
        "w-full h-9 lg:h-9  px-3 py-2 border border-gray-500 rounded-md mb-4 "
        "focus:outline-none focus:border-2 focus:border-green-600"
        )

    TAILWIND_CLASSES_SELECT = (
            "block h-10 lg:h-10 w-full px-3 py-2 border border-gray-600 rounded-md mb-4 text-sm  "
            "focus:outline-none focus:border-2 focus:border-green-600 dark:bg-[#111827]"
            )
    
    TAILWIND_CLASSES_TEXTAREA = (
            "block w-full px-3 py-2 border border-gray-600 rounded-md mb-4 resize-none text-sm h-20 "
            "focus:outline-none focus:border-2 focus:border-green "
            )
        
    for name, field in fields.items():
        # Ajout des classes pour les champs standard
        if hasattr(field.widget, 'attrs'):
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' ' + TAILWIND_CLASSES
            field.widget.attrs['placeholder'] = field.label 

        if name == 'shop':
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' ' + TAILWIND_CLASSES_SELECT

    




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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        include_tailwind_classes(self.fields)
            

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client 
        fields = ["complete_name", "email", "phoneNumber"]

    def clean(self):
        cleaned_data = super().clean()
        complete_name = cleaned_data.get("complete_name")
        phoneNumber = cleaned_data.get("phoneNumber")
        email = cleaned_data.get("email")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        include_tailwind_classes(self.fields)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product 
        fields = ["name", "price"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        price = cleaned_data.get("price")

        if len(name) < 2:
            raise forms.ValidationError("Le nom est trop court")

        elif price < 0:
            raise forms.ValidationError("Le prix est invalide")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        include_tailwind_classes(self.fields)


class SwitchShopForm(forms.Form):
    shop = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop'].queryset = user.shops.all()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        include_tailwind_classes(self.fields)
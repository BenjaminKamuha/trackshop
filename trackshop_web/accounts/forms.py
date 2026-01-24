from django import forms
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.models import User
from .models import Shop

def include_tailwind_classes(fields):
    TAILWIND_CLASSES = (
        "w-full h-9 lg:h-9  px-3 py-2 border border-gray-500 rounded-md mb-4 "
        "focus:outline-none focus:border-2 focus:border-blue-600"
        )
        
    for name, field in fields.items():
        # Ajout des classes pour les champs standard
        if hasattr(field.widget, 'attrs'):
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' ' + TAILWIND_CLASSES
            field.widget.attrs['placeholder'] = field.label 
    

class LoginForm(AuthenticationForm):
    pass # Utilisation du formulaire Django standard

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        include_tailwind_classes(self.fields)


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirmation = forms.CharField(widget=forms.PasswordInput, label="Confirmation")

    class Meta:
        model = User
        fields = ['username', 'email']
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("confirmation"):
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text=""
        self.fields['username'].label="Nom utilisateur"
        self.fields['username'].widget.attrs["autofocus"] = True

        include_tailwind_classes(self.fields)

class SwitchShopForm(forms.Form):
    shop = forms.ModelChoiceField(queryset=None)
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop'].queryset = user.owned_shops.all()

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'rccm_number', 'id_nat', 'address', 'phone' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs["autofocus"] = True

        include_tailwind_classes(self.fields)
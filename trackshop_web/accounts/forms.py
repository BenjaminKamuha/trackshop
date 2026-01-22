from django import forms
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    pass # Utilisation du formulaire Django standard

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    shop_name = forms.CharField(label="Nom de la boutique")

    class Meta:
        model = User 
        fields = ['username', 'email']
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        return cleaned_data
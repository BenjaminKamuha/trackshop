from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from .forms import LoginForm, RegisterForm, SwitchShopForm, ShopForm
from .models import UserProfile, Shop
from django.contrib.auth.decorators import login_required
from django.db import transaction


def index(request):
    if request.user.is_authenticated:
        return redirect("TrackShop:dashboard")
    return render(request, "accounts/index.html")

def login_view(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Ce compte est désactivé.")
            else:
                login(request, user)

                # Activation de la boutique
                profile = user.profile
                if not profile.active_shop and user.owned_shops.exists():
                    profile.active_shop = user.owned_shops.first()
                    profile.save()
                return redirect('TrackShop:dashboard')
        else:
            messages.error(
                request,
                "Nom d'utilisateur ou mot de passe incorrect."
            )
    return render(request, 'accounts/login.html', {
        'form': form
    })

def logout_view(request):
    logout(request)
    return redirect('Account:index')

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                )
                login(request, user)
            return redirect("Account:create-shop")
        else:
            return render(request, "accounts/register.html", {
                "form": form
            })
    else:
        form = RegisterForm()
    
    return render(request, "accounts/register.html", {
        "form": form
    })

@login_required
def create_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            profile = request.user.profile

            # Activer le shop pour l'utilisatetur
            if not profile.active_shop and request.user.owned_shops.exists():
                profile.active_shop = request.user.owned_shops.first()
                profile.save()

            return redirect("Account:setting")
        form = ShopForm(request.POST)
        return render(request, "accounts/shop_form.html", {
            "form": form,
        })
        
    form = ShopForm
    return render(request, "accounts/shop_form.html", {
        "form": form
    } )


@login_required
def settings(request):
    shop = request.active_shop 
    user = request.user
    return render(request, "accounts/settings.html", {
        "shop":shop, 
        "user":user 
    })


@login_required
def switch_shop(request):
	if request.method == 'POST':
		form = SwitchShopForm(request.user, request.POST)
		if form.is_valid():
			shop = form.cleaned_data['shop']
			profile = request.user.profile 
			profile.active_shop = shop 
			profile.save()
			messages.success(request, f"Boutique active: {shop.name}")

			return redirect("TrackShop:dashboard")
	form = SwitchShopForm(request.user)
	return render(request, 'accounts/switch_shop.html', {'form': form})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from .forms import LoginForm, RegisterForm, SwitchShopForm, ShopForm, EditFormUserForm
from .models import UserProfile, Shop
from django.contrib.auth.decorators import login_required
from django.db import transaction
from trackshop.models import Currency, ExchangeRate
from django.utils import timezone

now = timezone.now()



def get_today_rate(from_currency, to_currency):
	try:
		return ExchangeRate.objects.get(
			from_currency=from_currency,
			to_currency=to_currency,
			date=now.date()
		).rate 

	except ExchangeRate.DoesNotExist:
		raise ValidationError("Taux du jour non défini")
		


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
    source = request.GET.get('from')
    if request.method == 'POST':
        source = request.POST.get('from')
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
        if source == "setting":
            return render(request, "accounts/partials/new_shop.html", {
                "form": form 
            })

        return render(request, "accounts/shop_form.html", {
            "form": form,
        })
        
    form = ShopForm()
    if source == "setting":
        return render(request, "accounts/partials/new_shop.html", {
            "form": form
        })
    return render(request, "accounts/shop_form.html", {
        "form": form
    } )


@login_required
def settings(request):
    shop = request.active_shop 
    user = request.user

    try:
        rate = (
            ExchangeRate.objects.filter(shop=request.active_shop, from_currency=Currency.objects.get(code="CDF"), to_currency=Currency.objects.get(code="USD")).latest('date').rate
        )
    
    except:
        return redirect("TrackShop:set-exchange-rate")

    return render(request, "accounts/settings.html", {
        "shop":shop, 
        "user":user,
        "rate": rate,
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

			return redirect("Account:setting")
	form = SwitchShopForm(request.user)
	return render(request, 'accounts/partials/switch_shop.html', {'form': form})
    
@login_required
def edit_account(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    if request.method == "POST":
        user_form = EditFormUserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            print("Enregistrement du compte réussi")
            return redirect("Account:setting")
        else:
            return render(request, "accounts/partials/edit_profil.html", {
                "user_form": EditFormUserForm(request.POST, instance=user)
            })
    else:
        user_form = EditFormUserForm(instance=user)
    
    return render(request, "accounts/partials/edit_profile.html", {
        "form": user_form,
        "user": user,
    })

@login_required
def edit_shop(request, shop_pk):
    shop = get_object_or_404(Shop, pk=shop_pk)
    if request.method == "POST":
        shop_form = ShopForm(request.POST, instance=shop)
        if shop_form.is_valid():
            shop_form.save()
            return redirect("Account:setting")
    else:
        shop_form = ShopForm(instance=shop)
        return render(request, "accounts/partials/edit_shop.html", {
            "shop_form": shop_form,
            "shop": shop
        })
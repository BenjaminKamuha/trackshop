from django.shortcuts import redirect
from django.urls import reverse 
from django.utils.timezone import now 
from django.contrib import messages

from .models import ExchangeRate, Currency


class ExchangeRateRequiredMiddleware:
    """
    Bloque les opérations commerciales si le taux du jour n'est pas défini
    """
    PROTECTED_PATHS = [
        '/trackshop/dashboard/',
        '/trackshop/sale/new/',
        '/trackshop/payment/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        today = now().date()

        # Ignore admin & static
        if request.path.startswith('/admin'):
            return self.get_response(request)

        if any(request.path.startswith(p) for p in self.PROTECTED_PATHS):
            base_currency = Currency.objects.get(code='USD')

            rates_exist = ExchangeRate.objects.filter(
                to_currency=base_currency, 
                date=today
            ).exists()

            if not rates_exist:
                messages.error(request, "Taux de change du jour non défini")
                return redirect(reverse('TrackShop:set-exchange-rate'))
            
        return self.get_response(request)
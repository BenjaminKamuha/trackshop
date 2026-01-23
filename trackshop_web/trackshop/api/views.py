from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from .serializers import *
from trackshop.models import (
    Currency, 
    ExchangeRate, 
    Product,
    StockMovement,
    Sale,
    SaleItem,
    CashBook,
    Purchase,
    PurchaseItem,
)

# Pull Web vers Desktop
class ProductViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(shop=self.request.active_shop)

# Push Desktop vers web 
class SaleViewSet(ModelViewSet):
    serializer_class = SaleSerializer

    def get_queryset(self):
        return Sale.objects.filter(shop=self.request.active_shop)

    def perform_create(self, serializer):
        serializer.save(source='desktop', shop=self.request.active_shop)

class CashBookViewSet(ModelViewSet):
    serializer_class = CashBookSerialiser

    def get_queryset(self):
        return CashBook.objects.filter(shop=self.request.active_shop)

class StockMovementViewSet(ModelViewSet):
    serializer_class = StockMovementSerializer

    def get_queryset(self):
        return StockMovement.objects.filter(shop=self.request.active_shop)

class ExchangeRateViewSet(ModelViewSet):
    serializer_class = ExchangeRateSerializer

    def get_queryset(self):
        return ExchangeRate.objects.filter(shop=self.request.active_shop)

class CurrencyViewSet(ModelViewSet):
    serializer_class = CurrencySerializer

    def get_queryset(self):
        return Currency.objects.all()

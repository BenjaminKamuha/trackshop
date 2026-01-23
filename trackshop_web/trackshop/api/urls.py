from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('currencies', CurrencyViewSet, basename='currency')
router.register('products', ProductViewSet, basename='product')
router.register('sales', SaleViewSet, basename='sale')
router.register('cashbook', CashBookViewSet, basename='cashbook')
router.register('stock-movements', StockMovementViewSet, basename='stock_movement')
router.register('exchange-rates', ExchangeRateViewSet, basename='exchange_rate')

urlpatterns = router.urls
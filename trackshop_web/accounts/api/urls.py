from rest_framework.routers import DefaultRouter
from .views import ShopViewSet

router = DefaultRouter()
router = DefaultRouter()
router.register('shops', ShopViewSet, basename='shop')

urlpatterns = router.urls
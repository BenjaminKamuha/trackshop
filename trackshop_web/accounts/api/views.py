from rest_framework.viewsets import ReadOnlyModelViewSet 
from accounts.models import Shop 
from .serializers import ShopSerializer

class ShopViewSet(ReadOnlyModelViewSet):
    serializer_class = ShopSerializer

    def get_queryset(self):
        return Shop.objects.filter(owner=self.request.user)


    
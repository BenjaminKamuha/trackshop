from django.utils.deprecation import MiddlewareMixin

class ActiveShopMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.active_shop = getattr(request.user.profile, 'active_shop', None)
        else:
            request.active_shop = None

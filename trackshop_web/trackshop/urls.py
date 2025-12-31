from django.urls import path
from .views import index

app_name = "TrackShop"

urlpatterns = [
	path('index/',index, name='index'),
]
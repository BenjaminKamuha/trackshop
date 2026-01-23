from rest_framework import serializers
from accounts.models import Shop

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop 
        fields = [
            'id', 'uuid', 'name', 'default_currency', 'created_at', 'is_system'
        ]

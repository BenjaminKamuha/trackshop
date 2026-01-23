from rest_framework import serializers
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


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency 
        fields = '__all__'

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate 
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product 
        fields = '__all__'


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = '__all__'

class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale 
        fields = '__all__'

    def create(self, validated_data):
        items = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)

        for item in items:
            SaleItem.objects.create(sale=sale, **item)

        return sale 

class CashBookSerialiser(serializers.ModelSerializer):
    class Meta:
        model = CashBook
        fields = '__all__'

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        models = PurchaseItem
        fields = '__init__'

class PurchaseSerializer(serializers.ModelSerializer):
    itmes = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = '__all__'
from rest_framework import serializers
from apps.catalog.models import Product
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity')

    def get_product(self, obj):
        from apps.catalog.serializers import ProductSerializer
        return ProductSerializer(obj.product).data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'created_at', 'updated_at')

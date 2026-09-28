from rest_framework import serializers
from .models import Order, OrderItem
from apps.catalog.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'unit_price', 'total_price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'subtotal', 'shipping_cost', 'total', 'status', 'shipping_address', 'notes', 'created_at', 'items')

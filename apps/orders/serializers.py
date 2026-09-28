from rest_framework import serializers
from apps.catalog.serializers import ProductSerializer
from apps.orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'quantity', 'unit_price', 'total_price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'user_email', 'subtotal', 'shipping_cost', 'tax', 'total', 'status', 'shipping_address', 'notes', 'created_at', 'items')
        read_only_fields = ('id', 'order_number', 'subtotal', 'shipping_cost', 'tax', 'total', 'status', 'created_at')

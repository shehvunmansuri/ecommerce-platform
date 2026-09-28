from rest_framework import serializers
from .models import User, Category, Product, Review, Cart, CartItem, Order, OrderItem, Payment
from django.contrib.auth import get_user_model

User = get_user_model()

# User Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 'city', 'state', 'zip_code')
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_customer = True
        user.save()
        return user

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'image')

# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'product', 'rating', 'comment', 'user_name', 'created_at')
        read_only_fields = ('id', 'created_at')

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'price', 'discount_price', 'stock', 'image', 'image_url', 'category_name', 'is_active', 'rating', 'review_count', 'reviews', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return 'https://via.placeholder.com/400x300?text=Product'

# CartItem Serializer
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'created_at')
        read_only_fields = ('id', 'created_at')

# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_price(self, obj):
        total = 0
        for item in obj.items.all():
            price = item.product.discount_price or item.product.price
            total += price * item.quantity
        return total

# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'quantity', 'unit_price', 'total_price')
        read_only_fields = ('id', 'total_price')

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'user_email', 'subtotal', 'tax', 'shipping_cost', 'total', 'status', 'shipping_address', 'notes', 'items', 'created_at')
        read_only_fields = ('id', 'order_number', 'subtotal', 'tax', 'shipping_cost', 'total', 'status', 'created_at')

# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'order_number', 'amount', 'status', 'transaction_id', 'payment_method', 'created_at')
        read_only_fields = ('id', 'transaction_id', 'created_at')

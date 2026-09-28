from django.contrib import admin
from .models import User, Category, Product, Review, Cart, CartItem, Order, OrderItem, Payment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_customer', 'created_at')
    search_fields = ('email', 'username')
    list_filter = ('is_customer', 'created_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'stock', 'rating')
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username')
    list_filter = ('rating', 'created_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__email',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__email', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'status', 'created_at')
    search_fields = ('order_number', 'user__email')
    list_filter = ('status', 'created_at')
    readonly_fields = ('order_number', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    search_fields = ('order__order_number', 'product__name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'status', 'created_at')
    search_fields = ('transaction_id', 'order__order_number')
    list_filter = ('status', 'payment_method', 'created_at')
    readonly_fields = ('transaction_id', 'created_at')

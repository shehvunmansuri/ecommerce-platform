from apps.payments.payment_models import Payment
from django.contrib import admin

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'order__order_number')
    readonly_fields = ('transaction_id', 'created_at')

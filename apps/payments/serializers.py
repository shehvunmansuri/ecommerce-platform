from rest_framework import serializers
from .payment_models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'order_number', 'amount', 'status', 'transaction_id', 'payment_method', 'created_at')
        read_only_fields = ('id', 'transaction_id', 'created_at')

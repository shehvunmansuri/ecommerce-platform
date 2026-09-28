from decimal import Decimal
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        if not items:
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = sum((item.product.sale_price or item.product.price) * item.quantity for item in items)
        shipping_cost = Decimal('0')
        total = subtotal + shipping_cost

        order = Order.objects.create(
            user=request.user,
            order_number=f'ORD-{request.user.id}-{len(Order.objects.filter(user=request.user)) + 1}',
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total,
            shipping_address=request.data.get('shipping_address', ''),
            notes=request.data.get('notes', ''),
        )

        for item in items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.sale_price or item.product.price,
                total_price=(item.product.sale_price or item.product.price) * item.quantity,
            )
            item.product.stock = max(0, item.product.stock - item.quantity)
            item.product.save()

        cart.items.all().delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

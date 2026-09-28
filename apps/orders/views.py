from decimal import Decimal
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.cart.models import Cart, CartItem
from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            items = cart.items.select_related('product').all()
            
            if not items.exists():
                return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

            subtotal = Decimal('0')
            for item in items:
                product_price = item.product.sale_price or item.product.price
                subtotal += product_price * item.quantity

            tax = subtotal * Decimal('0.08')
            shipping_cost = Decimal('10.00') if subtotal > Decimal('0') else Decimal('0')
            total = subtotal + tax + shipping_cost

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    tax=tax,
                    total=total,
                    shipping_address=request.data.get('shipping_address', 'Not provided'),
                    notes=request.data.get('notes', ''),
                    status='pending'
                )

                for item in items:
                    product_price = item.product.sale_price or item.product.price
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=product_price,
                        total_price=product_price * item.quantity,
                    )
                    
                    item.product.stock = max(0, item.product.stock - item.quantity)
                    item.product.save()

                cart.items.all().delete()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, id=None):
        order = self.get_object()
        order.status = 'paid'
        order.save()
        return Response({'status': 'Order marked as paid', 'order': OrderSerializer(order).data})

    @action(detail=True, methods=['post'])
    def mark_as_shipped(self, request, id=None):
        order = self.get_object()
        if not request.user.is_admin:
            return Response({'detail': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        order.status = 'shipped'
        order.save()
        return Response({'status': 'Order marked as shipped', 'order': OrderSerializer(order).data})

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
import uuid

from .models import User, Category, Product, Review, Cart, CartItem, Order, OrderItem, Payment
from .serializers import (
    UserSerializer, RegisterSerializer, CategorySerializer, ProductSerializer,
    ReviewSerializer, CartSerializer, CartItemSerializer, OrderSerializer,
    OrderItemSerializer, PaymentSerializer
)

User = get_user_model()

# ============ AUTH VIEWS ============

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============ CATEGORY VIEWS ============

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

# ============ PRODUCT VIEWS ============

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    filterset_fields = ['category']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, id=None):
        product = self.get_object()
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not rating:
            return Response({'detail': 'Rating is required'}, status=status.HTTP_400_BAD_REQUEST)

        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )

        return Response(
            {'detail': 'Review added successfully', 'review': ReviewSerializer(review).data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

# ============ CART VIEWS ============

class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def view_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'detail': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
            return Response({'detail': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response(
            {'detail': 'Item added to cart', 'item': CartItemSerializer(item).data},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        item_id = request.data.get('item_id')
        if not item_id:
            return Response({'detail': 'item_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.delete()
            return Response({'detail': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if not item_id:
            return Response({'detail': 'item_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            if quantity <= 0:
                item.delete()
                return Response({'detail': 'Item removed from cart'})
            item.quantity = quantity
            item.save()
            return Response({'detail': 'Item updated', 'item': CartItemSerializer(item).data})
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({'detail': 'Cart cleared'})

# ============ ORDER VIEWS ============

class OrderViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        try:
            with transaction.atomic():
                cart, _ = Cart.objects.get_or_create(user=request.user)
                items = cart.items.select_related('product').all()

                if not items.exists():
                    return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

                # Calculate totals
                subtotal = Decimal('0')
                for item in items:
                    price = item.product.discount_price or item.product.price
                    subtotal += price * item.quantity

                tax = subtotal * Decimal('0.08')
                shipping_cost = Decimal('10.00')
                total = subtotal + tax + shipping_cost

                # Create order
                order = Order.objects.create(
                    user=request.user,
                    subtotal=subtotal,
                    tax=tax,
                    shipping_cost=shipping_cost,
                    total=total,
                    shipping_address=request.data.get('shipping_address', 'Not provided'),
                    notes=request.data.get('notes', ''),
                    status='pending'
                )

                # Create order items
                for item in items:
                    price = item.product.discount_price or item.product.price
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=price,
                    )
                    item.product.stock = max(0, item.product.stock - item.quantity)
                    item.product.save()

                # Clear cart
                cart.items.all().delete()

                # Create payment record
                Payment.objects.create(
                    order=order,
                    amount=total,
                    status='pending',
                    payment_method='demo'
                )

                return Response(
                    {'detail': 'Order created successfully', 'order': OrderSerializer(order).data},
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def order_detail(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({'detail': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# ============ PAYMENT VIEWS ============

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        order_id = request.data.get('order_id')
        card_number = request.data.get('card_number', '')

        if not order_id:
            return Response({'detail': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            payment = Payment.objects.get(order=order)
        except (Order.DoesNotExist, Payment.DoesNotExist):
            return Response({'detail': 'Order or Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        # Demo payment logic
        if card_number == '4111111111111111':
            payment.status = 'completed'
            payment.save()
            order.status = 'paid'
            order.save()
            return Response({
                'status': 'success',
                'message': 'Payment processed successfully',
                'transaction_id': payment.transaction_id,
                'order_number': order.order_number,
                'amount': str(order.total),
            })
        elif card_number == '4000000000000002':
            payment.status = 'failed'
            payment.save()
            return Response({
                'status': 'failed',
                'message': 'Payment declined',
                'transaction_id': payment.transaction_id,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Auto-approve for demo
            payment.status = 'completed'
            payment.save()
            order.status = 'paid'
            order.save()
            return Response({
                'status': 'success',
                'message': 'Demo payment processed',
                'transaction_id': payment.transaction_id,
                'order_number': order.order_number,
                'amount': str(order.total),
            })

    @action(detail=False, methods=['get'])
    def payment_status(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({'detail': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            payment = Payment.objects.get(order=order)
            return Response({
                'order_id': order.id,
                'order_number': order.order_number,
                'payment_status': payment.status,
                'order_status': order.status,
                'amount': str(order.total),
                'transaction_id': payment.transaction_id,
            })
        except (Order.DoesNotExist, Payment.DoesNotExist):
            return Response({'detail': 'Order or Payment not found'}, status=status.HTTP_404_NOT_FOUND)

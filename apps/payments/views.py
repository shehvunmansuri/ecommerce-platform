import stripe
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.orders.models import Order
from .payment_models import Payment
from .serializers import PaymentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_checkout_session(request):
    order_id = request.data.get('order_id')
    if not order_id:
        return Response({'detail': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    # Create payment record
    payment, _ = Payment.objects.update_or_create(
        order=order,
        defaults={
            'amount': order.total,
            'status': 'pending',
            'payment_method': 'demo'
        }
    )

    # Demo payment gateway response
    return Response({
        'status': 'success',
        'message': 'This is a demo payment gateway',
        'order_id': order.id,
        'order_number': order.order_number,
        'amount': str(order.total),
        'currency': 'USD',
        'transaction_id': payment.transaction_id,
        'demo_card_numbers': {
            'success': '4111 1111 1111 1111',
            'failure': '4000 0000 0000 0002',
        },
        'demo_cvv': 'Any 3-digit number',
        'demo_expiry': 'Any future date',
        'next_step': 'Process payment with POST /api/payments/process/'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_payment(request):
    order_id = request.data.get('order_id')
    card_number = request.data.get('card_number', '')
    
    if not order_id:
        return Response({'detail': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.get(order=order)

    # Demo payment logic - simulate different outcomes
    if card_number == '4111111111111111':
        payment.status = 'completed'
        order.status = 'paid'
        payment.save()
        order.save()
        return Response({
            'status': 'success',
            'message': 'Payment processed successfully',
            'transaction_id': payment.transaction_id,
            'order_number': order.order_number,
            'amount': str(order.total),
        }, status=status.HTTP_200_OK)
    elif card_number == '4000000000000002':
        payment.status = 'failed'
        payment.save()
        return Response({
            'status': 'failed',
            'message': 'Payment declined (demo)',
            'transaction_id': payment.transaction_id,
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Auto-approve for demo
        payment.status = 'completed'
        order.status = 'paid'
        payment.save()
        order.save()
        return Response({
            'status': 'success',
            'message': 'Demo payment processed',
            'transaction_id': payment.transaction_id,
            'order_number': order.order_number,
            'amount': str(order.total),
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        payment = Payment.objects.get(order=order)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return Response({'detail': 'Order or Payment not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'order_id': order.id,
        'order_number': order.order_number,
        'amount': str(order.total),
        'payment_status': payment.status,
        'order_status': order.status,
        'transaction_id': payment.transaction_id,
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def payment_success(request):
    order_id = request.query_params.get('order_id')
    return Response({
        'status': 'success',
        'message': 'Payment successful. Your order is being processed.',
        'order_id': order_id,
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def payment_cancel(request):
    order_id = request.query_params.get('order_id')
    return Response({
        'status': 'cancelled',
        'message': 'Payment cancelled. Your order remains pending.',
        'order_id': order_id,
    }, status=status.HTTP_200_OK)

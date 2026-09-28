import stripe
from decouple import config
from django.conf import settings
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.orders.models import Order
from .models import Payment

stripe.api_key = config('STRIPE_SECRET_KEY', default='')

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_checkout_session(request):
    order_id = request.data.get('order_id')
    if not order_id:
        return Response({'detail': 'order_id is required'}, status=400)

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=404)

    if not stripe.api_key:
        return Response({'status': 'mock', 'message': 'Stripe not configured. Add STRIPE_SECRET_KEY to environment.', 'order_id': order.id})

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f'Order {order.order_number}'},
                'unit_amount': int(order.total * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8000/api/payments/success/?order_id=' + str(order.id),
        cancel_url='http://localhost:8000/api/payments/cancel/?order_id=' + str(order.id),
    )

    Payment.objects.update_or_create(
        order=order,
        defaults={'amount': order.total, 'status': 'pending', 'stripe_session_id': session.id}
    )

    return Response({'checkout_url': session.url, 'session_id': session.id})

@api_view(['GET'])
def payment_success(request):
    order_id = request.query_params.get('order_id')
    return Response({'status': 'success', 'order_id': order_id})

@api_view(['GET'])
def payment_cancel(request):
    order_id = request.query_params.get('order_id')
    return Response({'status': 'cancelled', 'order_id': order_id})

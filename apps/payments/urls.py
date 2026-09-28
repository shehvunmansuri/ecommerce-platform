from django.urls import path
from .views import create_checkout_session, process_payment, payment_status, payment_success, payment_cancel

urlpatterns = [
    path('create-checkout-session/', create_checkout_session, name='create-checkout-session'),
    path('process/', process_payment, name='process-payment'),
    path('status/<int:order_id>/', payment_status, name='payment-status'),
    path('success/', payment_success, name='payment-success'),
    path('cancel/', payment_cancel, name='payment-cancel'),
]

from django.urls import path
from .views import cart_detail, add_to_cart, remove_from_cart

urlpatterns = [
    path('', cart_detail, name='cart-detail'),
    path('add/', add_to_cart, name='cart-add'),
    path('remove/<int:item_id>/', remove_from_cart, name='cart-remove'),
]

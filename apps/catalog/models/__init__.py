from django.db import models
from apps.catalog.product_models import Product

class Product(Product):
    class Meta:
        proxy = True

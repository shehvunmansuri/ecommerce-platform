import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.catalog.models import Category
from apps.catalog.product_models import Product
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding database...'))
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@shopwave.com',
                password='admin123',
                is_admin=True
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create demo customer
        if not User.objects.filter(username='customer').exists():
            User.objects.create_user(
                username='customer',
                email='customer@shopwave.com',
                password='customer123',
                is_customer=True
            )
            self.stdout.write(self.style.SUCCESS('Created demo customer'))
        
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Smart devices and gadgets'},
            {'name': 'Fashion', 'description': 'Clothing and accessories'},
            {'name': 'Home', 'description': 'Home decor and essentials'},
            {'name': 'Beauty', 'description': 'Cosmetics and skincare'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = cat
        
        self.stdout.write(self.style.SUCCESS('Created categories'))
        
        # Create products
        products_data = [
            {
                'category': 'Electronics',
                'name': 'Wireless Headphones Pro',
                'slug': 'wireless-headphones-pro',
                'description': 'Noise-cancelling wireless headphones with 40-hour battery life',
                'price': Decimal('129.99'),
                'sale_price': Decimal('99.99'),
                'stock': 50,
                'rating': 4.7,
                'review_count': 28
            },
            {
                'category': 'Electronics',
                'name': 'Smart Watch Ultra',
                'slug': 'smart-watch-ultra',
                'description': 'Advanced fitness tracking with AMOLED display',
                'price': Decimal('199.99'),
                'sale_price': Decimal('159.99'),
                'stock': 30,
                'rating': 4.8,
                'review_count': 41
            },
            {
                'category': 'Fashion',
                'name': 'Premium Leather Jacket',
                'slug': 'premium-leather-jacket',
                'description': 'Classic brown genuine leather jacket',
                'price': Decimal('149.99'),
                'sale_price': Decimal('119.99'),
                'stock': 15,
                'rating': 4.5,
                'review_count': 17
            },
            {
                'category': 'Home',
                'name': 'Modern Desk Lamp',
                'slug': 'modern-desk-lamp',
                'description': 'Touch-dimming LED desk lamp with warm light',
                'price': Decimal('79.99'),
                'sale_price': Decimal('59.99'),
                'stock': 40,
                'rating': 4.6,
                'review_count': 20
            },
            {
                'category': 'Beauty',
                'name': 'Vitamin C Serum',
                'slug': 'vitamin-c-serum',
                'description': 'Brightening face serum for glowing skin',
                'price': Decimal('49.99'),
                'sale_price': Decimal('39.99'),
                'stock': 60,
                'rating': 4.8,
                'review_count': 34
            },
            {
                'category': 'Electronics',
                'name': 'Portable Power Bank',
                'slug': 'portable-power-bank',
                'description': '20000mAh fast charging power bank',
                'price': Decimal('39.99'),
                'sale_price': Decimal('29.99'),
                'stock': 100,
                'rating': 4.4,
                'review_count': 56
            },
        ]
        
        for prod_data in products_data:
            category = categories[prod_data.pop('category')]
            Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={**prod_data, 'category': category, 'is_active': True}
            )
        
        self.stdout.write(self.style.SUCCESS('Created products'))
        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))

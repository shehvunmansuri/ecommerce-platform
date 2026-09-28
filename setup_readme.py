from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

README = '''# E-Commerce Django REST API

This repository contains a Django + DRF e-commerce backend.

## Features
- User registration and JWT login
- Product catalog with category support
- Cart management
- Order creation and management
- Stripe checkout integration ready
- PostgreSQL-ready configuration

## Quick start

1. Create a virtual environment
2. install dependencies
3. run migrations
4. create superuser
5. run server

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Optional env vars

```env
SECRET_KEY=your-secret-key
DEBUG=True
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLIC_KEY=pk_test_xxx
```

## API Highlights

- /api/auth/register/
- /api/auth/login/
- /api/auth/me/
- /api/catalog/products/
- /api/catalog/categories/
- /api/cart/
- /api/orders/
- /api/payments/create-checkout-session/
'''

Path('README.md').write_text(README)

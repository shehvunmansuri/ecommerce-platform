# ShopWave E-Commerce API

A complete Django REST Framework e-commerce backend with a single app structure.

## Features

✅ User registration and JWT authentication
✅ Product catalog with categories
✅ Shopping cart management
✅ Order creation and tracking
✅ Demo payment gateway integration
✅ Product reviews and ratings
✅ Admin dashboard
✅ Simple, single-app architecture

## Tech Stack

- Django 4.2.7
- Django REST Framework 3.14.0
- JWT Authentication (djangorestframework-simplejwt)
- SQLite (default) or PostgreSQL (production)
- CORS enabled for frontend integration

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/shehvunmansuri/ecommerce-platform.git
cd ecommerce-platform
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data  # Load demo data
```

### 3. Create Admin User (if needed)

```bash
python manage.py createsuperuser
```

### 4. Run Server

```bash
python manage.py runserver
```

Server runs at: http://localhost:8000

## Demo Accounts

**Admin:**
- Email: admin@shopwave.com
- Password: admin123
- URL: http://localhost:8000/admin/

**Customer:**
- Email: customer@shopwave.com
- Password: customer123

## API Endpoints

### Authentication
- `POST /api/store/auth/register/` - Register new user
- `POST /api/store/auth/login/` - Login (get JWT token)
- `POST /api/store/auth/refresh/` - Refresh token

### Products
- `GET /api/store/products/` - List all products
- `GET /api/store/products/{id}/` - Get product details
- `POST /api/store/products/{id}/add_review/` - Add product review

### Categories
- `GET /api/store/categories/` - List all categories
- `GET /api/store/categories/{id}/` - Get category details

### Cart
- `GET /api/store/cart/view_cart/` - View cart
- `POST /api/store/cart/add_item/` - Add item to cart
- `POST /api/store/cart/update_item/` - Update item quantity
- `POST /api/store/cart/remove_item/` - Remove item from cart
- `POST /api/store/cart/clear_cart/` - Clear entire cart

### Orders
- `GET /api/store/orders/my_orders/` - Get all my orders
- `POST /api/store/orders/create_order/` - Create new order
- `GET /api/store/orders/order_detail/` - Get order details

### Payments
- `POST /api/store/payments/process_payment/` - Process payment
- `GET /api/store/payments/payment_status/` - Check payment status

## Demo Payment Gateway

The payment system uses demo card numbers for testing:

**Success:**
```
Card Number: 4111 1111 1111 1111
CVV: Any 3 digits
Expiry: Any future date
```

**Failure:**
```
Card Number: 4000 0000 0000 0002
CVV: Any 3 digits
Expiry: Any future date
```

## Example API Calls

### Register
```bash
curl -X POST http://localhost:8000/api/store/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secure123", "password_confirm": "secure123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/store/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "secure123"}'
```

### Get Products
```bash
curl http://localhost:8000/api/store/products/
```

### Add to Cart
```bash
curl -X POST http://localhost:8000/api/store/cart/add_item/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### Create Order
```bash
curl -X POST http://localhost:8000/api/store/orders/create_order/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address": "123 Main St", "notes": "Special delivery"}'
```

### Process Payment
```bash
curl -X POST http://localhost:8000/api/store/payments/process_payment/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "card_number": "4111111111111111"}'
```

## Deployment

### To Railway.app (FREE)

1. Install Railway CLI: https://railway.app/
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`
5. Set environment variables in Railway dashboard

### To Render.com (FREE)

1. Push code to GitHub
2. Connect repository at https://render.com
3. Create web service with:
   - Build command: `pip install -r requirements.txt && python manage.py migrate`
   - Start command: `gunicorn ecommerce.wsgi:application`
4. Add environment variables

### To Heroku (Paid)

```bash
heroku login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
```

## Project Structure

```
ecommerce-platform/
├── manage.py
├── requirements.txt
├── ecommerce/                    # Main project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── store/                        # Single app with all models
│   ├── models.py                # All models: User, Product, Category, Cart, Order, Payment
│   ├── serializers.py          # All DRF serializers
│   ├── views.py                # All viewsets and API views
│   ├── urls.py                 # URL routing
│   ├── admin.py                # Django admin configuration
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py    # Demo data seeding
│   └── apps.py
└── README.md
```

## Testing the API

Use Postman or Insomnia to test endpoints:
- Import the API into Postman
- Set `Authorization` header with Bearer token from login
- Test all endpoints

## Next Steps for Production

1. Switch to PostgreSQL
2. Set strong SECRET_KEY
3. Set DEBUG=False
4. Configure ALLOWED_HOSTS
5. Use real payment gateway (Stripe, PayPal)
6. Set up email notifications
7. Add product images storage
8. Implement order tracking
9. Add inventory management
10. Set up logging and monitoring

## Support

For issues, create an issue on GitHub or contact support.

## License

MIT

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Address Schemas
class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int
    price: float
    discount_price: Optional[float] = None
    stock_quantity: int
    image_url: Optional[str] = None
    sku: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    rating: float
    total_reviews: int
    created_at: datetime
    category: CategoryResponse
    
    class Config:
        from_attributes = True

# Review Schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    product_id: int

class ReviewResponse(ReviewBase):
    id: int
    product_id: int
    user_id: int
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Cart Item Schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

class CartItemResponse(CartItemBase):
    id: int
    cart_id: int
    product: ProductResponse
    created_at: datetime
    
    class Config:
        from_attributes = True

# Cart Schemas
class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    total_price: float
    product: ProductResponse
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    shipping_address: str
    billing_address: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    order_number: str
    user_id: int
    total_amount: float
    discount_amount: float
    tax_amount: float
    final_amount: float
    status: str
    payment_method: Optional[str] = None
    payment_status: str
    items: List[OrderItemResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

# Payment Schemas
class PaymentBase(BaseModel):
    amount: float
    currency: str = "USD"
    payment_method: str

class PaymentCreate(PaymentBase):
    order_id: int

class PaymentResponse(PaymentBase):
    id: int
    order_id: int
    transaction_id: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

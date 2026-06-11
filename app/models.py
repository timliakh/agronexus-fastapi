from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class Category(str, Enum):
    TRACTORS = "tractors"
    HARVESTERS = "harvesters"
    PLOWS = "plows"
    SEEDERS = "seeders"
    SPRAYERS = "sprayers"
    ATTACHMENTS = "attachments"


class ProductFields(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    price: float = Field(..., gt=0)
    category: Category
    manufacturer: str = Field(..., min_length=2, max_length=80)
    configurations: list[str] = Field(..., min_length=1)
    in_stock: bool = True
    image_url: str | None = Field(default=None, max_length=500)


class ProductBase(ProductFields):
    slug: str = Field(..., min_length=2, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ProductCreate(ProductFields):
    slug: str | None = Field(default=None, min_length=2, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Product(ProductBase):
    id: int


class BrandOption(BaseModel):
    name: str
    slug: str


class ProductUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=2, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, min_length=10, max_length=500)
    price: float | None = Field(default=None, gt=0)
    category: Category | None = None
    manufacturer: str | None = Field(default=None, min_length=2, max_length=80)
    configurations: list[str] | None = Field(default=None, min_length=1)
    in_stock: bool | None = None
    image_url: str | None = Field(default=None, max_length=500)


class AdminLogin(BaseModel):
    password: str


class AdminStats(BaseModel):
    products_count: int
    orders_count: int
    feedbacks_count: int
    total_revenue: float


class AdminFeedback(BaseModel):
    id: int
    name: str
    message: str
    email: EmailStr
    phone: str | None
    is_premium: bool


class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    configuration: str = Field(..., min_length=1, max_length=30)
    quantity: int = Field(default=1, ge=1, le=10)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    items: list[OrderItem] = Field(..., min_length=1)


class Order(BaseModel):
    id: int
    customer_name: str
    email: EmailStr
    items: list[OrderItem]
    total_price: float


class Contact(BaseModel):
    email: EmailStr
    phone: str | None = None


class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)
    contact: Contact

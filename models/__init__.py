# models/__init__.py
# Khi import models, sẽ tự động load các module con
from .product import Product
from .users import User
__all__ = [
    'Product',
    'User'
]
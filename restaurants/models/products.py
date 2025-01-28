from django.db import models
from .content import ProductsPage
from .business import Business


class Product(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    products_page = models.ForeignKey(ProductsPage, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=64)
    featured = models.BooleanField(default=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    def __str__(self):
        return f"{self.name} - {self.business.business_name if self.business else 'No Business'}"
    
    def to_dict(self):
        """Convert product instance to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price),
            'image_url': self.image.url if self.image else None,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') else None,
        }
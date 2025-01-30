from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from .content import ServicesPage
from .business import Business
from .media import Image

class Service(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='services')
    services_page = models.ForeignKey(ServicesPage, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=64)
    featured = models.BooleanField(default=False)
    description = models.TextField()
    images = GenericRelation('Image')

    @property
    def image(self):
        """Returns the first image associated with this event"""
        return self.images.first()
    
    def to_dict(self):
        """Convert service instance to dictionary for API responses"""
        image = self.image  # This uses your @property method
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': image.image.url if image and image.image else None,  # Convert to URL string
            'thumbnail_url': image.thumbnail.url if image and image.thumbnail else None,  # Convert to URL string
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') else None,
        }
    def __str__(self):
        return f"{self.business.business_name} - {self.name}"
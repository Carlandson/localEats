from django.db import models
from .content import SubPage


class ServicesPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='services_content')
    description = models.TextField()

class Service(models.Model):
    services_page = models.ForeignKey(ServicesPage, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=64)
    featured = models.BooleanField(default=False)
    description = models.TextField()
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
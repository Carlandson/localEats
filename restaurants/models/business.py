from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django_google_maps import fields as map_fields
from .media import Image

User = get_user_model()

class Business(models.Model):
    NAV_CHOICES = [
        ('minimal', 'Minimal'),
        ('centered', 'Centered'),
        ('split', 'Split'),
    ]
    
    FOOTER_CHOICES = [
        ('detailed', 'Detailed'),
        ('minimal', 'Minimal'),
        ('simple', 'Simple'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    business_name = models.CharField(max_length=64)
    business_type = models.CharField(max_length=50)
    address = map_fields.AddressField(max_length=200)
    geolocation = map_fields.GeoLocationField(max_length=200, blank=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=20)
    timezone = models.CharField(max_length=50, default='UTC')
    email = models.EmailField(blank=True)
    description = models.TextField(max_length=200, default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    hours_of_operation = models.TextField(max_length=200, default="", blank=True)
    user_favorite = models.ManyToManyField(User, blank=True, related_name="regular")
    phone_number = PhoneNumberField()
    is_verified = models.BooleanField(default=False)
    subdirectory = models.SlugField(max_length=64, unique=True)
    # Component Settings
    navigation_style = models.CharField(max_length=20, choices=NAV_CHOICES, default='minimal')
    footer_style = models.CharField(max_length=20, choices=FOOTER_CHOICES, default='minimal')
    # Feature Toggles
    show_gallery = models.BooleanField(default=True)
    show_testimonials = models.BooleanField(default=True)
    show_social_feed = models.BooleanField(default=True)
    show_hours = models.BooleanField(default=True)
    show_map = models.BooleanField(default=True)
    # Affiliates
    affiliates = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='affiliated_with')
    # Customization Options
    primary_color = models.CharField(max_length=7, default='#4F46E5')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#1F2937')
    hover_color = models.CharField(max_length=7, default='#9333EA') 
    text_color = models.CharField(max_length=7, default='#000000')
    main_font = models.CharField(max_length=50, default='Inter')
    
    # Media
    images = GenericRelation(Image)
    def get_affiliates(self):
        """Get all businesses this business is affiliated with"""
        return self.affiliates.all()
    
    def get_affiliated_with(self):
        """Get all businesses that have marked this business as an affiliate"""
        return self.affiliated_with.all()
    
    def get_logo(self):
        """Get the business's logo image"""
        return self.images.filter(alt_text='logo').first()

    def get_hero_image(self, page_type='home'):
        """Get the hero image for a specific page"""
        content_type = ContentType.objects.get_for_model(self)
        return Image.objects.filter(
            content_type=content_type,
            object_id=self.id,
            alt_text__startswith=f'hero_{page_type}_'
        ).first()

    def get_slider_images(self, page_type='home'):
        """Get all slider images for a specific page"""
        content_type = ContentType.objects.get_for_model(self)
        return Image.objects.filter(
            content_type=content_type,
            object_id=self.id,
            alt_text__startswith=f'slider_{page_type}_'
        ).order_by('alt_text')
    
    def get_gallery_images(self):
        """Get all gallery images"""
        return self.images.exclude(alt_text__in=['logo', 'hero'])
    

    def clean(self):
        if Business.objects.filter(subdirectory=self.subdirectory).exclude(pk=self.pk).exists():
            raise ValidationError({'subdirectory': 'This subdirectory is already in use. Please choose a different one.'})

    def save(self, *args, **kwargs):
        if not self.subdirectory:
            self.subdirectory = slugify(self.business_name)
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.business_name}"

    def regular_count(self):
        return self.user_favorite.count()
    
    @classmethod
    def verified_business_exists(cls, address):
        return cls.objects.filter(address=address, is_verified=True).exists()
    
    @property
    def street_address(self):
        """Returns just the street address portion"""
        if isinstance(self.address, str):
            # If it's already a string, return it (it's already the street address)
            return self.address
        # If it's an Address object, get the street address component
        return str(self.address).split(',')[0] if self.address else ""

    def clean(self):
        super().clean()
        if not self.pk and Business.verified_business_exists(self.address):
            raise ValidationError("A verified business already exists at this address.")
        
    def serialize(self):
        return {
            "cuisine": self.cuisine.serialize(),
            "name": self.business_name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "description": self.description,
            "affiliates": [affiliate.business_name for affiliate in self.get_affiliates()]

        }
    
    class Meta:
        verbose_name_plural = "Businesses"
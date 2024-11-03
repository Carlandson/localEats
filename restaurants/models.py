from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_google_maps import fields as map_fields
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

# Image, SubPage, Menu, Course, Dish, AboutUsPage, EventsPage, Event, SpecialsPage, Kitchen, CuisineCategory
User = get_user_model()

class Image(models.Model):
    image = models.ImageField(upload_to='user_uploads/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_images')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.image = self.compress_image(self.image)
            self.create_thumbnail()
        super(Image, self).save(*args, **kwargs)

    def compress_image(self, uploadedImage):
        im = PILImage.open(uploadedImage)
        
        # Convert to RGB if necessary
        if im.mode != 'RGB':
            im = im.convert('RGB')
        
        # Resize if larger than 1920x1080
        if im.width > 1920 or im.height > 1080:
            output_size = (1920, 1080)
            im.thumbnail(output_size)
        
        # Convert to WebP
        im_io = BytesIO()
        im.save(im_io, 'WEBP', quality=70, optimize=True)
        new_image = InMemoryUploadedFile(im_io, 'ImageField', "%s.webp" % uploadedImage.name.split('.')[0], 'image/webp', sys.getsizeof(im_io), None)
        return new_image

    def create_thumbnail(self):
        if not self.image:
            return
        
        im = PILImage.open(self.image)
        im.thumbnail((100, 100))
        thumb_io = BytesIO()
        im.save(thumb_io, 'WEBP', quality=60)
        thumbnail = InMemoryUploadedFile(thumb_io, 'ImageField', "%s_thumb.webp" % self.image.name.split('.')[0], 'image/webp', sys.getsizeof(thumb_io), None)
        self.thumbnail.save("%s_thumb.webp" % self.image.name.split('.')[0], thumbnail, save=False)

    def __str__(self):
        return f"Image for {self.content_object} - {self.upload_date}"

class CuisineCategory(models.Model):
    cuisine = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.cuisine}"
    
    def serialize(self):
        return {
            "id" : self.id,
            "cuisine" : self.cuisine
        }


#https://github.com/SmileyChris/django-countries/
#https://pypi.org/project/django-google-maps/

class Kitchen(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    cuisine = models.ForeignKey(CuisineCategory, on_delete=models.CASCADE, related_name="cuisines")
    restaurant_name = models.CharField(max_length=64)
    address = map_fields.AddressField(max_length=200)
    geolocation = map_fields.GeoLocationField(max_length=200, blank=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=20)
    description = models.TextField(max_length=200, default="")
    created = models.DateTimeField(auto_now_add=True)
    user_favorite = models.ManyToManyField(User, blank=True, related_name="regular")
    phone_number = PhoneNumberField()
    is_verified = models.BooleanField(default=False)
    subdirectory = models.SlugField(max_length=64, unique=True)
    LAYOUT_CHOICES = [
        ('default', 'Default Layout'),
        ('modern', 'Modern Layout'),
        ('classic', 'Classic Layout'),
    ]
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='default')
    def clean(self):
        if Kitchen.objects.filter(subdirectory=self.subdirectory).exclude(pk=self.pk).exists():
            raise ValidationError({'subdirectory': 'This subdirectory is already in use. Please choose a different one.'})

    def save(self, *args, **kwargs):
        if not self.subdirectory:
            self.subdirectory = slugify(self.restaurant_name)
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.restaurant_name}"

    def regular_count(self):
        return self.user_favorite.count()
    
    @classmethod
    def verified_business_exists(cls, address):
        return cls.objects.filter(address=address, is_verified=True).exists()

    def clean(self):
        super().clean()
        if not self.pk and Kitchen.verified_business_exists(self.address):
            raise ValidationError("A verified business already exists at this address.")
        
    def serialize(self):
        return {
            "cuisine": self.cuisine.serialize(),
            "name": self.restaurant_name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "description": self.description
        }
    
class SubPage(models.Model):
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name='subpages')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)

    PAGE_TYPES = (
        ('about', 'About Us'),
        ('menu', 'Menu'),
        ('events', 'Events'),
        ('specials', 'Specials'),
    )
    page_type = models.CharField(max_length=10, choices=PAGE_TYPES)

    class Meta:
        ordering = ['order']

class Menu(models.Model):
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name="menus")
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    subpage = models.ForeignKey(SubPage, on_delete=models.SET_NULL, null=True, related_name='menu_content')

    def __str__(self):
        return f"{self.kitchen.restaurant_name} - {self.name}"

class Course(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="courses")
    name = models.CharField(max_length=64)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    # gluten free options, vegan options, etc.
    note = models.TextField(blank=True, null=True)  

    class Meta:
        ordering = ['order']

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.menu.name} - {self.name}"

class Dish(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2)
    name = models.CharField(max_length=64)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="dishes")
    image = models.ImageField(upload_to='dishes/', null=True, blank=True) 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="dishes")
    description = models.TextField(max_length=200, default="")
    date_added = models.DateField(auto_now=True)
    favorites = models.ManyToManyField(User, blank=True, related_name="user_favorite")
    is_special = models.BooleanField(default=False)
    included_sides = models.IntegerField(default=0)
    class Meta:
        unique_together = ['course', 'name']
    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "name" : self.name,
            "price" : str(self.price),
            "kitchen": self.menu.kitchen,
            "course": self.course.course_list,
            "description": self.description,
            "image_url": self.image_url.url if self.image_url else None
        }

class SideOption(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='side_options')
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # Price for premium sides
    is_premium = models.BooleanField(default=False)  # If True, this side costs extra
    available = models.BooleanField(default=True)

class AboutUsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='about_us_content')
    content = models.TextField()
    history = models.TextField(blank=True, null=True)
    team_members = models.TextField(blank=True, null=True)

class EventsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='events_content')

class Event(models.Model):
    events_page = models.ForeignKey(EventsPage, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

class SpecialsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='specials_content')


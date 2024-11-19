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
from django.contrib.contenttypes.fields import GenericRelation
import sys

# Image, SubPage, Menu, Course, Dish, AboutUsPage, EventsPage, Event, SpecialsPage, business, CuisineCategory
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
    cuisine = models.ManyToManyField(CuisineCategory, related_name="cuisines", blank=True)
    business_name = models.CharField(max_length=64)
    business_type = models.CharField(max_length=50)
    address = map_fields.AddressField(max_length=200)
    geolocation = map_fields.GeoLocationField(max_length=200, blank=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    description = models.TextField(max_length=200, default="", blank=True)
    created = models.DateTimeField(auto_now_add=True)
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
    
    # Customization Options
    primary_color = models.CharField(max_length=7, default='#4F46E5')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#1F2937')
    hover_color = models.CharField(max_length=7, default='#9333EA') 
    text_color = models.CharField(max_length=7, default='#000000')
    main_font = models.CharField(max_length=50, default='Inter')
    
    # Media
    images = GenericRelation(Image)

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
            "description": self.description
        }
    
    class Meta:
        verbose_name_plural = "Businesses"
    
class SubPage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='subpages')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    primary_color = models.CharField(max_length=7, default='#4F46E5')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#1F2937')
    hover_color = models.CharField(max_length=7, default='#9333EA')
    text_color = models.CharField(max_length=7, default='#000000')
    font_heading = models.CharField(max_length=50, default='Inter')
    font_body = models.CharField(max_length=50, default='Inter')

    PAGE_TYPES = [
        ('home', 'Home'),
        ('about', 'About'),
        ('menu', 'Menu'),  # For restaurants
        ('services', 'Services'),  # For service businesses
        ('products', 'Products'),  # For retail
        ('gallery', 'Gallery'),
        ('contact', 'Contact'),
    ]
    page_type = models.CharField(max_length=10, choices=PAGE_TYPES)

    HERO_CHOICES = [
        ('full-image', 'Full Image'),
        ('offset-left', 'Image with Left Text'),
        ('offset-right', 'Image with Right Text'),
        ('banner-slider', 'Banner Slider'),
    ]
    TEXT_ALIGN_CHOICES = [
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ]
    
    hero_layout = models.CharField(
        max_length=20,
        choices=HERO_CHOICES,
        default='full-image'
    )
        # Hero Text Content
    hero_heading = models.CharField(max_length=200, blank=True)
    hero_subheading = models.TextField(blank=True)
    hero_button_text = models.CharField(max_length=50, blank=True)
    hero_button_link = models.CharField(max_length=200, blank=True)
    hero_text_align = models.CharField(max_length=10, choices=TEXT_ALIGN_CHOICES, default='left')
    hero_text_color = models.CharField(max_length=7, default='#000000')  # Hex color
    hero_subtext_color = models.CharField(max_length=7, default='#6B7280')  # Hex color
    show_hero_heading = models.BooleanField(default=False)
    hero_heading_size = models.CharField(max_length=20, default='text-3xl')
    hero_subheading_size = models.CharField(max_length=20, default='text-lg')
    show_hero_subheading = models.BooleanField(default=False)
    hero_font = models.CharField(max_length=50, default='Inter')

    def get_hero_image(self):
        """Get the hero image for this subpage"""
        content_type = ContentType.objects.get_for_model(self)
        return Image.objects.filter(
            content_type=content_type,
            object_id=self.id,
            alt_text__startswith='hero_'  # Using alt_text instead of purpose
        ).first()

    def get_slider_images(self):
        """Get all slider images for this subpage"""
        content_type = ContentType.objects.get_for_model(self)
        return Image.objects.filter(
            content_type=content_type,
            object_id=self.id,
            alt_text__startswith='slider_'  # Using alt_text instead of purpose
        ).order_by('upload_date')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            if self.page_type == 'home':
                # For home page, use just the business subdirectory
                self.slug = self.business.subdirectory
            else:
                # For other pages, append the page type
                base_slug = f"{self.business.subdirectory}-{self.page_type}"
                self.slug = base_slug
                
                # If the slug exists, append a number
                counter = 1
                while SubPage.objects.filter(slug=self.slug).exists():
                    self.slug = f"{base_slug}-{counter}"
                    counter += 1
                
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['business', 'page_type']  # Ensure one page type per business
        ordering = ['order']

class Menu(models.Model):

    MENU_DISPLAY_CHOICES = [
        ('grid', 'Grid Layout'),
        ('list', 'List Layout'),
        ('cards', 'Card Layout'),
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="menus")
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    subpage = models.ForeignKey(SubPage, on_delete=models.SET_NULL, null=True, related_name='menu_content')
    display_style = models.CharField(max_length=20, choices=MENU_DISPLAY_CHOICES, default='grid')

    def __str__(self):
        return f"{self.business.business_name} - {self.name}"

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
            "business": self.menu.business,
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


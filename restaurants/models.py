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
from django.db.models import Case, When
import logging
import magic

logger = logging.getLogger(__name__)
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

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
    VALID_CONTENT_TYPES = {
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp'
    }

    def clean(self):
        if self.image:
            original_position = self.image.tell()
            
            try:
                # Content type check
                self.image.seek(0)
                content_type = magic.from_buffer(self.image.read(1024), mime=True)
                logger.debug(f"Content type check: {content_type}")
                if content_type not in self.VALID_CONTENT_TYPES:
                    raise ValidationError(f'Unsupported content type: {content_type}')
                
                # File size check
                self.image.seek(0)
                if self.image.size > self.MAX_FILE_SIZE:
                    raise ValidationError('File size cannot exceed 10MB.')
                
                # Extension check
                ext = self.image.name.split('.')[-1].lower()
                if ext not in self.ALLOWED_EXTENSIONS:
                    raise ValidationError(f'Unsupported file extension. Allowed types: {", ".join(self.ALLOWED_EXTENSIONS)}')
                
                # Image verification
                self.image.seek(0)
                try:
                    img = PILImage.open(self.image)
                    # Don't use verify() as it can be problematic
                    # Instead, try to load the image
                    img.load()
                except Exception as e:
                    logger.error(f"PIL Image verification failed: {str(e)}")
                    raise ValidationError(f'Invalid image file: {str(e)}')
                    
            except ValidationError:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in image validation: {str(e)}")
                raise ValidationError(f'Error processing image: {str(e)}')
            finally:
                self.image.seek(original_position)
            
    def save(self, *args, **kwargs):
        logger.debug(f"""
            Saving Image:
            - Alt Text: {self.alt_text}
            - Content Type: {self.content_type}
            - Object ID: {self.object_id}
            - Content Object: {self.content_object}
            - Image Path: {self.image.name if self.image else 'No image'}
        """)
        if not self.id:
            self.full_clean()
            self.image = self.compress_image(self.image)
            self.create_thumbnail()
        super(Image, self).save(*args, **kwargs)
        logger.debug(f"""
            Image Saved:
            - ID: {self.id}
            - Alt Text: {self.alt_text}
            - Content Type: {self.content_type}
            - Object ID: {self.object_id}
        """)

    def compress_image(self, uploadedImage):
        try:
            im = PILImage.open(uploadedImage)
            #verify image format
            if im.format.upper() not in ['PNG', 'JPEG', 'GIF', 'WEBP']:
                raise ValidationError('Unsupported image format')
        
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
        
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise ValidationError('Error processing image file')

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
        ('specials', 'Specials'),
        ('events', 'Events'),
        ('merch', 'Merch'),
        ('contact', 'Contact'),
        ('testimonials', 'Testimonials'),
    ]
    
    page_type = models.CharField(max_length=14, choices=PAGE_TYPES)

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
    HERO_SIZE_CHOICES = [
        ('full-screen', 'Full Screen'),
        ('half-screen', 'Half Screen'),
    ]
    hero_size = models.CharField(max_length=20, default='full-width', choices=HERO_SIZE_CHOICES)
    hero_heading = models.CharField(max_length=200, blank=True)
    hero_subheading = models.TextField(blank=True)
    hero_button_text = models.CharField(max_length=50, blank=True)
    hero_button_link = models.CharField(max_length=200, blank=True)
    hero_button_bg_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    hero_button_text_color = models.CharField(max_length=7, default='#FFFFFF')  # Hex color
    hero_button_size = models.CharField(max_length=20, default='md')
    show_hero_button = models.BooleanField(default=False)
    hero_text_align = models.CharField(max_length=10, choices=TEXT_ALIGN_CHOICES, default='left')
    hero_heading_color = models.CharField(max_length=7, default='#000000')  # Hex color
    hero_subheading_color = models.CharField(max_length=7, default='#6B7280')  # Hex color
    show_hero_heading = models.BooleanField(default=False)
    hero_heading_size = models.CharField(max_length=20, default='text-3xl')
    hero_subheading_size = models.CharField(max_length=20, default='text-lg')
    show_hero_subheading = models.BooleanField(default=False)
    hero_heading_font = models.CharField(max_length=50, default='Inter')
    hero_subheading_font = models.CharField(max_length=50, default='Inter')
    show_banner_2_heading = models.BooleanField(default=True)
    banner_2_heading = models.CharField(max_length=200, blank=True)
    banner_2_heading_font = models.CharField(max_length=100, default='Inter')
    banner_2_heading_size = models.CharField(max_length=20, default='text-4xl')
    banner_2_heading_color = models.CharField(max_length=7, default='#000000')  # Hex color
    show_banner_2_subheading = models.BooleanField(default=True)
    banner_2_subheading = models.TextField(blank=True)
    banner_2_subheading_font = models.CharField(max_length=100, default='Inter')
    banner_2_subheading_size = models.CharField(max_length=20, default='text-xl')
    banner_2_subheading_color = models.CharField(max_length=7, default='#6B7280')  # Hex color
    banner_2_text_align = models.CharField(max_length=10, choices=TEXT_ALIGN_CHOICES, default='left')
    banner_2_button_text = models.CharField(max_length=50, blank=True)
    banner_2_button_link = models.CharField(max_length=200, blank=True)
    banner_2_button_bg_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    banner_2_button_text_color = models.CharField(max_length=7, default='#FFFFFF')  # Hex color
    banner_2_button_size = models.CharField(max_length=20, default='md')
    show_banner_2_button = models.BooleanField(default=False)
    show_banner_3_heading = models.BooleanField(default=True)
    banner_3_heading = models.CharField(max_length=200, blank=True)
    banner_3_heading_font = models.CharField(max_length=100, default='Inter')
    banner_3_heading_size = models.CharField(max_length=20, default='text-4xl')
    banner_3_heading_color = models.CharField(max_length=7, default='#000000')  # Hex color
    show_banner_3_subheading = models.BooleanField(default=True)
    banner_3_subheading = models.TextField(blank=True)
    banner_3_subheading_font = models.CharField(max_length=100, default='Inter')
    banner_3_subheading_size = models.CharField(max_length=20, default='text-xl')
    banner_3_subheading_color = models.CharField(max_length=7, default='#6B7280')  # Hex color
    banner_3_text_align = models.CharField(max_length=10, choices=TEXT_ALIGN_CHOICES, default='left')
    banner_3_button_text = models.CharField(max_length=50, blank=True)
    banner_3_button_link = models.CharField(max_length=200, blank=True)
    banner_3_button_bg_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    banner_3_button_text_color = models.CharField(max_length=7, default='#FFFFFF')  # Hex color
    banner_3_button_size = models.CharField(max_length=20, default='md')
    show_banner_3_button = models.BooleanField(default=False)

    def get_hero_primary(self):
        """Get the hero image for this subpage"""
        content_type = ContentType.objects.get_for_model(self)
        logger.debug(f"""
            Searching for hero_primary:
            - SubPage ID: {self.id}
            - Content Type: {content_type.app_label}.{content_type.model}
        """)
        
        # First, let's see ALL images for this content type and object_id
        all_images = Image.objects.filter(
            content_type=content_type,
            object_id=self.id
        )
        logger.debug(f"All images found: {[f'ID:{img.id}, Alt:{img.alt_text}' for img in all_images]}")
        
        # Now try to find the specific hero_primary
        hero = Image.objects.filter(
            content_type=content_type,
            object_id=self.id,
            alt_text='hero_primary'
        ).first()
        
        logger.debug(f"Hero primary found: {hero.id if hero else 'None'}")
        return hero

    def get_banner_2(self):
        """Get the second banner image"""
        content_type = ContentType.objects.get_for_model(self)
        logger.debug(f"""
            Searching for banner_2:
            - SubPage ID: {self.id}
            - Content Type: {content_type.app_label}.{content_type.model}
        """)
        
        banner = Image.objects.filter(
            content_type=content_type,
            object_id=self.id,
            alt_text='banner_2'
        ).first()
        
        logger.debug(f"Banner 2 found: {banner.id if banner else 'None'}")
        return banner

    def get_banner_3(self):
        """Get the third banner image"""
        content_type = ContentType.objects.get_for_model(self)
        logger.debug(f"""
            Searching for banner_3:
            - SubPage ID: {self.id}
            - Content Type: {content_type.app_label}.{content_type.model}
        """)
        
        banner = Image.objects.filter(
            content_type=content_type,
            object_id=self.id,
            alt_text='banner_3'
        ).first()
        
        logger.debug(f"Banner 3 found: {banner.id if banner else 'None'}")
        return banner

    def serialize(self):
        """Return a dictionary representation of the subpage"""
        return {
            'page_type': self.page_type,
            'title': self.title,
            'slug': self.slug,  
            'is_published': self.is_published
        }
    
    def save(self, *args, **kwargs):
        logger.debug(f"Saving SubPage: {self.business.business_name} - {self.page_type}")
        if not self.slug:
            if self.page_type == 'home':
                self.slug = self.business.subdirectory
            else:
                base_slug = f"{self.business.subdirectory}-{self.page_type}"
                self.slug = base_slug
                
                counter = 1
                while SubPage.objects.filter(slug=self.slug).exists():
                    self.slug = f"{base_slug}-{counter}"
                    counter += 1
        
        logger.debug(f"Generated slug: {self.slug}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.business.business_name} - {self.page_type}"

    @classmethod
    def get_published_subpages(cls, business):
        """Class method to get serialized published subpages"""
        subpages = cls.objects.filter(
            business=business,
            is_published=True
        )
        return [page.serialize() for page in subpages]
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



def get_all_images(self):
    """Debug method to get all images for this subpage"""
    content_type = ContentType.objects.get_for_model(self)
    images = Image.objects.filter(
        content_type=content_type,
        object_id=self.id
    )
    logger.debug(f"""
        All Images for SubPage {self.id}:
        Content Type: {content_type.app_label}.{content_type.model}
        Images Found: {[{
            'id': img.id,
            'alt_text': img.alt_text,
            'content_type': img.content_type,
            'object_id': img.object_id
        } for img in images]}
    """)
    return images
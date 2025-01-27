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
    
    @classmethod
    def get_available_subpages(cls, business):
        """Class method to get available page types that haven't been created yet"""
        # Get existing page types for this business
        existing_page_types = set(
            cls.objects.filter(business=business).values_list('page_type', flat=True)
        )
        
        # Get all possible page types from PAGE_TYPES
        all_page_types = set(page_type for page_type, _ in cls.PAGE_TYPES)
        
        # Find page types that don't exist yet
        available_page_types = all_page_types - existing_page_types
        
        # Return formatted available pages
        return [
            {
                'page_type': page_type,
                'title': dict(cls.PAGE_TYPES)[page_type],
                'slug': f"{business.subdirectory}-{page_type}",
                'is_published': False
            }
            for page_type in available_page_types
        ]
    
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
    cuisine = models.ManyToManyField(CuisineCategory, related_name="menu_cuisines", blank=True)
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

    def serialize(self):
        return {
            "name": self.name,
            "menu": self.menu.name
        }

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
    special_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    included_sides = models.IntegerField(default=0)
    # new fields
    happy_hour = models.BooleanField(default=False)
    happy_hour_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
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
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_premium = models.BooleanField(default=False)
    available = models.BooleanField(default=True)

class HomePage(models.Model):
    LAYOUT_CHOICES = [
        ('grid', 'Grid Layout'),
        ('list', 'List Layout'),
        ('cards', 'Card Layout'),
    ]
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='grid')
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='home_content')
    welcome_title = models.CharField(max_length=200, blank=True, null=True)
    welcome_message = models.TextField(blank=True, null=True)
    show_welcome = models.BooleanField(default=False)
    show_daily_special = models.BooleanField(default=False)
    show_affiliates = models.BooleanField(default=False)
    show_newsfeed = models.BooleanField(default=False)
    show_upcoming_event = models.BooleanField(default=False)
    show_daily_special = models.BooleanField(default=False)
    show_featured_service = models.BooleanField(default=False)
    show_featured_product = models.BooleanField(default=False)
    show_hours = models.BooleanField(default=False)
    show_map = models.BooleanField(default=False)
    
class NewsFeed(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='news_feed')

class NewsPost(models.Model):
    news_feed = models.ForeignKey(NewsFeed, on_delete=models.CASCADE, related_name='news_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="user_liked")

class Comment(models.Model):
    news_post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

# Subpage Subclasses
class AboutUsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='about_us_content')
    content = models.TextField()
    history = models.TextField(blank=True, null=True)
    team_members = models.TextField(blank=True, null=True)
    show_history = models.BooleanField(default=False)
    show_team = models.BooleanField(default=False)
    mission_statement = models.TextField(blank=True)
    core_values = models.TextField(blank=True)
    show_mission = models.BooleanField(default=False)
    show_values = models.BooleanField(default=False)
    def __str__(self):
        return f"About Us Page"

    class Meta:
        verbose_name = "About Us Page"
        verbose_name_plural = "About Us Pages"


class ContactPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='contact_content')
    description = models.TextField(blank=True, null=True)
    show_description = models.BooleanField(default=False)
    show_map = models.BooleanField(default=False)
    show_contact_form = models.BooleanField(default=False)

class ContactMessage(models.Model):
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='contact_messages')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} to {self.business.business_name}"


class EventsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='events_content')
    description = models.TextField(blank=True, null=True)

class Event(models.Model):
    events_page = models.ForeignKey(EventsPage, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

class SpecialsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='specials_content')
    happy_hour_start = models.TimeField(null=True, blank=True)
    happy_hour_end = models.TimeField(null=True, blank=True)
    happy_hour_days = models.CharField(max_length=100, blank=True, help_text="Comma-separated days, e.g., 'Mon,Tue,Wed'")

class DailySpecial(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    specials_page = models.ForeignKey(SpecialsPage, on_delete=models.CASCADE, related_name='daily_specials')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    dishes = models.ManyToManyField('Dish', limit_choices_to={'is_special': True})
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['specials_page', 'day_of_week']
        ordering = ['day_of_week'] 

    def __str__(self):
        return f"{self.get_day_of_week_display()} Specials"

class ServicesPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='services_content')
    description = models.TextField()

class Service(models.Model):
    services_page = models.ForeignKey(ServicesPage, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=64)
    featured = models.BooleanField(default=False)
    description = models.TextField()
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)

class ProductsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='products_content')
    description = models.TextField()

class Product(models.Model):
    products_page = models.ForeignKey(ProductsPage, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=64)
    featured = models.BooleanField(default=False)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

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


"""
Printful
1. Create developer account
2. Create API key
3. Create POD account
4. Create POD product
"""
class PODAccount(models.Model):
    business = models.OneToOneField('Business', on_delete=models.CASCADE)
    provider = models.CharField(max_length=50, choices=[
        ('PRINTFUL', 'Printful'),
        ('PRINTIFY', 'Printify'),
    ])
    api_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['provider']),
        ]

class PODProduct(models.Model):
    business = models.ForeignKey('Business', on_delete=models.CASCADE)
    pod_account = models.ForeignKey(PODAccount, on_delete=models.CASCADE)
    provider_product_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    design_data = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['provider_product_id']),
            models.Index(fields=['business', 'is_active']),
        ]
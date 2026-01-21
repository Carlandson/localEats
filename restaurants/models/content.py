from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import logging
from .business import Business
from .media import Image
from django.contrib.contenttypes.fields import GenericRelation

logger = logging.getLogger(__name__)
# Image, SubPage, Menu, Course, Dish, AboutUsPage, EventsPage, Event, SpecialsPage, business, CuisineCategory
User = get_user_model()

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

    def __str__(self):
        return f"{self.subpage.business.business_name} - Home Page"
    
class NewsFeed(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='news_feed')

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
        return f"{self.subpage.business.business_name} - About Us Page"

    class Meta:
        verbose_name = "About Us Page"
        verbose_name_plural = "About Us Pages"


class ContactPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='contact_content')
    description = models.TextField(blank=True, null=True)
    show_description = models.BooleanField(default=False)
    show_map = models.BooleanField(default=False)
    show_contact_form = models.BooleanField(default=False)
    

class EventsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='events_content')
    show_description = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)


class ProductsPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='products_content')
    description = models.TextField()
    show_description = models.BooleanField(default=False)

class ServicesPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='services_content')
    description = models.TextField()
    show_description = models.BooleanField(default=False)

class GalleryPage(models.Model):
    subpage = models.OneToOneField(SubPage, on_delete=models.CASCADE, related_name='gallery_content')
    description = models.TextField(blank=True)
    show_description = models.BooleanField(default=False)
    images = GenericRelation(Image)

    def get_images(self):
        """Get all images associated with this gallery, ordered by upload date"""
        return self.images.all().order_by('-upload_date')

    def add_image(self, image_file, uploaded_by, alt_text='', caption=''):
        """Helper method to add a new image to the gallery"""
        return Image.objects.create(
            image=image_file,
            uploaded_by=uploaded_by,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            alt_text=alt_text,
            caption=caption
        )


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  # Import the default UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.admin import GenericTabularInline  # Add this import

from .models import (
    Business, HomePage, AboutUsPage, EventsPage, 
    SpecialsPage, Event, CuisineCategory, SubPage, 
    Menu, Product, ProductsPage, ServicesPage, Service,
    Image, GalleryPage, SideOption, Course, Dish
)

class BusinessInline(admin.StackedInline):
    model = Business
    extra = 0
    verbose_name_plural = 'Owned Businesses'
    fk_name = 'owner'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_businesses')
    inlines = [BusinessInline]
    
    def get_businesses(self, obj):
        businesses = Business.objects.filter(owner=obj)
        if businesses:
            return ', '.join([b.business_name for b in businesses])
        return 'No businesses'
    get_businesses.short_description = 'Businesses'

class BusinessAdminSite(admin.AdminSite):
    site_header = 'Restaurant Management'
    site_title = 'Restaurant Admin Portal'
    index_title = 'Business Management'
    index_template = 'admin/index.html'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        if request.user.is_superuser:
            businesses = Business.objects.all()
            users = User.objects.all()
        else:
            businesses = Business.objects.filter(owner=request.user)
            users = User.objects.filter(id=request.user.id)
        
        extra_context['businesses'] = businesses
        extra_context['users'] = users
        return super().index(request, extra_context)
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site, with their models grouped into categories.
        """
        app_dict = {}
        
        # Define categories
        categories = {
            'Business Management': {
                'models': ['Business', 'User'],
                'icon': '🏢'
            },
            'Business Pages': {
                'models': ['SubPage', 'HomePage', 'AboutUsPage', 'EventsPage', 
                          'SpecialsPage', 'ProductsPage', 'ServicesPage', 'GalleryPage'],
                'icon': '📄'
            },
            'Content': {
                'models': ['Event', 'Product', 'Service', 'Image'],
                'icon': '📝'
            },
            'Menu Management': {
                'models': ['Menu', 'Course', 'Dish', 'SideOption'],
                'icon': '🍽️'
            },
            'Settings': {
                'models': ['CuisineCategory'],
                'icon': '⚙️'
            }
        }
        
        # Get all registered models
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            model_name = model.__name__
            
            # Find which category this model belongs to
            category_name = None
            for cat_name, cat_info in categories.items():
                if model_name in cat_info['models']:
                    category_name = cat_name
                    break
            
            # If not found in categories, put in "Other"
            if not category_name:
                category_name = 'Other'
                if category_name not in categories:
                    categories[category_name] = {'models': [], 'icon': '📦'}
            
            # Create app structure if it doesn't exist
            if category_name not in app_dict:
                app_dict[category_name] = {
                    'name': category_name,
                    'app_label': category_name.lower().replace(' ', '_'),
                    'app_url': '#',
                    'has_module_perms': True,
                    'models': []
                }
            
            # Add model to category
            if model_admin:
                perms = model_admin.get_model_perms(request)
                if True in perms.values():
                    model_dict = {
                        'name': model._meta.verbose_name_plural or model._meta.verbose_name or model_name,
                        'object_name': model_name,
                        'perms': perms,
                        'admin_url': None,
                        'add_url': None,
                    }
                    
                    if perms.get('change') or perms.get('view'):
                        try:
                            model_dict['admin_url'] = self.get_model_admin_url(model, 'changelist')
                        except:
                            pass
                    
                    if perms.get('add'):
                        try:
                            model_dict['add_url'] = self.get_model_admin_url(model, 'add')
                        except:
                            pass
                    
                    app_dict[category_name]['models'].append(model_dict)
        
        # Sort models within each category
        for category in app_dict.values():
            category['models'].sort(key=lambda x: x['name'])
        
        # Return sorted list of categories
        app_list = sorted(app_dict.values(), key=lambda x: x['name'])
        return app_list
    
    def get_model_admin_url(self, model, url_type):
        """Helper to get admin URLs for models"""
        model_name = model._meta.model_name
        app_label = model._meta.app_label
        if url_type == 'changelist':
            return reverse(f'{self.name}:{app_label}_{model_name}_changelist')
        elif url_type == 'add':
            return reverse(f'{self.name}:{app_label}_{model_name}_add')
        return None

class SideOptionInline(admin.TabularInline):
    model = SideOption
    extra = 0
    fields = ('name', 'description', 'price', 'is_premium', 'available')

class DishInline(admin.StackedInline):
    model = Dish
    extra = 0
    fields = ('name', 'price', 'description', 'image')
    classes = ('collapse',)

class CourseInline(admin.StackedInline):
    model = Course
    extra = 0
    inlines = [DishInline]
    fields = ('name', 'description', 'note', 'order')
    classes = ('collapse',)
    show_change_link = True

class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'get_courses_count', 'get_dishes_count')
    list_filter = ('business',)
    search_fields = ('name', 'business__business_name')
    inlines = [CourseInline]

    def get_courses_count(self, obj):
        return obj.courses.count()
    get_courses_count.short_description = 'Courses'

    def get_dishes_count(self, obj):
        return Dish.objects.filter(course__menu=obj).count()
    get_dishes_count.short_description = 'Total Dishes'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(business__owner=request.user)
        return qs

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu', 'get_business', 'order', 'get_dishes_count', 'get_side_options_count')
    list_filter = ('menu__business',)
    search_fields = ('name', 'menu__name', 'menu__business__business_name')
    inlines = [DishInline, SideOptionInline]
    
    def get_business(self, obj):
        return obj.menu.business
    get_business.short_description = 'Business'
    
    def get_dishes_count(self, obj):
        return obj.dishes.count()
    get_dishes_count.short_description = 'Dishes'
    
    def get_side_options_count(self, obj):
        return obj.side_options.count()
    get_side_options_count.short_description = 'Side Options'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(menu__business__owner=request.user)
        return qs

class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'get_menu', 'get_business', 'price')
    list_filter = ('course__menu__business', 'course')
    search_fields = ('name', 'description', 'course__name', 'course__menu__business__business_name')
    
    def get_menu(self, obj):
        return obj.course.menu
    get_menu.short_description = 'Menu'
    
    def get_business(self, obj):
        return obj.course.menu.business
    get_business.short_description = 'Business'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(course__menu__business__owner=request.user)
        return qs

class SideOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'get_menu', 'get_business', 'price', 'is_premium', 'available')
    list_filter = ('course__menu__business', 'course', 'is_premium', 'available')
    search_fields = ('name', 'description', 'course__name')
    list_editable = ('price', 'is_premium', 'available')
    
    def get_menu(self, obj):
        return obj.course.menu
    get_menu.short_description = 'Menu'
    
    def get_business(self, obj):
        return obj.course.menu.business
    get_business.short_description = 'Business'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(course__menu__business__owner=request.user)
        return qs

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'featured', 'display_image')
    list_filter = ('business', 'featured')
    search_fields = ('name', 'description')

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;"/>',
                obj.image.image.url
            )
        return "No image"
    display_image.short_description = 'Image'  # Column header in admin

    # Optional: If you want to show a larger image in the detail view
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: cover; border-radius: 8px;"/>',
                obj.image.image.url
            )
        return "No image"
    preview_image.short_description = 'Image Preview'

    # Optional: Customize the detail view layout
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'business', 'services_page', 'featured')
        }),
        ('Content', {
            'fields': ('description',)
        }),
        ('Image', {
            'fields': ('preview_image',),
        }),
    )

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'content_type_name', 'uploaded_by', 'upload_date', 'preview_caption')
    list_filter = ('upload_date', 'content_type', 'uploaded_by')
    search_fields = ('alt_text', 'caption', 'uploaded_by__username')
    readonly_fields = ('display_image', 'upload_date', 'uploaded_by', 'content_type', 'object_id')

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;"/>',
                obj.thumbnail.url
            )
        return "No thumbnail"
    thumbnail_preview.short_description = 'Preview'

    def display_image(self, obj):
        if obj.image:
            return format_html("""
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <img src="{}" style="max-width: 500px; border-radius: 8px;"/>
                    <a href="{}" target="_blank" class="button" style="text-decoration: none; width: fit-content;">
                        View Full Size
                    </a>
                </div>
            """, obj.image.url, obj.image.url)
        return "No image"
    display_image.short_description = 'Image'

    def content_type_name(self, obj):
        if obj.content_object:
            return f"{obj.content_type.model.title()} - {obj.content_object}"
        return f"{obj.content_type.model.title()}"
    content_type_name.short_description = 'Associated With'

    def preview_caption(self, obj):
        if obj.caption:
            return obj.caption[:100] + '...' if len(obj.caption) > 100 else obj.caption
        return '-'
    preview_caption.short_description = 'Caption Preview'

    fieldsets = (
        ('Image', {
            'fields': ('display_image', 'image', 'thumbnail'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': (
                'alt_text', 
                'caption', 
                'uploaded_by', 
                'upload_date'
            ),
        }),
        ('Association', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',),
            'description': 'Shows which content this image is associated with'
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Only set uploaded_by on creation
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/images.css',)
        }
        js = ('admin/js/images.js',)

class GalleryImageInline(GenericTabularInline):
    model = Image
    fields = ('display_image', 'alt_text', 'caption', 'upload_date', 'uploaded_by')
    readonly_fields = ('display_image', 'upload_date', 'uploaded_by')
    extra = 0
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(content_type=ContentType.objects.get_for_model(GalleryPage))
    
    def display_image(self, obj):
        if obj and obj.thumbnail:
            return format_html("""
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;"/>
                    <a href="{}" target="_blank" class="button" style="text-decoration: none;">
                        View Full Image
                    </a>
                </div>
            """, obj.thumbnail.url, obj.image.url)
        elif obj and obj.image:
            return format_html("""
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;"/>
                </div>
            """, obj.image.url)
        return "No image"
    display_image.short_description = 'Preview'

class GalleryPageAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'image_count', 'show_description', 'preview_description')
    list_filter = ('show_description', 'subpage__business')
    search_fields = ('description', 'subpage__business__business_name')
    inlines = [GalleryImageInline]

    def business_name(self, obj):
        return obj.subpage.business.business_name if obj.subpage else '-'
    business_name.short_description = 'Business'
    
    def image_count(self, obj):
        return Image.objects.filter(
            content_type=ContentType.objects.get_for_model(GalleryPage),
            object_id=obj.id
        ).count()
    image_count.short_description = 'Number of Images'

    def preview_description(self, obj):
        if obj.description:
            return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        return '-'
    preview_description.short_description = 'Description Preview'

    fieldsets = (
        ('Gallery Settings', {
            'fields': ('subpage', 'show_description')
        }),
        ('Content', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/gallery.css',)
        }

        js = ('admin/js/gallery.js',) 

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_business', 'get_owner', 'date', 'end_date')
    list_filter = ('events_page__subpage__business', 'events_page__subpage__business__owner', 'date')
    search_fields = ('title', 'description', 'events_page__subpage__business__business_name', 
                     'events_page__subpage__business__owner__username')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    def get_business(self, obj):
        """Display the business name"""
        if obj.events_page and obj.events_page.subpage:
            return obj.events_page.subpage.business.business_name
        return "—"
    get_business.short_description = 'Business'
    get_business.admin_order_field = 'events_page__subpage__business__business_name'
    
    def get_owner(self, obj):
        """Display the business owner"""
        if obj.events_page and obj.events_page.subpage:
            return obj.events_page.subpage.business.owner.username
        return "—"
    get_owner.short_description = 'Owner'
    get_owner.admin_order_field = 'events_page__subpage__business__owner__username'
    
    def get_queryset(self, request):
        """Filter events based on user permissions"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Non-superusers only see events for their own businesses
            qs = qs.filter(events_page__subpage__business__owner=request.user)
        return qs.select_related('events_page__subpage__business__owner')

# Base admin class for page models (to avoid repetition)
class BasePageAdmin(admin.ModelAdmin):
    list_display = ('get_business_link', 'get_owner_link', 'get_subpage_info')
    list_filter = ('subpage__business', 'subpage__business__owner')
    search_fields = ('subpage__business__business_name', 'subpage__business__owner__username')
    
    def get_business_link(self, obj):
        """Create a clickable link to the business"""
        if obj.subpage and obj.subpage.business:
            business = obj.subpage.business
            url = reverse('business_admin:restaurants_business_change', args=[business.id])
            return format_html('<a href="{}">{}</a>', url, business.business_name)
        return "—"
    get_business_link.short_description = 'Business'
    get_business_link.admin_order_field = 'subpage__business__business_name'
    
    def get_owner_link(self, obj):
        """Create a clickable link to the owner/user"""
        if obj.subpage and obj.subpage.business and obj.subpage.business.owner:
            owner = obj.subpage.business.owner
            url = reverse('business_admin:auth_user_change', args=[owner.id])
            return format_html('<a href="{}">{}</a>', url, owner.username)
        return "—"
    get_owner_link.short_description = 'Owner'
    get_owner_link.admin_order_field = 'subpage__business__owner__username'
    
    def get_subpage_info(self, obj):
        """Display subpage title and type"""
        if obj.subpage:
            return f"{obj.subpage.title} ({obj.subpage.get_page_type_display()})"
        return "—"
    get_subpage_info.short_description = 'SubPage'
    
    def get_queryset(self, request):
        """Filter pages based on user permissions"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(subpage__business__owner=request.user)
        return qs.select_related('subpage__business__owner')

# Specific admin classes for each page type
class HomePageAdmin(BasePageAdmin):
    list_display = BasePageAdmin.list_display + ('subpage',)
    
class AboutUsPageAdmin(BasePageAdmin):
    list_display = BasePageAdmin.list_display + ('show_history', 'show_team', 'show_mission')
    
class EventsPageAdmin(BasePageAdmin):
    list_display = BasePageAdmin.list_display + ('show_description',)
    
class SpecialsPageAdmin(BasePageAdmin):
    list_display = BasePageAdmin.list_display + ('happy_hour_start', 'happy_hour_end')
    
class ProductsPageAdmin(BasePageAdmin):
    list_display = BasePageAdmin.list_display + ('show_description',)
    
class ServicesPageAdmin(BasePageAdmin):
    list_display = BasePageAdmin.list_display + ('show_description',)

# GalleryPageAdmin already exists, so extend it
class GalleryPageAdminExtended(GalleryPageAdmin, BasePageAdmin):
    list_display = ('get_business_link', 'get_owner_link', 'get_subpage_info', 
                    'image_count', 'show_description', 'preview_description')
    
    def get_queryset(self, request):
        """Filter pages based on user permissions"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(subpage__business__owner=request.user)
        return qs.select_related('subpage__business__owner')

# SubPage admin
class SubPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_business_link', 'get_owner_link', 'page_type', 'is_published', 'order')
    list_filter = ('business', 'business__owner', 'page_type', 'is_published')
    search_fields = ('title', 'business__business_name', 'business__owner__username')
    
    def get_business_link(self, obj):
        """Create a clickable link to the business"""
        if obj.business:
            url = reverse('business_admin:restaurants_business_change', args=[obj.business.id])
            return format_html('<a href="{}">{}</a>', url, obj.business.business_name)
        return "—"
    get_business_link.short_description = 'Business'
    get_business_link.admin_order_field = 'business__business_name'
    
    def get_owner_link(self, obj):
        """Create a clickable link to the owner/user"""
        if obj.business and obj.business.owner:
            url = reverse('business_admin:auth_user_change', args=[obj.business.owner.id])
            return format_html('<a href="{}">{}</a>', url, obj.business.owner.username)
        return "—"
    get_owner_link.short_description = 'Owner'
    get_owner_link.admin_order_field = 'business__owner__username'
    
    def get_queryset(self, request):
        """Filter subpages based on user permissions"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(business__owner=request.user)
        return qs.select_related('business__owner')

# Create instance of custom admin site
business_admin = BusinessAdminSite(name='business_admin')

# ============================================
# BUSINESS MANAGEMENT
# ============================================
business_admin.register(User, CustomUserAdmin)
business_admin.register(Business)

# ============================================
# BUSINESS PAGES
# ============================================
business_admin.register(SubPage, SubPageAdmin)
business_admin.register(HomePage, HomePageAdmin)
business_admin.register(AboutUsPage, AboutUsPageAdmin)
business_admin.register(EventsPage, EventsPageAdmin)
business_admin.register(SpecialsPage, SpecialsPageAdmin)
business_admin.register(ProductsPage, ProductsPageAdmin)
business_admin.register(ServicesPage, ServicesPageAdmin)
business_admin.register(GalleryPage, GalleryPageAdminExtended)

# ============================================
# CONTENT
# ============================================
business_admin.register(Event, EventAdmin)
business_admin.register(Product)
business_admin.register(Service, ServiceAdmin)
business_admin.register(Image, ImageAdmin)

# ============================================
# MENU MANAGEMENT
# ============================================
business_admin.register(Menu, MenuAdmin)
business_admin.register(Course, CourseAdmin)
business_admin.register(Dish, DishAdmin)
business_admin.register(SideOption, SideOptionAdmin)

# ============================================
# SETTINGS
# ============================================
business_admin.register(CuisineCategory)
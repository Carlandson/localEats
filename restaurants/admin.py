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
    Image, GalleryPage
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
# Create instance of custom admin site
business_admin = BusinessAdminSite(name='business_admin')

# Register User model with custom admin
business_admin.register(User, CustomUserAdmin)

# Register your other models
business_admin.register(Business)
business_admin.register(SubPage)
business_admin.register(Menu)
business_admin.register(HomePage)
business_admin.register(AboutUsPage)
business_admin.register(EventsPage)
business_admin.register(SpecialsPage)
business_admin.register(Event)
business_admin.register(CuisineCategory)
business_admin.register(Product)
business_admin.register(ProductsPage)
business_admin.register(ServicesPage)
business_admin.register(Service, ServiceAdmin)
business_admin.register(GalleryPage, GalleryPageAdmin)
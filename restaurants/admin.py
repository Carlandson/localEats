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
        return obj.dish_set.count()
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
# Create instance of custom admin site
business_admin = BusinessAdminSite(name='business_admin')

# Register User model with custom admin
business_admin.register(User, CustomUserAdmin)

# Register your other models
business_admin.register(Business)
business_admin.register(SubPage)
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
business_admin.register(Image, ImageAdmin)
business_admin.register(Menu, MenuAdmin)
business_admin.register(Course, CourseAdmin)
business_admin.register(Dish, DishAdmin)
business_admin.register(SideOption, SideOptionAdmin)
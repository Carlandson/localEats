from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  # Import the default UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    Business, HomePage, AboutUsPage, EventsPage, 
    SpecialsPage, Event, CuisineCategory, SubPage, 
    Menu, Product, ProductsPage, ServicesPage, Service
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
business_admin.register(Service)

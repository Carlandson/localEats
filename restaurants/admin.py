from django.contrib import admin
import json
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from .models import Image, CuisineCategory, Business, Menu, Course, Dish, SubPage, Event, AboutUsPage, EventsPage, SpecialsPage, SideOption

class SubPageInline(admin.StackedInline):
    model = SubPage
    extra = 1

class MenuInline(admin.TabularInline):
    model = Menu
    extra = 1

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'owner', 'is_verified', 'subdirectory']
    list_filter = ['is_verified', 'cuisine']
    search_fields = ['business_name', 'owner__username']
    fields = [
        'business_name',
        'business_type',
        'owner',
        'address',
        'city',
        'state',
        'zip_code',
        'phone_number',
        'subdirectory',
        'description',
        'cuisine',
        'is_verified',
    ]
    
    actions = ['verify_businesses']
    inlines = [MenuInline]
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget(attrs={
            'data-autocomplete-options': json.dumps({
                'types': ['geocode', 'establishment'],
                'componentRestrictions': {'country': 'us'}
            })
        })},
    }

    def verify_businesses(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} businesses were successfully verified.')
        
    verify_businesses.short_description = "Verify selected businesses"
    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            # Add error logging
            print(f"Error saving business: {str(e)}")
            print(f"Form errors: {form.errors}")
            raise

class AboutUsPageInline(admin.StackedInline):
    model = AboutUsPage

class EventsPageInline(admin.StackedInline):
    model = EventsPage

class SpecialsPageInline(admin.StackedInline):
    model = SpecialsPage

@admin.register(SubPage)
class SubPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'business', 'page_type', 'order', 'is_published']
    list_filter = ['page_type', 'is_published']
    search_fields = ['title', 'business__business_name']
    readonly_fields = ['slug']
    inlines = [AboutUsPageInline, EventsPageInline, SpecialsPageInline]

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'business', 'subpage']
    list_filter = ['business']
    search_fields = ['name', 'business__business_name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'menu', 'order']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'menu', 'course', 'price', 'is_special']
    list_filter = ['is_special', 'menu', 'course']
    search_fields = ['name', 'menu__name', 'course__name']

@admin.register(CuisineCategory)
class CuisineCategoryAdmin(admin.ModelAdmin):
    list_display = ['cuisine']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_business', 'date']
    list_filter = ['date', 'events_page__subpage__business']
    search_fields = ['title', 'events_page__subpage__business__business_name']

    def get_business(self, obj):
        return obj.events_page.subpage.business
    get_business.short_description = 'business'
    get_business.admin_order_field = 'events_page__subpage__business'

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uploaded_by', 'upload_date']

admin.site.register(SideOption)
admin.site.register(AboutUsPage)
admin.site.register(EventsPage)
admin.site.register(SpecialsPage)
from django.contrib import admin
import json
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from .models import Image, CuisineCategory, Kitchen, Menu, Course, Dish, SubPage, Event, AboutUsPage, EventsPage, SpecialsPage, SideOption

class SubPageInline(admin.StackedInline):
    model = SubPage
    extra = 1

class MenuInline(admin.TabularInline):
    model = Menu
    extra = 1

@admin.register(Kitchen)
class KitchenAdmin(admin.ModelAdmin):
    list_display = ['restaurant_name', 'owner', 'is_verified', 'subdirectory']
    list_filter = ['is_verified', 'cuisine']
    search_fields = ['restaurant_name', 'owner__username']
    actions = ['verify_restaurants']
    inlines = [SubPageInline, MenuInline]
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget(attrs={
            'data-autocomplete-options': json.dumps({
                'types': ['geocode', 'establishment'],
                'componentRestrictions': {'country': 'us'}
            })
        })},
    }

    def verify_restaurants(self, request, queryset):
        queryset.update(is_verified=True)
    verify_restaurants.short_description = "Verify selected restaurants"

class AboutUsPageInline(admin.StackedInline):
    model = AboutUsPage

class EventsPageInline(admin.StackedInline):
    model = EventsPage

class SpecialsPageInline(admin.StackedInline):
    model = SpecialsPage

@admin.register(SubPage)
class SubPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'kitchen', 'page_type', 'order', 'is_published']
    list_filter = ['page_type', 'is_published']
    search_fields = ['title', 'kitchen__restaurant_name']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [AboutUsPageInline, EventsPageInline, SpecialsPageInline]

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'kitchen', 'subpage']
    list_filter = ['kitchen']
    search_fields = ['name', 'kitchen__restaurant_name']

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
    list_display = ['title', 'get_kitchen', 'date']
    list_filter = ['date', 'events_page__subpage__kitchen']
    search_fields = ['title', 'events_page__subpage__kitchen__restaurant_name']

    def get_kitchen(self, obj):
        return obj.events_page.subpage.kitchen
    get_kitchen.short_description = 'Kitchen'
    get_kitchen.admin_order_field = 'events_page__subpage__kitchen'

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uploaded_by', 'upload_date']

admin.site.register(SideOption)
admin.site.register(AboutUsPage)
admin.site.register(EventsPage)
admin.site.register(SpecialsPage)
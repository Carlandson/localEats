from django.contrib import admin
import json
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from .models import User, Kitchen, MenuCourse, Dish, CuisineCategory

admin.site.register(Kitchen)
admin.site.register(MenuCourse)
admin.site.register(Dish)
admin.site.register(CuisineCategory)


class kitchenAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget':map_widgets.GoogleMapsAddressWidget(attrs={
            'data-autocomplete-options': json.dumps({ 'types': ['geocode', 'establishment'],
            'componentRestrictions': {'country':'us'}
            })
        })
    },
}
    
class KitchenAdmin(admin.ModelAdmin):
    list_display = ['restaurant_name', 'owner', 'is_verified']
    actions = ['verify_restaurants']

    def verify_restaurants(self, request, queryset):
        queryset.update(is_verified=True)
    verify_restaurants.short_description = "Verify selected restaurants"
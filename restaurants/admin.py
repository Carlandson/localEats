from django.contrib import admin
import json
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from .models import User, Kitchen, MenuCourse, Dish, CuisineCategory

admin.site.register(Kitchen)
admin.site.register(User)
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
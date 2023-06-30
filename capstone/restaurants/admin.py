from django.contrib import admin
import json
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from .models import User, kitchen, menu_course, dish, cuisine_categories

admin.site.register(kitchen)
admin.site.register(User)
admin.site.register(menu_course)
admin.site.register(dish)
admin.site.register(cuisine_categories)


class kitchenAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget':map_widgets.GoogleMapsAddressWidget(attrs={
            'data-autocomplete-options': json.dumps({ 'types': ['geocode', 'establishment'],
            'componentRestrictions': {'country':'us'}
            })
        })
    },
}
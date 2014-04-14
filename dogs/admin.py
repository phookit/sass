from copy import deepcopy

from django.contrib import admin

from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin


from .models import Dog

# never show published or expiry date
volunteerFieldsets = deepcopy(DisplayableAdmin.fieldsets)
volunteerFieldsets[0][1]["fields"].remove( ('publish_date', 'expiry_date' ) )



class DogAdmin(DisplayableAdmin, OwnableAdmin):

    fieldsets = (
        deepcopy(volunteerFieldsets[0]),
            ("Dog details",{
                'fields': ('age', 'content', 'state', 'image')
            }),
        deepcopy(volunteerFieldsets[1]),
    )

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)
        
admin.site.register(Dog, DogAdmin)


from copy import deepcopy

from django.contrib import admin

from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin


from .models import Supporter

# never show published or expiry date
supporterFieldsets = deepcopy(DisplayableAdmin.fieldsets)
supporterFieldsets[0][1]["fields"].remove( ('publish_date', 'expiry_date') )


class SupporterAdmin(DisplayableAdmin, OwnableAdmin):

    fieldsets = (
        deepcopy(supporterFieldsets[0]),
            ("Supporter details",{
            'fields': ('address', 'content', 'mappable_location', ('lat', 'lon'), 'image', 'visible')
            }),
        deepcopy(supporterFieldsets[1]),
    )

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)
        
admin.site.register(Supporter, SupporterAdmin)


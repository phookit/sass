from copy import deepcopy

from django.contrib import admin

from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin


from .models import Volunteer

# never show published or expiry date
volunteerFieldsets = deepcopy(DisplayableAdmin.fieldsets)
volunteerFieldsets[0][1]["fields"].remove( ('title' ) )
volunteerFieldsets[0][1]["fields"].remove( ('status' ) )
volunteerFieldsets[0][1]["fields"].remove( ('publish_date', 'expiry_date' ) )



class VolunteerAdmin(DisplayableAdmin):

    fieldsets = (
        deepcopy(volunteerFieldsets[0]),
            ("Volunteer details",{
                'fields': (('name', 'prevnames'), 'dob', 'gender', 'street1', 'street2', 'town', 'postcode', 'email', 'mobile', 'landline', 'reason', 'skills', 'num_dogs', ('can_homecheck', 'can_foster'), ('homechecked', 'homechecker'), 'validated' )
            }),
        deepcopy(volunteerFieldsets[1]),
    )

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        #OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)
        
admin.site.register(Volunteer, VolunteerAdmin)


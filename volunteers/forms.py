
from django.forms import ModelForm
from .models import Volunteer


class VolunteerForm(ModelForm):
    class Meta:
        model = Volunteer
        fields = ['name', 'prevnames', 'dob', 'gender', 'street1', 'street2', 'town', 'postcode', 'email', 'mobile', 'landline', 'reason', 'skills', 'num_dogs', 'can_homecheck', 'can_foster']

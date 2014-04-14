from django.db import models
import datetime


from django.forms import ValidationError

from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.conf import settings

#from geopy.geocoders import GoogleV3 as GoogleMaps
#from geopy.exc import GeocoderQueryError

        
class Volunteer(Displayable):
    gender_choices = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    submitted = models.DateField("Date", default=datetime.date.today)
    name = models.CharField("Your Full Name", max_length=128, blank=False)
    prevnames = models.CharField("Previous Names (If any)", max_length=128, blank=True)
    dob = models.CharField("Date of birth (YYYY-MM-DD)", max_length=128, blank=False)
    gender = models.CharField("Gender", max_length=10, blank=False, choices=gender_choices)
    street1 = models.CharField("Street 1", max_length=128, blank=False)
    street2 = models.CharField("Street 2", max_length=128, blank=True)
    town = models.CharField("Town or City", max_length=128, blank=False)
    postcode = models.CharField("Post Code", max_length=128, blank=False)
    email = models.CharField("Email", max_length=128, blank=True)
    mobile = models.CharField("Mobile Phone Number", max_length=64, blank=True)
    landline = models.CharField("Landline Number", max_length=64, blank=True)
    reason = models.TextField("Why do you want to be a volunteer?", blank=False)
    skills = models.TextField("Please give any skills you have.", blank=True)
    num_dogs = models.IntegerField("How many dogs are in your house", blank=False)
    can_homecheck = models.BooleanField(verbose_name="Will you be able to do homechecks?",
                                  default=False)
    can_foster = models.BooleanField(verbose_name="Will you be able to foster?",
                                     default=False)
                                     
    # "Private"
    homechecked = models.BooleanField(verbose_name="Has the volunteer been homechecked?",
                                      default=False)
    homechecker = models.CharField("Homechecker", max_length=128, blank=True, help_text="Who homechecked them?")
    
    validated = models.BooleanField(verbose_name="Is it okay to ask them to do things?",
                                    default=False)
                                      
    class Meta:
        verbose_name = "Volunteer"
        verbose_name_plural = "Volunteers"

    
    def clean(self):
        super(Volunteer, self).clean()
        
        self._validate_dob(self.dob)
        
        # must have at least 1 phone number
        if len(self.mobile) == 0 and len(self.landline) == 0:
            raise ValidationError("You must specify a phone number")
        self.title = self.name + ", " + self.town + ", " + self.postcode
        
        if self.homechecked:
            if len(homechecker) == 0:
                raise ValidationError("You need to state who homechecked them")
            
        
    @models.permalink
    def get_absolute_url(self):
        url_name = "volunteers:detail"
        kwargs = {"volunteer_id": self.id}
        return (url_name, (), kwargs)
        
        
    def _validate_dob(self, dob):
        fmt_err_str = "Invalid date of birth. Please use YYYY-MM-DD format."
        parts = dob.split('-')
        if len(parts) != 3:
            raise ValidationError(fmt_err_str)
        if len(parts[0]) != 4:
            raise ValidationError(fmt_err_str)
        try:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
        except ValueError:
            raise ValidationError(fmt_err_str + " All values must be numeric")
        self.dob = "%d-%02d-%02d" % (year, month, day)

        
        

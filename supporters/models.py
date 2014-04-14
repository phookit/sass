from django.db import models

from django.forms import ValidationError

from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable, RichText
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.conf import settings


from phookit.apps.geocoders.models import Geocoder
        
class Supporter(Displayable, Ownable, RichText, AdminThumbMixin, Geocoder):
    website = models.CharField(max_length=512, blank=True, null=True, help_text="The supporters website if known.")
    image = FileField(help_text="An image of the supporter or premises",
                        verbose_name=("Supporter Image"),
                        upload_to=upload_to("supporters.Supporter.image", "supporter"),
                        format="Image", max_length=255, null=True, blank=True) 
    visible = models.BooleanField(verbose_name="Show this supporter on the website?",
                                  default=True)
                                  
    class Meta:
        verbose_name = "Supporter"
        verbose_name_plural = "Supporters"
        ordering = ("title", "website")
            
    @models.permalink
    def get_absolute_url(self):
        url_name = "supporters:detail"
        kwargs = {"supporter_id": self.id}
        return (url_name, (), kwargs)
        
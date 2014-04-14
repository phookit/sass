from django.db import models

from django.forms import ValidationError

from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable, RichText
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.conf import settings


class Dog(Displayable, Ownable, RichText, AdminThumbMixin):
    state_choices = (
        ('available', 'Available'),
        ('rehomed', 'Rehomed'),
    )
    age = models.CharField(max_length=10, blank=False, null=False, help_text="Approx age of the dog.")
    state = models.CharField(max_length=10, choices=state_choices, blank=False, null=False, help_text="Is the dog available or rehomed?")
    image = FileField(help_text="An image of the dog",
                        verbose_name=("Dogs Image"),
                        upload_to=upload_to("dogs.Dog.image", "dog"),
                        format="Image", max_length=255, null=True, blank=True) 

                                  
    class Meta:
        verbose_name = "Dog"
        verbose_name_plural = "Dogs"
        #ordering = "date_published"
            
    @models.permalink
    def get_absolute_url(self):
        url_name = "dogs:detail"
        kwargs = {"dog_id": self.id}
        return (url_name, (), kwargs)
        
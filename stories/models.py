from django.db import models


from mezzanine.core.models import Displayable, Ownable, RichText
from mezzanine.utils.models import AdminThumbMixin
from mezzanine.conf import settings


class Story(Displayable, Ownable, RichText, AdminThumbMixin):
    type_choices = (
        ('story', 'Story'),
        ('poem', 'Poem'),
    )
    # model type
    mtype = models.CharField(max_length=10, choices=type_choices, blank=False, null=False, help_text="Is this a story or a poem?")
                                  
    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"
            
    @models.permalink
    def get_absolute_url(self):
        url_name = "stories:detail"
        kwargs = {"story_id": self.id}
        return (url_name, (), kwargs)
        
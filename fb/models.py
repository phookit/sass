
from django.db import models

from phookit.apps.events.models import Event

def fb_save_callback(event):
    pass


class FbTokens(models.Model):
    token = models.CharField("Token", max_length=255, blank=False)
    userid = models.CharField("Facebook User ID", max_length=32, blank=False)
    updated_date = models.DateTimeField("Expiry date", auto_now_add=True)
    # facebook seems to have stopped sending an expiry time!
    expires_date = models.DateTimeField("Expiry date", auto_now_add=True)


class FbEvent(models.Model):
    event = models.ForeignKey(Event, verbose_name="the related event")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    name = models.CharField("Event name", max_length=255, blank=False)
    location = models.CharField("Location", max_length=512, blank=False)
    description = models.CharField("Description", max_length=1024, blank=False)


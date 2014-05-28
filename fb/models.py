from datetime import datetime

from django.db import models
from django.db.models import signals
from django.utils import dateparse
from django.utils import timezone
import re
# import html2text

from phookit.apps.events.models import Event



def get_future_events():
    today = timezone.now()
    return FbEvent.objects.filter(start_time__gte=today)


class FbTokens(models.Model):
    token = models.CharField("Token", max_length=255, blank=False)
    userid = models.CharField("Facebook User ID", max_length=32, blank=False)
    updated_date = models.DateTimeField("Expiry date", auto_now_add=True)
    # facebook seems to have stopped sending an expiry time!
    expires_date = models.DateTimeField("Expiry date", auto_now_add=True)


class FbEvent(models.Model):
    event = models.OneToOneField(Event, verbose_name="the related event")
    eid = models.BigIntegerField()
    start_time = models.DateTimeField(blank=False, null=False)
    end_time = models.DateTimeField(blank=True, null=True)
    name = models.CharField("Event name", max_length=255, blank=False)
    location = models.CharField("Location", max_length=512, blank=False)
    description = models.CharField("Description", max_length=1024, blank=False)

    def compare(self, other):
        print "COMP:",self.start_time,other.start_time
        #st = django.utils.timezone.localtime(self.start_time)
        #et = django.utils.timezone.localtime(self.end_time)
        #print "COMP local:",st,et
        if str(self.eid) != str(other.eid):
            print "  EID",self.eid,other.eid
            return False
        if self.start_time != other.start_time:
            print "  ST",self.start_time,other.start_time
            return False
        if self.end_time != other.end_time:
            print "  ET",self.end_time,other.end_time
            return False
        if self.name != other.name:
            print "  NAME"
            return False
        if self.location != other.location:
            print "  LOC:",self.location,":",other.location
            return False
        if self.description != other.description:
            print "  DESC",self.description,other.description
            return False
        return True


def create_fb_event_from_site_event(e):
    print "CREATE FB:",e.start_date,e.end_date


    content = re.sub(r'</{0,1}[a-zA-Z]+>', '', e.content)
    # content = html2text.html2text(e.content).strip().decode('utf-8')
    print "CONTENT:",content

    location=e.address.replace("\n", ",")
    location=location.replace("\r", "")
    return FbEvent(event=e,
                    start_time=e.start_date,
                    end_time=e.end_date,
                    name=e.title,
                    location=location,
                    description=content)


def create_site_event_from_fb_live(lfbe):
    print "New event FBST:",lfbe.start_time
    print "New event FBET:",lfbe.end_time
    #sdt = dateparse.parse_datetime(lfbe.start_time)
    #edt = None
    #if lfbe.end_time:
    #    edt = dateparse.parse_datetime(lfbe.end_time)
    #print "New event ST:",sdt," FBST:",lfbe.start_time
    #print "New event ET:",edt," FBET:",lfbe.end_time

    content = '%s%s%s' % ('<p>', lfbe.description, '</p>')
    return Event(start_date=lfbe.start_time,
                       end_date=lfbe.end_time,
                       title=lfbe.name,
                       address=lfbe.location.replace(",","\n"),
                       mappable_location="",
                       content=content)

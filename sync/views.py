from datetime import datetime
import time

from django.http import Http404
from django.utils import dateparse
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.forms import ValidationError

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from phookit.apps.events.models import Event
from phookit.apps.events.models import get_future_events as future_site_events
from phookit.apps.fb.models import get_future_events as future_fb_events
from phookit.apps.fb.models import create_fb_event_from_site_event, create_site_event_from_fb_live
from phookit.apps.fb.models import FbEvent
from phookit.apps.fb.api import FbAuth, FbEvents, FbNotAuthorisedException

FB_PAGE_NAME = 'Blaaar De Blaar'


#def _totimestamp(dt, epoch=datetime.datetime(1970,1,1)):
#    td = dt - epoch
#    # return td.total_seconds()
#    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6

def syncevents(request):
    if not request.user.has_perm('events.add_event'):
        raise Http404

    try:
        fbevents = FbEvents(FbAuth(request))
    except FbNotAuthorisedException:
        # redirect to authorise
        # TODO Fix this reverse
        #r = reverse('fb.views.adminauth')
        #print "REV:%s" % r
        print "syncevents:SESSION:",request.session.session_key
        return redirect('/fb/adminauth?redir=/sync/syncevents')#'fb.views.adminauth')

    # ---------------------------------------------
    """
    events = fbevents.get_future_events(FB_PAGE_NAME)
    # 1481855942032466 <-- ID
    print "FUTURE EVENTS:",events
    fbe = events[0]
    fbe.name = 'Blaaar updated'
    #neweid = fbevents.create_event(FB_PAGE_NAME, FbEvent=fbe)
    #print "NEW EID=",neweid # 263957760453456
    fbe.eid = '263957760453456'
    fbe.location = 'fk1 2eg'
    result = fbevents.update_event(FB_PAGE_NAME, FbEvent=fbe)
    print "UPDATE RES:",result
    return
    """
    # ---------------------------------------------

    #latest_fb_events = fbevents.get_future_events(FB_PAGE_NAME)
    #for e in latest_fb_events:
    #    fbevents.delete_event(FB_PAGE_NAME, e.eid)
    #return

    #request.META.get('HTTP_ACCEPT', "accept-default")
    #request.META.get('CONTENT_TYPE', 'application/your_default'))

    handled_fb_eids = []
    site_events = future_site_events()
    # check all site events are on FB
    for e in site_events:
        try:
            fbe = FbEvent.objects.get(event=e)
            print "FOUND FB EVENT",e.start_date,e.end_date
            
            handled_fb_eids.append(fbe.eid)

            compevent = create_fb_event_from_site_event(e)
            compevent.eid = fbe.eid
            if not compevent.compare(fbe):
                print "UPDATING FB EVENT",compevent.eid,compevent.start_time,compevent.end_time
                fbevents.update_event(FB_PAGE_NAME, FbEvent=compevent)
        except FbEvent.DoesNotExist:
            with transaction.atomic():
                print "FB EVENT NOT EXIST, ADDING NEW FB EVENT"
                fbe = create_fb_event_from_site_event(e)
                try:
                    fbe.eid = fbevents.create_event(FB_PAGE_NAME, FbEvent=fbe)
                    print "FBE.eid=",fbe.eid

                    handled_fb_eids.append(fbe.eid)

                    fbe.save()
                except:
                    print "  Add new FB failed",fbe.eid
                    if fbe.eid:
                        fbevents.delete_event(FB_PAGE_NAME, fbe.eid)

    failed_events = []
    latest_fb_events = fbevents.get_future_events(FB_PAGE_NAME)
    for lfbe in latest_fb_events:
        if lfbe.eid in handled_fb_eids:
            continue
        #                                                   2014-07-04T17:00:00+0100
        try:
            fbe = FbEvent.objects.get(eid=lfbe.eid)
            print "FOUND EXISTING FB EVENT",fbe.eid
            # print "LFBE ST:",lfbe.start_time,"FBE ST:",fbe.start_time
            if not lfbe.compare(fbe):
                fbevents.update_event(FB_PAGE_NAME, FbEvent=lfbe)
        except FbEvent.DoesNotExist:    
            with transaction.atomic():
                print "FB EVENT NOT EXIST, ADDING NEW SITE EVENT AND FB EVENT"
                # add the FB event to the website
                site_event = create_site_event_from_fb_live(lfbe)
                site_event.user_id = request.user.id
                try:
                    site_event.clean()
                except ValidationError as e:
                    # Unmappable location
                    site_event.unmappable()
                    failed_events.append(lfbe)
                site_event.save()

                # Store the FB event
                fb_event = create_fb_event_from_site_event(site_event)
                fb_event.eid = lfbe.eid
                fb_event.save()
    context = {}           
    return render(request, 'sync/syncevents.html', context)

#@receiver(post_save, sender=Event)
#def event_save_handler(sender, **kwargs):
#    print "EVENT SAVE SIGNAL",sender,kwargs
#    event = kwargs.get('instance', None)
#    if event:
#        print " EVENT:",event
#        print "  Event ID:",event.id
#        print "  Event location:",event.address
#        print "  Event date:",event.event_date
#        fbe = FbEvent.objects.get(event=event)
#        if not fbe:
#            # add the event to FB
#            fbe = create_fb_event_from_site_event(event)
#            fbe.eid = fbevents.create_event(FB_PAGE_NAME, FbEvent=fbe)
#            fbe.save()
#        else:
#            # TODO Check if event data has changed
#            pass
# 

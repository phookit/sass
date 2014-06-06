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

from mezzanine.conf import settings

from phookit.apps.events.models import Event
from phookit.apps.events.models import get_future_events as future_site_events
from phookit.apps.fb.models import get_future_events as future_fb_events
from phookit.apps.fb.models import create_fb_event_from_site_event, create_site_event_from_fb_live
from phookit.apps.fb.models import FbEvent
from phookit.apps.fb.api import FbAuth, FbEvents, FbNotAuthorisedException

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
        return redirect('/fb/adminauth?redir=/sync/syncevents')#'fb.views.adminauth')

    # ---------------------------------------------
    """
    events = fbevents.get_future_events(settings.SYNC_FACEBOOK_PAGE_NAME)
    # 1481855942032466 <-- ID
    print "FUTURE EVENTS:",events
    fbe = events[0]
    fbe.name = 'Blaaar updated'
    #neweid = fbevents.create_event(settings.SYNC_FACEBOOK_PAGE_NAME, FbEvent=fbe)
    #print "NEW EID=",neweid # 263957760453456
    fbe.eid = '263957760453456'
    fbe.location = 'fk1 2eg'
    result = fbevents.update_event(settings.SYNC_FACEBOOK_PAGE_NAME, FbEvent=fbe)
    print "UPDATE RES:",result
    return
    """
    # ---------------------------------------------

    #latest_fb_events = fbevents.get_future_events(settings.SYNC_FACEBOOK_PAGE_NAME)
    #for e in latest_fb_events:
    #    fbevents.delete_event(settings.SYNC_FACEBOOK_PAGE_NAME, e.eid)
    #return

    handled_fb_eids = []
    failed_fb_events = []
    updated_fb_events = []
    failed_site_events = []
    site_events = future_site_events()
    # check all site events are on FB
    for e in site_events:
        try:
            fbe = FbEvent.objects.get(event=e)
            
            handled_fb_eids.append(fbe.eid)

            compevent = create_fb_event_from_site_event(e)
            compevent.eid = fbe.eid
            if not compevent.compare(fbe):
                fbevents.update_event(settings.SYNC_FACEBOOK_PAGE_NAME, FbEvent=compevent)
                updated_fb_events.append(compevent)
        except FbEvent.DoesNotExist:
            with transaction.atomic():
                fbe = create_fb_event_from_site_event(e)
                try:
                    fbe.eid = fbevents.create_event(settings.SYNC_FACEBOOK_PAGE_NAME, FbEvent=fbe)
                    handled_fb_eids.append(fbe.eid)

                    fbe.save()
                except:
                    failed_fb_events.append(fbe)
                    if fbe.eid:
                        fbevents.delete_event(settings.SYNC_FACEBOOK_PAGE_NAME, fbe.eid)

    latest_fb_events = fbevents.get_future_events(settings.SYNC_FACEBOOK_PAGE_NAME)
    for lfbe in latest_fb_events:
        if lfbe.eid in handled_fb_eids:
            continue
        #                                                   2014-07-04T17:00:00+0100
        try:
            fbe = FbEvent.objects.get(eid=lfbe.eid)
            # print "LFBE ST:",lfbe.start_time,"FBE ST:",fbe.start_time
            if not lfbe.compare(fbe):
                fbevents.update_event(settings.SYNC_FACEBOOK_PAGE_NAME, FbEvent=lfbe)
                updated_fb_events.append(lfbe)
        except FbEvent.DoesNotExist:    
            with transaction.atomic():
                # add the FB event to the website
                site_event = create_site_event_from_fb_live(lfbe)
                site_event.user_id = request.user.id
                try:
                    site_event.clean()
                except ValidationError as e:
                    # Unmappable location
                    site_event.unmappable()
                    failed_fb_events.append(lfbe)
                site_event_ok = False
                try:
                    site_event.save()
                    site_event_ok = True
                except:
                    failed_site_events.append(site_event)
                    
                if site_event_ok:
                    try:
                        # Store the FB event
                        fb_event = create_fb_event_from_site_event(site_event)
                        fb_event.eid = lfbe.eid
                        fb_event.save()
                    except:
                        failed_fb_events.append(fb_event)


    context = {'failed_site_events': failed_site_events,
            'failed_fb_events': failed_fb_events,
            'updated_fb_events': updated_fb_events}
    return render(request, 'sync/syncevents.html', context)

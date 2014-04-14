import urllib
import cgi

from django.utils import simplejson as json
from django.shortcuts import render
from django.shortcuts import redirect

from mezzanine.utils.views import set_cookie

from fb.auth import FbAuth
from facebook import GraphAPI


import random # test
import string



#FACEBOOK_APP_ID = "581369638626613"
#FACEBOOK_APP_SECRET = "2551a0f60825f2c199de75c8926cfa0f"
#FACEBOOK_AUTH_URL = 'http://testing.saveastaffie.net/fb/auth'
FACEBOOK_ACCESS_TOKEN_LIFETIME = 30 * 24 * 60 * 60 # time in seconds


def _fb_authorise():
    args = dict(client_id=FACEBOOK_APP_ID,
            redirect_uri=FACEBOOK_AUTH_URL,
            scope='create_event,manage_pages,publish_stream')

    return redirect(
            "https://graph.facebook.com/oauth/authorize?" +
            urllib.urlencode(args))



def _get_access_token(code):
    args = dict(client_id=FACEBOOK_APP_ID,
            redirect_uri=FACEBOOK_AUTH_URL,
            client_secret=FACEBOOK_APP_SECRET,
            code=code)

    atstr = urllib.urlopen(
            "https://graph.facebook.com/oauth/access_token?" +
            urllib.urlencode(args)).read()
    print "AT STR RESPONSE",atstr
    response = cgi.parse_qs(atstr)
    print "AT RESPONSE: ",response
    access_token = response["access_token"][-1]
    return access_token 


def _get_profile(access_token):
    profile = json.load(urllib.urlopen(
            "https://graph.facebook.com/me?" +
            urllib.urlencode(dict(access_token=access_token))))
    print "PROFILE: ", profile
    return profile


def _get_accounts(access_token):
    accounts_profile = json.load(urllib.urlopen(
            "https://graph.facebook.com/me/accounts?" +
            urllib.urlencode(dict(access_token=access_token))))
    print "ACCOUNTS PROFILE: ", accounts_profile
    return accounts_profile 



def _create_event(access_token, page_id):
    g = GraphAPI(access_token)
    result = g.put_object(page_id, "events", name="Test event",
            start_time='2014-20-04T09:00:00-0000',
            end_time='2014-20-04T19:00:00-0000',
            description='Event description goes here',
            location='4 Callendar Rd, Falkirk, Stirlingshire FK1 1XQ',
            no_feed_story=False)
    print "EVENT RESULT:",result


def _get_events(access_token, page_id):
    """
    [
      {
          u'description': u'Event description goes here', 
          u'start_time': u'2014-07-04T17:00:00+0100', 
          u'pic': u'https://fbcdn-profile-a.akamaihd.net/static-ak/rsrc.php/v2/yi/r/zSnTif5Rf_V.png', 
          u'end_time': u'2014-07-05T03:00:00+0100', 
          u'location': u'4 Callendar Rd, Falkirk, Stirlingshire FK1 1XQ', 
          u'name': u'Test event',
          u'eid': u'272510589575221', 
      }, 
      {
          u'description': u'Event description goes here', 
          u'start_time': u'2014-07-04T17:00:00+0100', 
          u'pic': u'https://fbcdn-profile-a.akamaihd.net/static-ak/rsrc.php/v2/yi/r/zSnTif5Rf_V.png', 
          u'end_time': u'2014-07-05T03:00:00+0100', 
          u'location': u'4 Callendar Rd, Falkirk, Stirlingshire FK1 1XQ', 
          u'name': u'Test event',
          u'eid': u'272510589575227', 
      }, 
      {
          u'description': u'.......
      }
    ]
    """
    print "Getting events..."
    q = """SELECT eid, name, pic, start_time, end_time, location, description
           FROM
             event
           WHERE
             eid IN ( SELECT eid FROM event_member WHERE uid = %s )
           AND
             start_time >= now()
           ORDER BY
             start_time desc""" % page_id
    print "q = [%s]" % q
    g = GraphAPI(access_token)
    resp = g.fql(q)
    print resp


def index(request):
    print "index..."
    print "SESSION:",request.session.session_key
    # return urllib.urlopen(url, urllib.urlencode(args)).read()
    return render(request, 'fb/index.html', {})


def sync_events(request):
    pass


def adminauth(request):
    print "FB admin auth..."
    fbprofile = request.COOKIES.get('fbprofile', None)
    if fbprofile:
        fbprofile = json.loads(fbprofile)

    fbauth = FbAuth(request.COOKIES.get('fbtok', None),
                                 request.COOKIES.get('fbprofile', None))
    if fbauth.authorised():
        print "Got FB token from cookies"
        # --- test getting event...
        acct = fbauth.get_account('Blaaar De Blaar')
        if fbauth.can_create_content(acct):
            _get_events(fbauth.access_token, acct['id'])
        # ---

        return redirect(request.COOKIES.get('fbredir', '/'))

    print "SESSION:",request.session.session_key

    fbauth.verify(True, request.GET.get("code", None))
    if fbauth.authorised():
        redir = request.COOKIES.get('fbredir', '/')
        print "GOT FB REDIR COOKIE:",redir
        response = redirect(redir)
        # delete the fb redirection cookie
        response.delete_cookie('fbredir')
        set_cookie(response, 'fbtok', fbauth.access_token, expiry_seconds=FACEBOOK_ACCESS_TOKEN_LIFETIME, secure=False)
        set_cookie(response, 'fbprofile', json.dumps(fbauth.user_profile), expiry_seconds=FACEBOOK_ACCESS_TOKEN_LIFETIME, secure=False)

        return response
    # dont have a verification code so request one
    response = fbauth.authorise()
    redir = request.GET.get("redir", None)
    if redir:
        print "SETTING REDIR COOKIE:",redir
        set_cookie(response, 'fbredir', redir, expiry_seconds=30, secure=False)
    return response



#args = dict(client_id=FACEBOOK_APP_ID,
#            redirect_uri=FACEBOOK_AUTH_URL)
#    if verification_code:
#        access_token = _get_access_token(verification_code)
#
#        profile = _get_profile(access_token)
#
#        accounts_profile = _get_accounts(access_token)
#        for page in accounts_profile['data']:
#            print "PAGE:",page
#            if page['name'] == 'Blaaar De Blaar':
#                print "*** ADDING TO PAGE *** "
#                at = page['access_token']
#                id = page['id']
#                g = GraphAPI(at)
#                randstr = chars = "".join( [random.choice(string.letters) for i in xrange(15)] )
#                g.put_wall_post("Test post by %s\n\n%s" % (profile["first_name"], randstr), {}, id)
#
#                _create_event(at, id)
#
#
#
#        #user = User(key_name=str(profile["id"]), id=str(profile["id"]),
#        #            name=profile["name"], access_token=access_token,
#        #            profile_url=profile["link"])
#        #user.put()
#        #set_cookie(response, "fb_user", str(profile["id"]),
#        #           expires=time.time() + 30 * 86400)
#        return redirect("/")
#    else:
#        return _fb_authorise()


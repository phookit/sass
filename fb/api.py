
import urllib
import cgi
from datetime import datetime, timedelta

from django.shortcuts import redirect
from django.utils import simplejson as json
from django.utils import dateparse

from mezzanine.utils.views import set_cookie

from facebook import GraphAPI

from .models import FbTokens 
from .models import FbEvent

FACEBOOK_APP_ID = '581369638626613'
FACEBOOK_APP_SECRET = '2551a0f60825f2c199de75c8926cfa0f'
FACEBOOK_AUTH_URL = 'http://testing.saveastaffie.net/fb/adminauth'
FACEBOOK_ACCESS_TOKEN_LIFETIME = 30 * 24 * 60 * 60 # time in seconds
FACEBOOK_ADMIN_UNAMES = 'roger.wilko.58'

class FbAuthException(Exception):
    pass

class FbAuthCookiesException(Exception):
    pass

class FbNotAuthorisedException(Exception):
    pass

class FbAccountException(Exception):
    pass

class FbEventException(Exception):
    pass

#
# PROFILE:  {
#  u'username': u'roger.wilko.58', 
#  u'bio': u"Exactly. So logically if she weighs the same as a duck she's made of wood and therefore a witch.", 
#  u'first_name': u'Roger', 
#  u'last_name': u'Wilko', 
#  u'verified': True, 
#  u'name': u'Roger Wilko', 
#  u'locale': u'en_GB', 
#  u'gender': u'male', 
#  u'updated_time': u'2014-02-06T22:53:47+0000', 
#  u'quotes': u"Tried to teach my dog to dance but he's rubbish, got 2 left feet.", 
#  u'link': u'https://www.facebook.com/roger.wilko.58', 
#  u'timezone': 1, 
#  u'id': u'753148941'
# }

class FbAuth(object):
    def __init__(self, request):
        self.access_token = request.COOKIES.get('fbtok', None)
        self.user_profile = request.COOKIES.get('fbprofile', None)
        if self.user_profile:
            self.user_profile = json.loads(self.user_profile)
        self.accounts = None
        #  print "*** FbAuth:",self.access_token,self.user_profile 


    def update_cookies(self, response):
        set_cookie(response, 'fbtok', self.access_token, expiry_seconds=FACEBOOK_ACCESS_TOKEN_LIFETIME, secure=False)
        set_cookie(response, 'fbprofile', json.dumps(self.user_profile), expiry_seconds=FACEBOOK_ACCESS_TOKEN_LIFETIME, secure=False)


    def verify(self, request): 
        verification_code = request.GET.get("code", None)
        if verification_code:
            if not request.COOKIES.get('fbvc', None):
                raise FbAuthCookiesException()

            try:
                self.access_token = self._get_access_token(verification_code)
                self.user_profile = self.get_profile()
                # self.accounts = self.get_accounts(self.access_token)

                try:
                    if self.user_profile['username'] in FACEBOOK_ADMIN_UNAMES.split(','):
                        fbt = FbTokens(token=self.access_token, 
                                userid=self.user_profile['id'])
                        fbt.save()
                    else:
                        print "%s is not an admin. id is %s" % (self.user_profile['username'], self.user_profile['id'])
                except:
                    pass
            except:
                # ensure token and profile are not set
                self.access_token = None
                self.user_profile = None
                raise 

    def authorise(self, scope=None):
        # request a verification code from FB
        args = dict(client_id=FACEBOOK_APP_ID,
                redirect_uri=FACEBOOK_AUTH_URL)
        scope='create_event,manage_pages,publish_stream'
        if scope:
            args['scope'] = scope

        response = redirect(
                "https://graph.facebook.com/oauth/authorize?" +
                urllib.urlencode(args))
        set_cookie(response, 'fbvc', '1', expiry_seconds=10, secure=False)
        return response


    def authorised(self):
        return self.access_token and self.user_profile 


    def _get_access_token(self, code):
        args = dict(client_id=FACEBOOK_APP_ID,
                redirect_uri=FACEBOOK_AUTH_URL,
                client_secret=FACEBOOK_APP_SECRET,
                code=code)

        atstr = urllib.urlopen(
                "https://graph.facebook.com/oauth/access_token?" +
                urllib.urlencode(args)).read()
        # the atstr response is:
        # "access_token=CAAIQwKr...."
        #  print "AT STR:",atstr

        response = cgi.parse_qs(atstr)
        try:
            access_token = response["access_token"][-1]
        except KeyError:
            raise FbAuthException("Failed to get access token")
        return access_token 


    def get_profile(self):
        if not self.user_profile:
            self.user_profile = json.load(urllib.urlopen(
                    "https://graph.facebook.com/me?" +
                    urllib.urlencode(dict(access_token=self.access_token))))
            #  print "PROFILE: ", self.user_profile
        return self.user_profile


    def get_accounts(self):
        if not self.accounts:
            self.accounts = json.load(urllib.urlopen(
                    "https://graph.facebook.com/me/accounts?" +
                    urllib.urlencode(dict(access_token=self.access_token))))
            # accounts_profile will return:
            # ACCOUNTS PROFILE:  {
            # u'paging': {
            # u'next': u'https://graph.facebook.com/753148941/accounts?access_token=CAAIQ..&limit=5000&offset=5000&__after_id=65..'
            # }, 
            # u'data': [
            #  {
            #   u'category': u'Community', 
            #   u'access_token': u'CAA...', 
            #   u'perms': [
            #     u'EDIT_PROFILE', u'CREATE_CONTENT', u'MODERATE_CONTENT', u'CREATE_ADS', u'BASIC_ADMIN'
            #   ], 
            #   u'name': u'Bob Tails', 
            #   u'id': u'464165853684341'
            #  }, 
            #  {
            #   u'category': u'Community', 
            #   u'access_token': u'CAA...', 
            #   u'perms': [
            #     u'ADMINISTER', u'EDIT_PROFILE', u'CREATE_CONTENT', u'MODERATE_CONTENT', u'CREATE_ADS', u'BASIC_ADMIN'
            #   ], 
            #   u'name': u'Save A Staffie Scotland', 
            #   u'id': u'202402606578930'
            #  }, 
            #  {
            #   u'category': u'Community',
            #   .....
            #  }
            #]
            #   print "ACCOUNTS PROFILE: ", self.accounts
        return self.accounts

    def get_account(self, page_name):
        accts = self.get_accounts()
        for p in accts['data']:
            if p['name'] == page_name:
                return p
        raise FbAccountException('No account for %s' % page_name)


    def can_create_content(self, acct):
        try:
            if 'CREATE_CONTENT' in acct['perms']:
                return True
        except:
            pass
        return False


class FbEvents(object):
    def __init__(self, fbauth):
        if not fbauth.authorised():
            raise FbNotAuthorisedException()
        self.fbauth = fbauth

    def delete_event(self, page_id, eid):
        acct = self.fbauth.get_account(page_id)
        g = GraphAPI(acct['access_token'])
        g.delete_object(eid)

    def _get_event_from_args(self, **kwargs):
        # get non-optional args
        fbe = kwargs.get('FbEvent', None)
        if fbe:
            n = fbe.name
            st = fbe.start_time
            et = fbe.end_time # optional
            d = fbe.description
            loc = fbe.location # optional
            eid = fbe.eid # optional
        else:    
            n = kwargs.get('name', None)
            st = kwargs.get('start_time', None)
            et = kwargs.get('end_time', None) # optional
            d = kwargs.get('description', None)
            loc = kwargs.get('location', None) # optional
            eid = kwargs.get('eid', None) # optional
        if eid:
            eid = str(eid)
        if not n:
            raise FbAccountException('missing required argument: name')
        if not st:
            raise FbAccountException('missing required argument: start_time')
        if not d:
            raise FbAccountException('missing required argument: description')
        #if not loc:
        #    raise FbAccountException('missing required argument: location')
        # optional args
        nfs = kwargs.get('no_feed_story', False)

        result = {}
        result['name'] = n
        result['start_time'] = st
        result['description'] = d
        result['location'] = loc
        if et:
            result['end_time'] = et
        if eid:
            result['eid'] = eid
        if nfs:
            result['no_feed_story'] = nfs
        return result

    def update_event(self, page_id, **kwargs):
        args = self._get_event_from_args(**kwargs)
        acct = self.fbauth.get_account(page_id)
        g = GraphAPI(acct['access_token'])
        return g.put_object(args['eid'], "",
                **args)
        #return g.put_object(args['eid'], "",
        #       start_time=args['start_time'],
        #       end_time=args['end_time'],
        #       description=args['description'],
        #       location=args['location'])

    def create_event(self, page_id, **kwargs):
        args = self._get_event_from_args(**kwargs)
        acct = self.fbauth.get_account(page_id)
        g = GraphAPI(acct['access_token'])
        pores = g.put_object(acct['id'], "events",
                **args)
        return pores['id']
        #return g.put_object(acct['id'], "events",
        #       name=args['name'],
        #       start_time=args['start_time'],
        #       end_time=args['end_time'],
        #       description=args['description'],
        #       location=args['location'],
        #       no_feed_story=args['nfs'])


    def get_future_events(self, page_id):
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
        acct = self.fbauth.get_account(page_id)

        q = """SELECT eid, name, pic, start_time, end_time, location, description
               FROM
                 event
               WHERE
                 eid IN ( SELECT eid FROM event_member WHERE uid = %s )
               AND
                 start_time >= now()
               ORDER BY
                 start_time desc""" % acct['id']
        g = GraphAPI(acct['access_token'])
        resp = g.fql(q)
        result = []
        for e in resp:
            sdt = dateparse.parse_datetime(e['start_time'])
            edt = None
            if e['end_time']:
                edt = dateparse.parse_datetime(e['end_time'])
            fbe = FbEvent(eid=e['eid'],
                    start_time=sdt,
                    end_time=edt,
                    name=e['name'],
                    location=e['location'],
                    description=e['description'])
            result.append(fbe)
        return result






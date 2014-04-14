
import urllib
import cgi
from datetime import datetime, timedelta

from django.shortcuts import redirect
from django.utils import simplejson as json

from .models import FbTokens 

FACEBOOK_APP_ID = '581369638626613'
FACEBOOK_APP_SECRET = '2551a0f60825f2c199de75c8926cfa0f'
FACEBOOK_AUTH_URL = 'http://testing.saveastaffie.net/fb/adminauth'
FACEBOOK_ACCESS_TOKEN_LIFETIME = 30 * 24 * 60 * 60 # time in seconds
FACEBOOK_ADMIN_UNAMES = 'roger.wilko.58'

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
    def __init__(self, at=None, profile=None):
        self.access_token = at
        self.user_profile = profile
        self.accounts = None

    def verify(self, request_token=False, verification_code=None):

        if not verification_code:
            if request_token:
                return
            # check if we already have an access token created within N days ago
            toks = FbTokens.objects.filter(
                updated_date__gte=datetime.today() - timedelta(seconds=FACEBOOK_ACCESS_TOKEN_LIFETIME)
            ).order_by(
                '-updated_date'    
            )
                
            if len(toks):
                # NOTE: Facebook seems to have stopped sending the expiry time...
                #       Update: offline access was deprecated 1st May 2014 grrr
                # just use the first one (most recent)
                self.access_token = toks[0].token
        else: # verification code - get a new access code
            try:
                self.access_token = self._get_access_token(verification_code)
                self.user_profile = self._get_profile(self.access_token)
                # self.accounts = self.get_accounts(self.access_token)

                if self.user_profile['username'] in FACEBOOK_ADMIN_UNAMES.split(','):
                    fbt = FbTokens(token=self.access_token, 
                            userid=self.user_profile['id'])
                    fbt.save()
                else:
                    print "%s is not an admin. id is %s" % (self.user_profile['username'], self.user_profile['id'])
            except KeyError:
                # error getting access token
                self.access_token = None
                self.user_profile = None

    def authorise(self, scope=None):
        # request a verification code from FB
        args = dict(client_id=FACEBOOK_APP_ID,
                redirect_uri=FACEBOOK_AUTH_URL)
        if scope:
            args['scope'] = scope
            # scope='create_event,manage_pages,publish_stream')

        return redirect(
                "https://graph.facebook.com/oauth/authorize?" +
                urllib.urlencode(args))


    def authorised(self):
        return self.access_token and self.user_profile 


    def _cookie_auth(self):
        self.access_token = request.COOKIES.get('fbtok', None)
        if self.access_token:
            self.user_profile = request.COOKIES.get('fbprofile', None)


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
        print "AT STR:",atstr

        response = cgi.parse_qs(atstr)
        try:
            access_token = response["access_token"][-1]
        except KeyError:
            print "Failed to get access token: ",response
            raise
        return access_token 


    def _get_profile(self, access_token):
        profile = json.load(urllib.urlopen(
                "https://graph.facebook.com/me?" +
                urllib.urlencode(dict(access_token=access_token))))
        print "PROFILE: ", profile
        return profile


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
            print "ACCOUNTS PROFILE: ", self.accounts
        return self.accounts

    def get_account(self, page_name):
        accts = self.get_accounts()
        for p in accts['data']:
            if p['name'] == page_name:
                return p
        return None


    def can_create_content(self, acct):
        try:
            if 'CREATE_CONTENT' in acct['perms']:
                return True
        except:
            pass
        return False




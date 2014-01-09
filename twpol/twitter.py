import oauth2 as oauth
import urllib
from httplib2 import ServerNotFoundError
import simplejson
import time
from longscript.models import saveSleep, saveSpecialError
import pdb

from twpol.twitter_accounts import *

############################# MULTIPLE TWITTER ACCOUNTS TO AVOID RATE LIMITING

CONSECUTIVE_CYCLES = [0]
CURRENT_ACCOUNT = [0]
def getCurrentTwitterAccount():
    index = CURRENT_ACCOUNT[0]
    return TWITTER_ACCOUNTS[index]
def cycleTwitterAccounts():
    CONSECUTIVE_CYCLES[0] += 1
    saveSpecialError('twitter_cycle')
    # print "+~~+ cycle twitter accounts"
    index = CURRENT_ACCOUNT[0]
    if index < len(TWITTER_ACCOUNTS)-1:
        CURRENT_ACCOUNT[0] += 1
    else:
        CURRENT_ACCOUNT[0] = 0
    # if next account is still rate limited, then we sleep until account is reset
    twitter_account = getCurrentTwitterAccount()
    now = time.time()

    if now < twitter_account.available:
        sleep_for = twitter_account.available - now + 5
        # print "+WW+: sleeping for " + str(sleep_for)
        saveSleep(int(sleep_for))
        time.sleep(twitter_account.available - now + 5)
        # print "~awake~"
        CONSECUTIVE_CYCLES[0] = 0       # after we wake up from sleeping, set consecutive cycles back to 0
    # if we have cycled through all the twitter accounts without sleeping
    elif CONSECUTIVE_CYCLES[0] > len(TWITTER_ACCOUNTS):
        saveSpecialError('too_many_consecutive_cycles')
        CONSECUTIVE_CYCLES[0] = 0
        raise TwitterAuthenticationException('too_many_cycles')

#############################

def oauth_req(url):
    twitter_account = getCurrentTwitterAccount()
    CONSUMER_KEY = twitter_account.consumer_key
    CONSUMER_SECRET = twitter_account.consumer_secret
    MY_KEY = twitter_account.my_key
    MY_SECRET = twitter_account.my_secret
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth.Token(key=MY_KEY, secret=MY_SECRET)
    client = oauth.Client(consumer, token)

    response_received = False
    while not response_received:
        try:
            resp, content = client.request(
                url,
                method="GET"
            )
            response_received = True
        except ServerNotFoundError:
            saveSpecialError('server_not_found')
            time.sleep(1)

    # rate limiting
    remaining = resp.get('x-rate-limit-remaining')
    reset = resp.get('x-rate-limit-reset')
    if reset and remaining:
        remaining = int(remaining)
        reset = int(reset)
        twitter_account.setAvailable(reset)
        if remaining < 4:
            cycleTwitterAccounts()
    else:
        saveSpecialError('twitter_broken')
        cycleTwitterAccounts()
        raise TwitterAuthenticationException('twitter_broken')

    # status error
    status = resp.get('status')
    # print url
    # print status
    # print "*: " + str(remaining)
    saveSpecialError('total_status_' + status)
    saveSpecialError('[' + str(CURRENT_ACCOUNT[0]) + '] status_' + status)
    if not status == '200':
        saveSpecialError('[' + str(CURRENT_ACCOUNT[0]) + '] errors')
        raise TwitterAuthenticationException(status)

    # return response
    return content


def getFolloweesIDSFromID(id):
    return getFollowersIDSFromID(id, which_way="followees")

# cursored, gets complete list of all twitter_ids of users followers.
# specify which_way="followees" to get followees/friends
def getFollowersIDSFromID(id, which_way="followers"):
    next_cursor = -1
    ids = []
    while next_cursor:
        if which_way == "followers":
            resource_url = 'https://api.twitter.com/1.1/followers/ids.json'
        elif which_way == "followees":
            resource_url = 'https://api.twitter.com/1.1/friends/ids.json'
        params = {'user_id':id, 'cursor':next_cursor,'stringify_ids':'true'}
        url = resource_url + "?" + urllib.urlencode(params)
        response = oauth_req(url)
        response_dict = simplejson.loads(response)
        if response_dict.get('error'):
            raise TwitterErrorResponseException(str(id))
        else:
            next_cursor = response_dict['next_cursor']
            ids_page = response_dict['ids']
            ids.extend(ids_page)
    return ids

def isAFollowingB(id_a, id_b):
    resource_url = 'http://api.twitter.com/1/friendships/exists.json'
    params = {'user_id_a':id_a, 'user_id_b':id_b}
    url = resource_url + "?" + urllib.urlencode(params)
    response = oauth_req(url)
    return response == 'true'


def getUserInfoFromID(id=None, screen_name=None):
    resource_url = 'https://api.twitter.com/1.1/users/show.json'
    if id:
        params = {'user_id':id}
    else:
        params = {"screen_name":screen_name}
    url = resource_url + "?" + urllib.urlencode(params)
    response = oauth_req(url)
    response_dict = simplejson.loads(response)
    return response_dict


# exceptions
class TwitterErrorResponseException(Exception):
    pass

class TwitterAuthenticationException(Exception):
    pass
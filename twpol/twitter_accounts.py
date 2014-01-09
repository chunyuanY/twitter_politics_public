import time
import simplejson
import pdb
from twpol.settings import PROJECT_PATH
import os

class TwitterAccount:
    def __init__(self, consumer_key, consumer_secret, my_key, my_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.my_key = my_key
        self.my_secret = my_secret
        self.available = time.time()
        self.stalled = False
    def setAvailable(self, when):
        self.available = when

def refreshTwitterAccounts(start_index=None, end_index=None):
    del TWITTER_ACCOUNTS[:]
    f_path = os.path.join(PROJECT_PATH, 'twitter_credentials.json')
    f = open(f_path, 'r')
    credentials_json = f.read()
    twitter_credentials = simplejson.loads(credentials_json)
    for x in twitter_credentials:
        twit_account = TwitterAccount(
            consumer_key = x['consumer_key'],
            consumer_secret = x['consumer_secret'],
            my_key = x['my_key'],
            my_secret = x['my_secret']
        )
        TWITTER_ACCOUNTS.append(twit_account)
    f.close()
    print "NUM TWITTER ACCOUNTS: " + str(len(TWITTER_ACCOUNTS))
    if end_index:
        saved = TWITTER_ACCOUNTS[start_index:end_index]
        del TWITTER_ACCOUNTS[:]
        for x in saved:
            TWITTER_ACCOUNTS.append(x)
        print "CURRENT_THREAD using: " +str(start_index) + " - " + str(end_index) + " (" + str(len(TWITTER_ACCOUNTS)) + ")"

TWITTER_ACCOUNTS = []
refreshTwitterAccounts()

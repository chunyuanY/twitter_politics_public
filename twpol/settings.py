import os

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
TDIR = os.path.dirname(PROJECT_PATH)
INSTALLED_APPS = ('twpol','longscript','south')
SECRET_KEY = "tbi3=9_@f(jp1assdtv9y9jnl(a1m!@jursdk62#_b6_(x9d1b"
GLOBAL = {}
DEBUG = True

import json, socket
SECRETS_PATH = os.path.join(PROJECT_PATH, "secret.json")
LOCAL = os.environ.get("LOCAL")
if LOCAL:
    SECRETS_DICT = json.loads(open(SECRETS_PATH, "r").read())
else:
    SECRETS_ENV = os.environ.get("SECRETS")
    SECRETS_DICT = json.loads(SECRETS_ENV)

# check if running on server
try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

print "host: " + HOSTNAME + " | local=" + str(LOCAL)

REMOTE = os.environ.get('USE_REMOTE_DB')
if REMOTE:
    print "USING REMOTE DB"

if REMOTE:
    DATABASES = SECRETS_DICT["DATABASES"]
# database settings for script running on local machine with test db
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'test',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        },
        'old': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECT_PATH, 'old.db'),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            }
    }


# email settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'maximusfowler@gmail.com'
EMAIL_HOST_PASSWORD = SECRETS_DICT["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = 'maximusfowler@gmail.com'
import MySQLdb
from twpol.settings import DATABASES, DEBUG
from django.db import connection
import datetime
from django.core.mail import EmailMessage

def enc(s):
    return s.encode('ascii', 'ignore')

def getDBHandle():
    db_config = DATABASES['default']
    port = db_config['PORT']
    if port:
        db_handle = MySQLdb.connect(user=db_config['USER'],
                                    passwd=db_config['PASSWORD'],
                                    db=db_config['NAME'],
                                    host=db_config['HOST'],
                                    port=int(port))
    else:
        db_handle = MySQLdb.connect(user=db_config['USER'],
                                    passwd=db_config['PASSWORD'],
                                    db=db_config['NAME'],
                                    host=db_config['HOST'])
    return db_handle

Q_COUNT = [0]
def printQueries():
    if DEBUG:
        for x in connection.queries[Q_COUNT[0]:]:
            Q_COUNT[0] += 1
            print x

def printETA(start_time, count, total):
    now = datetime.datetime.now()
    delta = now - start_time
    percentage_passed = (count / float(total)) * 100
    percentage_remaining = 100 - percentage_passed
    seconds_per_percent = delta.total_seconds() / percentage_passed
    seconds_remaining = percentage_remaining * seconds_per_percent
    print str(count) + ": " + str(int(seconds_remaining / 60.0))


MONITOR_EMAIL_RECIPIENTS = ["max_fowler@brown.edu"]

def sendSuccessEmail(subject, body):
    email = EmailMessage(subject=subject, body=body, to=MONITOR_EMAIL_RECIPIENTS)
    email.send()
    print "success email sent."

def sendErrorEmail(subject, body):
    email = EmailMessage(subject=subject, body=body, to=MONITOR_EMAIL_RECIPIENTS)
    email.send()
    print "error email sent."
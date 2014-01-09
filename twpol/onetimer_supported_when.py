# this script looks in the old database to also store the date at which all voters followed the candidates they follow
from django.db import connections
from twpol.models import *

def saveWhenVotersFollowed():
    print "+II+: saving when voters followed candidates"
    voters = Voter.objects.all()
    cursor = connections['old'].cursor()
    print "total: " + str(voters.count())
    count = 0
    for voter in voters:
        for candidate in voter.supports.all():
            s = Support.objects.filter(voter=voter, candidate=candidate)
            if not s:
                sql = "SELECT date FROM followers_nov5 " \
                      "WHERE userid = '" + candidate.twitter_screen_name + "' " \
                      "and followersid = " + voter.twitter_id + "';"
                cursor.execute(sql)
                old_db_entry = cursor.fetchone()
                date = old_db_entry[0]
                s = Support(voter=voter, candidate=candidate, when=date)
                s.save()
        count += 1
        if not count % 20:
            print count

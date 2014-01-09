# this script takes all the following relationships that are stored in ashwin's old schema, and migrates them
# to the django db

from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
from twpol.models import *
from twpol.common import *
from twpol.download_followers import downloadFollowersIDs
import functools, math
from longscript import monitor_script
from django.db.utils import IntegrityError

def migrateCandidateFollowers(candidate, download_followers=False):
    print "+II+: migrating followers for " + enc(candidate.name)
    cursor = connections['old'].cursor()
    cursor.execute("SELECT followersid FROM followers_nov5 WHERE userid = '" + candidate.twitter_screen_name + "'")
    candidate_followers = cursor.fetchall()
    item_fun = functools.partial(migrateCandidateFollower, candidate=candidate, download_followers=download_followers)
    monitor_script.runScript("migrateCandidateFollowers (" + str(enc(candidate.twitter_screen_name)) + ")", items=candidate_followers, item_fun=item_fun, resolution=5)
    candidate.migrated_followers = True
    candidate.save()

def migrateCandidateFollowersFast(candidate,download_followers=False):
    print "+II+: fast migrating followers for " + enc(candidate.name)
    cursor = connections['old'].cursor()
    cursor.execute("SELECT count(*) FROM followers_nov5 WHERE userid = '" + candidate.twitter_screen_name + "'")
    total_candidate_followers = cursor.fetchone()[0]
    #item_fun = functools.partial(migrateCandidateFollower, candidate=candidate, download_followers=download_followers)
    item_fun = functools.partial(migrateCandidateFollowerBlunt, candidate=candidate)
    window_size = 50000
    total_processed = 0
    num_windows = int(math.ceil(total_candidate_followers / float(window_size)))
    for c_window in range(0,num_windows):
        query = "SELECT followersid " \
                "FROM followers_nov5 " \
                "WHERE userid = '" + candidate.twitter_screen_name + "'"\
                + " LIMIT " + str(window_size)\
                + " OFFSET " + str(total_processed)
        cursor.execute(query)
        window = cursor.fetchall()
        total_processed += len(window)
        title = "migrateCandidateFollowers " + str(enc(candidate.twitter_screen_name)) + "(" + str(c_window) + "/" + str(num_windows)+ ")"
        monitor_script.runScript(name=title, items=window, item_fun=item_fun, resolution=5)

    candidate.migrated_followers = True
    candidate.save()


def migrateCandidateFollower(follower, candidate, download_followers=False):
    follower_twitter_id = follower[0]
    query = "SELECT id FROM twpol_voter WHERE twitter_id= '" + str(follower_twitter_id) + "'"
    try:
        voter = Voter.objects.raw(query)[0]
    except IndexError:
        voter = Voter(twitter_id=follower_twitter_id,
                      party = candidate.party,
                      district = candidate.district)
        voter.save()
    # voter supports candidate
    voter.supports.add(candidate)
    # if download followers flag, then download twitter follower ids for this voter
    if download_followers and not voter.downloaded_followers:
        downloadFollowersIDs(voter)


def migrateCandidateFollowerBlunt(follower, candidate):
    follower_twitter_id = follower[0]
    try:
        voter = Voter(twitter_id=follower_twitter_id,
                  party = candidate.party,
                  district = candidate.district)
        voter.save()
    except IntegrityError as e:
        pass
    from django.db import connections
    print connections["default"].queries[-1]


from twpol.export_to_stata import getSetOfRelevantIds
#TWITTER_IDS = getSetOfRelevantIds()
#IDS_TO_INSERT = []

def migrateFun():
    candidates = Candidate.objects.filter(candidate_type__in=[2,3,4,5], migrated_followers=False).order_by("name")
    item_fun = functools.partial(migrateCandidateFollowersFast, download_followers=False)
    monitor_script.runScript("migrateCandidateFollowers", items=candidates, item_fun=item_fun, resolution=5)

# main script migrates followers of all candidates   # have processed 756 so far
if __name__=="__main__":
    migrateFun()

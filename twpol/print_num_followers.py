from twpol.models import *
from django.db import connections

def getNumFollowersNov5(candidate):
    cursor = connections['old'].cursor()
    cursor.execute("SELECT count(*) FROM followers_nov5 WHERE userid = '" + candidate.twitter_screen_name + "'")
    total_candidate_followers = cursor.fetchone()[0]
    return total_candidate_followers

def printNumFollowers(nov5=True):
    candidates = Candidate.objects.all()
    c_types = {}
    no_followers = []
    total_followers = 0
    total_followers_not_downloaded = 0

    for x in candidates:
        if nov5:
            num_followers = x.num_followers
        else:
            num_followers = getNumFollowersNov5(x)
            x.num_followers = num_followers
            x.save()
        c_type = x.candidate_type
        if not c_type in c_types:
            c_types[c_type] = {"num_candidates":0,
                               "num_followers":0
                               }
        c_types[c_type]["num_candidates"] += 1
        c_types[c_type]["num_followers"] += num_followers

        total_followers += num_followers
        if not x.migrated_followers:
            total_followers_not_downloaded += num_followers

        if num_followers == 0:
            no_followers.append(x)

    print "TOTAL FOLLOWERS: " + str(total_followers)
    print "TOTAL NOT MIGRATED: " + str(total_followers_not_downloaded)
    print "NUM CANDIDATES WITH NO FOLLOWERS: " + str(len(no_followers))

    print c_types

    for c_type in c_types.keys():
        print("\n\n")
        candidates = Candidate.objects.filter(candidate_type=c_type)
        print "*** " + str(c_type) + " ***"
        for x in candidates.order_by("-num_followers"):
            print x.twitter_screen_name + ": " + str(x.num_followers)




if __name__=="__main__":
    printNumFollowers()


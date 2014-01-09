# exports data to stata

from twpol.models import *
import os, sys
from traceback import format_exception
from twpol.settings import PROJECT_PATH
from django.db import connections
from twpol.common import *
from MySQLdb import cursors
import datetime, json


def getCandidateDict():
    candidate_dict = {}
    for candidate in Candidate.objects.all():
        candidate_dict[candidate.twitter_screen_name] = candidate
        candidate_dict[candidate.twitter_id] = candidate
    return candidate_dict

# keep set of all voter twitter ids in memory
def getSetOfRelevantIds(only_downloaded=True):
    db_handle = getDBHandle()
    cursor = db_handle.cursor()
    if only_downloaded:
        query = "SELECT twitter_id" \
                " FROM twpol_voter" \
                " WHERE downloaded_followers=1"
    else:
        query = "SELECT twitter_id" \
            " FROM twpol_voter"
    print "query: " + query
    cursor.execute(query)
    result = cursor.fetchall()
    twitter_ids = set([])
    print "enumerating..."
    for i,x in enumerate(result):
        twitter_ids.add(x[0])
        if not i % 1000:
            print i
    return twitter_ids


# convert all voters with downloaded followers ids into m2ms between voters
def calculatePrunedIDs():

    db_handle = getDBHandle()
    cursor = db_handle.cursor()

    twitter_ids = getSetOfRelevantIds(only_downloaded=True)
    total = len(twitter_ids)

    # loop to set pruned_followers_ids
    print "total: " + str(total)
    results = 0
    start_time = datetime.datetime.now()
    offset_id = 0
    while results < total:
        query = "SELECT id, twitter_id" \
            " FROM twpol_voter" \
            " WHERE downloaded_followers=1" \
            " AND pruned=0" \
            " AND id>%s" \
            " ORDER BY id" \
            " LIMIT 10000"
        voters = Voter.objects.raw(query, [offset_id])
        for voter in voters:
            offset_id = voter.id
            results += 1
            followers_ids = set(voter.getFollowersIDS())
            pruned_followers_ids = followers_ids.intersection(twitter_ids)
            stringified = ",".join(pruned_followers_ids)
            voter.pruned_followers_ids = stringified
            voter.pruned = True
            voter.save()
            if not results % 100:
                printETA(start_time, results, total)



# voter, voter file
# followee, follower
def exportVoterVoterFile(output_path, real_time=False, raw=False):
    if not real_time:
        relevant_ids = set([])
    else:
        relevant_ids = getSetOfRelevantIds(only_downloaded=True)
    output_file = open(output_path, 'w')
    total = Voter.objects.filter(downloaded_followers=True).count()
    print "total: " + str(total)
    results = 0
    start_time = datetime.datetime.now()
    offset_id = 0
    while results < total:
        query = "SELECT id, twitter_id" \
            " FROM twpol_voter" \
            " WHERE downloaded_followers=1" \
            " AND id>%s" \
            " ORDER BY id" \
            " LIMIT 10000"
        voters = Voter.objects.raw(query, [offset_id])
        for voter in voters:
            offset_id = voter.id
            results += 1
            if raw:
                for follower_id in voter.getFollowersIDS():
                    line = str(voter.twitter_id) + "," + str(follower_id) + "\n"
                    output_file.write(line)
            else:
                if not real_time:
                    pruned_ids = voter.getPrunedFollowersIDS()
                else:
                    all_ids = set(voter.getFollowersIDS())
                    pruned_ids = all_ids.intersection(relevant_ids)
                for follower_id in pruned_ids:
                    line = str(voter.twitter_id) + "," + str(follower_id) + "\n"
                    output_file.write(line)
            if not results % 100:
                output_file.flush()
                printETA(start_time, results, total)
    output_file.flush()
    output_file.close()


# candidate voter file
# candidate, follower, candidate_type
def exportCandidateVoterFile(output_path):
    output_file = open(output_path, 'w')
    db_handle = getDBHandle()
    total = Voter.objects.filter(downloaded_followers=True).count()
    print "total: " + str(total)
    results = 0
    start_time = datetime.datetime.now()
    offset_id = 0
    while results < total:
        query = "SELECT id, twitter_id" \
            " FROM twpol_voter" \
            " WHERE downloaded_followers=1" \
            " AND id>%s" \
            " ORDER BY id" \
            " LIMIT 10000"
        voters = Voter.objects.raw(query, [offset_id])
        for voter in voters:
            offset_id = voter.id
            results += 1
            for canidate in voter.supports.all():
                    #line = str(candidate.twitter_id) + "," + str(voter.twitter_id) + "\n"
                    candidate_type = candidate.candidate_type
                    line = str(candidate.twitter_screen_name) + "," + str(voter.twitter_id) + "," + str(candidate_type) + "\n"
                    output_file.write(line)
            if not results % 100:
                output_file.flush()
                printETA(start_time, results, total)

    output_file.flush()
    output_file.close()


# candidate voter file
# candidate, follower, candidate_type
def exportCandidateVoterFileFromOldDB(output_path, only_downloaded=True):
    candidate_dict = getCandidateDict()
    if only_downloaded:
        relevant_ids = getSetOfRelevantIds(only_downloaded=True)
    else:
        relevant_ids = []
    output_file = open(output_path, 'w')
    db_handle = getDBHandle()
    results = 0
    start_time = datetime.datetime.now()
    offset_id = 0
    old_cursor = connections['old'].cursor()
    count_query = "SELECT count(*) from followers_nov5"
    print count_query
    old_cursor.execute(count_query)
    total = old_cursor.fetchone()[0]
    print "total: " + str(total)
    windows = 0
    while results < total:
        windows += 1
        print "window: " + str(windows)
        query = "SELECT p_id, userid, id_str, followersid" \
            " FROM followers_nov5" \
            " WHERE p_id>%s" \
            " ORDER BY p_id" \
            " LIMIT 10000"
        old_cursor.execute(query, [offset_id])
        rows = old_cursor.fetchall()
        if not len(rows):
            print("+XX+ EMPTY QUERY")
            break
        for row in rows:
            results += 1
            offset_id = row[0]
            candidate_screen_name = row[1]
            candidate_twitter_id = row[2]
            follower_id = row[3]
            if only_downloaded:
                dont_write = follower_id not in relevant_ids
            else:
                dont_write = False
            if not dont_write:
                candidate = candidate_dict.get(candidate_screen_name) or candidate_dict.get(candidate_twitter_id)
                candidate_type = candidate.candidate_type
                line = str(candidate.twitter_screen_name) + "," + str(follower_id) + "," + str(candidate_type) + "\n"
                output_file.write(line)
            if not results % 1000:
                output_file.flush()
                printETA(start_time, results, total)
    output_file.flush()
    output_file.close()
    print "results: " + str(results)
    print "total windows: " + str(windows)
    print "total: " + str(total)
    print "offset_id: " + str(offset_id)
    print "query: " + str(query)


def updateSupports():
    candidate_dict = getCandidateDict()
    total = Voter.objects.count()
    print "total: " + str(total)
    old_cursor = connections['old'].cursor()
    results = 0
    start_time = datetime.datetime.now()
    offset_id = 0
    while results < total:
        query = "SELECT id, twitter_id" \
            " FROM twpol_voter" \
            " WHERE id>%s" \
            " ORDER BY id" \
            " LIMIT 10000"
        voters = Voter.objects.raw(query, [offset_id])
        for voter in voters:
            offset_id = voter.id
            results += 1
            supports_query = "SELECT userid, id_str" \
            " FROM followers_nov5" \
            " WHERE followersid=%s"
            old_cursor.execute(supports_query, voter.twitter_id)
            rows = old_cursor.fetchall()
            for row in rows:
                candidate_screen_name = row[0]
                candidate_twitter_id = row[1]
                candidate = candidate_dict.get(candidate_twitter_id) or candidate_dict.get(candidate_screen_name)
                if candidate:
                    voter.supports.add(candidate)
                else:
                    print("+EE+: " + candidate_screen_name)
            if not results % 100:
                printETA(start_time, results, total)




# all ids that voters are following
# folowee, voter
def exportRawVoterFolloweesFile(output_path, voters=None):
    output_file = open(output_path, 'w')
    if not voters: voters = Voter.objects.filter(downloaded_followers=True)
    print "voters: " + str(voters.count())
    count = 0
    for voter in voters:
        for followee_id in voter.getFolloweesIDS():
            line = str(followee_id) + "," + str(voter.twitter_id) + "\n"
            output_file.write(line)
        count += 1
        if not count % 50:
            print count

# all ids of followers of voters
# voter, follower
def exportRawVoterFollowersFile(output_path, voters=None):
    output_file = open(output_path, 'w')
    if not voters: voters = Voter.objects.filter(downloaded_followers=True)
    print "voters: " + str(voters.count())
    count = 0
    for voter in voters:
        for follower_id in voter.getFollowersIDS():
            line = str(voter.twitter_id) + "," + str(follower_id) + "\n"
            output_file.write(line)
        count += 1
        if not count % 50:
            print count

# candidate voter file
# candidateid, follower twitter_id
def exportCandidateVoterFileFromOldDBSimple(output_path):
    output_file = open(output_path, 'w')
    cursor = connections['old'].cursor()
    cursor.execute("SELECT * FROM followers_nov5")
    candidate_followers = cursor.fetchall()
    print "total: " + str(len(candidate_followers))
    count = 0
    for x in candidate_followers:
        candidate_num = x[1]
        follower_twitter_id = x[4]
        candidate_type = candidate_num [0]  # consult data/candidate_id_explained.txt for explanation
        line = str(candidate_num) + "," + str(follower_twitter_id) + "," + str(candidate_type) + "\n"
        output_file.write(line)
        count += 1
        if not count % 50:
            print count

# output data from new db
def outputVoterDataToText():
    # calculate which
    # calculatePrunedIDs()
    # candidatevoter
    candidatevoter_output_file = os.path.join(PROJECT_PATH, 'data/candidatevoter_all_jan3.txt')
    exportCandidateVoterFileFromOldDB(candidatevoter_output_file, only_downloaded=False)
    # exportCandidateVoterFile(candidatevoter_output_file)
    # votervoter
    # votervoter_output_file = os.path.join(PROJECT_PATH, 'data/votervoter_onlydownloaded.txt')
    # exportVoterVoterFile(votervoter_output_file)
    # # rawfollowers
    # rawfollowers_output_file = os.path.join(PROJECT_PATH, 'data/rawfollowers.txt')
    # exportVoterVoterFile(rawfollowers_output_file, raw=True)
    # rawfollowees
    # rawfollowees_output_file = os.path.join(PROJECT_PATH, 'data/rawfollowees_dec22.txt')
    # exportRawVoterFolloweesFile(rawfollowees_output_file)

def mainExportFun():
    try:
        outputVoterDataToText()
        # updateSupports()
    except Exception as e:
        e_type, the_exception, traceback = sys.exc_info()
        e_strings = format_exception(e_type, the_exception, traceback)
        e_message = ""
        for i,x in enumerate(e_strings):
            e_message += x + "\n"
        e_message = "[Stata Export Error]\n" + str(e_message)
        sendErrorEmail(subject="XXX Stata Export Error XXX", body=e_message)
    else:
        sendSuccessEmail(subject="Stata Export Finished", body="yay")
        # from twpol.monitor_email import EmailMonitor
        # email_monitor = EmailMonitor()
        # safety_switch_dict = {"safety_switch_off":0}
        # email_monitor.setSafetySwitch(json.dumps(safety_switch_dict))

# main script
if __name__=="__main__":
    mainExportFun()
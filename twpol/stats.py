from twpol.models import *
from django.db import connections
import xlwt
import os, json
from twpol.settings import PROJECT_PATH

# see how many voters there are total
def calcTotalCandidateFollowers(candidates=None):
    if not candidates: candidates = Candidate.objects.all()
    print "num candidates: " + str(candidates.count())
    total = 0
    count = 0
    for x in candidates:
        total += x.getNumFollowers()
        count += 1
        if not count % 20:
            print count
    print "total followers: " + str(total)

def countCandidateFollowers(candidate):
    cursor = connections['old'].cursor()
    cursor.execute("SELECT COUNT(*) FROM followers_nov5 WHERE userid = '" + candidate.twitter_screen_name + "'")
    result = cursor.fetchall()
    num = result[0][0]
    return num

def outputNumCandidateFollowers(output_file, candidates=None):
    wb = xlwt.Workbook(encoding="utf-8")
    candidates_sheet = wb.add_sheet("Num Followers By Candidate")
    state_codes = {}
    if not candidates: candidates = Candidate.objects.all()
    for count,candidate in enumerate(candidates):
        candidate.num_followers = countCandidateFollowers(candidate)
        if not count % 20:
            print count
    for row,candidate in enumerate(sorted(list(candidates), key=lambda x: x.num_followers, reverse=True)):
        # write to .xls
        candidates_sheet.write(row,0, candidate.name)
        candidates_sheet.write(row,1, candidate.twitter_screen_name)
        candidates_sheet.write(row,2, candidate.num_followers)
        # keep track of num followers by state
        if not candidate.district:
            print "+WW+: " + candidate.twitter_screen_name
            continue
        state_code = candidate.district.state_code
        if not state_code in state_codes:
            state_codes[state_code] = 0
        state_codes[state_code] += candidate.num_followers
    states_sheet = wb.add_sheet("Num Followers By State")
    row = 0
    for state_code,num_followers in state_codes.items():
        states_sheet.write(row,0, state_code)
        states_sheet.write(row,1, num_followers)
        row += 1
    # save .xls
    wb.save(output_file)

# candidateid, follower twitter_id
# candidatetype (1=house candidate, 2=senate candidate, 3=senator not up for re-election, 4=house lameduck, 5=senate lameduck, 6=presidential candidate, 7=media market)
def countCandidateFollowersFromOldDB():
    cursor = connections['old'].cursor()
    cursor.execute("SELECT * FROM followers_nov5")
    candidate_followers = cursor.fetchall()
    print "total: " + str(len(candidate_followers))
    count = 0
    candidate_types = {}
    for x in candidate_followers:
        candidate_num = x[1]
        candidate_type = candidate_num[0]
        if not candidate_type in candidate_types:
            candidate_types[candidate_type] = 0
        candidate_types[candidate_type] += 1
        count += 1
        if not count % 50:
            print count
    for k,v in candidate_types.items():
        print str(k) + ": " + str(v)

# average number of voter links
def voterLinksStats(voters=None):
    if not voters: voters = Voter.objects.all()
    total_links = 0
    total_voters = len(voters)
    downloaded_followers = voters.filter(downloaded_followers=True)
    print "total voters: " + str(total_voters)
    print "downloaded followers for: " + str(downloaded_followers.count())
    print "over max followers: " + str(voters.filter(over_max_followers=True).count())
    print "------ error codes for others --------"
    error_codes = set([])
    for x in voters:
        error_code = x.error_code
        if error_code:
            error_codes.add(error_code)
    for error_code in error_codes:
        print error_code + ": " + str(voters.filter(error_code=error_code).count())
    total_followers = 0
    for x in voters:
        num_followers = len(x.getFollowersIDS())
        total_followers += num_followers
        num_links = len(x.getPrunedFollowersIDS())
        total_links += num_links
    print "------ num followers stats --------"
    print "total voters with followers downloaded: " + str(downloaded_followers.count())
    print "mean followers: " + str(total_followers / float(downloaded_followers.count()))
    print "total links: " + str(total_links)
    print "mean links: " + str(total_links / float(downloaded_followers.count()))


def distributionOfErrors():
    cursor = connections['default'].cursor()
    # get total percentage of voters successfully downloaded who at somepoint had an error
    query = "SELECT count(*) FROM twpol_voter where error_code!=''"
    print "query: " + query
    cursor.execute(query)
    total_errors = cursor.fetchone()[0]
    print "TOTAL NUM ERRORS: " + str(total_errors)
    query = "SELECT count(*) FROM twpol_voter where error_code!='' and downloaded_followers=1"
    print "query: " + query
    cursor.execute(query)
    total_successes = cursor.fetchone()[0]
    print "NUM SUCCESSES 2nd PASS: " + str(total_successes)
    # look at success rate by error
    query = "SELECT DISTINCT error_code FROM twpol_voter"
    print "query: " + query
    cursor.execute(query)
    results = cursor.fetchall()
    error_codes = {}
    for x in results:
        error_code = x[0]
        # get total with error_code
        query = "SELECT count(*) FROM twpol_voter where error_code=%s"
        print "query: " + query
        cursor.execute(query, [error_code])
        total = cursor.fetchone()[0]
        # get num successful downloads with error_code
        query = "SELECT count(*) FROM twpol_voter where error_code=%s and downloaded_followers=1"
        print "query: " + query
        cursor.execute(query, [error_code])
        successes = cursor.fetchone()[0]
        error_codes[error_code] = {"total":total,"successes":successes}
    print "++ ERROR DISTRIBUTION ++ "
    print json.dumps(error_codes)


# main script
if __name__=="__main__":
    distributionOfErrors()
    # output_file = os.path.join(PROJECT_PATH, 'data/num_followers.xls')
    # candidates = Candidate.objects.filter(district__state_code=47)
    # outputNumCandidateFollowers(output_file, candidates=candidates)
    # voterLinksStats()
    #countCandidateFollowersFromOldDB()
# store voter objects for each unique follower of a house candidate on nov 5 2012
# download twitter_ids of all followers for every voter

from django.db import connections
from twpol.models import *
from twpol.migrate_voters import *
from twpol.parse_candidates import parseCandidatesFromSpreadSheet
import functools
from longscript import monitor_script
from longscript.models import resetSleepCounter, clearSavedExceptions, clearSavedScripts, clearSavedSpecialErrors
from twpol.download_followers import downloadFollowersForStrayVotersFast, downloadFolloweesIDs
import os
from twpol.settings import PROJECT_PATH

def analyzeState(state_code):
    candidates = Candidate.objects.filter(district__state_code=state_code, migrated_followers=False)
    item_fun = functools.partial(migrateCandidateFollowers, download_followers=True)
    monitor_script.runScript("analyzeState (" + str(state_code) + ")", items=candidates, item_fun=item_fun, resolution=1)

def analyzeDistrict(district):
    candidates = Candidate.objects.filter(district=district)
    item_fun = functools.partial(migrateCandidateFollowers, download_followers=False)
    monitor_script.runScript("analyzeDistrict ( " + str(district.district_number) + ")", items=candidates, item_fun=item_fun, resolution=5)

def clearFun():
    print "clearingLongScripts"
    cursor = connections['default'].cursor()
    cursor.execute("DELETE FROM longscript_script")
    cursor.execute("DELETE FROM longscript_scriptexception")
    cursor.execute("DELETE FROM longscript_scriptsleep")
    cursor.execute("DELETE FROM longscript_scriptspecialerror")
    cursor.close()
    print "deleted."

def mainFun():
    clearFun()
    migrateFun()

    #candidates_xls = os.path.join(PROJECT_PATH, 'data/candidates.xls')
    #parseCandidatesFromSpreadSheet(candidates_xls)
    #downloadFollowersForStrayVotersFast(num_total_threads=10)
    # candidates = Candidate.objects.filter(migrated_followers=False).exclude(twitter_screen_name="RepPaulRyan").exclude(twitter_screen_name="PaulRyanVP")
    # candidates = Candidate.objects.filter(migrated_followers=False)
    # item_fun = functools.partial(migrateCandidateFollowersFast, download_followers=False)
    # monitor_script.runScript("House Candidates Except RepPaulRyan and PaulRyanVP", items=candidates, item_fun=item_fun, resolution=5)
    # voters = Voter.objects.filter(district__state_code=47, downloaded_followees=False)
    # monitor_script.runScript("Download NC Followees", items=voters, item_fun=downloadFolloweesIDs, resolution=5)
    #createManyTwitterAccounts()

# main script
if __name__=="__main__":
    mainFun()


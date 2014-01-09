# file for ease of testing scripts

from twpol.settings import PROJECT_PATH
from twpol.main import mainFun
from twpol import parse_candidates
from longscript import monitor_script
from twpol.stats import *
import os
import pdb
from twpol.export_to_stata import *
from twpol.selenium_download import seleniumDownload
from twpol.create_twitter_account import createTwitterAccount, createManyTwitterAccounts
from twpol.fix import fixFun, deleteDuplicatesFun
from twpol.heroku_launch import backupDatabase, waitForDatabaseBackupToComplete, scaleUpDynos, mainLaunchFun, \
    resetThreadCounter, printThreadCounter, returnAllVotersToMainTable
from twpol.stats import distributionOfErrors
from twpol.migrate_voters import migrateFun, migrateCandidateFollowerBlunt
from twpol.monitor_email import mainMonitorEmailFun
from twpol.monitor_processes import findPythonProcesses

#candidates_xls = os.path.join(PROJECT_PATH, 'data/candidates.xls')
#parse_candidates.parseCandidatesFromSpreadSheet(candidates_xls)

#migrate_candidate_followers.migrateAllCandidateFollowers()

#analyzeState(33)

#monitor_script.clearScripts()
#monitor_script.currentStatusRunningScripts()

#calcTotalVoters()

# output_file = os.path.join(PROJECT_PATH, 'data/num_followers.xls')
# candidates = Candidate.objects.filter(district__state_code=47)
# outputNumCandidateFollowers(output_file, candidates=candidates)

#voters = Voter.objects.filter(district__state_code=47)
#voterLinksStats(voters)


candidatevoter_output_file = os.path.join(PROJECT_PATH, 'data/candidatevoter_testrun.xls')
exportCandidateVoterFile(candidatevoter_output_file)
# # votervoter
# votervoter_output_file = os.path.join(PROJECT_PATH, 'data/votervoter_nc.xls')
# exportVoterVoterFile(votervoter_output_file, voters
# )

# mainFun()
# deleteDuplicatesFun()

# calculateWhichFollowersAreVoters()

# createManyTwitterAccounts()

# monitor_script.displayScriptProgress()

#createManyTwitterAccounts()

#backupDatabase()

#waitForDatabaseBackupToComplete()

# mainLaunchFun()

#startFirstDyno()

# resetThreadCounter()
# printThreadCounter()
#scaleUpDynos()

# returnAllVotersToMainTable()

#distributionOfErrors()

#migrateFun()

#mainFun()

#c = Candidate.objects.all()[0]
#f = [100000605]
#migrateCandidateFollowerBlunt(f,c)

#mainMonitorEmailFun()

# print findPythonProcesses()
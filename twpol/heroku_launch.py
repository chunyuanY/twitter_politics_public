# launches heroku parallel download machine
TOTAL_THREADS = 6


from subprocess import call
from exceptions import OSError
from twpol.models import *
from twpol.common import *
from traceback import format_exception
from django.db import connections
from twpol.main import clearFun
import time, datetime, sys
from django.core.mail import EmailMessage
from longscript.monitor_script import displayScriptProgress
import boto
import boto.rds
from twpol.settings import SECRETS_DICT, TDIR
import heroku


# this is code that should be modified to effect who is processed by batch download
def calculateShouldProcess():
    cursor = connections['default'].cursor()
    query = "UPDATE twpol_voter SET should_process=0"
    print "query: " + query
    cursor.execute(query)
    query = "UPDATE twpol_voter SET should_process=1 where downloaded_followees=0 and num_followee_attempts<2"
    print "query: " + query
    cursor.execute(query)
    cursor.close()

# global variables keeping track of how many threads we want to use
def printThreadCounter():
    total_threads = DataPoint.objects.get(name="total_threads")
    print "TOTAL THREADS: " + str(total_threads.value)
    running_threads = DataPoint.objects.get(name="running_threads")
    print "RUNNING THREADS: " + str(running_threads.value)

def resetThreadCounter():
    total_threads = DataPoint.objects.get(name="total_threads")
    total_threads.value = TOTAL_THREADS
    total_threads.save()
    running_threads = DataPoint.objects.get(name="running_threads")
    running_threads.value = 0
    running_threads.save()

# count how many in each table, for sanity
def countTable(table, should_process=-1):
    cursor = connections['default'].cursor()
    if should_process == -1:
        query = "SELECT count(*) from " + table
    else:
        query = "SELECT count(*) from " + table + " where should_process=" + str(should_process)
    cursor.execute(query)
    number = cursor.fetchone()[0]
    cursor.close()
    return number

def countAllVoterTables():
    twpol_voter = countTable("twpol_voter")
    extraneous_voter = countTable("extraneous_voter")
    twpol_voter_should_not_process = countTable("twpol_voter", should_process=0)
    return {
        "twpol_voter":twpol_voter,
        "extraneous_voter":extraneous_voter,
        "twpol_voter_should_not_process":twpol_voter_should_not_process,
        "num_total_voters":twpol_voter + extraneous_voter
    }

# voter migrations
def migrateExtraneousVoters():
    cursor = connections['default'].cursor()
    query = "INSERT extraneous_voter SELECT * FROM twpol_voter WHERE should_process=0"
    print "query: " + query
    cursor.execute(query)
    # check if increase in extraneous_voter is same size as twpol_voter where should_process=0... if not raise
    query = "DELETE from twpol_voter WHERE should_process=0"
    print "query: " + query
    cursor.execute(query)
    cursor.close()

def returnAllVotersToMainTable():
    cursor = connections['default'].cursor()
    query = "INSERT twpol_voter SELECT * FROM extraneous_voter"
    print "query: " + query
    cursor.execute(query)
    # check if twpol_voter is now equal to form twpol_voter + former extraneous_voter
    query = "TRUNCATE TABLE extraneous_voter"
    print "query: " + query
    cursor.execute(query)
    cursor.close()

# visual feedback
def pPrintDict(some_dict):
    for k,v in some_dict.items():
        print k + ": " + str(v)


LAUNCH_EMAIL_RECIPIENTS = ["max_fowler@brown.edu"]
def sendHerokuErrorEmail(error):
    error_message = "Error: " + error
    sendErrorEmail(subject='Launch Error', body=error_message)

def sendHerokuSuccessEmail():
    sendSuccessEmail(subject='**** Heroku Launched ****', body="")


class LostVotersException(Exception):
    pass

# amazon rds backup
def backupDatabase():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
    snapshot_id = "mhfowler-" + str(st)
    snapshot_id = snapshot_id.replace(" ","")
    rds = boto.connect_rds()
    instances = rds.get_all_dbinstances()
    db = instances[0]
    db.snapshot(snapshot_id)
    print("backing up database...")
    waitForDatabaseBackupToComplete()
    print("database back up successful.")

def waitForDatabaseBackupToComplete():
    rds = boto.connect_rds()
    still_backing_up = True
    while still_backing_up:
        still_backing_up = False
        snapshots = rds.get_all_dbsnapshots()
        for x in snapshots:
            if x.status != "available":
                still_backing_up = True
        time.sleep(30)
    print ".. finished waiting .."

# scale up dynos, using shell
def bashScaleDynos(num_dynos):
    try:
        cmd = "cd " + TDIR + " && heroku ps:scale tw=" + str(num_dynos)
        retcode = call(cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "bashScale: Child was terminated by signal", -retcode
            raise Exception("Couldn't bash scale dynos to " + str(num))
        else:
            print >>sys.stderr, "bashScale: Child returned", retcode
    except OSError as e:
        print >>sys.stderr, "bashScale: Execution failed:", e
        raise e

# scale up the dynos appropriately. You need to get the first dyno started by above
def scaleUpDynos():
    heroku_username = SECRETS_DICT["HEROKU_USERNAME"]
    heroku_password = SECRETS_DICT["HEROKU_PASSWORD"]
    cloud = heroku.from_pass(heroku_username, heroku_password)
    apps = cloud.apps
    app = apps['twitter-politics']
    dyno = app.processes['tw']
    for i in range(1,TOTAL_THREADS):
        print "++ starting dyno: " + str(i+1)
        dyno.scale(i+1)
        time.sleep(120)
    displayScriptProgress(to_email=LAUNCH_EMAIL_RECIPIENTS)


# launch heroku
def herokuLaunch():
    # make sure dynos are scaled all the way off
    bashScaleDynos(0)
    # launch time
    launch_time = time.time()
    # count initial voter tables
    initial_voter_counts = countAllVoterTables()
    pPrintDict(initial_voter_counts)
    # backup database
    # print("backupDatabase")
    # backupDatabase()
    # move all voters to twpol
    print("returnAllVotersToMainTable")
    returnAllVotersToMainTable()
    step1_voter_counts = countAllVoterTables()
    if not step1_voter_counts["num_total_voters"] == step1_voter_counts["twpol_voter"] == initial_voter_counts["num_total_voters"]:
        raise LostVotersException("returnAllVotersToMainTable")
    # calculate should_process
    print("calculateShouldProcess")
    calculateShouldProcess()
    # migrate extraneous voters
    print("migrateExtraneousVoters")
    pre_migrate_counts = countAllVoterTables()
    migrateExtraneousVoters()
    post_migrate_counts = countAllVoterTables()
    if not pre_migrate_counts["num_total_voters"] == post_migrate_counts["num_total_voters"]:
        raise LostVotersException("migrateExtraneousVoters")
    if not post_migrate_counts["extraneous_voter"] == pre_migrate_counts["twpol_voter_should_not_process"]:
        raise LostVotersException("migrateExtraneousVoters")
    pPrintDict(post_migrate_counts)
    # reset thread counter
    resetThreadCounter()
    printThreadCounter()
    # clear longscripts
    clearFun()
    # scale first dyno via bash, then wait, then scale up the rest of the dynos using heroku api
    bashScaleDynos(1)
    time.sleep(120)
    scaleUpDynos()
    # calculate time taken to prepare launch
    end_time = time.time()
    time_elapsed = end_time - launch_time
    print("time_elapsed: " + str(int(time_elapsed)))
    print("-> heroku launched")

def mainLaunchFun():
    try:
        herokuLaunch()
    except Exception as e:
        e_type, the_exception, traceback = sys.exc_info()
        e_strings = format_exception(e_type, the_exception, traceback)
        e_message = ""
        for i,x in enumerate(e_strings):
            e_message += x + "\n"
        print e_message
        sendHerokuErrorEmail(e_message)
    else:
        sendHerokuSuccessEmail()

if __name__=="__main__":
    mainLaunchFun()


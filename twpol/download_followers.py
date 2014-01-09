# this script iterate through each voter in the database, downloads their followers
# and then looks at the political alignment of any/all of those followers
from twpol.models import *
from twpol.twitter_accounts import TWITTER_ACCOUNTS, refreshTwitterAccounts
from django.db import connections
from twpol.twitter import TwitterAuthenticationException
from django.core.exceptions import ObjectDoesNotExist
from longscript import monitor_script
import functools, math, thread, json
from multiprocessing import Process
from django.core.mail import EmailMessage

MAX_FOLLOWERS = 10000
# this version of function just straight up downloads the follower ids of all voters in the db
def downloadFollowersIDs(voter, force=False):
    try:
        voter.num_follower_attempts += 1
        # if not force=True, then check if this user has too many followers before downloading them all
        if not force:
            if voter.downloaded_followers == True:
                return
            followers_count = voter.getNumFollowers()
            if followers_count > MAX_FOLLOWERS:
                voter.over_max_followers = True
                voter.save()
                raise OverMaxFollowersException(str(voter.twitter_id))
        followers_ids = voter.getFollowers()
        stringified = ",".join(followers_ids)
        voter.followers_ids = stringified
        voter.downloaded_followers = True
        voter.save()
    except TwitterAuthenticationException as e:
        #print "error: " + str(e.message)
        voter.error_code = e.message[0:2]
        voter.save()
        raise e

# this version of function just straight up downloads the followee ids of all voters in the db
def downloadFolloweesIDs(voter, force=False):
    try:
        voter.num_followee_attempts += 1
        # if not force=True, then check if this user has too many followers before downloading them all
        if not force:
            if voter.downloaded_followees == True:
                return
        followees_ids = voter.getFollowees()
        stringified = ",".join(followees_ids)
        voter.followees_ids = stringified
        voter.downloaded_followees = True
        voter.save()
    except TwitterAuthenticationException as e:
        #print "error: " + str(e.message)
        voter.followee_error_code = e.message[0:2]
        voter.save()
        raise e

def downloadFollowersForStrayVoters(voters=None):
    if not voters: voters = Voter.objects.all()
    voters = voters.filter(downloaded_followers=False, over_max_followers=False)
    monitor_script.runScript("download_followers", items=voters, item_fun=downloadFollowersIDs, resolution=5)


def makePartitionsOfStrayVoters(num_partitions):
    total_voters_to_process = Voter.objects.count()
    # divide voters into segments marked by id
    partition_size = int(math.floor(total_voters_to_process / float(num_partitions)))
    cursor = connections['default'].cursor()
    partition_index = 0
    partition_start_id = 0
    twitter_partition_size = int(math.floor(len(TWITTER_ACCOUNTS) / float(num_partitions)))
    partitions = []
    # put an even number of voters in each partition
    for i in range(0, num_partitions):
        # if not the last partition
        if i < (num_partitions - 1):
            query = "SELECT id FROM twpol_voter where id>%s ORDER BY id LIMIT 1 OFFSET %s"
            cursor.execute(query, [partition_start_id, partition_size])
            max_partition_id = cursor.fetchone()[0]
            partition_end_id = max_partition_id
        else: # else if its the last, we want the id one greater than any voter id that exists
            query = "SELECT id FROM twpol_voter ORDER BY id DESC LIMIT 1"
            cursor.execute(query, [])
            biggest_id_of_all = cursor.fetchone()[0]
            partition_end_id = biggest_id_of_all + 1
        accounts_start_index = twitter_partition_size*i
        accounts_end_index = accounts_start_index + twitter_partition_size
        partition = {
            'accounts_start_index':accounts_start_index, # inclusive
            'accounts_end_index':accounts_end_index,     # not inclusive
            'partition_start_id':partition_start_id,     # inclusive
            'partition_end_id':partition_end_id          # inclusive
        }
        partitions.append(partition)
        # values for next go around in loop
        partition_start_id = partition_end_id+1

    return partitions

def downloadFollowersForStrayVotersFast(num_total_threads, start_index=None, end_index=None):
    print "start: " + str(start_index) + " | end: " + str(end_index)
    partitions = makePartitionsOfStrayVoters(num_total_threads)
    if not end_index:
        start_index = 0
        end_index = len(partitions)
    num_threads_on_this_machine = end_index - start_index
    # for each of the partitioned ranges of ids and ranges of twitter accounts, spawn a process to download followers in that range
    for partition in partitions[start_index:end_index]:
        accounts_start_index = partition['accounts_start_index']
        accounts_end_index = partition['accounts_end_index']
        voter_start_id = partition['partition_start_id']
        voter_end_id = partition['partition_end_id']
        recipients = ["max_fowler@brown.edu"]
        email = EmailMessage(subject='Partition Thread Email', body=json.dumps(partition), to=recipients)
        email.send()
        if num_threads_on_this_machine > 1:
            args = (accounts_start_index,
                accounts_end_index,
                voter_start_id,
                voter_end_id)
            p = Process(target=partitionedDownloadFollowersForVoters, args=args)
            p.start()
        else:
            partitionedDownloadFollowersForVoters(accounts_start_index, accounts_end_index, voter_start_id, voter_end_id)

def partitionedDownloadFollowersForVoters(accounts_start_index, accounts_end_index, voter_start_id, voter_end_id):
    """
    :param accounts_start_index: first twitter account to use
    :param accounts_end_index: last twitter account to use
    :param voter_start_id: id of voter marks edge of partition
    """
    refreshTwitterAccounts(accounts_start_index, accounts_end_index)
    # print "# twitter accounts: " + str(len(TWITTER_ACCOUNTS))
    total_stray_voters = Voter.objects.filter(id__gte=voter_start_id, id__lte=voter_end_id, downloaded_followers=False, over_max_followers=False).count()
    window_size = 1000
    num_windows = int(math.ceil(total_stray_voters / float(window_size)))
    for c_window in range(0,num_windows):
        start_index = (c_window * window_size)
        query = "SELECT id, twitter_id, twitter_screen_name,num_followee_attempts FROM twpol_voter where id>=%s AND id<=%s ORDER BY id LIMIT %s OFFSET %s"
        voters = list(Voter.objects.raw(query, [voter_start_id, voter_end_id, window_size, start_index]))
        title = "downloadFolloees " + str(voter_start_id) + "|" + str(voter_end_id) + " (" + str(c_window) + "/" + str(num_windows)+ ")"
        monitor_script.runScript(name=title, items=voters, item_fun=downloadFolloweesIDs, resolution=5)
    email_body = {"voter_start_id":voter_start_id, "voter_end_id":voter_end_id}
    email = EmailMessage(subject='Heroku Worker Finished!', body=json.dumps(email_body), to=["max_fowler@brown.edu"])
    email.send()

def resetThreadCounts(total_threads=16):
    try:
        num_total_threads = DataPoint.objects.get(name="total_threads")
        num_total_threads.value = total_threads
        num_total_threads.save()
    except ObjectDoesNotExist:
        num_total_threads = DataPoint(name="total_threads", value=total_threads)
        num_total_threads.save()
    try:
        num_running_threads = DataPoint.objects.get(name="running_threads")
        num_running_threads.value = 0
        num_running_threads.save()
    except ObjectDoesNotExist:
        num_running_threads = DataPoint(name="running_threads", value=0)
        num_running_threads.save()

def mainDownloadFun():
    num_total_threads = DataPoint.objects.get(name="total_threads").value
    num_running_thread_object = DataPoint.objects.get(name="running_threads")
    num_threads_on_this_machine = 1
    num_running_threads_before = num_running_thread_object.value
    num_running_threads_after = num_running_thread_object.value + num_threads_on_this_machine
    num_running_thread_object.value = num_running_threads_after
    num_running_thread_object.save()
    downloadFollowersForStrayVotersFast(num_total_threads, num_running_threads_before, num_running_threads_after)

# main script
if __name__=="__main__":
    mainDownloadFun()


# exceptions
class OverMaxFollowersException(Exception):
    pass
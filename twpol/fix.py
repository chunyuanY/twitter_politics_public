from twpol.models import *
from django.core.exceptions import ObjectDoesNotExist
from MySQLdb import cursors

import csv, datetime
from twpol.common import *


def findDuplicatesFun():

    duplicates_file_path = "data/duplicates.csv"
    duplicates_file = open(duplicates_file_path, "w+")
    dup_writer = csv.writer(duplicates_file)
    db_handle = getDBHandle()

    cursor = db_handle.cursor(cursorclass=cursors.DictCursor)
    count_query =   "SELECT count(*)" \
                    "FROM twpol_voter"
    cursor.execute(count_query)
    total_voters = cursor.fetchone()['count(*)']
    select_ids_query = "SELECT id, twitter_id" \
            " FROM twpol_voter" \
            " WHERE id>%s" \
            " ORDER BY id" \
            " LIMIT 1000"
    results = 0
    offset_id  = 0
    duplicates_found = 0
    start_time = datetime.datetime.now()
    while results < total_voters:
        voters_chunk = Voter.objects.raw(select_ids_query, [offset_id])
        for voter in voters_chunk:
            results += 1
            duplicates_query = "SELECT id" \
            " FROM twpol_voter" \
            " WHERE twitter_id=%s"
            duplicates = list(Voter.objects.raw(duplicates_query, [voter.twitter_id]))
            if len(duplicates) > 1:
                duplicates_found += 1
                to_write = [x.id for x in duplicates]
                dup_writer.writerow(to_write)
            offset_id = voter.id
            printQueries()
            if not results % 100:
                printETA(start_time,count=results, total=total_voters)

    duplicates_file.flush()
    duplicates_file.close()

    print "duplicates found: " + str(duplicates_found)


def deleteDuplicatesFun():

    # db handle
    db_handle = getDBHandle()
    cursor = db_handle.cursor(cursorclass=cursors.DictCursor)

    # read lines of duplicates from csv
    duplicates_file_path = "data/duplicates.csv"
    duplicates_file = open(duplicates_file_path, "r")

    lines = 0
    f = open(duplicates_file_path, "r")
    for line in f:
        lines += 1
    f.close()

    # create set of keeper id
    keeper_ids = set([])
    duplicate_ids = set([])

    # keep first duplicate from every line (keeper)
    for row in csv.reader(duplicates_file):
        for x in row[1:]:
            if x in keeper_ids:
                continue
        keeper_ids.add(row[0])
        duplicate_ids.update(row[1:])

    assert len(keeper_ids.intersection(duplicate_ids)) == 0

    print "keepers: " + str(len(keeper_ids))
    print "duplicates: " + str(len(duplicate_ids))
    added = 0
    duplicates_file = open(duplicates_file_path, "r")
    count = 0
    # for each politician every duplicate is following, make keeper follow that politician
    for row in csv.reader(duplicates_file):
        keeper_id = row[0]
        if keeper_id in keeper_ids:
            voter = Voter.objects.get(id=keeper_id)
            for duplicate_id in row[1:]:
                duplicate = Voter.objects.get(id=duplicate_id)
                for politician in duplicate.supports.all():
                    if not politician in voter.supports.all():
                        added += 1
                        print "add"
                        voter.supports.add(politician)
        printQueries()
        count += 1
        if not count % 50:
            print count

    for i,duplicate_id in enumerate(duplicate_ids):
        try:
            duplicate = Voter.objects.get(id=duplicate_id)
            duplicate.delete()
        except ObjectDoesNotExist:
            pass
        if not i % 10:
            print i

    print "added supported: " + str(added)



def fixFun():
    findDuplicatesFun()

if __name__=="__main__":
    fixFun()
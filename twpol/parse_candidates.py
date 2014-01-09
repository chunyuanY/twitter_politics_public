# this file is meant to migrate old data into the new schema

# candidate spread sheet
# full name | url | candidate_id | twitter_screen_name
# candidate_id
# nine digit id:
# type (1=house candidate, 2=senate candidate, 3=senator not up for re-election, 4=house lameduck, 5=senate lameduck, 6=presidential candidate, 7=media market)
# ICPSR state code (99 for President and media markets),
# two-digit district (0 for at-large, 99 for Senate, President, and media market)
# party (1=democrat, 2=republican, 3=other, 9 for media markets),
# two-digit candidate [alphabetic by first name for types 1, 2, and 6, 1 for types 3,4, and 5, sequential for media outlets]
# one-digit account number (1, 2, 3, etc)

from xlrd import open_workbook
from twpol.settings import PROJECT_PATH
from twpol.models import *
from twpol.common import *
from longscript import monitor_script
import os
import functools

def getPartyLetterFromPartyNumber(party_num):
    if party_num == 1:
        return 'D'
    elif party_num == 2:
        return 'R'
    else:
        return 'O'

def parseCandidatesFromSpreadSheet(spreadsheet):
    wb = open_workbook(spreadsheet)
    sheet = wb.sheet_by_index(0)
    items = range(1,sheet.nrows)
    item_fun = functools.partial(parseCandidateFromSpreadSheet, sheet=sheet)
    monitor_script.runScript(name="parseCandidates", items=items, item_fun=item_fun, resolution=5)

def parseCandidateFromSpreadSheet(row, sheet):
    # parse all values from spreadsheet
    name = sheet.cell(row,3).value
    candidate_id = str(sheet.cell(row,21).value)[:9]
    twitter_url = sheet.cell(row, 6).value
    twitter_screen_name = twitter_url.replace("https://twitter.com/","")
    candidate_type = int(candidate_id[0])           # 1=house_candidate, 2=senate candidate
    state_code = int(candidate_id[1:3])
    district_number = int(candidate_id[3:5])
    party_num = int(candidate_id[5])
    candidate_number = int(candidate_id[6:8])
    account_number = int(candidate_id[8])
    # check if candidate with same candidate_id already exists
    already_exists = Candidate.objects.filter(twitter_screen_name=twitter_screen_name)
    if already_exists:
        print enc("+EE+: " + twitter_screen_name)
    else:
        print enc("+II+: " + twitter_screen_name)
        candidate = Candidate(
            candidate_id=candidate_id,
            name=name,
            twitter_url=twitter_url,
            twitter_screen_name=twitter_screen_name,
            candidate_type=candidate_type,
            party_num=party_num,
            party=getPartyLetterFromPartyNumber(party_num),
            candidate_number=candidate_number,
            account_number=account_number
        )
        candidate.save()
        candidate.addDistrictByNumbers(district_number, state_code)
        if not candidate.updateTwitterID():
            raise TwitterScreenNameDoesNotExistException(twitter_screen_name)

# main script parses all candidates from spreadsheet
if __name__=="__main__":
    candidates_xls = os.path.join(PROJECT_PATH, 'data/candidates.xls')
    parseCandidatesFromSpreadSheet(candidates_xls)

# exceptions

class TwitterScreenNameDoesNotExistException(Exception):
    # when the twitter screen name of a candidate does not exist on twitter anymore
    pass
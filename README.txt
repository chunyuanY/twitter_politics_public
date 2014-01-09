Analyzing political views and ideological segregation on twitter.
================

OVERVIEW OF METHODOLOGY

For all 'candidates' running in the 2012 election we manually researched their twitter accounts.
We call a 'voter' any twitter account which is following any one of these candidate twitter accounts.

Over the past 6 months, I build a system to download all the followers and followees of the voters.

The goal is to use this data to look at who is following who, are liberals following liberals vs republicans following
republicans etc.

Starting from the beginning though, below is a section of describing where the database of Voters came from,
which was before my time.


DATABASE OF VOTERS

I was given a database of which twitter users were following twitter accounts of political candidates as of
November 5th, 2012.

This database can be found on the toronto server at ip address: 128.100.177.31

This data came from an RA before me, and I am not sure exactly how it was acquired, although there is a lot of code
in the /home/ directory, in particular I think the followers of political candidates were downloaded using code in
/home/namsoman/Somang/

In particular, the table I used was followers_nov5 in the database tw_politic

+-------------+----------+------+-----+---------+-------+
| Field       | Type     | Null | Key | Default | Extra |
+-------------+----------+------+-----+---------+-------+
| id          | int(11)  | YES  |     | NULL    |       |
| candidateid | char(40) | YES  |     | NULL    |       |
| userid      | char(40) | YES  |     | NULL    |       |
| id_str      | char(40) | YES  |     | NULL    |       |
| followersid | char(40) | YES  |     | NULL    |       |
| date        | date     | YES  |     | NULL    |       |
+-------------+----------+------+-----+---------+-------+

This table has 8,326,793 rows, one for each of the users following a particular candidate.

From a conversation I had with the original RA about what the meaning of the columns in this table
are I concluded:

'candidateid' is a special id for candidates whose meaning is described in the file twpol/data/candidate_id_explained.txt
'id_str' is the twitter id of the candidate
'userid' is the screen name of the candidate
'followersid' is the twitter id of the follower
'date' is the date the following relationship was downloaded

You can see the transcript of the conversation I had with the former RA in the file 'former_ra_conversation_transcript.txt'


WHY DOWNLOADING ALL FOLLOWERS OF VOTERS ENDED UP BEING REALLY COMPLICATED

To download the ids of the twitter accounts of who is following a particular voter, you need to use twitter's API.

https://dev.twitter.com/docs/rate-limiting/1.1

Unfortunately, twitter's API has a rate limit, such that you can only make 15 calls to the API to download followers
per 15 minutes. Additionally each call will only return 20 ids at a time, so for users with many followers it can
take many calls to get them all.

Thusly, working within the constraints of the rate limit, it would take many years to download all of the followers
of all 8 million voters.

So, this entire code base is pretty much a system to avoid twitter's rate limit. It works!


AVOIDING RATE LIMITING

twpol/twitter_credentials.json

Is a json which is a list of dictionaries. Each element of the list looks like:
{"consumer_secret": "02NdFzcuqDeauSmBbCUNTKBTN0Nb0hpNA4tBqfvt7E",
"my_secret": "FghDwTkWMmHtb2H56SrTpFXLjYfRaCRpm6bxXpqNh8",
"my_key": "1461327583-PZLqeByUNONj17TfL0tbegR6Bnkc51RskBS5Yzh",
"consumer_key": "8KUqX5jvpDIjqp1B1nzag"}

These 4 strings are what you need to authenticate as a user with the twitter API.

The twitter API is rate limited per user, so by switching between different authentication credentials you can avoid
the rate limit.

There are 632 accounts  in the json, so we can get 632 times the speed.

By this point, the bottleneck in download speeds was no longer the rate limit, it became simply the internet connection
speed. So I parallelized it, and divided the voters into chunks, having different machines process different
chunks simultaneously.

twpol/heroku_launch.py has a method herokuLaunch() which launches an arbitrary number of heroku machines to do
the downloading.



TOOLS

I used Django ORM as an abstraction layer with the database. This database is called twpol, and almost all
interaction with it goes through the models.py

Everything within the folder longscript, is a tool I built to help monitor the progress of a script as it runs.

I used a ton of weird stuff to write a script to automate creating twitter accounts, hopefully you don't need
to create any more accounts, as twitter_credentials.json has all hte data you need. So you can ignore the files
create_twitter_account.py
proxies.txt
shit_proxies.txt
ninja.txt

IMPORTANT FILES

download_followers.py ... is all about downloading followers
export_to_stata.py ... is about exporting data from database into a csv so it is readable by stata
heroku_launch.py ... is about initializing parallelized download process
migrate_voters.py ... is about migrating voters from tw_politic to tw_pol
models.py ... is db schema, object oriented design
monitor_email.py ... you can ignore, I was thinking of setting up an automated error detection system using email
monitor_processes.py ... was a short workaround, for when export_to_stata.py was crashing and processes needed to be restarted
onetimer_supported_when.py ... not sure, you can probably ignore it
parse_candidates.py ... takes in a manually researched .xls file and puts data into database
parse_log.py ... is trash, it was never used (sorry for clutter)
print_num_followers.py ... is likewise, irrelevant
selenium_download.py ... is an alternate method for downloading followers, based on browser automation instead of rest API
settings.py ... is django settings file
stats.py ... irrelevant
test.py ... is my entry point for running methods via my IDE
twitter.py ... all interaction with the twitter rest API goes through this file
twitter_accounts.py ... transforms twitter_credentials.json into python objects usable by the rest of the code base

heroku_startpoint.py ... is the file that gets called when a heroku instance initializes

LONGSCRIPT

I was hoping to polish and open source this tool. I never quite got around to it, and the version of longscript in this
project is slightly divergent from the one on github I was going to opensource (but only barely). On github is the
best documentation on longscript available.. I think it's really cool.
https://github.com/maximusfowler/python-longscripts



UNFORTUNATELY

I tried downloading the followees of all voters, and it looks like the twitter authentication tokens must have expired,
because it is throwing a lot errors. So you may have to create new twitter accounts to make the whole thing work,
create_twitter_account.py could probably get the job done.


THAT'S IT

If you have any questions, my email is max_fowler at brown dot edu

Goodluck!









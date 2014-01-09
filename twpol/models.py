from django.db import models
from twpol import twitter

# store districts as db objects
class District(models.Model):
    district_number = models.IntegerField()
    state_code = models.IntegerField()

# abstract data for twitter user
class TwitterUser(models.Model):
    twitter_name = models.CharField(max_length=100, null=True)
    twitter_id = models.CharField(max_length=50, null=True, db_index=True, unique=True)
    twitter_screen_name = models.CharField(max_length=100, null=True)
    num_followers = models.IntegerField(default=0)
    district = models.ForeignKey(District, null=True, related_name="%(class)s_primarily_lives_in")   # null if multiple
    party = models.CharField(max_length=1, null=True)   # D, R, B (both), O (other)
    party_num = models.IntegerField(null=True)
    # takes in a district number and state code and updates model appropriately
    def addDistrictByNumbers(self, district_number, state_code):
        district = District.objects.filter(district_number=district_number, state_code=state_code)
        if not district:
            district = District(district_number=district_number, state_code=state_code)
            district.save()
        else:
            district = district[0]
        self.district = district
        self.save()
    # interact with twitter rest api
    def getFollowers(self):
        return twitter.getFollowersIDSFromID(self.twitter_id)
    def getNumFollowers(self):
        user_info = self.getUserInfo()
        followers_count = user_info.get("followers_count")
        if followers_count:
            return followers_count
        else:
            return 0
    def getFollowees(self):
        return twitter.getFolloweesIDSFromID(self.twitter_id)
    def isFollowing(self, twitter_id):
        return twitter.isAFollowingB(self.twitter_id, twitter_id)
    def getUserInfo(self):
        return twitter.getUserInfoFromID(self.twitter_id, self.twitter_screen_name)
    def getNameFromTwitter(self):
        user_info = self.getUserInfo()
        name = user_info.get('name')
        return name
    def updateTwitterID(self):
        user_info = self.getUserInfo()
        twitter_id = user_info.get('id')
        if not twitter_id:
            print "+WW+: no twitter id for " + str(self.twitter_screen_name)
            print user_info
            return False
        self.twitter_id = twitter_id
        self.save()
        return True
    # getters
    def getParty(self):
        return self.party
    def getDistrictNumber(self):
        if self.district:
            return self.district.district_number
        else:
            return None
    def getStateCode(self):
        if self.district:
            return self.district.state_code
        else:
            return None
    # setters
    def setParty(self, party):
        self.party = party
        self.save()
    # abstract class
    class Meta:
        abstract = True

# model for elected official
class Candidate(TwitterUser):
    name = models.CharField(max_length=100, null=True)
    twitter_url = models.CharField(max_length=100, null=True)
    candidate_type = models.IntegerField(null=True)
    candidate_number = models.IntegerField(null=True)
    account_number = models.IntegerField(null=True)
    candidate_id = models.CharField(max_length=9, null=True)
    migrated_followers = models.BooleanField(default=False)
    # helpers
    def getTwitterIDFromTwitterURL(self, twitter_url):
        return twitter_url

# model for voter
class Voter(TwitterUser):
    supports = models.ManyToManyField(Candidate)
    followers = models.ManyToManyField("self")
    followers_ids = models.TextField(blank=True)                  # comma separated list of ids of twitter_ids of all of the voters followers
    pruned_followers_ids = models.TextField(blank=True)           # comma separated list of twitter_ids of all the voters followers who are also voters
    followees = models.ManyToManyField("self")
    followees_ids = models.TextField(blank=True)                    # comma separated list of twitters_ids of all of the users voter is following
    pruned_followees_ids = models.TextField(blank=True)             # comma separated list of twitters_ids of all of the users voter is following who are also voters
    invalid = models.BooleanField(default=False)
    # flags indicating status of db object
    pruned = models.BooleanField(default=False)     # true if pruned_followers_ids is correct
    over_max_followers = models.BooleanField(default=False) # if voter has over 10000 followers, then don't download followers
    num_follower_attempts = models.IntegerField(default=0)    # number of attempts which have been made to download this voter's followers
    num_followee_attempts = models.IntegerField(default=0)    # number of attempts which have been made to download this voter's followees
    downloaded_followers = models.BooleanField(default=False)
    downloaded_followees = models.BooleanField(default=False)
    should_process = models.BooleanField(default=False)
    error_code = models.CharField(max_length=3, default="")
    followee_error_code = models.CharField(max_length=3, default="")
    def setInvalid(self, bool):
        self.invalid = bool
    def addFollower(self, follower):
        self.followers.add(follower)
    def getPrunedFollowersIDS(self):
        if not self.pruned_followers_ids:
            return []
        else:
            return self.pruned_followers_ids.split(",")
    def getFollowersIDS(self):
        if not self.followers_ids:
            return []
        else:
            return self.followers_ids.split(",")
    def getPrunedFolloweesIDS(self):
        if not self.pruned_followees_ids:
            return []
        else:
            return self.pruned_followees_ids.split(",")
    def getFolloweesIDS(self):
        if not self.followees_ids:
            return []
        else:
            return self.followees_ids.split(",")

# model for support relationship between voter and candidate
class Support(models.Model):
    candidate = models.ForeignKey(Candidate)
    voter = models.ForeignKey(Voter)
    when = models.DateField()


class DataPoint(models.Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField()


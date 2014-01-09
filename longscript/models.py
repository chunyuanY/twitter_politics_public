from django.db import models
import simplejson
from datetime import datetime

class ScriptException(models.Model):
    exception_type = models.CharField(max_length=50)
    message = models.TextField()
    when = models.DateTimeField(auto_now_add=True)
    item_id = models.IntegerField(null=True)

class Script(models.Model):
    name = models.CharField(blank=True, max_length=50)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    running = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    # script progress
    num_total_items = models.IntegerField(default=0)
    num_processed_items = models.IntegerField(default=0)
    num_exceptions = models.IntegerField(default=0)
    num_successes = models.IntegerField(default=0)
    exceptions = models.ManyToManyField(ScriptException)
    bonus_data = models.TextField()                         # json encoded dictionary
    time_distribution = models.TextField()                  # json encoded dictionary

    def setBonusData(self, vals):
        self.bonus_data = simplejson.dumps(vals)
        self.save()
    def getBonusData(self):
        return simplejson.loads(self.bonus_data)

    def setTimeDistribution(self, vals):
        self.time_distribution = simplejson.dumps(vals)
        self.save()
    def getTimeDistribution(self):
        return simplejson.loads(self.time_distribution)

    def getUniqueID(self):
        return self.id
    def getName(self):
        return self.name
    def getStartTime(self):
        return self.start
    def getEndTime(self):
        return self.end
    def getNumProcessedItems(self):
        return self.num_processed_items
    def getNumExceptions(self):
        return self.num_exceptions
    def getNumTotalItems(self):
        return self.num_total_items
    def getSecondsPassed(self):
        if not self.finished:
            now = datetime.now()
            time_passed = now - self.getStartTime()
        else:
            time_passed = self.getEndTime() - self.getStartTime()
        return time_passed.total_seconds()
    def getSecondsRemaining(self):
        if self.finished:
            return 0
        total_items = float(self.getNumTotalItems())
        if not total_items:
            return 0
        else:
            percentage_complete = self.getNumProcessedItems() / float(self.getNumTotalItems())
            if percentage_complete:
                time_remaining = self.getSecondsPassed() / percentage_complete - self.getSecondsPassed()
            else:
                time_remaining = -1
            return time_remaining

    def startRunning(self):
        self.running = True
        self.start = datetime.now()
        self.save()
    def setFinished(self):
        self.running = False
        self.end = datetime.now()
        self.finished = True
        self.save()

    def getExceptionNumsDictionary(self):
        exception_types = {}
        for x in self.exceptions.all():
            e_type = x.exception_type
            if not e_type in exception_types:
                exception_types[e_type] = 0
            exception_types[e_type] += 1
        return exception_types

# single model for storing how much time a script has slept
class ScriptSleep(models.Model):
    seconds_slept = models.IntegerField(default=0)

def getScriptSleepObject():
    s = ScriptSleep.objects.all()
    if s:
        return s[0]
    else:
        s = ScriptSleep()
        s.save()
    return s

def saveSleep(seconds):
    s = getScriptSleepObject()
    s.seconds_slept += seconds
    s.save()

def getTotalMinutesSlept():
    return getScriptSleepObject().seconds_slept / 60.0

def resetSleepCounter():
    s = getScriptSleepObject()
    s.seconds_slept = 0
    s.save()

def clearSavedScripts():
    for x in Script.objects.all():
        x.delete()

def clearSavedExceptions():
    for x in ScriptException.objects.all():
        x.delete()

def clearSavedSpecialErrors():
    for x in ScriptSpecialError.objects.all():
        x.delete()

# single model for storing how many times a script gets a special error
class ScriptSpecialError(models.Model):
    which_error = models.CharField(max_length=50)
    num_errors = models.IntegerField(default=0)

def saveSpecialError(which_error):
    already = ScriptSpecialError.objects.filter(which_error=which_error)
    if already:
        error = already[0]
    else:
        error = ScriptSpecialError(which_error=which_error)
        error.save()
    error.num_errors += 1
    error.save()

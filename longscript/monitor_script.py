# log exceptions and time distribution of script
from longscript.models import *
from django.core.mail import EmailMessage
from traceback import format_exception
import sys

EMAIL_ALERT_RECIPIENTS = ['max_fowler@brown.edu','yosh.halberstam@utoronto.ca','brian_knight@brown.edu']

def runScript(name, items, item_fun, resolution=100):
    script = Script(name=name, num_total_items=len(items))
    script.save()
    print "script_id (" + name + "): " + str(script.getUniqueID())
    script.startRunning()
    found_exceptions = []
    for count,item in enumerate(items):
        try:
            item_fun(item)
            script.num_successes += 1
        except:
            e_type, the_exception, traceback = sys.exc_info()
            e_strings = format_exception(e_type, the_exception, traceback)
            e_message = ""
            for i,x in enumerate(e_strings):
                e_message += x + "\n"
            script_exception = ScriptException(exception_type=((str(e_type))[:49]), message=e_message, item_id=count)
            found_exceptions.append(script_exception)
            script.num_exceptions += 1
        finally:
            script.num_processed_items += 1
        if not count % resolution:
            script.save()
            for x in found_exceptions:
                x.save()
                script.exceptions.add(x)
            found_exceptions = []
    script.setFinished()


def probeScript(script_id):
    script = Script.objects.get(id=script_id)
    msg = ""
    msg += "name: " + script.getName() + "\n"
    msg += "running: " + str(script.running) + "\n"
    msg += "started: " + script.getStartTime().strftime("%m/%d %H:%M") + "\n"
    msg += "num processed: " + str(script.getNumProcessedItems()) + "\n"
    msg += "total exceptions: " + str(script.getNumExceptions()) + "\n"
    msg += "total items: " + str(script.getNumTotalItems()) + "\n"
    msg += "time passed: " + minutesToReadable(script.getSecondsPassed() / 60.0) + "\n"
    msg += "time remaining: " + minutesToReadable((script.getSecondsRemaining() / 60.0)) + "\n"
    msg += "------ exceptions ----" + "\n"
    for k,v in script.getExceptionNumsDictionary().items():
        msg += k + ": " + str(v) + "\n"
    msg += "----------" + "\n"
    return msg


# automatically probe all running scripts and send me an email with the results
def displayScriptProgress(email_alert=True, special_errors=True, to_email=None):
    message = ''
    scripts = list(Script.objects.filter(running=True).order_by("start"))
    finished_scripts = list(Script.objects.filter(running=False).order_by("name"))
    scripts.extend(finished_scripts)
    #scripts = list(Script.objects.all().order_by("name"))
    for script in scripts:
        message += probeScript(script.getUniqueID())
    # special errors footer
    if special_errors:
        message += "-------- special errors ------ \n"
        message += "minutes slept: " + str(getTotalMinutesSlept()) + "\n"
        for special_error in ScriptSpecialError.objects.all().order_by("which_error"):
            message += str(special_error.which_error) + ": " + str(special_error.num_errors) + "\n"
        message += "-------------\n"
    if email_alert:
        recipients = to_email or EMAIL_ALERT_RECIPIENTS
        email = EmailMessage(subject='Script Update', body=message, to=recipients)
        email.send()
    else:
        print message

def clearScripts():
    scripts = Script.objects.all()
    scripts.delete()

def minutesToReadable(minutes):
    minutes = int(minutes)
    hours = minutes / 60
    minutes = minutes - 60*hours
    days = hours / 24
    hours = hours - 24*days
    to_return = ""
    if days:
        to_return += str(days) + " days and "
    if hours:
        to_return += str(hours) + " hours and "
    to_return += str(int(minutes)) + " minutes"
    return to_return

# main script print probe for
if __name__=="__main__":
    args = sys.argv
    script_id = args[1]
    probeScript(script_id=script_id)
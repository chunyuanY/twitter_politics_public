from gmail import Gmail
from twpol.settings import SECRETS_DICT
from twpol.heroku_launch import mainLaunchFun
from twpol.settings import PROJECT_PATH
import os, sys, json
from twpol.common import *
from traceback import format_exception

SAFETY_SWITCH_PATH = os.path.join(PROJECT_PATH, "monitor_email_safety_switch.txt")

# https://github.com/charlierguo/gmail
class EmailMonitor():
    def __init__(self):
        pass

    #  monitor email monitoring
    def sendMonitorErrorEmail(self, error):
        error_message = "Error: " + error
        sendErrorEmail(subject='XXXX Monitor Email Error XXXX', body=error_message)
        safety_switch_dict = {"safety_switch_off":0}
        self.setSafetySwitch(json.dumps(safety_switch_dict))
        print "safety switch turned on."

    def sendMonitorSuccessEmail(self, success_message):
        sendSuccessEmail(subject="**** Monitor Email ****", body=success_message)

    # set value of safety switch file
    def setSafetySwitch(self, vals_json):
        safety_switch_file_path = SAFETY_SWITCH_PATH
        write_safety_switch_file = open(safety_switch_file_path, 'w+')
        write_safety_switch_file.write(vals_json)
        write_safety_switch_file.close()

    # returns true if safey_switch_off == 1, returns False otherwise
    def isSafetySwitchOff(self):
        f = open(SAFETY_SWITCH_PATH, 'r')
        safety_switch_json = f.read()
        safety_switch_dict = json.loads(safety_switch_json)
        f.close()
        safety_switch_off = safety_switch_dict.get("safety_switch_off")
        return safety_switch_off == 1

    def handleEmail(self, message):
        subject = message.subject
        print "SUBJECT: " + str(subject)
        if subject == "[TEST_MONITOR_SYSTEM]":
            self.sendMonitorSuccessEmail("monitor system is working.")
            message.add_label("Monitor Email Job Success")
            message.read()
        elif subject == "[FEEDBACK]" + "[HEROKU_CRASH]":
            mainLaunchFun()
            self.sendMonitorSuccessEmail("mainLaunchFun")
            message.add_label("Monitor Email Job Success")
            message.read()

    def monitorEmail(self):
        if not self.isSafetySwitchOff():
            self.sendMonitorErrorEmail("Monitor Email still broken: safety switch turned on")
            return

        g = Gmail()
        g.login(SECRETS_DICT['EMAIL_USERNAME'], SECRETS_DICT['EMAIL_PASSWORD'])
        # play with your gmail...
        messages = g.inbox().mail(unread=True, sender="maximusfowler@gmail.com")
        for x in messages:
            x.fetch()
            try:
                self.handleEmail(x)
            except Exception as e:
                x.add_label("Monitor Email Job Error")

        g.logout()

def mainMonitorEmailFun():
    email_monitor = EmailMonitor()
    email_monitor.sendMonitorSuccessEmail("Checking for new emails to respond to.")
    try:
        email_monitor.monitorEmail()
    except:
        e_type, the_exception, traceback = sys.exc_info()
        e_strings = format_exception(e_type, the_exception, traceback)
        e_message = ""
        for i,x in enumerate(e_strings):
            e_message += x + "\n"
        e_message = "[Handle email error]\n" + str(e_message)
        email_monitor.sendMonitorErrorEmail(e_message)

if __name__=="__main__":
    mainMonitorEmailFun()



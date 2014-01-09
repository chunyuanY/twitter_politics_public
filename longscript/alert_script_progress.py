# run this file to send email alert with the progress of all currently running scripts

from longscript.monitor_script import *
import datetime, sys

if __name__=="__main__":
    if len(sys.argv) > 1:
        to_email = sys.argv[1:]
    else:
        to_email = None
    print str(datetime.datetime.now())
    print "to_email: " + str(to_email)
    displayScriptProgress(to_email=to_email)
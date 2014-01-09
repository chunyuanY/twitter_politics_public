import subprocess
from twpol.export_to_stata import mainExportFun
from twpol.common import sendSuccessEmail
from twpol.settings import PROJECT_PATH
import os
from twpol.monitor_email import EmailMonitor

def findPythonProcesses():
    ps= subprocess.Popen("ps -ef | grep python", shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    processes = output.split("\n")
    return len(processes)

def startPythonProcess():
    script_path = os.path.join(PROJECT_PATH, "export_to_stata.py")
    log_path = os.path.join(PROJECT_PATH, "calculate_out.txt")
    subprocess.call('nohup python ' + script_path + " > " + log_path + " &", shell=True)

def monitorProcessesFun():
    email_monitor = EmailMonitor()
    if email_monitor.isSafetySwitchOff():
        num_python_processes = findPythonProcesses()
        print "num processes: " + str(num_python_processes)
        if num_python_processes < 5:
            startPythonProcess()
            sendSuccessEmail(subject="[Script Restarted]", body="hmm...")

if __name__=="__main__":
    monitorProcessesFun()



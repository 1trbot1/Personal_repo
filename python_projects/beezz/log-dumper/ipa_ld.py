#!/usr/bin/python3
from __main__ import errors, timestampStr, header, bcolors, ssh_exec
import os
import sys
#Prevent cache file creation from python
sys.dont_write_bytecode = True
##########################################################################
#Main
def ipa_status(host, user, **args):
    ##########################################################################
    #Connection errors
    miss_auth_error = None
    unable_auth_error = None
    ##########################################################################
    #Error logger
    title = module = "[FreeIPA]"
    ##########################################################################
    #SSH Connect
    if "password" in args:
        ssh = ssh_exec(host, user, password = args["password"])
    else:
        ssh = ssh_exec(host, user, p_key_file = args["p_key_file"])
    ##########################################################################
    #Main
    log_dir = args["out_dir"] + "/ipa"
    status = None
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    #--------------------------------------------------
    # Create Log file and open it
    filename = '%s/%s-%s-%s.%s' % (log_dir, host,  timestampStr ,"ipa_ctl", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '%s/%s-%s-%s_%d.%s' % (log_dir, host, timestampStr, "ipa_ctl", filename_dup ,"log")
        filename_dup += 1
    with open(filename, "a") as outfile:
        outfile.writelines(header("=", title)+"\n")
        #--------------------------------------------------
        command = "ipactl status"
        stdin, stdout, stderr = ssh.exec_command(command)
        if "%s: command not found" % (command.split(" ")[0]) in stderr.readline():
            error = "{}: command not found.".format(command)
            errors.append({"host" : host, "module": module,  "error" : error, "time" : timestampStr})
            return 0
        #--------------------------------------------------
        for l in stdout:
            outfile.writelines(l)
            if "STOPPED" in l:
                if "ntpd" in l:
                    pass
                else:
                    errors.append({"host" : host, "module": module,  "error" : l, "time" : timestampStr})
    ssh.close()
#!/usr/bin/python3
from __main__ import errors, timestampStr, header, bcolors, ssh_exec
import os
import sys
#Prevent cache file creation from python
sys.dont_write_bytecode = True
##########################################################################
#Main
def sys_info(host, user, commands, **args):
    module = "[System]"
    ##########################################################################
    #SSH Connect
    if "password" in args:
        ssh = ssh_exec(host, user, password = args["password"])
    else:
        ssh = ssh_exec(host, user, p_key_file = args["p_key_file"])
    ##########################################################################
    #Main
    log_dir = args["out_dir"] + "/system/info"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # Create Log file and open it
    filename = '%s/%s-%s-%s.%s' % (log_dir, host,  timestampStr ,"system-info", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '%s/%s-%s-%s_%d.%s' % (log_dir, host, timestampStr, "system-info", filename_dup ,"log")
        filename_dup += 1
    outfile = open(filename, "a")
    for command in commands:
        outfile.writelines(header("=", command.upper().split(" ")[0]) + "\n")
        # print(header("=", command.upper().split(" ")[0], bcolors.HEADER) + "\n")
        stdin, stdout, stderr = ssh.exec_command(command)
        if "%s: command not found" % (command.split(" ")[0]) in stderr.readline():
            outfile.writelines("[ Warning ] %s: command not found\n" % (command.split(" ")[0]))
            error = "{}: command not found.".format(command)
            continue
        for i in stdout:
            outfile.writelines(i)
            if "uptime" in command:
                if "day" not in i:
                    error = "Up time less then 1 day."
                    errors.append({"host" : host, "module": module, "error" : error, "time" : timestampStr})
                if "NTP synchronized: no" in i:
                    error = "Time not synchronized with NTP server."
                    errors.append({"host" : host, "module": module, "error" : error, "time" : timestampStr})
    outfile.close()
    ssh.close()
    ##########################################################################
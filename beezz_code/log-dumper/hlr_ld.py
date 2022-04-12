#!/usr/bin/python3
from __main__ import errors, timestampStr, header, bcolors, ssh_exec
import os
import sys
import time
#Prevent cache file creation from python
sys.dont_write_bytecode = True
##########################################################################
#Error logger
module = "[ HLR ]"
##########################################################################
#HLR Logs
def hlr_get_logs(host, user, **args):
    title = "[HLR %s]" % (host) 
    ##########################################################################
    #SSH Connection
    if "password" in args:
        ssh = ssh_exec(host, user, password = args["password"])
    if "p_key_file" in args:
        ssh = ssh_exec(host, user, p_key_file = args["p_key_file"])
    sftp = ssh.open_sftp()
    ##########################################################################
    #Main
    #--------------------------------------------------
    # Create Log file and open it
    log_dir = args["out_dir"] + "/hlr/%s/logs" % (host)
    status = None
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    remotepath = '/home/beezz/logs'
    log_files = []
    for f in sftp.listdir(remotepath):
        log_files.append(f)
    #--------------------------------------------------
    # Downloading progress 
    progress = 0
    #--------------------------------------------------
    for f in log_files:
        sftp.get(remotepath + "/" + f, log_dir + "/" + f)
        # Update progress
        progress+=1
        done = str(int((float(progress)/len(log_files))*100))
        sys.stdout.write("[ HLR ]: Donwloading logs...  %s%%      %s"%(done,"\r"))
        sys.stdout.flush()
    #--------------------------------------------------
    time.sleep(2)
    sftp.close()
    ssh.close()
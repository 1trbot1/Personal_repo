#!/usr/bin/python3
from __main__ import errors, timestampStr, header, bcolors, ssh_exec
import os
import sys
#Prevent cache file creation from python
sys.dont_write_bytecode = True
##########################################################################
#Main
def ndb_show(host, user, **args):
    ##########################################################################
    #Error logger
    module = "[ NDB ]"
    title = "[ NDB Cluster ]"
    ##########################################################################
    #SSH Connection
    if "password" in args:
        ssh = ssh_exec(host, user, password = args["password"])
    else:
        ssh = ssh_exec(host, user, p_key_file = args["p_key_file"])
    ##########################################################################
    #Main
    log_dir = args["out_dir"] + "/ndb"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # Create Log file and open it
    filename = '%s/%s-%s-%s.%s' % (log_dir, host,  timestampStr ,"ndb_cluster", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '%s/%s-%s-%s_%d.%s' % (log_dir, host, timestampStr, "ndb_cluster", filename_dup ,"log")
        filename_dup += 1
    with open(filename, "w") as outfile:
        outfile.writelines(header("=", title)+"\n")
        stdin, stdout, stderr = ssh.exec_command("ndb_mgm -e show")
        if "ndb_mgm: command not found" in stderr.readlines():
            print("[ %sERROR%s ] ndb_mgm: command not found\n" % (bcolors.FAIL, bcolors.ENDC))
            error = "ndb_mgm: command not found"
            errors.append({"host" : host, "module": module,  "error" : error, "time" : timestampStr})
            return "ERROR"
        section = None
        for l in stdout:
            # Connected servers counter
            if "[ndbd(NDB)]" in l:
                section = "NDB"
                ndb_con = 0            
            if "[ndb_mgmd(MGM)]" in l:
                section = None             
            if "[mysqld(API)]" in l:
                section = "SQL"
                sql_con = 0
            if section == "NDB" and "id" in l:
                if "not connected" in l:
                    pass
                else:
                    ndb_con += 1
            if section == "SQL" and "id" in l:
                if "not connected" in l:
                    pass
                else:
                    sql_con += 1
            # STDOUT
            if "Connected to Management" in l:
                continue
            outfile.writelines(l)
        # NDB errors
        if ndb_con < 2:
            error = "ERROR: Less then 2 NDB nodes connected"
            errors.append({"host" : host, "module": module,  "error" : error, "time" : timestampStr})
        if sql_con < 2:
            error = "ERROR: Less then 2 SQL nodes connected"
            errors.append({"host" : host, "module": module,  "error" : error, "time" : timestampStr})
        # STDOUT errors
        for l in stderr:
            outfile.writelines("Error: " + l + "\n")
    ssh.close()
    ##########################################################################
#!/usr/bin/python3
from __main__ import errors, timestampStr, header, bcolors, ssh_exec
import os
import sys
#Prevent cache file creation from python
sys.dont_write_bytecode = True
##########################################################################
#Main
def elk_status(host, user, **args):
    ##########################################################################
    #Connection errors
    miss_auth_error = None
    unable_auth_error = None
    ##########################################################################
    #Error logger
    module = "[ ELK ]"
    title = "[ELK Cluster]"
    ##########################################################################
    #SSH Connect
    if "password" in args:
        ssh = ssh_exec(host, user, password = args["password"])
    else:
        ssh = ssh_exec(host, user, p_key_file = args["p_key_file"])
    ##########################################################################
    #Main
    log_dir = args["out_dir"] + "/elk"
    status = None
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    #--------------------------------------------------
    # Create Log file and open it
    filename = '%s/%s-%s-%s.%s' % (log_dir, host,  timestampStr ,"elk_cluster", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '%s/%s-%s-%s_%d.%s' % (log_dir, host, timestampStr, "elk_cluster", filename_dup ,"log")
        filename_dup += 1
    outfile = open(filename, "a")
    outfile.writelines(header("=", title)+"\n")
    #--------------------------------------------------
    if "elk_pass" and "elk_user" in args:
        command = "curl --user %s:%s -X GET '%s:9200/_cluster/health?wait_for_status=yellow&timeout=50s&pretty'" % (args['elk_user'], args['elk_pass'], host)
    else:
        command = "curl -X GET '%s:9200/_cluster/health?wait_for_status=yellow&timeout=50s&pretty'" % (host)
    stdin, stdout, stderr = ssh.exec_command(command)
    output = []
    #--------------------------------------------------
    for l in stdout:
        output.append(l)
        if "missing authentication" in l:
            miss_auth_error = True
        if "unable to authenticate user" in l:
            unable_auth_error = True
    #--------------------------------------------------
    if miss_auth_error:
        print("%sERROR: Missing authentication credentials for REST request%s\nAuthentication requerd, specify elasticsearch credentials in 'config.ini' file.\n" % (bcolors.FAIL, bcolors.ENDC))
    elif unable_auth_error:
        print("%sERROR: unable to authenticate user [%s] %s\nWrong ELK credentials specified in 'config.ini' file.\n" % (bcolors.FAIL, args['elk_user'], bcolors.ENDC))
    else:
        if "yellow" in output:
            error = "[ WARNING ] Cluster status Yellow"
            errors.append({"host" : host, "module": module,  "error" : error, "time" : timestampStr})
        elif "red" in output:
            errors = "[ ERROR ] Cluster status Red"
            errors.append({"host" : host, "module": module,  "error" : error, "time" : timestampStr})
        for l in output:
            outfile.writelines(l.strip("{}"))
    #--------------------------------------------------
    outfile.close()
    ssh.close()
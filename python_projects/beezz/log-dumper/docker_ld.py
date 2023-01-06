#!/usr/bin/python3
from __main__ import errors, timestampStr, header, bcolors, ssh_exec
import os
import sys
#Prevent cache file creation from python
sys.dont_write_bytecode = True
##########################################################################
#Main
def containers_status(host, user, **args):
    ##########################################################################
    #Error logger
    module = "[Docker containers]"
    ##########################################################################
    #SSH Connect
    if "password" in args:
        ssh = ssh_exec(host, user, password = args["password"])
    else:
        ssh = ssh_exec(host, user, p_key_file = args["p_key_file"])
    command = "docker ps -a --format '{{.Names}}: [{{.Status}}]: {{.ID}}: {{.Image}}'"
    log_dir = args["out_dir"] + "/" + args["group"] + "/containers_status"
    stdin, stdout, stderr = ssh.exec_command(command)
    ##########################################################################
    if "docker: command not found" in stderr.readline():
        print("[ %sERROR%s ] docker: command not found\n" % (bcolors.FAIL, bcolors.ENDC))
        return 0
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    filename = '%s/%s-%s-%s.%s' % (log_dir, host, timestampStr , "containers-status", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '%s/%s-%s-%s_%d.%s' % (log_dir, host, timestampStr , "containers-status", filename_dup ,"log")
        filename_dup += 1
    outfile = open(filename, "a")
    outfile.writelines(header("=", "Containers: Status") + "\n")# Header file split line
    outfile.writelines(" " * 50  + host  + " " * 50 + "\n")# Header stdout split line
    outfile.writelines("Name"+" "*36+"ID"+" "*17+"Version"+" "*34+"Status\n")# Header stdout split line
    try:
        for i in stdout:# List containers and format output
            name,status,ID,version = i.split(': ')
            ID = ID.strip("\n")
            try:
                version = version.split(":")[1]
            except:
                pass
            version = version.strip("\n")
            outfile.writelines('{:<40}[{}] ==> {:<40} {:>}\n'.format(name, ID,version ,status))
            if "Exited (0)" in status:
                error = "conatainer '%s' is down." % (name)
                errors.append({"host" : host, "module": module,  "error" : error, "time" : timestampStr})
        outfile.writelines(header("=", timestampStr) +"\n")# End file split line
    except Exception as e:
        return e
    outfile.close()
    ssh.close()

#############################################################################
def containers_logs(host, user, **args):
    #Log directory 
    log_dir = args["out_dir"] + "/" + args["group"] + "/containers_logs/" + host
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    ##########################################################################
    #SSH Connect
    try:
        ssh = ssh_exec(host, user, password = args["password"])
    except:
        ssh = ssh_exec(host, user, p_key_file = args["p_key_file"])
    ##########################################################################
    progress = 0
    for container in args['containers']: 
        stdin, stdout, stderr = ssh.exec_command("docker logs %s --tail 500" % (container))
        if "No such container" in stderr.readline():
            continue
        if "docker: command not found" in stderr.readlines():
            print("[ %sERROR%s ] docker: command not found\n" % (bcolors.FAIL, bcolors.ENDC))
            continue
        filename = '%s/%s-%s.%s' % (log_dir, timestampStr , container, "log")
        filename_dup = 1
        while os.path.exists(filename):
          filename = '%s/%s-%s_%d.%s' % (log_dir, timestampStr , container, filename_dup ,"log")
          filename_dup += 1
        outfile = open(filename, "a")
        outfile.writelines(header("=", container) + "\n")# Header file split line
        for i in stdout:
            outfile.writelines(i + '\n')
                # Update progress
        progress+=1
        done = str(int((float(progress)/len(args['containers']))*100))
        sys.stdout.write("Containers logs download...  %s%%      %s"%(done,"\r"))
        sys.stdout.flush()
        outfile.close()
    ssh.close()


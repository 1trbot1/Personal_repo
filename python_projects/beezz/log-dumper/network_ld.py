#!/usr/bin/python3
from __main__ import errors, timestampStr, header, ssh_exec, FileError, SftpError
import os
import sys
import time
#Prevent cache file creation from python
sys.dont_write_bytecode = True
##########################################################################
#Main
def fg_system_status(host, user, password, **args):
    module = "[ FG ]"
    title = "[FG {}]".format(host) 
    ##########################################################################
    #SSH Connect
    ssh = ssh_exec(host, user, password = password)
    ##########################################################################
    #Main
    log_dir = args["out_dir"] + "/network/FG/system_status"
    status = None
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    #--------------------------------------------------
    # Create Log file and open it
    filename = '{}/{}-{}-{}.{}'.format(log_dir, host,  timestampStr ,"FG", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '{}/{}-{}-{}_{}.{}'.format(log_dir, host, timestampStr, "FG", filename_dup ,"log")
        filename_dup += 1
    outfile = open(filename, "w")
    outfile.writelines(header("=", title)+"\n")
    #--------------------------------------------------
    command = "get system status"
    stdin, stdout, stderr = ssh.exec_command(command)
    output = []
    #--------------------------------------------------
    for l in stdout:
        outfile.writelines(l.replace("FG600D_RH1 # ","").replace("--More-- ",""))
        sys.stdout.write("[ FG ]: Donwloading system info dump ...\r")
        sys.stdout.flush()
    outfile.close()
    statinfo = os.stat(filename)
    if statinfo.st_size <= 10:
        raise FileError("[ ERROR ]: Download faild.")
    ssh.close()
def fg_tac_report(host, user, password, **args):
    module = "[ FG ]"
    title = "[FG {}]".format(host) 
    ##########################################################################
    #SSH Connect
    ssh = ssh_exec(host, user, password = password)
    ##########################################################################
    #Main
    log_dir = args["out_dir"] + "/network/FG/tac_reports"
    status = None
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    #--------------------------------------------------
    # Create Log file and open it
    filename = '{}/{}-{}-{}.{}'.format(log_dir, host,  timestampStr ,"FG", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '{}/{}-{}-{}_{}.{}'.format(log_dir, host, timestampStr, "FG", filename_dup ,"log")
        filename_dup += 1
    outfile = open(filename, "w")
    outfile.writelines(header("=", title)+"\n")
    #--------------------------------------------------
    command = "config global \n execute tac report"
    stdin, stdout, stderr = ssh.exec_command(command)
    output = []
    #--------------------------------------------------
    try:
        for l in stdout:
            outfile.writelines(l)
            sys.stdout.write("[ FG ]: Donwloading tac report ...\r")
            sys.stdout.flush()
    except:
        raise
    statinfo = os.stat(filename)
    outfile.close()
    ssh.close()
    # if statinfo.st_size <= 1024:
    #     raise FileError("[ ERROR ]: Download faild.")
def sw_tech_report(host, user, password, **args):
    module = "[ BBSW ]"
    title = "[BBSW {}]".format(host) 
    ##########################################################################
    #SSH Connect
    ssh = ssh_exec(host, user, password = password)
    ##########################################################################
    #Main
    log_dir = args["out_dir"] + "/network/sw/support_reports"
    status = None
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    #--------------------------------------------------
    # Create Log file and open it
    filename = '{}/{}-{}-{}.{}'.format(log_dir, host,  timestampStr ,"sw", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '{}/{}-{}-{}_{}.{}'.format(log_dir, host, timestampStr, "sw", filename_dup ,"log")
        filename_dup += 1
    outfile = open(filename, "a")
    outfile.writelines(header("=", title)+"\n")
    #--------------------------------------------------
    # command = "request support information"
    commands = [ "show chassis alarms", "show chassis hardware", "show ver", "show virtual-chassis", "show system uptime" ]
    output = []
    #--------------------------------------------------
    progress = 0
    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        outfile.writelines(header("=",command))
        # Update progress
        progress+=1
        done = str(int((float(progress)/len(commands))*100))
        sys.stdout.write("[ BBSW ]: Donwloading tech report...  {}%      {}".format(done,"\r"))
        sys.stdout.flush()
        for l in stdout:
            if "root@BB1sw>" in l:
                continue
            else:
                outfile.writelines(l)
    #--------------------------------------------------
    if len(errors) > 0:
        error_sum(errors, host)
    #--------------------------------------------------
    outfile.close()
    ssh.close()
    if os.stat(filename).st_size <= 10: # larger then 1KB
        raise FileError("[ ERROR ]: Download faild.")
def pgw_report(host, user, password, **args):
    module = "[ PGW ]"
    title = "[PGW {}]".format(host) 
    ##########################################################################
    #SSH Connect
    ssh = ssh_exec(host, user, password = password)
    channel = ssh.invoke_shell(width=2000, height=20000)
    ##########################################################################
    #Main
    #--------------------------------------------------
    # Create Log file and open it
    log_dir = args["out_dir"] + "/network/pgw/reports"
    status = None
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    filename = '{}/{}-{}-{}.{}'.format(log_dir, host,  timestampStr ,"pgw_report", "log")
    filename_dup = 1
    while os.path.exists(filename):
        filename = '{}/{}-{}-{}_{}.{}'.format(log_dir, host, timestampStr, "pgw_report", filename_dup ,"log")
        filename_dup += 1
    outfile = open(filename, "a")
    outfile.writelines(header("=", title)+"\n")
    #--------------------------------------------------
    # commands
    commands = [
        "show system information",
        "show version",
        "show system time",
        "show system alarms",
        "show system license",
        "show system virtual-fabric",
        "show system rollback",
        "show chassis detail",
        "show bof booted",
        "show card detail",
        "show mda detail",
        "show port detail",
        "show lag detail",
        "show router 1 status",
        "show router 2 status",
        "show router 3 status",
        "show router 4 status",
        "show router 5 status",
        "show router 1 interface detail",
        "show router 2 interface detail",
        "show router 3 interface detail",
        "show router 4 interface detail",
        "show router 5 interface detail",
        "show router 1 bfd session",
        "show router 2 bfd session",
        "show router 3 bfd session",
        "show router 4 bfd session",
        "show router 5 bfd session",
        "show router 1 route-table",
        "show router 2 route-table",
        "show router 3 route-table",
        "show router 4 route-table",
        "show router 5 route-table",
        "show mobile-gateway system",
        "show mobile-gateway mg-vm cpu",
        "show mobile-gateway mg-vm memory-pools",
        "show mobile-gateway connections detail ",
        "show mobile-gateway pdn statistics",
        "show mobile-gateway pdn statistics attach-failure-statistics",
        "show mobile-gateway pdn ref-point-peers gx",
        "show mobile-gateway pdn ref-point-peers gy",
        "show mobile-gateway pdn ref-point-peers rf",
        "show mobile-gateway pdn ref-point-stats gx",
        "show mobile-gateway pdn ref-point-stats gy",
        "show mobile-gateway pdn ref-point-stats rf",
        "show mobile-gateway pdn ref-point-stats gn aggregate",
        "show mobile-gateway pdn ref-point-stats gp aggregate",
        "show mobile-gateway pdn ref-point-stats s5 aggregate",
        "show mobile-gateway pdn ref-point-stats s8 aggregate",
        "show mobile-gateway pdn gtp-load-overload-control",
        "show mobile-gateway pdn gtp-local-load-control stats",
        "show mobile-gateway pdn gtp-local-overload-control stats",
        "admin display-config",
        " "
    ]
    #--------------------------------------------------
    progress =  0
    for command in commands:
        # Send command
        channel.send('{}\n'.format(command))
        # Update progress
        while not channel.recv_ready():
            time.sleep(0.3)
        progress+=1
        done = str(int((float(progress)/len(commands))*100))
        sys.stdout.write("[ PGW ]: Generating report...  {}%     {}".format(done,"\r"))
        sys.stdout.flush()
        output = channel.recv(9999999)
        outfile.writelines(output.decode("ascii").replace("\n",""))
    channel.close()
    outfile.close()
    statinfo = os.stat(filename)
    if statinfo.st_size <= 10:
        raise FileError(" [ ERROR ]: Download faild.")
    ssh.close()
def pgw_cf2_logs(host, user, password, **args):
    module = "[ PGW ]"
    ssh = ssh_exec(host, user, password = password)
    sftp = ssh.open_sftp()
    localpath = args["out_dir"] + "/network/pgw/reports/" + host + "-cf2"
    if not os.path.exists(localpath):
        os.makedirs(localpath)
    remotepath = '/cf2:/log'
    cf2_logs = []
    progress =  0
    try:
        for f in sftp.listdir(remotepath):
            cf2_logs.append(f)
    except:
        errors.append({"host" : host, "module" : module,  "error" : "cf2 disk not found", "time" : timestampStr})
        raise FileError(" [ ERROR ]: cf2 disk not found.")
    for f in cf2_logs:
        sftp.get(remotepath + "/" + f, localpath + "/" + f)
        # Update progress
        progress+=1
        done = str(int((float(progress)/len(cf2_logs))*100))
        sys.stdout.write("[ PGW ]: Downloading logs from \"cf2\" disk...  {}%      {}".format(done,"\r"))
        sys.stdout.flush()
    sftp.close()
    #--------------------------------------------------
    ssh.close()
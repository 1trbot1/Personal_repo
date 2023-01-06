#!/usr/bin/python3
# import pdb; pdb.set_trace() <<<<< #Debugger
version = "v0.98"
import signal
import sys
import os
import shutil
import yaml
from prettytable import PrettyTable
from exceptions_ld import *
from datetime import datetime
#Prevent cache file creation from python
sys.dont_write_bytecode = True
##########################################################################
#Colors defeniton
from colorama import Fore, Style, init
init()
class bcolors:
    HEADER = Style.BRIGHT + Fore.YELLOW 
    OKBLUE = Style.BRIGHT + Fore.BLUE
    OKGREEN = Style.BRIGHT + Fore.GREEN
    WARNING = Style.BRIGHT + Fore.YELLOW
    FAIL = Style.BRIGHT + Fore.RED
    ENDC = Style.RESET_ALL
    BOLD = Style.BRIGHT
#Print format templates
def header(char, title, color = None):
    if color == None:
        if len(title) % 2 == 0:
            return "{0}{1}{0}\n".format(char*int(((100-len(title)))/2),title)
        else:
            return "{0}{2}{1}\n".format(char*int(((101-len(title)))/2),char*int(((100-len(title)))/2),title)
    else:
        if len(title) % 2 == 0:
            return "{0}{2}{1}{3}{0}\n".format(char*int(((100-len(title)))/2),title,color,bcolors.ENDC)
        else:
            return "{0}{3}{2}{4}{1}\n".format(char*int(((101-len(title)))/2),char*int(((100-len(title)))/2),title,color,bcolors.ENDC)
def status(title,status,err = None):
    if status == "OK":
        title.append(" [{}OK{}]\n".format(bcolors.OKGREEN,bcolors.ENDC))
        title_len = sum([len(s) for s in title])
        print("{0[0]}{1}{0[1]}".format(title,"-" * (header_len-title_len)))
    elif status == "ERROR":
        title.append(" {}{}{}\n".format(bcolors.FAIL,err,bcolors.ENDC))
        title_len = sum([len(s) for s in title])
        print("{0[0]}{1}{0[1]}".format(title,"-" * (header_len-title_len)))
##########################################################################
#Init
title = """
  ____  _____ _____ __________  _____ _____ ____ _   _   ____  _   _ __  __ ____  
 | __ )| ____| ____|__  /__  / |_   _| ____/ ___| | | | |  _ \| | | |  \/  |  _ \ 
 |  _ \|  _| |  _|   / /  / /    | | |  _|| |   | |_| | | | | | | | | |\/| | |_) |
 | |_) | |___| |___ / /_ / /_    | | | |__| |___|  _  | | |_| | |_| | |  | |  __/ 
 |____/|_____|_____/____/____|   |_| |_____\____|_| |_| |____/ \___/|_|  |_|_|  {}{}                                                                                 
""".format(bcolors.OKBLUE,version)
print(header("", title, bcolors.HEADER))
################################### TIME #################################
#TimeStamp
dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%d-%m-%Y(%H.%M)")
################################## CONFIG ################################
# Import configs
if not os.path.isdir("".join([os.getcwd(), '/config'])):
    sys.exit("[{}ERROR{}] : 'config' directory not found.".format(bcolors.FAIL,bcolors.ENDC))
#-------------------------------------------------------------------------
if not os.path.isfile("".join([os.getcwd(), '/config/config.yml'])):
    sys.exit("[{}ERROR{}] : './config/config.yml' file not found.".format(bcolors.FAIL,bcolors.ENDC))
#-------------------------------------------------------------------------
with open("".join([os.getcwd(), '/config/config.yml'])) as config_file:
    config = yaml.safe_load(config_file)
    print("{}CONFIG{}:{:<2} {}".format(bcolors.OKBLUE,bcolors.ENDC,"",config_file.name))
################################# HOSTS ##################################
# Import hosts file
if not os.path.isfile("".join([os.getcwd(), '/config/hosts.yml'])):
    sys.exit("[{}ERROR{}] : './config/hosts.yml' file not found.".format(bcolors.FAIL,bcolors.ENDC))
#-------------------------------------------------------------------------
with open("".join([os.getcwd(), '/config/hosts.yml'])) as hosts_file:
    print("{}HOSTS{}:{:<3} {}".format(bcolors.OKBLUE,bcolors.ENDC,"",hosts_file.name))
    hosts = yaml.safe_load(hosts_file)
################################ HANDLERS ################################
# CTRL + C Exit
def signal_handler(signal, frame):
    print('\nAborted!')
    exit(0)
signal.signal(signal.SIGINT, signal_handler)
################################ HANDLERS ################################
# ERROR SUM
errors = []
def errors_sum():
    pt = PrettyTable()
    pt.right_padding_width = 2
    pt.field_names = ["Host", "Module", "Error", "Time"]
    with open("/".join((output_dir, "error_sum.log")), "w") as f:
        for e in errors:
            pt.add_row([e["host"], e["module"], e["error"], e["time"]])
        f.write(pt.get_string()+"\n")
    pt.align["Error"] = "l"
    print(pt.get_string(title=f"{bcolors.BOLD}Summary{bcolors.ENDC}"))
############################## FUNCTIONS ##################################
#Import SSH module << Need to be placed here cuz it depends on "bcolors" class declaration.
ssh_timeout = config["ssh"]["timeout"]
from ssh_ld import ssh_exec
#System info log
def sys_info(host):
    #Import System Module
    try:
        system_ld
    except NameError:
        import system_ld
    except Exception as e:
        raise e
    #Get System Info
    commands = [ "uname -a" ,"uptime" ,"timedatectl" ,"ntpq -p" ,"chronyc sources" ,"df -kh" ]
    try:
        if "password" in config["ssh"]:
            system_ld.sys_info(host, config["ssh"]["username"], commands, password = config["ssh"]["password"], out_dir = output_dir)
        elif "ssh_private_key" in config["ssh"]:
            system_ld.sys_info(host, config["ssh"]["username"], commands, p_key_file = config["ssh"]["ssh_private_key"], out_dir = output_dir)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# Containers status
def containers_status(host, group):
    #Import Docker Module
    try:
        docker_ld
    except NameError:
        import docker_ld
    except Exception as e:
        print(e)
    # Get Containers Status    
    try:
        if "password" in config["ssh"]:
            docker_ld.containers_status(host, config["ssh"]["username"], password = config["ssh"]["password"], out_dir = output_dir, group = group)
        elif "ssh_private_key" in config["ssh"]:
            docker_ld.containers_status(host, config["ssh"]["username"], p_key_file = config["ssh"]["ssh_private_key"], out_dir = output_dir, group = group)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# Containers logs
def containers_logs(host, containers, group):
    #Import Docker Module
    try:
        docker_ld
    except NameError:
        import docker_ld   
    except Exception as e:
        print(e)
    #Get Containers logs
    try:
        if "password" in config["ssh"]:
            docker_ld.containers_logs(host, config["ssh"]["username"], password = config["ssh"]["password"], out_dir = output_dir, containers = containers, group = group)
        elif "ssh_private_key" in config["ssh"]:
            docker_ld.containers_logs(host, config["ssh"]["username"], p_key_file = config["ssh"]["ssh_private_key"], out_dir = output_dir, containers = containers, group = group)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# NDB status
def ndb_show(host):
    #Import NDB Module
    try:
        db_ld
    except NameError:
        import db_ld
    except Exception as e:
        print(e)
    #Get NDB Cluster status
    try:
        if "password" in config["ssh"]:
            db_ld.ndb_show(host, config["ssh"]["username"], password = config["ssh"]["password"], out_dir = output_dir)
        elif "ssh_private_key" in config["ssh"]:
            db_ld.ndb_show(host, config["ssh"]["username"], p_key_file = config["ssh"]["ssh_private_key"], out_dir = output_dir)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# FreeIPA status
def ipa_status(host):
    #Import IPA module
    try:
        ipa_ld
    except NameError:
        import ipa_ld   
    except Exception as e:
        print(e)
    #Get FreeIPA Status
    try:
        if "password" in config["ssh"]:
            ipa_ld.ipa_status(host, config["ssh"]["username"], password = config["ssh"]["password"], out_dir = output_dir)
        elif "ssh_private_key" in config["ssh"]:
            ipa_ld.ipa_status(host, config["ssh"]["username"], p_key_file = config["ssh"]["ssh_private_key"], out_dir = output_dir)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# ELK status
def elk_status(host):
    #Import ELK module
    try:
        elk_ld
    except NameError:
        import elk_ld 
    except Exception as e:
        print(e)
    #Get ELK status  
    if config["elk"]["elk_auth"]:
        try:
            if "password" in config["ssh"]:
                elk_ld.elk_status(host, config["ssh"]["username"], password = config["ssh"]["password"], out_dir = output_dir, elk_user = config["elk"]["elk_user"], elk_pass = config["elk"]["elk_pass"])
            elif "ssh_private_key" in config["ssh"]:
                elk_ld.elk_status(host, config["ssh"]["username"], p_key_file = config["ssh"]["ssh_private_key"], out_dir = output_dir, elk_user = config["elk"]["elk_user"], elk_pass = config["elk"]["elk_pass"])
        except SshError as e:
            raise SshError(e.value)
        except Exception as e:
            raise e
    else:
        try:
            if "password" in config["ssh"]:
                elk_ld.elk_status(host, config["ssh"]["username"], password = config["ssh"]["password"], out_dir = output_dir)
            elif "ssh_private_key" in config["ssh"]:
                elk_ld.elk_status(host, config["ssh"]["username"], p_key_file = config["ssh"]["ssh_private_key"], out_dir = output_dir)
        except SshError as e:
            raise SshError(e.value)
        except Exception as e:
            raise e
#-------------------------------------
# FG: System info
def fg_sys_info(host):
    #Import Network Module
    try:
        network_ld
    except NameError:
        import network_ld
    except Exception as e:
        print(e)
    #Get FG System Info
    try:
        network_ld.fg_system_status(host, config["fg"]["fg_user"], config["fg"]["fg_pass"], out_dir = output_dir)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# FG: Tac report
def fg_tac(host):
    #Import Network Module
    try:
        network_ld
    except NameError:
        import network_ld
    except Exception as e:
        print(e)
    #Get FG TAC Report
    try:    
        network_ld.fg_tac_report(host, config["fg"]["fg_user"], config["fg"]["fg_pass"], out_dir = output_dir)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# BBSW: Support report
def bbsw_report(host):
    #Import Network Module
    try:
        network_ld
    except NameError:
        import network_ld
    except Exception as e:
        print(e)
    #Get Switch report
    try:
        network_ld.sw_tech_report(host, config["bbsw"]["bbws_user"], config["bbsw"]["bbsw_pass"], out_dir = output_dir)
    except SshError as e:
        raise SshError(e.value)
    except FileError:
        raise FileError("Download failed")
    except Exception as e:
       raise e
#-------------------------------------
# PGW: Report
def pgw_report(host):
    #Import Network Module
    try:
        network_ld
    except NameError:
        import network_ld
    except Exception as e:
        print(e)
    #Get PGW report
    try:
        network_ld.pgw_report(host, config["pgw"]["pgw_user"], config["pgw"]["pgw_pass"], out_dir = output_dir)
    # except SshError as e:
    #     raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# PGW: CF2 Logs
def pgw_cf2_logs(host):
    #Import Network Module
    try:
        network_ld
    except NameError:
        import network_ld
    except Exception as e:
        print(e)
    #Get PGW Logs file from cf2 disk
    try:
        network_ld.pgw_cf2_logs(host, config["pgw"]["pgw_user"], config["pgw"]["pgw_pass"], out_dir = output_dir)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
#-------------------------------------
# HLR: Logs
def hlr_get_logs(host):
    #Import Network Module
    try:
        hlr_ld
    except NameError:
        import hlr_ld
    except Exception as e:
        print(e)
    #Get HLR Logs
    try:
        if "password" in config["ssh"]:
            hlr_ld.hlr_get_logs(host, config["ssh"]["username"], password = config["ssh"]["password"], out_dir = output_dir)
        elif "ssh_private_key" in config["ssh"]:
            hlr_ld.hlr_get_logs(host, config["ssh"]["username"], p_key_file = config["ssh"]["ssh_private_key"], out_dir = output_dir)
    except SshError as e:
        raise SshError(e.value)
    except Exception as e:
        raise e
################################ MAIN ##################################### 
# INFO
output_dir = config["logs"]["output_dir"]
print("{}OUTPUT{}:{:<2} {}\n".format(bcolors.OKBLUE,bcolors.ENDC,"","{}_{}.zip".format(output_dir, timestampStr)))

#-------------------------------------
#Containers logs dump
for host in hosts["all"]:
    print(header("=", host, bcolors.HEADER))
    header_len = len(header("=", host, bcolors.HEADER))
    #-------------------------------------
    # System info
    if host in hosts["linux"]:
        title = ["[ System ]: System Info. "]
        try:
            sys_info(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # Docker servers: Containers status dump
    if host in hosts["dockers"]:
        title = ["[ DOCKER ]: Containers status Info. "]
        try:
            containers_status(host, "dockers")
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # Docker servers: Containers logs dump
    if host in hosts["dockers"]:
        title = ["[ DOCKER ]: Services Containers Logs. "]
        try:
            containers_logs(host, config["dockers"]["containers"], "dockers")
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # CGS: Containers status dump
    if host in hosts["cgs"]:
        title = ["[ CGS ]: Containers Status. "]
        try:
            containers_status(host, "cgs")
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # CGS: Containers logs dump
    if host in hosts["cgs"]:
        title = ["[ CGS ]: Containers Log. "]
        try:
            containers_logs(host, config["cgs"]["cgs_containers"], "cgs")
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # NDB
    if host in hosts["brain"]:
        title = ["[ NDB ]: Cluster Info. "]
        try:
            ndb_show(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # ELK
    if host in hosts["elk"]:
        title = ["[ ELK ]: Cluster Info. "]
        try:
            elk_status(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # FreeIPA
    if host in hosts["ipa"]:
        title = ["[ FreeIPA ]: Services Status. "]
        try:
            ipa_status(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # FG: SYS info
    if host in hosts["fg"]:
        title = ["[ FG ]: System Info. "]
        try:
            fg_sys_info(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # FG: TAC report
    if host in hosts["fg"]:
        title = ["[ FG ]: TAC report. "]
        try:
            fg_tac(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # SW: Support report
    if host in hosts["switches"]:
        title = ["[ BBSW ]: Support report. "]
        try:
            bbsw_report(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # PGW: Report
    if host in hosts["pgw"]:
        title = ["[ PGW ]: Report. "]
        try:
            pgw_report(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # PGW: CF2 Logs Download
    if host in hosts["pgw"]:
        title = ["[ PGW ]: CF2 disk logs. "]
        try:
            pgw_cf2_logs(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    #-------------------------------------
    # HLR: Logs
    if host in hosts["hlr"]:
        title = ["[ HLR ]: Logs. "]
        try:
            hlr_get_logs(host)
            status(title,"OK")
        except Exception as e:
            status(title,"ERROR",err = e)
            continue
    print("")
try:
    errors_sum()
    shutil.make_archive("./dump_{}".format(timestampStr), 'zip', output_dir)
    shutil.rmtree(output_dir) 
except Exception:
    pass
input("Press Enter to exit...")
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# edump:  Version 1.0
# Install prerequisites:
# apt install python-pip
# pip install configparser, elasticsearch, docker, optparse-pretty
#########################################################################
# region :  Banner:
banner = """\
          ███████╗    ██████╗ ██╗   ██╗███╗   ███╗██████╗ 
          ██╔════╝    ██╔══██╗██║   ██║████╗ ████║██╔══██╗
          █████╗█████╗██║  ██║██║   ██║██╔████╔██║██████╔╝
          ██╔══╝╚════╝██║  ██║██║   ██║██║╚██╔╝██║██╔═══╝ 
          ███████╗    ██████╔╝╚██████╔╝██║ ╚═╝ ██║██║     
          ╚══════╝    ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝        V: 1.0
        """
#endregion
##########################################################################
# region :  Imports
# 1) Signals - User interupt handling
import signal
# 2) OptionParser - Passing  options to programm
from optparse import *
from optparse import OptionParser, OptionGroup
from optparse_mooi import CompactHelpFormatter, CompactColorHelpFormatter
# 3) Docker - Interacting with local docker's api
import docker
# 4) re - Regex module
import re
# 5) os - Folder and files operations
import os
# 6) Elasticsearch - Interacting with elasticsearch server
from elasticsearch import Elasticsearch
# 7) sys - Parsing system arguments passed with command
import sys
# 8) globe - List directory content
import fnmatch
#endregion
##########################################################################
# region :  Variables
#Windows size
rows = "0"
columns = "0"
#endregion
##########################################################################
# region :  Classes:
# 1) Colors variables
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GREY = '\033[38;5;239m'
# 2) Regex variables
class regex:
    expression = r"(^http[s]?):\/\/(\w*\.\w[a-z A-z .]*|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b):([0-9]{2,6})"
    protocol = r"(http[s]?:\/\/).*"
    protocol_position = 1
    ip_position = 2
    port_position = 3
#endregion
##########################################################################
# region :  Functions:
# 1) CTRL + C graceful exit without errors
def signal_handler(sig, frame):
          print('\nExiting....')
          sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# 2) User input checkers
def YorN(prompt):
    YorN.user_input = ""
    while YorN.user_input.lower() not in ("y", "n", "yes", "no"):
        YorN.user_input = raw_input(prompt)
        if YorN.user_input.lower() not in ("y", "n", "yes", "no"):
            print("Wrong inpute, use Y/n")

# 3) Validate source and target + determinate either local folder or remote server specified 
def SourceType(target):
    is_url = re.search(regex.protocol, target)
    if is_url:
        return "Server"
    else:
        return "Directory"

# 4) Elasticsearch connection check
def ElastickCheck(target):
    try:
      re_compile_target = re.compile(regex.expression)
      elastic_host = re_compile_target.match(target).group(regex.ip_position)
      elastic_port = re_compile_target.match(target).group(regex.port_position)
      if Elasticsearch(hosts=[{'host': str(elastic_host), 'port': str(elastic_port)}]).ping():
         return True
      else:
         return False
    except AttributeError:
      if target == options.input:
          print("\n" + bcolors.FAIL + "[ERROR]" + bcolors.ENDC + ": Source URL format error")
          print('         Example (http://0.0.0.0:9200) \n         Use "edump -h" for additional information \n')
          exit()
      else:
          print("\n" + bcolors.FAIL + "[ERROR]" + bcolors.ENDC + ": Destination URL format error")
          print('         Example (http://0.0.0.0:9200) \n         Use "edump -h" for additional information \n')
          exit()
       
# 5) Elasticsearch list indexes
def IndexList(target, expression):
  if input_type == "Server":
    re_compile_target = re.compile(regex.expression)
    elastic_host = re_compile_target.match(target).group(regex.ip_position)
    elastic_port = re_compile_target.match(target).group(regex.port_position)
    es = Elasticsearch(hosts=[{'host': str(elastic_host), 'port': str(elastic_port)}])
    return es.indices.get(expression)
  elif input_type == "Directory":
    indexes = []
    for f in os.listdir(target): 
     if fnmatch.fnmatch(f, expression):
             indexes.append(f)
    return indexes



# 6) Establish connection to local docker API
def DockerConnect():
  DockerConnect.env = docker.from_env()
  DockerConnect.api = docker.APIClient(base_url='unix://var/run/docker.sock')

# 7) Run dump container
def Dump(container_name):
  try:
      DockerConnect.api.remove_container(container_name)
  except:
      pass
  if output_type == "Directory":
    try:
      os.remove(options.output + "/" + index)
    except:
      pass
    DockerConnect.env.containers.run('taskrabbit/elasticsearch-dump',
                    '--input=' + options.input + '/' + index + ' --output=/tmp/' + index + ' --type=' + options.type.lower(),
                    name=container_name,
                    remove=True,
                    environment=["NODE_TLS_REJECT_UNAUTHORIZED = 0"],
                    volumes=[options.output + ":/tmp"])
                    
  elif input_type == "Directory":
    DockerConnect.env.containers.run('taskrabbit/elasticsearch-dump',
                    '--input=/tmp/' + index + ' --output=' + options.output + '/' + index + ' --type=' + options.type.lower(),
                    name=container_name,
                    remove=True,
                    environment=["NODE_TLS_REJECT_UNAUTHORIZED = 0"],
                    volumes=[options.input + ":/tmp"])
  else:
    DockerConnect.env.containers.run('taskrabbit/elasticsearch-dump',
                    '--input=' + options.input + '/' + index +' --output=' + options.output + '/' + index + ' --type=' + options.type.lower(),
                    name=container_name,
                    remove=True,
                    environment=["NODE_TLS_REJECT_UNAUTHORIZED = 0"],
                    volumes=["/tmp:/tmp"])  
#endregion
##########################################################################
# region :  OptionParser
# Set OptionParser as variable to make it usage more easy.
description = '''\
EDUMP based on "elasticsearch" open source project.
This program allows to dump multiple indexes from server or localfile to anouther server or local file.\
'''

parser = OptionParser(usage= bcolors.ENDC + ": %prog " + bcolors.WARNING + "[pattern] [options]"
                       + bcolors.OKBLUE + "\nExample" + bcolors.ENDC                      
                       + ": %prog" + bcolors.WARNING + " 'cgs*' " + bcolors.ENDC
                       + "--source " + bcolors.WARNING + "http://0.0.0.0:9200 " + bcolors.ENDC
                       + "--dest " + bcolors.WARNING + "/mnt/backup" + bcolors.ENDC,
                        version='%prog v1.0',
#     formatter = CompactHelpFormatter(
#         align_long_opts=True,
#         width = 80,
#         metavar_column = 17,
#     ),

    formatter = CompactColorHelpFormatter(
        metavar_column = 17,
        align_long_opts=True,
        description_color = 'white',
        heading_color = 'blue-bold',
        usage_color   = 'blue-bold',
        shopt_color   = 'white-bold',
        lopt_color    = 'white-bold',
        metavar_color = 'white-bold',
        help_color    = 'white-bold',
        option_colormap = {
            '-B': ('white', 'white-bold',  'green-bold', 'red-bold'),
            ('-f', '--to'): ('red-bold', 'red', 'white', 'blue-bold')
        }
    ),
    description     = description,
    add_help_option = False
)

general_options = OptionGroup(parser, 'General options')

o = general_options.add_option
o('-h', '--help',        action='help',         help='show this help message and exit'),
# Operators definition
o("-s", "--source",
                   dest="input",
                   help="Source of dump, can be folder or elastic server's url."),

o("-d", "--dest",
                   dest="output",
                   help="Destination of dump, can be folder or elastic server's url."),
                   
o("-t", "--data-type", 
                   dest="type",
                   type='choice',
                   action='store',
                   choices=['Data', 'Mapping', 'All',],
                   help="Data or Mapping", 
                   default="Data")
      

parser.add_option_group(general_options)
# Operators parsing
(options, args) = parser.parse_args()
#endregion
##########################################################################
# region:   Errors
# 1) Pattern not specified
try:
  assert (str(sys.argv[1])), bcolors.FAIL + "[ERROR]" + bcolors.ENDC + ": Index pattern not specified"
except IndexError:
    print(bcolors.FAIL + "[ERROR]" + bcolors.ENDC + ": Index pattern not specified")
    print('         You must specify destination. Use "edump -h" for additional information ')
    exit()

# 2) Source optionmissing
try:
  assert (options.input), bcolors.FAIL + "[ERROR]" + bcolors.ENDC + ": Source not specified"
except AssertionError as error:
    print(error)
    print('         You must specify source. Use "edump -h" for additional information ')
    exit()
# 3) Destination option missing
try:
  assert (options.output), bcolors.FAIL + "[ERROR]" + bcolors.ENDC + ": Destination not specified"
except AssertionError as error:
    print(error)
    print('         You must specify destination. Use "edump -h" for additional information ')
    exit()
# 4) No connection to server
def no_connection(server):
    print( bcolors.FAIL + "\n[ERROR]: " + bcolors.ENDC + "Cant connect to: " + bcolors.OKBLUE + server + "\n")
    exit()

# 5) Directory not exist or not accessible  
def not_exist(folder):
    print( bcolors.FAIL + "\n[ERROR]: " + bcolors.ENDC + "Directory not exist or not accessible: " + bcolors.OKBLUE + folder + "\n")
    exit()

#endregion
##########################################################################
# region :  Program:
# 1) Validate source and distenation, and set ther type values
# 1.1) Validate source 
if SourceType(options.input) == "Server":
  input_type = "Server"
  if not ElastickCheck(options.input):
    no_connection(options.input)
elif SourceType(options.input) == "Directory":
  input_type = "Directory"
  if not os.path.exists(options.input):
    not_exist(options.input)

# 1.2) Validate destination 
if SourceType(options.output) == "Server":
  output_type = "Server"
  if not ElastickCheck(options.output):
    no_connection(options.output)
elif SourceType(options.output) == "Directory":
  output_type = "Directory"
  if not os.path.exists(options.output):
    not_exist(options.output)

##########################################################################
# 2) Program Name Banner
# 2.1) Clear screen before on program start
os.system('clear')
# 2.2) Print Program name and version
print(bcolors.OKGREEN + banner + bcolors.ENDC)

##########################################################################
# List indexes and dump
# 3.1) Print message to user 
print(bcolors.HEADER + "You are about to dump this indexes from " + bcolors.OKBLUE +
      options.input + bcolors.HEADER + " to " + bcolors.OKBLUE + options.output + bcolors.ENDC + "\n")
# 3.2) List all indeces matching to users(sys.argv[1]) pattern
list_to_copy = []
for index in IndexList(options.input, str(sys.argv[1])):
      list_to_copy.append(index)
      print( bcolors.WARNING + index + bcolors.ENDC)
YorN("\nContinue? [Y/n]")
# 3.3) Clear screen before on program start
os.system('clear')
# 3.4) Print Program name and version
print(bcolors.OKGREEN + banner + bcolors.ENDC)

# 3.5) Window parameters
if os.popen('stty size', 'r').read():
  rows, columns = os.popen('stty size', 'r').read().split()

# 3.6) If user permit to continue, then create create dump container for each index.
if YorN.user_input.lower() in ("y", "yes"):
      gap  = ''.join([' '] * ((int(columns) / 4) - (int(len("INDEX NAME")))))
      print("INDEX NAME" + gap + "STATUS")
      DockerConnect()
      for index in list_to_copy:
          Dump(index)
          gap  = ''.join([' '] * ((int(columns) / 4) - (int(len(index)))))
          print( bcolors.WARNING + index + bcolors.OKGREEN + gap + "[Dumped]")
else:
      os.system('clear')
      exit()

#endregion




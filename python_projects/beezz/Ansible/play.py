#!/usr/bin/python2
# Version 2.7
# Install prerequisites:
# apt install python # install python2
# update-alternatives --install /usr/bin/python python /usr/bin/python2 1
# update-alternatives --install /usr/bin/python python /usr/bin/python3 2
# update-alternatives --config python # select default python2
# python --version
# install pip2
# wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
# python2 get-pip.py
# pip2 install configparser
# apt install ansible
#########################################################################
# region [ Import ]
from optparse import OptionParser
import os, sys, subprocess, configparser, signal
#endregion
##########################################################################
# region [ Vars ]
#Set OptionParser as variable to make it ysage more easy.
environment = [None]
arguments = [None]
parser = OptionParser(usage="Usage: play <playbook file> -i <inventory folder> -g <inventory subfolder> -e var1=value -e var2=value -d y/n -a <argument of ansible-playbook>\n play --version", version="%prog v2.6")
#Operators definition
parser.add_option("-i", dest="inventory", metavar="inventory_name", help="name of inventory")
parser.add_option("-a", dest="arguments", metavar="arguments", action="append", help="pass arguments to anisible-playbook")
parser.add_option("-e", dest="environment", metavar="enironment_variables", action="append",  help="pass additional environment variables")
parser.add_option("-g", dest="group", metavar="group_name", help="name of group in inventory")
parser.add_option("-d", dest="drymode", metavar="Y/n", help="run role in dry mode (default 'Y')")
(options, args) = parser.parse_args()
if options.environment:
  environment = ' -e '.join([''] + options.environment)
else:
  environment = ""

if options.arguments:
  arguments = ' -'.join([''] + options.arguments)
else:
  arguments = ""

##########################################################################
#Colors defeniton
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

###########################################################################
#Variables and lists
#Set config file parser variable
config = configparser.RawConfigParser()

# Set inventories list with first value Null so list start with 1 instead 0
inventories = [None]
groups = [None]

# Set checkmode with empty value to loope user prompt till correct answer
checkmode = None

# Set Error string to empty
error = None

# Set inventory selected by default
if config.read('play.conf'):
  default_inventory = config["defaults"]["default_inventory"]
else:
  default_inventory = None

# Set variable fo default group
if config.read('play.conf'):
  default_group = config["defaults"]["default_group"]
else:
  default_group = None

#Inventories base path
inventories_base = os.getcwd() + "/inventories/"

#Windows size
rows = "0"
columns = "0"
##########################################################################
#Window parameters (used for split line)
if os.popen('stty size', 'r').read():
  rows, columns = os.popen('stty size', 'r').read().split()

#endregion
##########################################################################
# region [ Functions ]
# 1. Error handler
#  reason = String that will be shown to user as reason of error
def ERROR(reason):
    error = "[ERROR]: " + reason
    errorline = ''.join(['='] * (int(columns) - (int(len(error) + 1))))
    print(bcolors.FAIL + error + " " + bcolors.WARNING + errorline + bcolors.ENDC + "\n")
    parser.print_help()
    sys.exit()

# 2. List  folder function and store
#  folder_path = Path to folder to list
#  array_name = array name that function use to store output
def lsdir(folder_path, array_name):
  #Errors
  # Path is not directory error
  if not os.path.isdir(folder_path):
    return ERROR("Specified path (" + folder_path + ") is not directry")

  # Directory is empty error
  elif len(os.listdir(folder_path)) == 0:
    return ERROR("Specified direcotry (" + folder_path + ") is empty")

  # List directory to array
  else:
    for folder in os.listdir(folder_path):                      # For each folder in folder_path
      if os.path.isdir(os.path.join(folder_path, folder)):      # Mark each folder as folder variable
        if not folder.startswith('.'):                          # Do not include hiden and root folders
            array_name.append(folder)                           # Append listed folders to array

# 3. Task header line
#  message = header message string
def header(message):
     blockline = ''.join(['='] * (int(columns) - (int(len(message) + 3)))) #Breack line defenition
     print(bcolors.OKGREEN + "[" + message + "]" + " " + bcolors.OKBLUE + blockline + bcolors.ENDC + "\n")  # Print message and breack line


# 4. CTRL + C graceful exit without errors
def signal_handler(sig, frame):
          print('\nExiting....')
          sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#endregion
#####################################################################################
# region [ Prog ]
# Check passed arguments
# 1. Playbook doesnot specified
if not len(sys.argv) > 1:
  print(ERROR("Specify playbook file"))
# 2. Specified file not exist
if not os.path.isfile(sys.argv[1]):
 print(ERROR("Specified file not exist"))

#####################################################################################
# List inventories in case user didnt specify inventory option
if not options.inventory:
  lsdir(inventories_base, inventories)  #List inventories dir to inventories array
  header("Select inventory")            #Header message
  for inventory in inventories:         #Print avaible options
    if inventory is not None:
        print(str(inventories.index(inventory)) + ") " + bcolors.OKGREEN + inventory + bcolors.ENDC + "\n")

  #Assigne default inventory as first item in list if doesnot provided in conf file
  if default_inventory == None:
    default_inventory = inventories[1]
  default_index = inventories.index(default_inventory)

  #Seletc inventory based on user input or default if input is empty
  inventory = inventories[int(raw_input(bcolors.HEADER + "Default(" + bcolors.GREY + default_inventory + bcolors.HEADER + "):" + bcolors.ENDC + "\n") or default_index )] + "/"

#In case user did specify inventory option
elif options.inventory:
    inventory = options.inventory + "/"
    # Directory not exist error
    if not os.path.isdir(inventories_base + inventory):
      print(ERROR("There is no such directory "  + inventory))

    # Directory is empty error
    elif len(os.listdir(inventories_base + inventory)) == 0:
      print(ERROR("Specified direcotry (" + inventory + ") is empty"))

#####################################################################################
# List groups if user didnt specify grop option
if not options.group:
  lsdir(inventories_base + inventory, groups)  #List inventories dir to inventories array
  header("Select group")                                          #Header message
  for group in groups:
   if group is not None:
    print(str(groups.index(group)) + ") " + bcolors.OKGREEN + group + bcolors.ENDC + "\n")

  #Assigne default group as first item in list if doesnot provided in conf file
  if default_group == None:
    default_group = inventories[1]
  default_index = groups.index(default_group)

  #Seletc Group based on user input or default if input is null
  group = groups[int(raw_input(bcolors.HEADER + "Default(" + bcolors.GREY + default_group + bcolors.HEADER + "):" + bcolors.ENDC + "\n") or default_index)] + "/"

#In case user did specify group option
elif options.group:
    group = options.group + "/"
    # Directory not exist error
    if not os.path.isdir(inventories_base + inventory + group):
      print(ERROR("There is no such directory "  + inventory + group))

    # Directory is empty error
    elif len(os.listdir(inventories_base + inventory)) == 0:
      print(ERROR("Specified direcotry (" + inventory + ") is empty"))


#####################################################################
#Dry run (user input)
if not options.drymode:
  header("Run playbook in Dry run")
  while checkmode not in ("y", "n"):
    checkmode = raw_input( bcolors.HEADER + "Y/N | Default(" + bcolors.GREY + "y" + bcolors.HEADER + "):" + bcolors.ENDC + "\n").lower() or "y"
    if checkmode not in ("y", "n"):
      print("Please enter y or n.")
  if checkmode == "y":
    check_option = " --check"
  else:
    check_option = ""
#Dry run (option)
elif options.drymode:
  if options.drymode.lower() not in ("y", "n"):
    ERROR("Provide Y or N with dry run option")
  elif options.drymode.lower() == "y":
    check_option = " --check"
  elif options.drymode.lower() == "n":
    check_option = ""

#####################################################################
# Run playbook
os.system('ansible-playbook ' + sys.argv[1] + ' -e inventory_name=' + inventory.translate(None, '/') + ' -e repo_base_path=' + os.getcwd() + ' ' + environment +' -i ' + inventories_base + inventory + group + check_option + arguments)
# endregion
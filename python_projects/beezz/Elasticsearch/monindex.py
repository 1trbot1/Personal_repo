#!/usr/bin/env python
# region [ about ]
# -*- coding: utf-8 -*-
#########################################################################
#                          ______              __
#   /'\_/`\                /\__  _\            /\ \                  
#  /\      \    ___     ___\/_/\ \/     ___    \_\ \     __   __  _  
#  \ \ \__\ \  / __`\ /' _ `\ \ \ \   /' _ `\  /'_` \  /'__`\/\ \/'\ 
#   \ \ \_/\ \/\ \L\ \/\ \/\ \ \_\ \__/\ \/\ \/\ \L\ \/\  __/\/>  </ 
#    \ \_\\ \_\ \____/\ \_\ \_\/\_____\ \_\ \_\ \___,_\ \____\/\_/\_\
#     \/_/ \/_/\/___/  \/_/\/_/\/_____/\/_/\/_/\/__,_ /\/____/\//\/_/ v1.0
#
#========================================================================
# Monindex program made to monitor and log Elasticsearch indexes update
# frequency and usage.
# ----
# All stdout writen to /var/log/monindex.log
# All data writen to /var/log/elasticsearch/indexes.status file.  
# ----
#========================================================================
# Install prerequisites:
# apt install python-pip
# pip install configparser elasticsearch
# endregion
#########################################################################
# region [ import ]
from optparse import OptionParser
import os, sys, subprocess, configparser, signal, re
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import json
#endregion
#########################################################################
# region [ vars ]
# ===============
#
# Set OptionParser as variable to make it usage more easy.
# =======================================================
parser = OptionParser()

# Operators definition
# =======================================================
parser.add_option("-s", dest="elk_server", metavar="Elastic Server", help="Elasticsearch IP/FQDN")
(options, args) = parser.parse_args()

# Elasticsearch connection variable(using -e argumen as elasticsearch server address)
# =======================================================
es = Elasticsearch(options.elk_server)

# Time and date variables
# =======================================================
now = datetime.now()
utc = datetime.utcnow()
# List of all indexes
# =======================================================
names = es.indices.get_alias("*")

# Regex filters
# =======================================================
phlr_regex_filter = re.compile(r'phlr-\w+-.*' + str('%02d' %now.year) + "." + str('%02d' %now.month))
rf_regex_filter = re.compile(r'rf-' + str('%02d' % now.year) + "." + str('%02d' % now.month) + '-\w+')
cg_regex_filter = re.compile(r'cg-events-'+ str('%02d' % now.year) + "." + str('%02d' % now.month) +'-\w+')

# Check if log directory exist and set file's path variables
log_dir = "/var/log/elasticsearch/"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
status = open("/var/log/elasticsearch/indexes.status", "w+")
log = open("/var/log/elasticsearch/monindex.log", "w+")

# Log variables
counter = 0
outdated_counter = 0 
server = options.elk_server
# endregion
#########################################################################
# region [ functions ]
# =====================
#
# indexes function: listing and filtering indexes on elasticsearch server to "selected_files" list 
# ========================================================================
def indexes():
        selected_files = list(filter(phlr_regex_filter.search, names)) + list(filter(rf_regex_filter.search, names)) + list(filter(cg_regex_filter.search, names))
        return selected_files


# endregion
#########################################################################
# region [ code ]
   #------------------------------------------------------------------------
   # region [ query ]
# For indec in list recived from indexes function
for indec in indexes():
   # Queried indexes counter(log)
   counter +=1
   # Connect to elasticsearch and search for indec from list, sort result by timestamp and select recent one hit
   res = es.search(index=indec , body={"query": {"match_all": {}},"size": 1,"sort": [{"@timestamp": {"order": "desc"}}]})
   # Retrieve hit information from elasticsearch query and store it as "doc" array 
   for doc in res['hits']['hits']:
       # last hit time variable takes index hit timestamp and add to it 3 hours to make it actual to local time
       last_hit = datetime.strptime(doc['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=3)
       # hit id variable
       hit_id = doc['_id']
       # last update variable represents delta between local time and last indec hit timestamp
       last_update = datetime.strptime(str(utc), "%Y-%m-%d %H:%M:%S.%f") - (datetime.strptime(doc['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"))
       # define index status 
       if last_update > timedelta(hours=1):
          index_status="Outdated"
          outdated_counter +=1
       else:
          index_status = "Updated"
       # Write index status to file 
       status.write('\r\n=========================================================================\r\n' +
                  'Index name : ' + indec + '\r\n' 
                  'Hit ID: ' + hit_id + '\r\n' + 
                  'Last hit time: ' + last_hit.strftime("%Y-%m-%d %H:%M:%S") + '\r\n' +
                  'Index status: ' + index_status + '\r\n'
                  )
#Close file when done
status.close()
# endregion
   #------------------------------------------------------------------------
   # region [ log ]
log.write(
     'Last run : ' + datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S") + ' \r\n'
     'Elasticsearch IP/FQDN used: ' + str(server) + '\r\n'
     'Total indexes quered :' + str(counter) + ' \r\n'
     'Total outdated indexes : ' + str(outdated_counter) + '\r\n'
)
log.close()
# endregion
# endregion

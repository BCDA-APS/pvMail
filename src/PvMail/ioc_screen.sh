#!/bin/sh

# run the EPICS soft IOC in a detached screen session

/usr/bin/screen -d -m ./ioc_run.sh

# start the IOC in a screen session
#  type:
#   screen -r   to start interacting with the IOC command line
#   ^a-d        to stop interacting with the IOC command line
#   ^c          to stop the IOC

#!/bin/sh
################################################################################
################################################################################
# Name:   bandwUsageByMac.sh
# Usage:  bandwUsageByMac.sh [yamon data folder] [mac] [hour|day]
# Created:  2013-10-17
# Last Modified:
# Copyright 2009, Victor Mendonca - http://wazem.org
# License: Released under the terms of the GNU GPL license
################################################################################
################################################################################

#-------------------------------------------------------------------------------
# Sets variables
#-------------------------------------------------------------------------------

RUN_FOLDER="$1" # Usually /opt/YAMON/data
MAC="$2"
MODE="$3"
USAGE="Usage: bandwUsageByMac.sh [yamon data folder] [mac] [hour|day]
"
HOUR=$(date +%H)
DATE=$(date +%d-%m-%Y)
YESTERDAY=$(awk -v days="-1" 'BEGIN{print \
strftime("%d",systime()+(days*86400))}')
LAST_HOUR=$(awk -v hour="-1" 'BEGIN{print \
strftime("%H",systime()+(hour*3600))}')

# Change this as needed
SUBJECT="DD-WRT Usage"
MAIL_FROM=""
MAIL_TO=""
MAIL_FROM_NAME=""
DAILY_LIMIT="1024"
HOUR_LIMIT="250"
export LD_LIBRARY_PATH=""

#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------

SendMail () {
## Example command
# echo "$VAR1" | msmtp -C msmtprc user@domain.com

## Example Body
#To: user@domain.com
#FROM: router@home.com
#Subject: DD-WRT - Usage
#This is a test.
#Ciao

MAIL="To: $MAIL_TO
FROM: $MAIL_FROM_NAME
Subject: $SUBJECT
$BODY"

echo "$MAIL" | msmtp -C /jffs/etc/msmtprc $MAIL_TO
}


CalcMB () {
echo "scale=2;(${1}*9.5367)/10000000" | bc
}


## => Daily Usage <= ##
getDayUsage () {
LOG_TOTL=$(ls -tr *mac_data.html | tail -1)
if [ "x$LOG_TOTL" = "x" ] ; then
  echo "Could not find daily usage file"
  exit 1
fi

#-- Daily download
DOWNLOAD_TOTAL=$(grep -i "${MAC}.*${YESTERDAY}$" ${LOG_TOTL} | awk -F, '{print $3}')
if [ "x$DOWNLOAD_TOTAL" = "x" ] ; then
  exit 0
fi
DOWNLOAD_TOTAL=$(CalcMB ${DOWNLOAD_TOTAL})

#-- Daily upload
UPLOAD_TOTAL=0
UPLOAD_TOTAL=$(grep -i "${MAC}.*${YESTERDAY}$" ${LOG_TOTL} | awk -F, '{print $4}')
UPLOAD_TOTAL=$(echo "scale=2;(${UPLOAD_TOTAL}*9.5367)/10000000" | bc)
DAILY_TOTAL=$(echo ${DOWNLOAD_TOTAL} + ${UPLOAD_TOTAL} | bc)
if [[ $(echo "$DAILY_TOTAL $DAILY_LIMIT" | awk '{if ($1 > $2) print "1"; else print "0";}') -eq 1 ]] ; then
  BODY="
Total day usage has gone over limit of ${DAILY_LIMIT}MB

DOWN: ${DOWNLOAD_TOTAL}MB UP: ${UPLOAD_TOTAL}MB
TOTAL: ${DAILY_TOTAL}MB"
  SendMail
else
  echo "Usage ok"
fi

echo "TOTAL - DOWN: $DOWNLOAD_TOTAL UP: $UPLOAD_TOTAL"
}


## => Hour Usage <= ##
getHourUsage () {
LOG_HOUR="${DATE}-hourly_data.html"
if [ "x$LOG_HOUR" = "x" ] ; then
  echo "Could not find hour usage file"
  exit 1
fi

#-- Hourly download
DOWNLOAD_HOUR=$(grep -i "${MAC}.*${LAST_HOUR}$" ${LOG_HOUR} | awk -F, '{print $3}')
if [ "x$DOWNLOAD_HOUR" = "x" ] ; then
  echo "No hourly file"
  exit 0
fi
DOWNLOAD_HOUR=$(echo "scale=2;(${DOWNLOAD_HOUR}*9.5367)/10000000" | bc)

#-- Hourly upload
UPLOAD_HOUR=$(grep -i "${MAC}.*${LAST_HOUR}$" ${LOG_HOUR} | awk -F, '{print $4}')
UPLOAD_HOUR=$(echo "scale=2;(${UPLOAD_HOUR}*9.5367)/10000000" | bc)

HOUR_TOTAL=$(echo ${DOWNLOAD_HOUR} + ${UPLOAD_HOUR} | bc)
if [[ $(echo "$HOUR_TOTAL $HOUR_LIMIT" | awk '{if ($1 > $2) print "1"; else print "0";}') -eq 1 ]] ; then
  BODY="
Total hour usage has gone over limit of ${HOUR_LIMIT}MB

DOWN: ${DOWNLOAD_HOUR}MB UP: ${UPLOAD_HOUR}MB
TOTAL: ${HOUR_TOTAL}MB"
  SendMail
else
  echo "Usage ok"
fi

echo "Hour - DOWN: $DOWNLOAD_HOUR UP: $UPLOAD_HOUR"
}

#-------------------------------------------------------------------------------
# Starts script
#-------------------------------------------------------------------------------

if [[ $# -ne 3 ]] ; then
  echo $USAGE
  exit 1
fi

if [[ $(cd "$RUN_FOLDER" 2> /dev/null ; echo $?) -eq 0 ]] ; then
  cd "$RUN_FOLDER"
else
  echo "yamon data folder could not be found"
  exit 1
fi

case $MODE in
 day) getDayUsage ;;
 hour) getHourUsage ;;
 *) echo "$USAGE"
    exit 1 ;;
esac

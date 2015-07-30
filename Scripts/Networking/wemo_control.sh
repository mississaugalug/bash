#!/bin/bash

################################################################################
################################################################################
# Name:          wemo_control.sh
# Usage:         [IP] [ON|OFF|GETSTATE|GETSIGNALSTRENGTH|GETFRIENDLYNAME]
# Description:   
# Created:       2015-07-30
# Last Modified: 
# Copyright 2014, Victor Mendonca - http://wazem.org
# License: Released under the terms of the GNU GPL license v3
################################################################################
################################################################################

#-------------------------------------------------------------------------------
# Sets variables
#-------------------------------------------------------------------------------

USAGE="wemo_control.sh [IP|network] [on|off|getstate|getsignal|getname|find]"

if [[ $# -ne 2 ]] ; then
  echo "$USAGE"
  exit 0
fi

IP="$1"
CMD="$2"


#-------------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------------

getPort () {
  PORTTEST=$(curl -s "$IP":49152 | grep "404")

  if [ "$PORTTEST" = "" ] ; then
    PORT=49153
  else
    PORT=49152
  fi
}

turnON () {
getPort
curl -0 -A '' -X POST -H 'Accept: ' -H \
'Content-type: text/xml; charset="utf-8"' -H \
"SOAPACTION: \"urn:Belkin:service:basicevent:1#SetBinaryState\"" --data \
'<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>1</BinaryState></u:SetBinaryState></s:Body></s:Envelope>' \
-s http://$IP:$PORT/upnp/control/basicevent1 | grep "<BinaryState" | cut -d">" \
-f2 | cut -d "<" -f1 | sed 's/0/OFF/g' | sed 's/1/ON/g'
}

turnOFF () {
getPort
curl -0 -A '' -X POST -H 'Accept: ' -H \
'Content-type: text/xml; charset="utf-8"' -H \
"SOAPACTION: \"urn:Belkin:service:basicevent:1#SetBinaryState\"" --data \
'<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>0</BinaryState></u:SetBinaryState></s:Body></s:Envelope>' \
-s http://$IP:$PORT/upnp/control/basicevent1 | grep "<BinaryState"  | cut \
-d">" -f2 | cut -d "<" -f1 | sed 's/0/OFF/g' | sed 's/1/ON/g'
}

getName () {
getPort
curl -0 -A '' -X POST -H 'Accept: ' -H \
'Content-type: text/xml; charset="utf-8"' -H \
"SOAPACTION: \"urn:Belkin:service:basicevent:1#GetFriendlyName\"" --data \
'<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:GetFriendlyName xmlns:u="urn:Belkin:service:basicevent:1"><FriendlyName></FriendlyName></u:GetFriendlyName></s:Body></s:Envelope>' \
-s http://$IP:$PORT/upnp/control/basicevent1 |     grep "<FriendlyName" | cut \
-d">" -f2 | cut -d "<" -f1
}

getState () {
getPort
curl -0 -A '' -X POST -H 'Accept: ' -H \
'Content-type: text/xml; charset="utf-8"' -H \
"SOAPACTION: \"urn:Belkin:service:basicevent:1#GetBinaryState\"" \
--data '<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:GetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>1</BinaryState></u:GetBinaryState></s:Body></s:Envelope>' \
-s http://$IP:$PORT/upnp/control/basicevent1 | grep "<BinaryState"  | cut \
-d">" -f2 | cut -d "<" -f1 | sed 's/0/OFF/g' | sed 's/1/ON/g'
}

getSigStrength () {
getPort
curl -0 -A '' -X POST -H 'Accept: ' -H \
'Content-type: text/xml; charset="utf-8"' -H "SOAPACTION: \"urn:Belkin:service:basicevent:1#GetSignalStrength\"" \
--data '<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:GetSignalStrength xmlns:u="urn:Belkin:service:basicevent:1"><GetSignalStrength>0</GetSignalStrength></u:GetSignalStrength></s:Body></s:Envelope>' \
-s http://$IP:$PORT/upnp/control/basicevent1 | grep "<SignalStrength"  | cut \
-d">" -f2 | cut -d "<" -f1
}

findDevices () {
which nmap > /dev/null || \
  ( echo "nmap is not installed and it's needed for this option" ; exit 1 )

echo "$IP" | grep -q '\*'
if [[ $? -ne 0 ]] ; then
  echo "You need to provide a network for this option. It should be similar \
to 1.1.1.*"
  exit 1
fi

echo "Finding. This may take a while..."
DEVICES=$(nmap -p 49153 --open "$IP" | grep 'scan report for' | awk '{print $5}')
if [ "$DEVICES" ] ; then
  echo "IP           NAME"
  echo "---------------------"
  for DEVICE in $DEVICES ; do
    IP="$DEVICE"
    echo "$DEVICE $(getName )"
  done
else
  echo "Did not find any devices"
fi
}

#-------------------------------------------------------------------------------
# Starts script
#-------------------------------------------------------------------------------

case "$CMD" in
  on) turnON ;;
  off) turnOFF ;;
  getstate) getState ;;
  getsignal) getSigStrength ;;
  getname) getName ;;
  find) findDevices ;;
  *) echo "Unknown option" && exit 1 ;;
esac

exit 0
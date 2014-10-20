#!/bin/bash

USER=
PASSWD=
FQDN=

NETFACE=$(/bin/netstat -i | egrep -v '(^Kernel|^Iface|^lo|^tun)' | awk \
'{print $1}' | tail -1)
CURRENT_LIP=$(/sbin/ifconfig $NETFACE | sed -En \
's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')

curl "http://${USER}:${PASSWD}@dynupdate.no-ip.com/nic/update?hostname=${FQDN}&myip=$CURRENT_LIP"

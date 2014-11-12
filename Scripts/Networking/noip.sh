#!/bin/bash
################################################################################
################################################################################
# Name:          noip.sh
# Usage:
# Description:   Updates noip FQDN (same as noip2)
# Created:
# Last Modified:
# Copyright 2009, Victor Mendonca - http://wazem.org
# License: Released under the terms of the GNU GPL license
################################################################################
################################################################################

USER=""
PASSWD=""
FQDN=""

NETFACE=$(/bin/netstat -i | egrep -v '(^Kernel|^Iface|^lo|^tun)' | awk \
'{print $1}' | tail -1)
CURRENT_LIP=$(/sbin/ifconfig $NETFACE | sed -rn \
's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')

curl "http://${USER}:${PASSWD}@dynupdate.no-ip.com/nic/update?hostname=${FQDN}&myip=$CURRENT_LIP"

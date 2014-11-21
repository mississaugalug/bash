#!/system/bin/sh
################################################################################
################################################################################
# Name:          noip-android.sh
# Usage:
# Description:   Updates noip FQDN with wifi from an adroid device
# Created:
# Last Modified:
# Copyright 2009, Victor Mendonca - http://wazem.org
# License: Released under the terms of the GNU GPL license
################################################################################
################################################################################

USERNAME=""
PASSWORD=""
FQDN=""

WLAN_IP=$(ip addr list wlan0 | grep 'inet ' | awk '{print $2}' | awk -F/ '{print $1}')

curl "http://${USERNAME}:${PASSWORD}@dynupdate.no-ip.com/nic/update?hostname=${FQDN}&myip=${WLAN_IP}"

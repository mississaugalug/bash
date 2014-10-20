#!/bin/bash
#-------------------------------------------------------
# Script:  unplash-desktop.sh
# Version: 1.0
# Description:
# Parameters:
# Created by:  Victor Mendonça
# Create Date: 2014-08-25
#-------------------------------------------------------
# To do:       
#-------------------------------------------------------
# Details:
#
#-------------------------------------------------------
# Modification History
#-------------------------------------------------------
# NAME -    DATE    - DESCRIPTION
# V.M. - 2014-07-14 - Changed for new wireless card
#-------------------------------------------------------

# Checks that connection to internet is ok
ping -q -c 2 -w 5 unsplash.com > /dev/null 2>&1
if [[ $? -ne 0 ]] ; then
  exit 1
fi

# Creates the folder if needed
if [ !  -f "${HOME}/Pictures/Unsplash" ] ; then
  mkdir -p ${HOME}/Pictures/Unsplash
fi


#-------------------------------------------------------------------------------
# Work
#-------------------------------------------------------------------------------

rm -rf ${HOME}/Pictures/Unsplash/*.jpg

cd ${HOME}/Pictures/Unsplash

TODAYS_PHOTO_URL=$(wget -q http://unsplash.com/ -O - | grep jpg | head -1 | \
awk -F\" '{print $2}')
TODAYS_PHOTO=$(echo $TODAYS_PHOTO_URL | awk -F/ '{print $4}')

if [ "$TODAYS_PHOTO_URL" ] ; then
  wget -q $TODAYS_PHOTO_URL -O ${TODAYS_PHOTO}.jpg
else
  exit 1
fi

if [ -f ${HOME}/Pictures/Unsplash/${TODAYS_PHOTO}.jpg ] ; then
  gsettings set org.cinnamon.desktop.background picture-uri \
"file://${HOME}/Pictures/Unsplash/${TODAYS_PHOTO}.jpg"
else
  exit 1
fi

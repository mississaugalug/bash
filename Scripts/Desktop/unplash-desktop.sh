#!/bin/bash
################################################################################
################################################################################
# Name:          unsplash-desktop.sh
# Usage:
# Description:   Downloads 10 new wallpapers from http://unsplash.com/
# Created:       2014-08-25
# Last Modified: 2014-10-21
# Copyright 2009, Victor Mendonca - http://wazem.org
# License: Released under the terms of the GNU GPL license
################################################################################
################################################################################

# Creates the folder if needed
if [ ! -f "${HOME}/Pictures/Unsplash" ] ; then
  mkdir -p ${HOME}/Pictures/Unsplash/.var
fi

# Gets OS
DISTRO=$(lsb_release -si)
UNSPLASH_DIR="${HOME}/Pictures/Unsplash"
DATE=$(date +%Y%m%d)
CURRENT="${UNSPLASH_DIR}/.var/current"
WEEKLY=${UNSPLASH_DIR}/.var/weekly

#-------------------------------------------------------------------------------
# Function
#-------------------------------------------------------------------------------

GetNewPhotos () {
# Checks that connection to internet is ok
# ping -q -c 2 -w 5 google.com > /dev/null 2>&1
# if [[ $? -ne 0 ]] ; then
#   echo "It looks like you might not be online."
#   exit 1
# fi

# Checks that unsplash is up
wget -q http://unsplash.com/ -O - > /dev/null
if [[ $? -ne 0 ]] ; then
  echo "It looks like Unsplash is down."
  exit 1
fi

# Moves old photos to another dir if they exist
ll ${UNSPLASH_DIR}/*.jpg > /dev/null 2>&1
if [[ $? -eq 0 ]] ; then
  mkdir -p ${UNSPLASH_DIR}/Used
  mv ${UNSPLASH_DIR}/*.jpg ${UNSPLASH_DIR}/Used/.
fi

# Gets URLs for this weeks photos
THIS_WEEKS_PHOTOS=$(wget -q http://unsplash.com/ -O - | grep jpg | grep -v \
twitter | awk -F= '{print $2}' | sed 's/\?q//' | sed 's/"//')

# Downloads this weeks photos
if [ "$THIS_WEEKS_PHOTOS" ] ; then
  for PHOTO in $THIS_WEEKS_PHOTOS ; do
    cd ${UNSPLASH_DIR}
    wget -q $PHOTO
  done
else
  echo "Could not get string for this weeks photos"
  exit 1
fi

# Makes sure all files have lower case jpg
cd ${UNSPLASH_DIR}
rename 'y/*.JPG/*.jpg/' *.JPG

SetNewPhoto

# Set new photos file
touch ${WEEKLY}
}

SetNewPhoto () {
# Sets photo for today
cd ${UNSPLASH_DIR}
TODAYS_PHOTO=$(ls -t *.jpg | head -1)

# Sets background based on distro and desktop
if [ -f "${UNSPLASH_DIR}/${TODAYS_PHOTO}" ] ; then
  case $DISTRO in
    Ubuntu)
        gsettings set org.gnome.desktop.background picture-uri "file://${UNSPLASH_DIR}/${TODAYS_PHOTO}"
        ;;
    LinuxMint)
        # Let's find out what desktop version
        if [ -f /etc/linuxmint/info ] ; then
          DESKTOP=$(grep DESKTOP /etc/linuxmint/info)
          case $DESKTOP in
            Gnome)
              gsettings set org.cinnamon.desktop.background picture-uri "file://${UNSPLASH_DIR}/${TODAYS_PHOTO}"
              ;;
            MATE)
              mateconftool-2 -t string -s /desktop/mate/background/picture_filename "${UNSPLASH_DIR}/${TODAYS_PHOTO}"
              ;;
          esac
        fi
        ;;
    *)
        echo "I don't know what distro you are running"
        exit 1
        ;;
  esac
  echo "$DATE $TODAYS_PHOTO" > $CURRENT
else
  echo "No files in the directory"
  exit 1
fi
}

ChangeByDay () {
# Checks that we already did not run today
if [ ! -f $CURRENT ] ; then
  echo "Something went wrong"
  exit 1
elif [[ $(cat $CURRENT | awk '{print $1}') == $DATE ]] ; then
  echo "Already ran today"
  exit 0
fi

if [[ $(ls ${UNSPLASH_DIR}/*.jpg | wc -l) -le 1 ]] ; then
  echo "Already on last photo"
  exit 0
fi

CURRNT_PHOTO=$(cat $CURRENT | awk '{print $2}')
mkdir -p ${UNSPLASH_DIR}/Used
mv ${UNSPLASH_DIR}/$CURRNT_PHOTO ${UNSPLASH_DIR}/Used/.
SetNewPhoto
}

#-------------------------------------------------------------------------------
# Work
#-------------------------------------------------------------------------------

if [ ! -f ${UNSPLASH_DIR}/.var/weekly ] ; then
    GetNewPhotos
elif [ -f ${UNSPLASH_DIR}/.var/weekly ] ; then
  CHECK_DATE=$(find ${UNSPLASH_DIR}/.var -name index -mtime +10)
  if [ "$CHECK_DATE" ] ; then
    GetNewPhotos
  else
    ChangeByDay
  fi
fi

exit 0

#!/bin/bash

export COWPATH=/home/victor/bin/lib/cowpath/
#cowsay $(fortune -s)
cowsay -f $(ls $(cowsay -l | awk 'NR==1 {print $4}' | sed 's/://') | \
shuf -n1) $(fortune -n 80 -s)

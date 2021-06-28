#! /bin/bash

Srv=smil.cmm.mines-paristech.fr
Dir=/export/vhosts/smil.cmm/htdocs/benchmark

ResDir=$(echo $(hostname) | awk -F. '{print $1}')

rsync -aq --delete $ResDir ${Srv}:${Dir}/
rsync -aq --delete images  ${Srv}:${Dir}/

[ -f README.txt ] && rsync -aq --delete README.txt  ${Srv}:${Dir}/


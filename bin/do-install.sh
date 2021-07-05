#! /bin/bash

Srv=smil.cmm.mines-paristech.fr
Dir=/export/vhosts/smil.cmm/htdocs/benchmark

ResDir=$(echo $(hostname) | awk -F. '{print $1}')

rsync -av --delete $ResDir ${Srv}:${Dir}/
#rsync -av --delete images  ${Srv}:${Dir}/

#[ -f README.txt ] && rsync -av --delete README.txt  ${Srv}:${Dir}/


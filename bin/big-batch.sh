#! /bin/bash

DOIT=no
for opt in $*
do
  [ "$opt" == "yes" ] && DOIT=yes
done

imBin=""
imBin+=" alumine.png"
imBin+=" balls.png"
imBin+=" bubbles_bin.png"
imBin+=" cells.png"
imBin+=" coffee.png"
imBin+=" eutectic.png"
imBin+=" gruyere.png"
imBin+=" hubble_EDF_bin.png"
imBin+=" metal.png"

imGray=""
imGray+=" astronaut.png"
imGray+=" bubbles_gray.png"
imGray+=" hubble_EDF_gray.png"
imGray+=" lena.png"

function doIt()
{
  echo "* Entering doIt : $*"
  type=
  funcs=
  opts=
  for arg in $*
  do
    case $arg in
      bin|gray)
        type=$arg
        ;;
      funcs=*)
        funcs=$arg
        ;;
      nb=*)
        opts+=" $arg"
        ;;
      *)
        ;;
    esac
  done

  [ -z "$type" ] && return  
  Imgs=
  [ "$type" == "bin" ] && Imgs="$imBin"
  [ "$type" == "gray" ] && Imgs="$imGray"
  fn=generic
  [ -n "$funcs" ] && fn=$(echo $funcs | awk -F= '{print $2}')
  for im in $Imgs
  do
    [ -f stopnow ] && break
    printf "  %-4s : %s\n" $type $im
    flock=$(printf "%s-%s-%s.witness" $type $im $fn)
    [ -f var/$flock ] && continue
    [ "$DOIT" == "yes" ] && bin/do-all.sh $type $im "$funcs" "$opts"
    if [ "$DOIT" == "yes" ]
    then
      bin/do-install.sh    
      touch var/$flock
    fi
  done
  echo ""
}

mkdir -p var

# default functions for binary images
doIt bin

# default functions for gray images
doIt gray

# binary images : watershed
doIt bin  funcs=watershed nb=7

# binary images : areaThreshold
doIt bin  funcs=areaThreshold nb=5

# slow functions
doIt gray funcs=areaOpen nb=5
doIt gray funcs=hMinima  nb=7

# doIt gray funcs=hMaxima

exit 0



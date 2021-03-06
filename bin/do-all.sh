#! /bin/bash

Files=

grayFiles="tools.png lena.png astronaut.png hubble_EDF_gray bubbles_gray.png"

grayFuncs="erode open hMaxima hMinima areaOpen"
grayFuncs="erode open hMinima"
grayFuncs="erode open"

binFiles="cells.png gruyere.png alumine.png balls.png"

binFuncs="erode open distance areaThreshold label"
binFuncs="erode open distance label"
binFuncs="erode open label"

Prefix=gray
Files="$grayFiles"
Funcs="$grayFuncs"


Nb=10
Repeat=5

minImSize=256
maxImSize=8192
maxSeSize=8

ResDir=$(echo $(hostname) | awk -F. '{print $1}')

declare -i ti
ti=$(date +%s)
hi=$(date "+%H:%M:%S")

Opt=

for arg in $*
do
  case $arg in
    funcs=*)
      Funcs=$(echo $arg | awk -F= '{print $2}' | sed -e "s/,/ /g")
      ;;
    short|quick|fast)
      Nb=2
      Repeat=2
      ;;
    bin)
      Prefix=bin
      Files="$binFiles"
      Funcs="$binFuncs"
      Opt+=" --binary"
      ;;
    nb=*)
      Nb=$(echo $arg | awk -F= '{print $2}' | sed -e "s/,/ /g")
      ;;
    repeat=*)
      Repeat=$(echo $arg | awk -F= '{print $2}' | sed -e "s/,/ /g")
      ;;
    --*=*)
      Opt+=" $arg"
      ;;
    --*)
      Opt+=" $arg"
      ;;
    *)
      [ -f images/$arg ] && Files="$arg"
      ;;
  esac
done

[ -z "$Files" ] && Files=lena.png

mkdir -p $ResDir

for fname in $Files
do
  echo "  =====> File $fname"
  bname=$(basename $fname .png)
  fout=$(echo $fname | sed s/png/txt/)
  #cp /dev/null $ResDir/$fout
  for f in $Funcs
  do
    echo "  Doing $f"

    declare -i xti
    xti=$(date +%s)
    xhi=$(date "+%H:%M:%S")

    fout=$(echo $fname | sed s/png/txt/)
    fout=${Prefix}-${bname}-${f}.txt
    bin/smil-vs-skimage.py  --image $fname \
                            --function $f \
                            --minImSize=$minImSize \
                            --maxImSize=$maxImSize \
                            --maxSeSize=$maxSeSize \
                            --nb $Nb --repeat $Repeat \
                            $Opt \
                            > $ResDir/$fout

    declare -i xtf
    xtf=$(date +%s)
    declare -i xdt
    xdt=$((xtf - xti))
    xhf=$(date "+%H:%M:%S")

    printf "=> Elapsed time : %d secs\n" $xdt >> $ResDir/$fout
    printf "   Begin        : %s\n" $xhi      >> $ResDir/$fout
    printf "   End          : %s\n" $xhf      >> $ResDir/$fout
  done
done

declare -i tf
tf=$(date +%s)
declare -i dt
dt=$((tf - ti))
hf=$(date "+%H:%M:%S")

printf "=> Elapsed time : %d secs\n" $dt
printf "   Begin        : %s\n" $hi
printf "   End          : %s\n" $hf
printf "\n"

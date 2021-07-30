#! /bin/bash

DoIt=no
DoInstall=no

for opt in $*
do
  case $opt in
    --doit|--run|yes)
      DoIt=yes
      ;;
    --doinstall|--install)
      DoInstall=yes
      ;;
    *)
      ;;
  esac
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
imGray+=" tools.png"

function runIt()
{
  echo "* Entering runIt : $*"
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
      nb=*|repeat=*)
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
    printf "  %-4s : %-30s" $type $im
    flock=$(printf "%s-%s-%s.witness" $type $im $fn)
    [ -f var/$flock ] && printf "done\n" && continue
    printf "to do\n"
    if [ "$DoIt" == "yes" ]
    then
      bin/do-all.sh $type $im "$funcs" "$opts"
      [ "$?" == 0 ] || continue
      touch var/$flock
      [ "$DoInstall" == "yes" ] && bin/do-install.sh
    fi
  done
  echo ""
}

mkdir -p var

# default functions for binary images
runIt bin funcs=erode          repeat=7
runIt bin funcs=open           repeat=7
runIt bin funcs=label          repeat=7
runIt bin funcs=distance       repeat=7
runIt bin funcs=areaThreshold  repeat=7

# default functions for gray images
runIt gray funcs=erode         repeat=7
runIt gray funcs=open          repeat=7
runIt gray funcs=tophat        repeat=7
runIt gray funcs=gradient      repeat=7

# segmentation
runIt gray funcs=segmentation  repeat=7
runIt bin  funcs=segmentation  repeat=7

# slow functions
runIt gray funcs=hMinima       repeat=7
runIt gray funcs=areaOpen      repeat=7

runIt bin  funcs=zhangSkeleton repeat=7
runIt bin  funcs=thinning      repeat=7

exit 0



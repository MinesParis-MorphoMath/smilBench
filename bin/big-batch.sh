#! /bin/bash

DoIt=no
DoInstall=no

for opt in $*
do
  case $opt in
    --doit|yes)
      DoIt=yes
      ;;
    --doinstall)
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
runIt bin funcs=erode          nb=15 repeat=7
runIt bin funcs=open           nb=15 repeat=7
runIt bin funcs=label          nb=15 repeat=7
runIt bin funcs=distance       nb=15 repeat=5
runIt bin funcs=areaThreshold  nb=15 repeat=7

# default functions for gray images
runIt gray funcs=erode         nb=15 repeat=7
runIt gray funcs=open          nb=15 repeat=7
runIt gray funcs=tophat        nb=20 repeat=5

# watershed
runIt gray funcs=watershed     nb=15 repeat=5
runIt bin  funcs=watershed     nb=15 repeat=5


# slow functions
runIt gray funcs=hMinima       nb=5
runIt gray funcs=areaOpen      nb=5

runIt bin  funcs=zhangSkeleton nb=5
runIt bin  funcs=thinning      nb=5 repeat=3

exit 0



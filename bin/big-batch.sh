
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

#
# Simple functions
#
for im in $imBin
do
  echo "Bin   : $im"
  #bin/do-all.sh bin $im
done

for im in $imGray
do
  echo "Gray  : $im"
  #bin/do-all.sh gray $im
done

#
# A little bit heavier
#
for im in $imBin
do
  echo "Bin   : $im"
  #bin/do-all.sh bin funcs=watershed $im
done

for im in $imBin
do
  echo "Bin   : $im"
  #bin/do-all.sh bin funcs=areaThreshold $im nb=5
done

#
#
#
for im in $imGray
do
  echo "Gray  : $im"
  #bin/do-all.sh gray $im funcs=areaOpen nb=5
done

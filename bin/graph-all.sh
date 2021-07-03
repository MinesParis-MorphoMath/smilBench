#! /bin/bash

top=results
dirout=www/images

for dir in $*
do
  banner $dir
  mkdir -p $dirout/$dir

  find $top/$dir -name "*szse.csv" | sort | while read x
  do
    fin=$(basename $x)
 
    echo "========= $fin"; 
    bin/do-graph-times.py \
      --dirin $top/$dir \
      --dirout $dirout/$dir \
      --fin $fin \
      --xscale lin \
      --yscale log \
      --save

    bin/do-graph-times.py \
      --dirin $top/$dir \
      --dirout $dirout/$dir \
      --fin $fin \
      --xscale lin \
      --yscale log \
      --speedup \
      --save   
  done

  find $top/$dir -name "*szim.csv" | sort | while read x
  do
    fin=$(basename $x)
 
    echo "========= $fin"; 
    bin/do-graph-times.py \
      --dirin $top/$dir \
      --dirout $dirout/$dir \
      --fin $fin \
      --xscale log \
      --yscale log \
      --save
    bin/do-graph-times.py \
      --dirin $top/$dir \
      --dirout $dirout/$dir \
      --fin $fin \
      --xscale log \
      --yscale log \
      --speedup \
      --save   
  done
done


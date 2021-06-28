#! /usr/bin/env python3

import sys
import os
import smilPython as sp


def resizeImage(fIm, kmax):
  if not os.path.isfile(fIm):
    print("File not found : ", fIm)
    return
  
  print("* Doing for ", fIm)
  im = sp.Image(fIm)
  imName, _ = os.path.splitext(fIm)
  w = im.getWidth()
  k = 0.5
  for i in range(0, kmax):
    szIm = int(k * w)
    fOut = "{:s}-{:04d}.png".format(imName, szIm)
    print("  {:4.1f} {:5d} {:s}".format(k, szIm, fOut))

    imOut = sp.Image()
    sp.scale(im, k, imOut)
    sp.write(imOut, fOut)
    k *= 2

files = sys.argv[1:]

for f in files:
  resizeImage(f, 7)


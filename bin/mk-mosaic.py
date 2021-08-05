#! /usr/bin/env python3

import sys
import os
import smilPython as sp
import skimage.morphology as skm
import numpy as np
import timeit as tit

nx = 4
ny = 4


def mkMosaic(fin = None, nx = 2, ny = 2):
  imIn = sp.Image(fin)

  w = imIn.getWidth()
  h = imIn.getHeight()

  imOut = sp.Image(imIn)
  imOut.setSize(w * nx, h * ny)

  sp.copyPattern(imIn, 0, 0, w, h, imOut, nx, ny)
  return imOut, w * nx, h * ny

nr = 2

def main(args):
  files = sys.argv[1:]

  for f in files:
    r = 1
    for i in range(1, 10):
      imOut, w, h = mkMosaic(f, r, r)
      imLabel = sp.Image(imOut, 'UINT32')

      ct = tit.Timer(lambda: sp.label(imOut, imLabel, sp.CrossSE()))
      n, t = ct.autorange()
      if t < 1:
        n = int(n / t)
      print("  Running Smil")
      dtsm = ct.repeat(nr, n)
      dtsm = np.array(dtsm) * 1000. / n

      smMax = sp.label(imOut, imLabel, sp.CrossSE())

      imArr = imOut.getNumArray()
      ct = tit.Timer(lambda: skm.label(imArr, connectivity = 1))
      n, t = ct.autorange()
      if t < 1:
        n = int(n / t)
      print("  Running skImage")
      dtsk = ct.repeat(nr, n)
      dtsk = np.array(dtsk) * 1000. / n

      skLabel = skm.label(imArr, connectivity = 1)
      skMax = skLabel.max()

      tsm = dtsm.min()
      tsk = dtsk.min()
      sUp = tsk / tsm
      print("{:3d} - {:6d} {:6d} - {:9.3f} {:9.3f} - {:7.3f} - {:7d} {:7d}".format(i, w, h, tsm, tsk, sUp, smMax, skMax))

      r *= 2


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

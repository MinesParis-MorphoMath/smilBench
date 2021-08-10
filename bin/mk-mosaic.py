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
szTst = 16384

def main(args):
  files = sys.argv[1:]

  for f in files:
    r = 1
    for i in range(1, 7):
      imMosaic, w, h = mkMosaic(f, r, r)
      imTst = sp.Image()
      if False:
        sp.copy(imMosaic, imTst)
      else:
        sp.resize(imMosaic, szTst, szTst, imTst, "closest")
      imLabel = sp.Image(imTst, 'UINT32')

      ct = tit.Timer(lambda: sp.label(imTst, imLabel, sp.CrossSE()))
      n, t = ct.autorange()
      if t < 1:
        n = int(n / t)
      print("* {:8d}".format(w))
      print("  Running Smil")
      dtsm = ct.repeat(nr, n)
      dtsm = np.array(dtsm) * 1000. / n

      smMax = sp.label(imTst, imLabel, sp.CrossSE())

      imArr = imTst.getNumArray()
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

      fmt = "{:3d} - {:6d} {:6d} - {:9.3f} {:9.3f} - {:7.3f} - {:7d} {:7d}"
      print(fmt.format(i, w, h, tsm, tsk, sUp, smMax, skMax))

      r *= 2


if __name__ == '__main__':
    import sys

    pid = os.getpid()
    print("pid : {:d}".format(pid)
    input("Hit enter to continue")

    sys.exit(main(sys.argv))

#! /usr/bin/env python3

import sys
import os
import smilPython as sp
import skimage.morphology as skm
import numpy as np
import timeit as tit

import argparse as ap
import configparser as cp

nx = 4
ny = 4


# -----------------------------------------------------------------------------
#
#
def getCliArgs():
  parser = ap.ArgumentParser()

  parser.add_argument('--debug', help='', action="store_true")
  parser.add_argument('--verbose', help='', action="store_true")

  parser.add_argument('--showpid',
                      help='break to show pid',
                      action='store_true')

  parser.add_argument('--function',
                      default='label',
                      help='function to test',
                      type=str)
  parser.add_argument('--which',
                      default='both',
                      help='which ? both, smil skimage',
                      type=str)
  parser.add_argument('--csv', help='output CSV format', action='store_true')

  parser.add_argument('--repeat', default=7, help='', type=int)
  parser.add_argument('--imsize', default=8192, help='', type=int)
  parser.add_argument('--resize', help='resize image to imsize', action="store_true")

  parser.add_argument('files',
                      metavar='file',
                      type=str,
                      nargs='+',
                      help='image files')

  cli = parser.parse_args()
  return cli


def mkMosaic(fin=None, nx=2, ny=2):
  imIn = sp.Image(fin)

  w = imIn.getWidth()
  h = imIn.getHeight()

  imOut = sp.Image(imIn)
  imOut.setSize(w * nx, h * ny)

  sp.copyPattern(imIn, 0, 0, w, h, imOut, nx, ny)
  return imOut, w * nx, h * ny


def main(cli, args):

  #
  #
  #
  def getNumber(ct):
    n, t = ct.autorange()
    if t < 1:
      n = int(n / t)
    return n

  #
  # L A B E L
  #
  def skLabel(imTst):
    if cli.verbose:
      print("*  Running skImage ({:d}x{:d})".format(w, h))

    imArr = imTst.getNumArray()

    ct = tit.Timer(lambda: skm.label(imArr, connectivity=1))
    n = getNumber(ct)
    dtsk = ct.repeat(nr, n)

    dtsk = np.array(dtsk) * 1000. / n
    skLabel = skm.label(imArr, connectivity=1)

    skMax = skLabel.max()
    tsk = dtsk.min()
    return tsk, skMax

  def smLabel(imTst):
    if cli.verbose:
      print("*  Running Smil ({:d}x{:d})".format(w, h))

    imLabel = sp.Image(imTst, 'UINT32')

    ct = tit.Timer(lambda: sp.label(imTst, imLabel, sp.CrossSE()))
    n = getNumber(ct)
    dtsm = ct.repeat(nr, n)

    dtsm = np.array(dtsm) * 1000. / n

    smMax = sp.label(imTst, imLabel, sp.CrossSE())
    tsm = dtsm.min()

    return tsm, smMax

  #
  # O P E N
  #
  def skOpen(imTst):
    if cli.verbose:
      print("*  Running skImage ({:d}x{:d})".format(w, h))

    imArr = imTst.getNumArray()

    se = skm.selem.diamond(1)
    ct = tit.Timer(lambda: skm.opening(imArr, se))
    n = getNumber(ct)
    dtsk = ct.repeat(nr, n)

    dtsk = np.array(dtsk) * 1000. / n

    skMax = 0
    tsk = dtsk.min()
    return tsk, skMax

  def smOpen(imTst):
    if cli.verbose:
      print("*  Running Smil ({:d}x{:d})".format(w, h))

    se = sp.CrossSE()
    imOut = sp.Image(imTst)

    ct = tit.Timer(lambda: sp.open(imTst, imOut, se))
    n = getNumber(ct)
    dtsm = ct.repeat(nr, n)

    dtsm = np.array(dtsm) * 1000. / n

    smMax = 0
    tsm = dtsm.min()

    return tsm, smMax

  #
  # M A I N
  #
  #files = sys.argv[1:]
  files = cli.files

  nr = cli.repeat

  for f in files:
    r = 1
    for i in range(0, 8):
      imMosaic, w, h = mkMosaic(f, r, r)
      imTst = sp.Image()
      if cli.resize:
        sp.resize(imMosaic, cli.imsize, cli.imsize, imTst, "closest")
      else:
        sp.copy(imMosaic, imTst)

      #
      # skimage
      #
      dtsk = np.array([])
      skMax = 0
      tsk = 0
      if cli.which in ['skimage', 'both']:
        if cli.function == 'label':
          tsk, skMax = skLabel(imTst)
        if cli.function == 'open':
          tsk, skMax = skOpen(imTst)

      #
      # smil
      #
      dtsm = np.array([])
      smMax = 0
      tsm = 0
      if cli.which in ['both', 'smil']:
        if cli.function == 'label':
          tsm, smMax = smLabel(imTst)
        if cli.function == 'open':
          tsm, smMax = smOpen(imTst)

      #
      # the end
      #
      if cli.which in ['both']:
        sUp = tsk / tsm
      else:
        sUp = 0

      fmt = "{:3d} - {:6d} {:6d} - {:9.3f} {:9.3f} - {:7.3f} - {:7d} {:7d}"
      print(fmt.format(i, w, h, tsm, tsk, sUp, smMax, skMax))

      r *= 2


if __name__ == '__main__':
  import sys

  cli = getCliArgs()
  if cli.showpid:
    pid = os.getpid()
    print("pid : {:d}".format(pid))
    input("Hit enter to continue")

  sys.exit(main(cli, sys.argv))

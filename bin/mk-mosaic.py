#! /usr/bin/env python3

import sys
import os
import gc
import time

import smilPython as sp
import skimage.morphology as skm
from skimage.filters import rank
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import skimage.segmentation as sks

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
                      help='function to test (default : label)',
                      type=str)
  parser.add_argument('--which',
                      default='both',
                      help='which ? both, smil skimage (default : both)',
                      type=str)
  parser.add_argument('--csv', help='output CSV format', action='store_true')

  parser.add_argument('--repeat', default=7, help='', type=int)
  parser.add_argument('--imsize',
                      default=8192,
                      help='work image size (default : 8192)',
                      type=int)
  parser.add_argument('--resize',
                      help='resize image to imsize',
                      action="store_true")

  parser.add_argument('--ri',
                      default=1,
                      help='initial image size multiplier (default : 1)',
                      type=int)
  parser.add_argument('--nr',
                      default=1,
                      help='number of rounds (default : 1)',
                      type=int)

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
    if t < 2:
      n = int(2 * n / t)
    return n

  #
  # L A B E L
  #
  def skLabel(imTst):
    if cli.verbose:
      print("*  Running skImage ({:d}x{:d})".format(w, h))

    imArr = imTst.getNumArray().copy()

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

    imArr = imTst.getNumArray().copy()

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
  # watershed
  #
  def skWatershed(imTst):
    wsData = {
      'astronaut.png': [2, 5],
      'bubbles_gray.png': [1, 3],
      'hubble_EDF_gray.png': [1, 2],
      'lena.png': [3, 5],
      'tools.png': [1, 3],
    }

    if cli.verbose:
      print("*  Running skImage ({:d}x{:d})".format(w, h))

    imArr = imTst.getNumArray().copy()

    fin = 'lena.png'
    if fin in wsData:
      szg, szo = wsData[fin]
    else:
      szg, szo = 3, 5
    imIn = imArr.astype('uint8')
    denoised = rank.median(imIn, skm.disk(szo))
    markers = rank.gradient(denoised, skm.disk(szg)) < 10
    markers = ndi.label(markers)[0]
    gradient = rank.gradient(denoised, skm.disk(2))

    ct = tit.Timer(lambda: watershed(gradient, markers))
    n = getNumber(ct)
    dtsk = ct.repeat(repeat=nr, number=n)

    dtsk = np.array(dtsk) * 1000. / n

    skMax = 0
    tsk = dtsk.min()

    return tsk, skMax

  def smWatershed(imTst):
    wsData = {
      'astronaut.png': [10, 0],
      'bubbles_gray.png': [10, 5],
      'hubble_EDF_gray.png': [5, 1],
      'lena.png': [5, 0],
      'tools.png': [10, 1],
    }
    if cli.verbose:
      print("*  Running Smil ({:d}x{:d})".format(w, h))

    se = sp.CrossSE()
    fin = 'lena.png'
    if not fin in wsData:
      h, sz = wsData[fin]
    else:
      h, sz = 10, 1
    if sz > 0:
      sp.open(imTst, imTst, sp.HexSE(sz))
    imGrad = sp.Image(imTst)
    imMin = sp.Image(imTst)
    sp.gradient(imTst, imGrad, se)
    sp.hMinima(imGrad, 10, imMin, se)
    imLabel = sp.Image(imTst, 'UINT32')
    sp.label(imMin, imLabel)
    imOut = sp.Image(imTst)
    ct = tit.Timer(lambda: sp.watershed(imGrad, imLabel, imOut, se))
    n = getNumber(ct)
    dtsm = ct.repeat(repeat=nr, number=n)

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
    r = cli.ri
    for i in range(0, cli.nr):
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
        if cli.function == 'watershed':
          tsk, skMax = skWatershed(imTst)
        gc.collect()

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
        if cli.function == 'watershed':
          tsm, smMax = smWatershed(imTst)
        gc.collect()

      #
      # the end
      #
      if cli.which in ['both']:
        sUp = tsk / tsm
      else:
        sUp = 0

      if cli.csv:
        fmt = "{:d};{:d};{:d};{:d};{:.3f};{:.3f};{:.3f};{:d};{:d}"
      else:
        fmt = "{:3d} - {:3d} - {:6d} {:6d} - {:10.3f} {:10.3f} - {:7.3f} - {:7d} {:7d}"
      print(fmt.format(i, r, w, h, tsm, tsk, sUp, smMax, skMax))

      r *= 2


if __name__ == '__main__':
  import sys

  cli = getCliArgs()
  if cli.showpid:
    pid = os.getpid()
    print("pid : {:d}".format(pid))

    # taurus-watershed-lena-skimage-04-01-16384.csv
    bName = os.path.basename(cli.files[0])
    iName, _ = os.path.splitext(bName)
    fmt = "usage-{:s}-{:s}-{:s}-{:03d}-{:02d}-{:05d}.csv"
    s = fmt.format(cli.function, iName, cli.which, cli.ri, cli.nr, cli.imsize)
    print("bin/pid-monitor.py --csv --pid {:d} > {:s}".format(pid, s))

    input("Hit enter to continue")
    print("OK ! Let's go...")


  r = main(cli, sys.argv)
  time.sleep(1)
  sys.exit(r)

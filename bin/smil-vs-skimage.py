#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  untitled.py
#
#  Copyright 2021 jose-marcio <martins@jose-marcio.org>
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
import os
import sys
import time

import timeit as tit
from datetime import datetime, timezone

import argparse as ap

import smilPython as sp

import skimage as ski
import skimage.io as io
import skimage.morphology as skm
from skimage.transform import rescale, resize, downscale_local_mean

import scipy.ndimage as sci

import numpy as np

import statistics as st

#
#
#


def printHeader():
  fmt = '{:4s} - {:>6s} {:2s} - {:>10s} {:>10s} {:>10s} {:>10s}'
  s = fmt.format('', 'Side', 'SE', 'Mean', 'Std Dev', 'Min', 'Max')
  print(s)
  print('-' * len(s))


#
# #####     #    #    #  ######     #     #####
#   #       #    ##  ##  #          #       #
#   #       #    # ## #  #####      #       #
#   #       #    #    #  #          #       #
#   #       #    #    #  #          #       #
#   #       #    #    #  ######     #       #
#


#
#  ####   #    #     #    #
# #       ##  ##     #    #
#  ####   # ## #     #    #
#      #  #    #     #    #
# #    #  #    #     #    #
#  ####   #    #     #    ######
#
def smilTime(cli, fs, imIn, sz, nb, repeat, px=1):
  imOut = sp.Image(imIn)
  sp.copy(imIn, imOut)
  if cli.squareSe:
    se = sp.SquSE(sz)
  else:
    se = sp.CrossSE(sz)

  dt = np.zeros(repeat)

  if fs == 'erode':
    dt = tit.repeat(lambda: sp.erode(imIn, imOut, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'open':
    dt = tit.repeat(lambda: sp.open(imIn, imOut, se), number=nb, repeat=repeat)

  if fs == 'hMaxima':
    dt = tit.repeat(lambda: sp.hMaxima(imIn, 10, imOut, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'hMinima':
    dt = tit.repeat(lambda: sp.hMinima(imIn, 10, imOut, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'label':
    imOut = sp.Image(imIn, 'UINT32')
    dt = tit.repeat(lambda: sp.label(imIn, imOut, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'fastLabel':
    imOut = sp.Image(imIn, 'UINT32')
    dt = tit.repeat(lambda: sp.fastLabel(imIn, imOut, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'areaOpen':
    if cli.arg is None:
      cli.arg = 500
    dt = tit.repeat(lambda: sp.areaOpen(imIn, int(cli.arg * px * px), imOut, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'areaThreshold':
    if cli.arg is None:
      cli.arg = 500
    dt = tit.repeat(
      lambda: sp.areaThreshold(imIn, int(cli.arg * px * px), imOut, True),
      number=nb,
      repeat=repeat)

  if fs == 'distance':
    dt = tit.repeat(lambda: sp.distanceEuclidean(imIn, imOut),
                    number=nb,
                    repeat=repeat)

  dt = np.array(dt)
  dt *= (1000. / nb)

  return dt


#
#
#
def doSmil(cli, fin=None, fs=None, szIm=[], szSE=[1], nb=10, repeat=7):
  if fs is None:
    return []

  print("* Smil\n")

  im = sp.Image(fin)
  side = im.getWidth()

  imt = sp.Image(im)

  m = []
  printHeader()
  for r in szIm:
    if r != 1.:
      if sp.isBinary(im):
        sp.scale(im, r, imt, "closest")
      else:
        sp.scale(im, r, r, imt, "bilinear")
    else:
      sp.copy(im, imt)
    imo = sp.Image(imt)

    for sz in szSE:
      dt = smilTime(cli, fs, imt, sz, nb, repeat, r)
      fmt = '{:4.1f} - {:6.0f} {:2d} - {:10.3f} {:10.3f} {:10.3f} {:10.3f} - (ms)'
      print(
        fmt.format(r, r * side, sz, dt.mean(), dt.std(), dt.min(), dt.max()))
      m.append(dt.mean())
  print()
  return np.array(m)


#
#  ####   #    #     #    #    #    ##     ####   ######
# #       #   #      #    ##  ##   #  #   #    #  #
#  ####   ####       #    # ## #  #    #  #       #####
#      #  #  #       #    #    #  ######  #  ###  #
# #    #  #   #      #    #    #  #    #  #    #  #
#  ####   #    #     #    #    #  #    #   ####   ######
#


#
# Structuring elements
#
def mkSquareSE(sz=1, D3=False):
  dim = 2 * sz + 1
  if D3:
    se = np.ndarray((dim, dim, dim), dtype='uint8')
    se[:, :, :] = 1
  else:
    se = np.ndarray((dim, dim), dtype='uint8')
    se[:, :] = 1

  return se


def mkCrossSE(sz=1, D3=False):
  dim = 2 * sz + 1
  if D3:
    se = np.ndarray((dim, dim, dim), dtype='uint8')
    se[:, :, :] = 0
    se[:, :, dim // 2] = 1
    se[:, dim // 2, :] = 1
    se[dim // 2, :, :] = 1
  else:
    se = np.ndarray((dim, dim), dtype='uint8')
    se[:, :] = 0
    se[:, dim // 2] = 1
    se[dim // 2, :] = 1

  return se


#
#
#
def skTime(cli, fs, imIn, sz, nb, repeat, px=1):
  dt = np.zeros(repeat)
  if cli.squareSe:
    se = mkSquareSE(sz)
  else:
    se = mkCrossSE(sz)

  if fs == 'erode':
    dt = tit.repeat(lambda: skm.erosion(imIn, se), number=nb, repeat=repeat)

  if fs == 'open':
    dt = tit.repeat(lambda: skm.opening(imIn, se), number=nb, repeat=repeat)

  if fs == 'hMaxima':
    dt = tit.repeat(lambda: skm.h_maxima(imIn, 10, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'hMinima':
    dt = tit.repeat(lambda: skm.h_minima(imIn, 10, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'label':
    dt = tit.repeat(lambda: skm.label(imIn, connectivity=2),
                    number=nb,
                    repeat=repeat)

  if fs == 'fastLabel':
    dt = tit.repeat(lambda: skm.label(imIn, connectivity=2),
                    number=nb,
                    repeat=repeat)

  if fs == 'areaOpen':
    if cli.arg is None:
      cli.arg = 1000
    dt = tit.repeat(lambda: skm.area_opening(
      imIn, area_threshold=int(cli.arg * px * px), connectivity=1),
                    number=nb,
                    repeat=repeat)

  if fs == 'areaThreshold':
    if cli.arg is None:
      cli.arg = 1000
    dt = tit.repeat(lambda: skm.area_opening(
      imIn, area_threshold=int(cli.arg * px * px), connectivity=1),
                    number=nb,
                    repeat=repeat)

  if fs == 'distance':
    dt = tit.repeat(lambda: sci.distance_transform_edt(imIn),
                    number=nb,
                    repeat=repeat)

  dt = np.array(dt)
  dt *= (1000. / nb)

  return dt


#
#
#
def doSkImage(cli, fin=None, fs=None, szIm=[], szSE=[1], nb=10, repeat=7):
  if fs is None:
    return []

  print("* skImage\n")

  im = io.imread(fin)
  side = im.shape[0]
  sz = 1

  m = []
  printHeader()
  for r in szIm:
    if r != 1:
      order = 1
      if cli.binary:
        order = 0
      imt = rescale(im,
                    r,
                    preserve_range=True,
                    order=order,
                    anti_aliasing=True,
                    multichannel=False)
    else:
      imt = im.copy()

    for sz in szSE:
      dt = skTime(cli, fs, imt, sz, nb, repeat, r)
      fmt = '{:4.1f} - {:6.0f} {:2d} - {:10.3f} {:10.3f} {:10.3f} {:10.3f} - (ms)'
      print(
        fmt.format(r, r * side, sz, dt.mean(), dt.std(), dt.min(), dt.max()))
      m.append(dt.mean())
  print()
  return np.array(m)


#
# #    #    ##       #    #    #
# ##  ##   #  #      #    ##   #
# # ## #  #    #     #    # #  #
# #    #  ######     #    #  # #
# #    #  #    #     #    #   ##
# #    #  #    #     #    #    #
#


#
#
#
def printSpeedUp(sz, msm, msk):
  if len(msk) != len(sz) or len(msk) != len(msm):
    return
  rkm = msk / msm
  rmk = msm / msk
  lKm = np.log10(rkm)
  lMk = np.log10(rmk)

  print("* Speed-up : (dt_skimage / dt_Smil)")
  print()
  h = "  {:5s} | {:>11s} | {:>11s} | {:^21s}".format('', 'T(Smil)',
                                                     'T(skImage)',
                                                     'T(skImage)/T(Smil) [*]')
  print(h)
  print('-' * (len(h) + 3))
  for i in range(0, len(sz)):
    print("  {:5d} | {:11.3f} | {:11.3f} | {:14.3f} {:6.3f}".format(
      int(sz[i]), msm[i], msk[i], rkm[i], lKm[i], rmk[i], lMk[i]))
  print("\n  - [*] : ratio and log10(ratio) in columns")


#
#
#
def saveResults(cli, sz, tSm, tSk, fName=None, suffix="szim"):
  if len(tSm) != len(sz) or len(tSk) != len(sz):
    return
  # fname = gray|bin + image + function + szse|seim
  if fName is None:
    if cli.binary:
      fName = "bin"
    else:
      fName = "gray"
    b, x = os.path.splitext(cli.fname)
    fName += '-{:s}-{:s}-{:s}.csv'.format(b, cli.function, suffix)

  if not os.path.isdir(cli.node):
    os.mkdir(cli.node)
  fPath = os.path.join(cli.node, fName)

  with open(fPath, "w") as fout:
    s = '{:s};{:s};{:s}\n'.format(suffix, "Smil", "skImage")
    fout.write(s)
    for i in range(0, len(sz)):
      s = "{:d};{:.5f};{:.5f}\n".format(int(sz[i]), tSm[i], tSk[i])
      fout.write(s)


#
#
#
def printElapsed(ti, tf):
  print()
  print('* Elapsed time : {:.1f} s'.format(float(tf - ti)))


#
#
#
def printSectionHeader(s=None):
  print()
  print('-*-' * 25)
  print()
  if not s is None:
    s = "*** " + s + " ***"
    print(s.center(64))
    print()


# -----------------------------------------------------------------------------
#
#

funcs = [
  'erode', 'open', 'hMaxima', 'hMinima', 'label', 'fastLabel', 'areaOpen',
  'distance', 'areaThreshold'
]

noStrEltCheck = ['areaOpen', 'distance', 'areaThreshold']


#
#
#
def getCliArgs():
  parser = ap.ArgumentParser()
  parser.add_argument('--fname',
                      default='lena.png',
                      help='Image file',
                      type=str)

  parser.add_argument('--debug', help='', action="store_true")
  parser.add_argument('--verbose', help='', action="store_true")

  parser.add_argument('--nb', default=20, help='nb execs', type=int)
  parser.add_argument('--repeat', default=7, help='nb rounds', type=int)

  parser.add_argument('--minImSize',
                      default=256,
                      help='Min image size',
                      type=int)
  parser.add_argument('--maxImSize',
                      default=4096,
                      help='Max image size',
                      type=int)
  parser.add_argument('--imGrow',
                      default='g',
                      help='Image growing : g geometric - a arithmetic',
                      type=str)

  parser.add_argument('--maxSeSize',
                      default=8,
                      help='Max Structuring Element size',
                      type=int)

  parser.add_argument('--binary',
                      default=False,
                      help='Image is binary',
                      action="store_true")
  parser.add_argument('--squareSe',
                      default=False,
                      help='Structuring Element Square (default is Cross)',
                      action='store_true')
  
  parser.add_argument('--arg',
                      help='Generic argument',
                      type=float)

  sFuncs = ' | '.join(funcs)
  parser.add_argument('--function', default='erode', help=sFuncs, type=str)
  cli = parser.parse_args()

  if cli.function in funcs:
    idx = funcs.index(cli.function)
    cli.fSel = idx
  else:
    print("Not found : {:s}".format(cli.function))
    exit(1)

  if not cli.imGrow in ['g', 'a']:
    print('imGrow must be "a" or "g"')
    exit(1)

  return cli


#
#
#
def getImageSizes(fin):
  im = sp.Image(fin)
  width = im.getWidth()
  height = im.getHeight()
  depth = im.getDepth()
  isBin = sp.isBinary(im)
  return width, height, depth, isBin


#
#
#
cli = getCliArgs()

nb = 20
repeat = 7
fSel = 3

fin = cli.fname
nb = cli.nb
repeat = cli.repeat
fSel = cli.fSel
funcName = cli.function

imPath = os.path.join('images', fin)
if not os.path.isfile(imPath):
  print("Image file {:s} not found".format(imPath))
  exit(1)

cli.node = os.uname().nodename.split('.')[0]

width, height, depth, isBin = getImageSizes(imPath)

dt = datetime.now()
print('Date     : {:s}'.format(dt.strftime("%d/%m/%Y %I:%M:%S %p")))
print('Image    : {:s}'.format(fin))
print('  width  : {:5d}'.format(width))
print('  height : {:5d}'.format(height))
print('  depth  : {:5d}'.format(depth))
if isBin:
  print('  type   : binary')
else:
  print('  type   : gray')
print('Function : {:s}'.format(cli.function))
print('  nb     : {:5d}'.format(nb))
print('  repeat : {:5d}'.format(repeat))

print()

szCoefs = []
k = cli.minImSize / width
while width * k <= cli.maxImSize:
  szCoefs.append(k)
  if cli.imGrow == 'a':
    k += 1
  else:
    k *= 2
if len(szCoefs) == 0:
  szCoefs.append(1.)

if isBin and not cli.binary:
  cli.binary = True

seSizes = [k for k in range(1, cli.maxSeSize + 1)]

#
# Varying image size
#

printSectionHeader("Image size")

msm = []
msk = []

ti = time.time()
msm = doSmil(cli, imPath, cli.function, szCoefs, [1], nb=nb, repeat=repeat)
msk = doSkImage(cli, imPath, cli.function, szCoefs, [1], nb=nb, repeat=repeat)
tf = time.time()

sz = width * np.array(szCoefs)

printSpeedUp(sz, msm, msk)
saveResults(cli, sz, msm, msk, fName=None, suffix="szim")
printElapsed(ti, tf)

#
# Varying Structuring Element Size
#

msm = []
msk = []

if not cli.function in noStrEltCheck:
  printSectionHeader("Structuring element size")
  ti = time.time()
  msm = doSmil(cli, imPath, cli.function, [1], seSizes, nb=nb, repeat=repeat)
  msk = doSkImage(cli,
                  imPath,
                  cli.function, [1],
                  seSizes,
                  nb=nb,
                  repeat=repeat)
  tf = time.time()

  sz = np.array(seSizes)
  printSpeedUp(sz, msm, msk)
  saveResults(cli, sz, msm, msk, fName=None, suffix="szse")
  printElapsed(ti, tf)
  print()

printSectionHeader()

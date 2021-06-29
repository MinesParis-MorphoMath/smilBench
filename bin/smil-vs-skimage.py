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
  fmt = '{:4s} - {:>6s} {:2s} - {:>11s} {:>11s} {:>11s} {:>11s}'
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
def smilTime(fs, imIn, sz, nb, repeat, px=1):
  imOut = sp.Image(imIn)
  sp.copy(imIn, imOut)
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
    dt = tit.repeat(lambda: sp.areaOpen(imIn, int(1000 * px * px), imOut, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'areaThreshold':
    dt = tit.repeat(
      lambda: sp.areaThreshold(imIn, int(1000 * px * px), imOut, True),
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
def mkCrossSE(sz=1):
  dim = 2 * sz + 1
  se = np.ndarray((dim, dim), dtype='uint8')
  se[:, :] = 0
  se[:, dim // 2] = 1
  se[dim // 2, :] = 1

  return se


def skTime(fs, imIn, sz, nb, repeat, px=1):
  dt = np.zeros(repeat)
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
    dt = tit.repeat(lambda: skm.area_opening(
      imIn, area_threshold=int(1000 * px * px), connectivity=1),
                    number=nb,
                    repeat=repeat)

  if fs == 'areaThreshold':
    dt = tit.repeat(lambda: skm.area_opening(
      imIn, area_threshold=int(1000 * px * px), connectivity=1),
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
#  ####   #    #     #    #
# #       ##  ##     #    #
#  ####   # ## #     #    #
#      #  #    #     #    #
# #    #  #    #     #    #
#  ####   #    #     #    ######
#
def doSmil(fin=None, fs=None, szIm=[], szSE=[1], nb=10, repeat=7):
  if fs is None:
    return []

  v = []
  if len(szIm) > 1:
    v.append("Image size")
  if len(szSE) > 1:
    v.append("Structuring element")
  print("* Smil : {:s}\n".format(" and ".join(v)))

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
      dt = smilTime(fs, imt, sz, nb, repeat, r)
      fmt = '{:4.1f} - {:6.0f} {:2d} - {:11.4f} {:11.4f} {:11.4f} {:11.4f} - (ms)'
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


def doSkImage(fin=None, fs=None, szIm=[], szSE=[1], nb=10, repeat=7):
  if fs is None:
    return []

  v = []
  if len(szIm) > 1:
    v.append("Image size")
  if len(szSE) > 1:
    v.append("Structuring element")
  print("* skImage : {:s}\n".format(" and ".join(v)))

  im = io.imread(fin)
  side = im.shape[0]
  sz = 1

  m = []
  printHeader()
  for r in szIm:
    if r != 1:
      #imt = 255 * rescale(im, r, anti_aliasing=True, multichannel=False)
      #imt = imt.astype('uint8')

      imt = rescale(im,
                    r,
                    preserve_range=True,
                    order=0,
                    anti_aliasing=True,
                    multichannel=False)
    else:
      imt = im.copy()

    for sz in szSE:
      dt = skTime(fs, imt, sz, nb, repeat, r)
      fmt = '{:4.1f} - {:6.0f} {:2d} - {:11.4f} {:11.4f} {:11.4f} {:11.4f} - (ms)'
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
def printSpeedUp(sz, msm, msk):
  if len(msk) != len(sz) or len(msk) != len(msm):
    return
  rkm = msk / msm
  rmk = msm / msk
  lKm = np.log10(rkm)
  lMk = np.log10(rmk)

  print("* Speed-up : (dt_skimage / dt_Smil)")
  print()
  h = "  {:5s} | {:>11s} | {:>11s} | {:^21s}".format('', 'T(Smil)', 'T(skImage)', 'T(skImage) / T(Smil)')
  print(h)
  print('-' * (len(h) + 3))
  for i in range(0, len(sz)):
    print("  {:5d} | {:11.4f} | {:11.4f} | {:14.3f} {:6.3f}".format(
      int(sz[i]), msm[i], msk[i], rkm[i], lKm[i], rmk[i], lMk[i]))
  print("\n  - OBS: ratio and log10(ratio) in columns")


def printElapsed(ti, tf):
  print()
  print('* Elapsed time : {:.1f} s'.format(float(tf - ti)))
  print()


# -----------------------------------------------------------------------------
#
#

funcs = [
  'erode', 'open', 'hMaxima', 'hMinima', 'label', 'fastLabel', 'areaOpen',
  'distance', 'areaThreshold'
]

noStrEltCheck = ['areaOpen', 'distance', 'areaThreshold']


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


def getImageSides(fin):
  im = sp.Image(fin)
  w = im.getWidth()
  h = im.getHeight()
  return w, h


#
#
#
cli = getCliArgs()

nb = 20
repeat = 7
fSel = 3

fin = "lena.png"

fin = cli.fname
nb = cli.nb
repeat = cli.repeat
fSel = cli.fSel
funcName = cli.function

print('Image    : {:s}'.format(fin))
print('  func   : {:5d} {:s}'.format(fSel, cli.function))
print('  nb     : {:5d}'.format(nb))
print('  repeat : {:5d}'.format(repeat))

print()

imPath = os.path.join('images', fin)
if not os.path.isfile(imPath):
  print("Image file {:s} not found".format(imPath))
  exit(1)

w, h = getImageSides(imPath)

szCoefs = []
k = cli.minImSize / w
while w * k <= cli.maxImSize:
  szCoefs.append(k)
  if cli.imGrow == 'a':
    k += 1
  else:
    k *= 2
if len(szCoefs) == 0:
  szCoefs.append(1.)

seSizes = [k for k in range(1,cli.maxSeSize + 1)]

#
# Varying image size
#
print()
print('-*-' * 25)
print()

msm = []
msk = []

ti = time.time()
msm = doSmil(imPath, cli.function, szCoefs, [1], nb=nb, repeat=repeat)
msk = doSkImage(imPath, cli.function, szCoefs, [1], nb=nb, repeat=repeat)
tf = time.time()

sz = w * np.array(szCoefs)

printSpeedUp(sz, msm, msk)
printElapsed(ti, tf)

#
# Varying Structuring Element Size
#
print()
print('-*-' * 25)
print()

msm = []
msk = []

if not cli.function in noStrEltCheck:
  ti = time.time()
  msm = doSmil(imPath, cli.function, [1], seSizes, nb=nb, repeat=repeat)
  msk = doSkImage(imPath, cli.function, [1], seSizes, nb=nb, repeat=repeat)
  tf = time.time()

  sz = np.array(seSizes)
  printSpeedUp(sz, msm, msk)
  printElapsed(ti, tf)
  print()
  print('-*-' * 25)
  print()

print('\n')

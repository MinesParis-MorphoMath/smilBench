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
szImages = [0.5, 1., 2., 4., 8., 16.]
szStrElt = [1, 2, 3, 4, 5, 6, 7, 8]

szImages = [0.5, 1., 2.]
#
#
#


def printHeader():
  fmt = '{:4s} - {:>6s} - {:>11s} {:>11s} {:>11s} {:>11s}'
  s = fmt.format('', 'Side', 'Mean', 'Std Dev', 'Min', 'Max')
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
def smilTime(fs, imIn, sz, nb, repeat):
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

  if fs == 'areaOpen':
    dt = tit.repeat(lambda: sp.areaOpen(imIn, 1000, imOut, se),
                    number=nb,
                    repeat=repeat)

  if fs == 'areaThreshold':
    dt = tit.repeat(lambda: sp.areaThreshold(imIn, 1000, imOut, True),
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


def skTime(fs, imIn, sz, nb, repeat):
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
    dt = tit.repeat(lambda: skm.label(imIn, connectivity=2), number=nb, repeat=repeat)

  if fs == 'areaOpen':
    dt = tit.repeat(
      lambda: skm.area_opening(imIn, area_threshold=1000, connectivity=1),
      number=nb,
      repeat=repeat)

  if fs == 'areaThreshold':
    dt = tit.repeat(
      lambda: skm.area_opening(imIn, area_threshold=1000, connectivity=1),
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
  print("* Smil : varying Image size\n")
  im = sp.Image(fin)
  side = im.getWidth()

  imt = sp.Image(im)

  m = []
  printHeader()
  for r in szIm:
    if r != 1.:
      sp.scale(im, r, r, imt, "bilinear")
    else:
      sp.copy(im, imt)
    imo = sp.Image(imt)

    for sz in szSE:
      dt = smilTime(fs, imt, sz, nb, repeat)
      fmt = '{:4.1f} - {:6.0f} {:2d} - {:11.4f} {:11.4f} {:11.4f} {:11.4f} - (ms)'
      print(
        fmt.format(r, r * side, sz, dt.mean(), dt.std(), dt.min(), dt.max()))
      m.append(dt.mean())
  print()
  return np.array(m)


def smilSizeImage(fin=None, fs=0, nb=10, repeat=7):
  print("* Smil : varying Image size\n")
  im = sp.Image(fin)
  side = im.getWidth()

  imt = sp.Image(im)

  m = []
  printHeader()
  for r in szImages:
    if r != 1.:
      sp.scale(im, r, r, imt, "bilinear")
    else:
      sp.copy(im, imt)
    imo = sp.Image(imt)

    dt = smilTime(fs, imt, 1, nb, repeat)
    fmt = '{:4.1f} - {:6.0f} - {:11.4f} {:11.4f} {:11.4f} {:11.4f} - (ms)'
    print(fmt.format(r, r * side, dt.mean(), dt.std(), dt.min(), dt.max()))
    m.append(dt.mean())
  print()
  return np.array(m)


def smilSizeSE(fin=None, fs=0, nb=10, repeat=7):
  print("* Smil : varying Structuring Element size\n")
  im = sp.Image(fin)
  side = im.getWidth()

  imt = sp.Image(im)
  imo = sp.Image(imt)

  m = []
  printHeader()
  for sz in szStrElt:
    dt = smilTime(fs, imt, sz, nb, repeat)

    fmt = '{:4.0f} - {:6.0f} - {:11.4f} {:11.4f} {:11.4f} {:11.4f} - (ms)'
    print(fmt.format(sz, side, dt.mean(), dt.std(), dt.min(), dt.max()))
    m.append(dt.mean())
  print()
  return np.array(m)


#
#
#

#
#  ####   #    #     #    #    #    ##     ####   ######
# #       #   #      #    ##  ##   #  #   #    #  #
#  ####   ####       #    # ## #  #    #  #       #####
#      #  #  #       #    #    #  ######  #  ###  #
# #    #  #   #      #    #    #  #    #  #    #  #
#  ####   #    #     #    #    #  #    #   ####   ######
#


def doSkImage(fin=None, fs=None, szIm=[], szSE=[1], nb=10, repeat=7):
  print("* skImage : varying Image size\n")
  im = io.imread(fin)
  side = im.shape[0]
  sz = 1

  m = []
  printHeader()
  for r in szIm:
    if r != 1:
      imt = 256 * rescale(im, r, anti_aliasing=True, multichannel=False)
      imt = imt.astype('uint8')
    else:
      imt = im.copy()

    for sz in szSE:
      dt = skTime(fs, imt, sz, nb, repeat)
      fmt = '{:4.1f} - {:6.0f} - {:11.4f} {:11.4f} {:11.4f} {:11.4f} - (ms)'
      print(fmt.format(r, r * side, dt.mean(), dt.std(), dt.min(), dt.max()))
      m.append(dt.mean())
  print()
  return np.array(m)


def skImageSizeImage(fin=None, fs=0, nb=10, repeat=7):
  print("* skImage : varying Image size\n")
  im = io.imread(fin)
  side = im.shape[0]
  sz = 1

  m = []
  printHeader()
  for r in szImages:
    if r != 1:
      imt = 256 * rescale(im, r, anti_aliasing=True, multichannel=False)
      imt = imt.astype('uint8')
    else:
      imt = im.copy()

    dt = skTime(fs, imt, sz, nb, repeat)
    fmt = '{:4.1f} - {:6.0f} - {:11.4f} {:11.4f} {:11.4f} {:11.4f} - (ms)'
    print(fmt.format(r, r * side, dt.mean(), dt.std(), dt.min(), dt.max()))
    m.append(dt.mean())
  print()
  return np.array(m)


def skImageSizeSE(fin=None, fs=0, nb=10, repeat=7):
  print("* skImage : varying Structuring Element size\n")
  im = io.imread(fin)
  side = im.shape[0]

  m = []
  printHeader()
  for sz in szStrElt:
    dt = skTime(fs, im, sz, nb, repeat)
    fmt = '{:4.0f} - {:6.0f} - {:11.4f} {:11.4f} {:11.4f} {:11.4f} - (ms)'
    print(fmt.format(sz, side, dt.mean(), dt.std(), dt.min(), dt.max()))
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
  ratio = msk / msm
  logr = np.log10(ratio)
  print("* Speed-up : (dt_skimage / dt_Smil)")
  print()
  h = "  {:5s} | {:^14s} | {:^7s}".format('', 'Speed Up', 'Log')
  print(h)
  print('-' * (len(h) + 3))
  for i in range(0, len(sz)):
    print("  {:5d} | {:14.3f} | {:7.3f}".format(int(sz[i]), ratio[i], logr[i]))


# -----------------------------------------------------------------------------
#
#

funcs = [
  'erode', 'open', 'hMaxima', 'hMinima', 'label', 'areaOpen', 'distance',
  'areaThreshold'
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

  parser.add_argument('--seSizes',
                      help='Sizes StrElt (comma separated values',
                      type=str)
  parser.add_argument('--imSizes',
                      help='Sizes Img (comma separated multipliers)',
                      type=str)

  sFuncs = ' | '.join(funcs)
  parser.add_argument('--function', default='erode', help=sFuncs, type=str)
  cli = parser.parse_args()

  if cli.seSizes is None:
    cli.seSizes = [1, 2, 3, 4, 5, 6, 7, 8]
  else:
    cli.seSizes = cli.seSizes.replace(' ', '')
    sz = cli.imSizes.split(',')
    cli.seSizes = []
    for s in sz:
      try:
        v = int(s)
        cli.seSizes.append(v)
      except ValueError:
        print("Error : only integer values")
        exit(1)

  if cli.imSizes is None:
    cli.imSizes = [0.5, 1., 2., 4.]
  else:
    cli.imSizes = cli.imSizes.replace(' ', '')
    sz = cli.imSizes.split(',')
    cli.imSizes = []
    for s in sz:
      try:
        v = float(s)
        cli.imSizes.append(v)
      except ValueError:
        print("Error : only float values")
        exit(1)

  if cli.function in funcs:
    idx = funcs.index(cli.function)
    cli.fSel = idx
  else:
    print("Not found : {:s}".format(cli.function))
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
#fin = "astronaut-bw.png"

fin = cli.fname
nb = cli.nb
repeat = cli.repeat
fSel = cli.fSel
funcName = cli.function

szImages = cli.imSizes

print('Image    : {:s}'.format(fin))
print('  func   : {:5d} {:s}'.format(fSel, cli.function))
print('  nb     : {:5d}'.format(nb))
print('  repeat : {:5d}'.format(repeat))

print()

imPath = os.path.join('images', fin)
if not os.path.isfile(imPath):
  print("Image file {:s} not found".format(imPath))
  exit(1)

#
# Varying image size
#
print()
print('-*-' * 25)
print()

msm = []
msk = []

tia = time.time()
# msm = smilSizeImage(imPath, cli.function, nb=nb, repeat=repeat)
msm = doSmil(imPath, cli.function, cli.imSizes, [1], nb=nb, repeat=repeat)
#msk = skImageSizeImage(imPath, cli.function, nb=nb, repeat=repeat)
msk = doSkImage(imPath, cli.function, cli.imSizes, [1], nb=nb, repeat=repeat)
tfa = time.time()
dta = tfa - tia

w, h = getImageSides(imPath)
sz = w * np.array(szImages)
printSpeedUp(sz, msm, msk)

#
# Varying Structuring Element Size
#
print()
print('-*-' * 25)
print()

msm = []
msk = []

dtb = 0
if not cli.function in noStrEltCheck:
  tib = time.time()
  #msm = smilSizeSE(imPath, cli.function, nb=nb, repeat=repeat)
  msm = doSmil(imPath, cli.function, [1], cli.seSizes, nb=nb, repeat=repeat)
  msk = skImageSizeSE(imPath, cli.function, nb=nb, repeat=repeat)
  tfb = time.time()
  dtb = tfb - tib

  printSpeedUp(szStrElt, msm, msk)
  print()
  print('-*-' * 25)
  print()

print('\n')

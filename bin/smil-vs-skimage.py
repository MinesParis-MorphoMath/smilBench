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
import configparser as cp

import smilPython as sp

#import skimage as ski
import skimage.io as io
import skimage.morphology as skm
from skimage.transform import rescale, resize

#import scipy.ndimage as sci
from scipy import ndimage as ndi

from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from skimage.filters import rank

import numpy as np
import math as m

import statistics as st

# -----------------------------------------------------------------------------
#
#


def printHeader():
  fmt = '{:5s} - {:>6s} {:2s} - {:>11s} {:>11s} {:>11s} {:>11s}'
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
# -----------------------------------------------------------------------------
#
#
t0 = time.time()

def timeInit():
  global t0
  t0 = time.time()

def getProcTime():
  return time.time() - t0

def printProcTime(s = ''):
  print('= Time {:8.1f} : {:s}'.format(time.time() - t0, s))

def getNbAuto(tc=None):
  if tc is None:
    return 1
  # (nb, dt) returned by autorange()
  lnb = tc.autorange()
  N = lnb[0]
  if lnb[1] < 1.:
    N = m.ceil(lnb[0] * (1. / lnb[1]))
  return N


#
#  ####   #    #     #    #
# #       ##  ##     #    #
#  ####   # ## #     #    #
#      #  #    #     #    #
# #    #  #    #     #    #
#  ####   #    #     #    ######
#
def smilTime(cli, fs, imIn, sz, repeat, px=1):

  wsData = {
    'astronaut.png': [10, 0],
    'bubbles_gray.png': [10, 5],
    'hubble_EDF_gray.png': [5, 1],
    'lena.png': [5, 0],
    'tools.png': [10, 1],
  }

  #
  #
  #
  def binSegmentation(imIn, imOut):
    dt = []
    se = sp.HexSE()
    imDist = sp.Image(imIn)
    sp.distance(imIn, imDist)
    sp.inv(imDist, imDist)
    sp.watershed(imDist, imOut, se)
    sp.inv(imOut, imOut)
    sp.inf(imIn, imOut, imOut)
    return dt

  #
  #
  #
  def graySegmentation(imIn, imOut, h=5, sz=0):
    se = sp.HexSE()
    imOpen = sp.Image(imIn)
    if sz > 0:
      sp.open(imIn, imOpen, sp.HexSE(sz))
    else:
      sp.copy(imIn, imOpen)
    imGrad = sp.Image(imIn)
    imMin = sp.Image(imIn)
    sp.gradient(imOpen, imGrad, se)
    sp.hMinima(imGrad, h, imMin, se)
    imLabel = sp.Image(imOpen, 'UINT16')
    sp.label(imMin, imLabel)
    sp.watershed(imGrad, imLabel, imOut, se)

  #
  #
  #
  imOut = sp.Image(imIn)
  sp.copy(imIn, imOut)
  if cli.squareSe:
    se = sp.SquSE(sz)
  else:
    se = sp.CrossSE(sz)

  dt = np.zeros(repeat)
  ctit = None

  nb = 1
  if fs == 'erode':
    ctit = tit.Timer(lambda: sp.erode(imIn, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'open':
    ctit = tit.Timer(lambda: sp.open(imIn, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'tophat':
    ctit = tit.Timer(lambda: sp.topHat(imIn, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == "gradient":
    ctit = tit.Timer(lambda: sp.gradient(imIn, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'hMaxima':
    ctit = tit.Timer(lambda: sp.hMaxima(imIn, 10, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'hMinima':
    ctit = tit.Timer(lambda: sp.hMinima(imIn, 10, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'label':
    imOut = sp.Image(imIn, 'UINT32')
    ctit = tit.Timer(lambda: sp.label(imIn, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'fastLabel':
    imOut = sp.Image(imIn, 'UINT32')
    ctit = tit.Timer(lambda: sp.fastLabel(imIn, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'segmentation':
    if cli.binary:
      ctit = tit.Timer(lambda: binSegmentation(imIn, imOut))
      nb = getNbAuto(ctit)
      dt = ctit.repeat(repeat = repeat, number = nb)
    else:
      h, sz = wsData[cli.image]
      ctit = tit.Timer(lambda: graySegmentation(imIn, imOut, h, sz))
      nb = getNbAuto(ctit)
      dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'watershed':
    if cli.binary:
      se = sp.HexSE()
      imDist = sp.Image(imIn)
      sp.distance(imIn, imDist)
      sp.inv(imDist, imDist)
      ctit = tit.Timer(lambda: sp.watershed(imDist, imOut, se(4)))
      nb = getNbAuto(ctit)
      dt = ctit.repeat(repeat = repeat, number = nb)
    else:
      h, sz = wsData[cli.image]
      se = sp.HexSE()
      imOpen = sp.Image(imIn)
      if sz > 0:
        sp.open(imIn, imOpen, sp.HexSE(sz))
      else:
        sp.copy(imIn, imOpen)
      imGrad = sp.Image(imIn)
      imMin = sp.Image(imIn)
      sp.gradient(imOpen, imGrad, se)
      sp.hMinima(imGrad, h, imMin, se)
      imLabel = sp.Image(imOpen, 'UINT16')
      sp.label(imMin, imLabel)
      ctit = tit.Timer(lambda: sp.watershed(imGrad, imLabel, imOut, se))
      nb = getNbAuto(ctit)
      dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'areaOpen':
    if cli.arg is None:
      cli.arg = 500
    sz = int(cli.arg * px * px)
    ctit = tit.Timer(lambda: sp.areaOpen(imIn, sz, imOut, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'areaThreshold':
    if cli.arg is None:
      cli.arg = 500
    sz = int(cli.arg * px * px)
    ctit = tit.Timer(lambda: sp.areaThreshold(imIn, sz, imOut, True))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'distance':
    ctit = tit.Timer(lambda: sp.distanceEuclidean(imIn, imOut))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'zhangSkeleton':
    ctit = tit.Timer(lambda: sp.zhangSkeleton(imIn, imOut))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'thinning':
    ctit = tit.Timer(lambda: sp.fullThin(imIn, sp.HMT_hL(6), imOut))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if cli.debug:
    print("  Debug : nb {:d}".format(int(nb)))

  if False and not ctit is None:
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  dt = np.array(dt)
  dt *= (1000. / nb)

  return dt


# -----------------------------------------------------------------------------
#
#
def doSmil(cli, fin=None, fs=None, szIm=[], szSE=[1], repeat=7):
  if fs is None:
    return []

  print("* Smil\n")

  im = sp.Image(fin)
  side = im.getWidth()

  imt = sp.Image(im)

  m = []
  npm = np.array(())
  printHeader()

  for szi in szIm:
    if szi != 1.:
      if sp.isBinary(im):
        sp.scale(im, szi, imt, "closest")
      else:
        sp.scale(im, szi, szi, imt, "bilinear")
    else:
      sp.copy(im, imt)
    imo = sp.Image(imt)

    for sz in szSE:
      if cli.debug:
        printProcTime('Call smilTime({:4.1f}, {:2d})'.format(szi, sz))
      dt = smilTime(cli, fs, imt, sz, repeat, szi)
      if cli.debug:
        printProcTime('Back from smilTime()')
      fmt = '{:5.1f} - {:6.0f} {:2d} - {:11.3f} {:11.3f} {:11.3f} {:11.3f} - (ms)'
      print(
        fmt.format(szi, szi * side, sz, dt.mean(), dt.std(), dt.min(),
                   dt.max()))
      m.append(dt.min())
      npm = np.append(npm, [dt.mean(), dt.std(), dt.min(), dt.max()])

  print()
  npm = npm.reshape((npm.shape[0] // 4, 4))
  return np.array(m), npm


#
#  ####   #    #     #    #    #    ##     ####   ######
# #       #   #      #    ##  ##   #  #   #    #  #
#  ####   ####       #    # ## #  #    #  #       #####
#      #  #  #       #    #    #  ######  #  ###  #
# #    #  #   #      #    #    #  #    #  #    #  #
#  ####   #    #     #    #    #  #    #   ####   ######
#


# -----------------------------------------------------------------------------
# Structuring elements
#
def mkSquareSE(cli, sz=1, D3=False):
  dim = 2 * sz + 1
  if D3:
    se = np.ndarray((dim, dim, dim), dtype='uint8')
    se[:, :, :] = 1
  else:
    se = np.ndarray((dim, dim), dtype='uint8')
    se[:, :] = 1
    se = skm.selem.square(2 * sz + 1)
  return se


# -----------------------------------------------------------------------------
#
#
def mkCrossSE(cli, sz=1, D3=False):
  dim = 2 * sz + 1
  if D3:
    se = np.ndarray((dim, dim, dim), dtype='uint8')
    se[:, :, :] = 0
    se[:, :, dim // 2] = 1
    se[:, dim // 2, :] = 1
    se[dim // 2, :, :] = 1
  else:
    se = skm.selem.diamond(sz)

  return se


# -----------------------------------------------------------------------------
#
#
def skTime(cli, fs, imIn, sz, repeat, px=1):

  wsData = {
    'astronaut.png': [2, 5],
    'bubbles_gray.png': [1, 3],
    'hubble_EDF_gray.png': [1, 2],
    'lena.png': [3, 5],
    'tools.png': [1, 3],
  }

  #
  #
  #
  def binSegmentation(imIn):
    imIn = imIn.astype(int)
    # https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_watershed.html
    distance = ndi.distance_transform_edt(imIn)
    coords = peak_local_max(distance, footprint=np.ones((3, 3)), labels=imIn)
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers, _ = ndi.label(mask)
    labels = watershed(-distance, markers, mask=mask)
    return labels

  def graySegmentation(imIn, szg, szo):
    imIn = imIn.astype('uint8')
    # denoise image
    denoised = rank.median(imIn, skm.disk(szo))
    # find continuous region (low gradient -
    # where less than 10 for this image) --> markers
    # disk(5) is used here to get a more smooth image
    markers = rank.gradient(denoised, skm.disk(szg)) < 10
    markers = ndi.label(markers)[0]
    # local gradient (disk(2) is used to keep edges thin)
    gradient = rank.gradient(denoised, skm.disk(2))
    # process the watershed
    labels = watershed(gradient, markers)

  #
  #
  #
  def skAreaThreshold(imIn, sz):
    imb = skm.label(imIn)
    imOut = skm.remove_small_objects(imb, sz)
    return imOut

  #
  #
  #
  if cli.squareSe:
    se = mkSquareSE(cli, sz)
  else:
    se = mkCrossSE(cli, sz)

  dt = np.zeros(repeat)
  ctit = None

  nb = 1
  if fs == 'erode':
    ctit = tit.Timer(lambda: skm.erosion(imIn, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'open':
    ctit = tit.Timer(lambda: skm.opening(imIn, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'tophat':
    ctit = tit.Timer(lambda: skm.white_tophat(imIn, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'gradient':
    imIn = imIn.astype('uint8')
    ctit = tit.Timer(lambda: rank.gradient(imIn, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'hMaxima':
    ctit = tit.Timer(lambda: skm.h_maxima(imIn, 10, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'hMinima':
    ctit = tit.Timer(lambda: skm.h_minima(imIn, 10, se))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'label':
    ctit = tit.Timer(lambda: skm.label(imIn, connectivity=1))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'fastLabel':
    ctit = tit.Timer(lambda: skm.label(imIn, connectivity=2))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'segmentation':
    if cli.binary:
      ctit = tit.Timer(lambda: binSegmentation(imIn))
      nb = getNbAuto(ctit)
      dt = ctit.repeat(repeat = repeat, number = nb)
    else:
      szg, szo = wsData[cli.image]
      ctit = tit.Timer(lambda: graySegmentation(imIn, szg, szo))
      nb = getNbAuto(ctit)
      dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'watershed':
    if cli.binary:
      imIn = imIn.astype(int)
      dist = ndi.distance_transform_edt(imIn)
      se = skm.selem.diamond(3)
      coords = peak_local_max(dist,
                              footprint=se,
                              labels=imIn)
      mask = np.zeros(dist.shape, dtype=bool)
      mask[tuple(coords.T)] = True
      markers, _ = ndi.label(mask)
      ctit = tit.Timer(lambda: watershed(-dist, markers, mask=imIn))
      nb = getNbAuto(ctit)
      dt = ctit.repeat(repeat = repeat, number = nb)
    else:
      szg, szo = wsData[cli.image]
      imIn = imIn.astype('uint8')
      # denoise image
      denoised = rank.median(imIn, skm.disk(szo))
      # find continuous region (low gradient -
      # where less than 10 for this image) --> markers
      # disk(5) is used here to get a more smooth image
      markers = rank.gradient(denoised, skm.disk(szg)) < 10
      markers = ndi.label(markers)[0]
      # local gradient (disk(2) is used to keep edges thin)
      gradient = rank.gradient(denoised, skm.disk(2))
      # process the watershed
      ctit = tit.Timer(lambda: watershed(gradient, markers))
      nb = getNbAuto(ctit)
      dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'areaOpen':
    if cli.arg is None:
      cli.arg = 500
    sz = int(cli.arg * px * px)
    ctit = tit.Timer(
      lambda: skm.area_opening(imIn, area_threshold=sz, connectivity=1))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'areaThreshold':
    if cli.arg is None:
      cli.arg = 500
    sz = int(cli.arg * px * px)
    ctit = tit.Timer(lambda: skAreaThreshold(imIn, sz=sz))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'distance':
    ctit = tit.Timer(lambda: ndi.distance_transform_edt(imIn))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'zhangSkeleton':
    imIn = imIn.astype(bool)
    ctit = tit.Timer(lambda: skm.skeletonize(imIn))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if fs == 'thinning':
    imIn = imIn.astype(bool)
    ctit = tit.Timer(lambda: skm.thin(imIn))
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  if cli.debug:
    print(" Debug : nb {:d}".format(int(nb)))

  if False and not ctit is None:
    nb = getNbAuto(ctit)
    dt = ctit.repeat(repeat = repeat, number = nb)

  dt = np.array(dt)
  dt *= (1000. / nb)

  return dt


# -----------------------------------------------------------------------------
#
#
def doSkImage(cli, fin=None, fs=None, szIm=[], szSE=[1], repeat=7):
  if fs is None:
    return []

  print("* skImage\n")

  im = io.imread(fin, as_gray=True)
  side = im.shape[0]
  sz = 1

  m = []
  npm = np.array(())
  printHeader()
  for szi in szIm:
    if szi != 1:
      order = 1
      if cli.binary:
        order = 0
      imt = rescale(im,
                    szi,
                    preserve_range=True,
                    order=order,
                    anti_aliasing=True,
                    multichannel=False)
    else:
      imt = im.copy()

    for sz in szSE:
      if cli.debug:
        printProcTime('Call skTime({:4.1f}, {:2d})'.format(szi, sz))
      dt = skTime(cli, fs, imt, sz, repeat, szi)
      if cli.debug:
        printProcTime('Back from skTime()')
      fmt = '{:5.1f} - {:6.0f} {:2d} - {:11.3f} {:11.3f} {:11.3f} {:11.3f} - (ms)'
      print(
        fmt.format(szi, szi * side, sz, dt.mean(), dt.std(), dt.min(),
                   dt.max()))
      m.append(dt.min())
      npm = np.append(npm, [dt.mean(), dt.std(), dt.min(), dt.max()])

  print()
  npm = npm.reshape((npm.shape[0] // 4, 4))
  return np.array(m), npm


#
# #    #    ##       #    #    #
# ##  ##   #  #      #    ##   #
# # ## #  #    #     #    # #  #
# #    #  ######     #    #  # #
# #    #  #    #     #    #   ##
# #    #  #    #     #    #    #
#


# -----------------------------------------------------------------------------
#
#
def printSpeedUp(sz, msm, msk):
  if len(msk) != len(sz) or len(msk) != len(msm) or len(sz) == 0:
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


# -----------------------------------------------------------------------------
#
#
def saveResults(cli, sz, vSm, vSk, fName=None, suffix="szim"):
  if vSm.shape[0] != len(sz) or vSk.shape[0] != len(sz):
    return
  # fname = gray|bin + image + function + szse|seim
  if fName is None:
    if cli.binary:
      fName = "bin"
    else:
      fName = "gray"
    b, x = os.path.splitext(cli.image)
    fName += '-{:s}-{:s}-{:s}.csv'.format(b, cli.function, suffix)

  if not os.path.isdir(cli.node):
    os.mkdir(cli.node)
  fPath = os.path.join(cli.node, fName)

  cName = ['mean', 'stdev', 'min', 'max']
  with open(fPath, "w") as fout:
    h = [suffix]
    for j in range(0, vSm.shape[1]):
      h.append('Smil-{:s}'.format(cName[j]))
    for j in range(0, vSm.shape[1]):
      h.append('skImage-{:s}'.format(cName[j]))
    fout.write(';'.join(h) + '\n')

    for i in range(0, len(sz)):
      sl = []
      sl.append('{:d}'.format(int(sz[i])))
      for j in range(0, vSm.shape[1]):
        sl.append('{:.5f}'.format(vSm[i, j]))
      for j in range(0, vSk.shape[1]):
        sl.append('{:.5f}'.format(vSk[i, j]))
      s = ';'.join(sl)
      fout.write(s + '\n')


# -----------------------------------------------------------------------------
#
#
def printElapsed(ti, tf):
  print()
  print('* Elapsed time : {:.1f} s'.format(float(tf - ti)))


# -----------------------------------------------------------------------------
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

kFuncs = {
  'erode': True,
  'open': True,
  'tophat': True,
  'gradient': True,
  'hMaxima': True,
  'hMinima': True,
  'label': False,
  'fastLabel': False,
  'areaOpen': False,
  'distance': False,
  'areaThreshold': False,
  'segmentation': False,
  'watershed': False,
  'watershedOnly': False,
  'zhangSkeleton': False,
  'thinning': False
}


# -----------------------------------------------------------------------------
#
#
def appLoadFileConfig(fconfig=None):
  if fconfig is None:
    return None

  if not os.path.isfile(fconfig):
    return None

  config = cp.ConfigParser(interpolation=cp.ExtendedInterpolation(),
                           default_section="default")

  config.BOOLEAN_STATES['Vrai'] = True
  config.BOOLEAN_STATES['Faux'] = False

  config.read(fconfig)

  return config


# -----------------------------------------------------------------------------
#
#
def getCliArgs():
  parser = ap.ArgumentParser()
  parser.add_argument('--image',
                      default='notfound.png',
                      help='Image file',
                      type=str)

  parser.add_argument('--debug', help='', action="store_true")
  parser.add_argument('--verbose', help='', action="store_true")

  parser.add_argument('--repeat', default=7, help='nb rounds', type=int)
  parser.add_argument('--selector',
                      default='mean',
                      help='measurement selector : mean, min, max',
                      type=str)

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

  parser.add_argument('--arg', help='Generic argument', type=float)

  sFuncs = ' | '.join(kFuncs.keys())
  parser.add_argument('--function', default='erode', help=sFuncs, type=str)
  cli = parser.parse_args()

  okSel = ['mean', 'min', 'max']
  if not cli.selector in okSel:
    print('Invalid values for selector : {:s} - Choose one of {:s}'.format(
      cli.selector, ', '.join(okSel)))
    exit(1)

  if not cli.function in kFuncs:
    print("Not found : {:s}".format(cli.function))
    exit(1)

  if not cli.imGrow in ['g', 'a']:
    print('imGrow must be "a" or "g"')
    exit(1)

  return cli


# -----------------------------------------------------------------------------
#
#
def appSaveFileConfig(config=None, fconfig=None):
  if config is None or fconfig is None:
    return False
  with open(fconfig, "w") as cf:
    config.write(cf)


# -----------------------------------------------------------------------------
#
#
def getAppConfig(argv, CAppl=None):
  if CAppl is None:
    CAppl = {}
  CAppl['cli'] = getCliArgs(argv)
  CAppl['config'] = appLoadFileConfig("etc/bench.ini")
  CAppl['section'] = 'default'

  section = CAppl['section']
  #cli = CAppl['cli']
  #config = CAppl['config']

  appSaveFileConfig(CAppl['config'], "tmp/covid.ini")

  # copy cli to conf
  for k in CAppl['cli'].keys():
    if not CAppl['cli'][k] is None:
      CAppl['config'][section][k] = str(CAppl['cli'][k])

  return CAppl


# -----------------------------------------------------------------------------
#
#
def XgetConfigValues(argv):
  cli = getCliArgs(argv)
  config = appLoadFileConfig("etc/covid.ini")

  for k in cli.keys():
    if not cli[k] is None:
      config["default"][k] = str(cli[k])

  #if config["default"]['debug']:
  #  showConfig(config)
  appSaveFileConfig(config, "tmp/covid.ini")

  return config


# -----------------------------------------------------------------------------
#
#
def getImageSizes(fin):
  im = sp.Image(fin)
  width = im.getWidth()
  height = im.getHeight()
  depth = im.getDepth()
  isBin = sp.isBinary(im)
  return width, height, depth, isBin


# -----------------------------------------------------------------------------
#
#
def whichData(arr, selector="mean"):
  if selector == "mean":
    return arr[:, 0]
  if selector == "min":
    return arr[:, 2]
  if selector == "max":
    return arr[:, 3]
  return arr[:, 0]


# -----------------------------------------------------------------------------
#
#
cli = getCliArgs()

repeat = 7

fin = cli.image
repeat = cli.repeat
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
msm, npsm = doSmil(cli,
                   imPath,
                   cli.function,
                   szCoefs, [1],
                   repeat=repeat)
msk, npsk = doSkImage(cli,
                      imPath,
                      cli.function,
                      szCoefs, [1],
                      repeat=repeat)
tf = time.time()

msm = whichData(npsm, cli.selector)
msk = whichData(npsk, cli.selector)

sz = width * np.array(szCoefs)

printSpeedUp(sz, msm, msk)
saveResults(cli, sz, npsm, npsk, fName=None, suffix="szim")
printElapsed(ti, tf)

#
# Varying Structuring Element Size
#

msm = []
msk = []

if kFuncs[cli.function]:
  printSectionHeader("Structuring element size")
  ti = time.time()
  msm, npsm = doSmil(cli,
                     imPath,
                     cli.function, [1],
                     seSizes,
                     repeat=repeat)
  msk, npsk = doSkImage(cli,
                        imPath,
                        cli.function, [1],
                        seSizes,
                        repeat=repeat)
  tf = time.time()

  msm = whichData(npsm, cli.selector)
  msk = whichData(npsk, cli.selector)

  sz = np.array(seSizes)
  printSpeedUp(sz, msm, msk)
  saveResults(cli, sz, npsm, npsk, fName=None, suffix="szse")
  printElapsed(ti, tf)
  print()

printSectionHeader()

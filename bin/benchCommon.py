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

import inspect

import timeit as tit
from datetime import datetime, timezone

import argparse as ap
import configparser as cp

import smilPython as sp

import skimage as ski
import skimage.io as io
import skimage.morphology as skm
from skimage.transform import rescale, resize, downscale_local_mean

import scipy.ndimage as sci
from scipy import ndimage as ndi

from skimage.segmentation import watershed
from skimage.feature import peak_local_max

import numpy as np

import statistics as st

# -----------------------------------------------------------------------------
#
#


def printHeader():
  fmt = '{:4s} - {:>6s} {:2s} - {:>11s} {:>11s} {:>11s} {:>11s}'
  s = fmt.format('', 'Side', 'SE', 'Mean', 'Std Dev', 'Min', 'Max')
  print(s)
  print('-' * len(s))




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

kFuncs = {
  'erode': True,
  'open': True,
  'hMaxima': True,
  'hMinima': True,
  'label': True,
  'fastLabel': True,
  'areaOpen': False,
  'distance': False,
  'areaThreshold': False,
  'watershed': False,
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

  parser.add_argument('--arg', help='Generic argument', type=float)

  sFuncs = ' | '.join(kFuncs.keys())
  parser.add_argument('--function', default='erode', help=sFuncs, type=str)
  cli = parser.parse_args()

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
def getAppConfig(argv, CAppl = None):
  if CAppl is None:
    CAppl = {}
  cli = getCliArgs()
  CAppl['cli'] = {}
  for i in inspect.getmembers(cli):
    if not i[0].startswith('_'):
        if not inspect.ismethod(i[1]):
          CAppl['cli'][i[0]] = i[1]

  cliFields = CAppl['cli']
  for k in sorted(cliFields.keys()):
    print('  {:<12s} : {:s}'.format(k, str(cliFields[k])))

  print(cli.__dict__)
  for k in sorted(cli.__dict__.keys()):
    print('  {:<12s} : {:s}'.format(k, str(cli.__dict__[k])))

  CAppl['config'] = appLoadFileConfig("etc/bench.ini")
  CAppl['section'] = 'default'

  section = CAppl['section']
  #cli = CAppl['cli']
  #config = CAppl['config']

  appSaveFileConfig(CAppl['config'], "tmp/bench.ini")

  # copy cli to conf
  for k in CAppl['cli'].keys():
    if not CAppl['cli'][k] is None:
      CAppl['config'][section][k] = str(CAppl['cli'][k])

  return CAppl



# -----------------------------------------------------------------------------
#
#
cli = getCliArgs()

CAppl = getAppConfig(sys.argv)



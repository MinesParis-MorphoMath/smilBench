#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  pid-monitor.py
#
#  Copyright 2021 José Marcio Martins da Cruz <martins@jose-marcio.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


import os
import sys
import psutil

import fnmatch as fn
import re
import datetime

import math as m

import pandas as pd
import numpy as np

import argparse as ap
import configparser as cp

# import smilPython as sp

##import skimage as ski
#import skimage.io as io
#import skimage.morphology as skm
#import skimage.transform  as skt
#
#import scipy.ndimage as sdi
#
#from skimage.segmentation import watershed
#from skimage.feature import peak_local_max
#from skimage.filters import rank


# -----------------------------------------------------------------------------
#
#
def getCliArgs():
  parser = ap.ArgumentParser()

  parser.add_argument('--debug', help='', action="store_true")
  parser.add_argument('--verbose', help='', action="store_true")

  parser.add_argument('--pid', default=None, help='PID to monitor', type=int)
  parser.add_argument('--dt', default=1, help='time interval', type=int)
  parser.add_argument('--csv', help='output CSV format', action='store_true')

  cli = parser.parse_args()
  return cli

# =============================================================================
#
#
#
def main(args):
  cli = getCliArgs()

  if cli.pid is None:
    return 1

  try:
    process = psutil.Process(cli.pid)
    _ = process.cpu_percent(1.)
  except:
    return 1

  t = cli.dt
  if cli.csv:
    print('{:s};{:s};{:s};{:s}'.format('date','cpu','virt','res'))
  while True:
    try:
      cpu = process.cpu_percent(cli.dt)
    except:
      break
    mem = process.memory_info()
    rss = mem.rss // 1024
    vms = mem.vms // 1024
    if not cli.csv:
      print("{:6d} : {:7.2f} % - {:10d} {:10d}".format(t, cpu, vms, rss))
    else:
      print("{:d};{:.2f};{:d};{:d}".format(t, cpu, vms, rss))
    t += cli.dt

  return 0


if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

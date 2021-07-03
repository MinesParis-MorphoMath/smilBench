#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  do-graph-times.py
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
import time

import timeit as tit
from datetime import datetime, timezone

import argparse as ap

import smilPython as sp

import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

figsize = [6,6]

#
#
#
def getCliArgs():
  parser = ap.ArgumentParser()

  parser.add_argument('--debug', help='', action="store_true")
  parser.add_argument('--verbose', help='', action="store_true")
  parser.add_argument('--showconf', help='', action="store_true")

  parser.add_argument('--dirin',
                      default='.',
                      help='Input file directory (default is .)',
                      type=str)
  parser.add_argument('--dirout',
                      help='Output file directory (default is dirin)',
                      type=str)
  parser.add_argument('--fin', help='Input file name', type=str)
  parser.add_argument('--fout',
                      help='Output file name (default is auto)',
                      type=str)
  parser.add_argument('--save',
                      default=False,
                      help='Save images (default is False)',
                      action='store_true')

  parser.add_argument('--title', help='Plot title', type= str)
  parser.add_argument('--xscale',
                      default='auto',
                      help='X axis scale - auto lin log (default is auto)',
                      type=str)
  parser.add_argument('--xmin', help='X min (default is auto)', type=float)
  parser.add_argument('--xmax', help='X max (default is auto)', type=float)

  parser.add_argument('--yscale',
                      default='auto',
                      help='Y axis scale - auto lin log (default is auto)',
                      type=str)
  parser.add_argument('--ymin', help='Y min (default is auto)', type=float)
  parser.add_argument('--ymax', help='Y max (default is auto)', type=float)

  parser.add_argument('--speedup',
                      default=False,
                      help='Draw speedup or times (default is times)',
                      action='store_true')

  cli = parser.parse_args()

  if not cli.xscale in ['auto', 'lin', 'linear', 'log']:
    print('Error : invalid scale for X axis :', cli.xscale)
    exit(1)
  if not cli.yscale in ['auto', 'lin', 'linear', 'log']:
    print('Error : invalid scale for Y axis :', cli.yscale)
    exit(1)
  if cli.xscale == 'lin':
    cli.xscale = 'linear'
  if cli.yscale == 'lin':
    cli.yscale = 'linear'

  if cli.fin is None and not cli.showconf:
    print('Error : Must provide an input file name')
    exit(1)

  if cli.dirout is None:
    cli.dirout = cli.dirin

  if cli.debug or cli.showconf:
    for k in cli.__dict__.keys():
      print('* {:16s} {:}'.format(k, cli.__dict__[k]))
    if cli.showconf:
      exit(0)

  return cli


# -----------------------------------------------------------------------------
#
#
#
def plotSetFontSize(size='small', which='font'):
  """
    SMALL_SIZE = 8
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 12

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    """
  SMALL_SIZE = 8
  MEDIUM_SIZE = 10
  BIGGER_SIZE = 12

  Sizes = {'small': SMALL_SIZE, 'medium': MEDIUM_SIZE, 'bigger': BIGGER_SIZE}

  if size is None:
    size = 'small'

  if isinstance(size, int):
    plt.rc(which, size=size)
  else:
    if not size in Sizes.keys():
      size = 'small'
    plt.rc(which, size=Sizes[size])
  plt.rc('axes', titlesize=BIGGER_SIZE)


plotSetFontSize()


#
#
#
def calcLimits(v=None, scale="log", cmax=True):
  if scale == "log":
    if cmax:
      return np.power(10., np.ceil(np.log10(v)))
    else:
      return np.power(10., np.floor(np.log10(v)))
  if scale == "linear":
    dx = np.power(10., np.floor(np.log10(v)))
    if cmax:
      vm = (v // dx) * dx
      if vm == v:
        return vm
      else:
        return vm + dx
    else:
      return (v // dx) * dx
  return 0.

#
#
#
def mkFileName(cli):
  fname = os.path.splitext(cli.fin)[0]
  if cli.speedup:
    fname += '-speedup.png'
  else:
    fname += '-times.png'
  fpath = os.path.join(cli.dirout, fname)
  return fpath

#
#
#
def mkTitle(cli):
  arg = cli.fin.split('-')

  if cli.speedup:
    title = 'Speed Up'
  else:
    title = 'Processing time' 
  title +=  '\n'
  title += 'Image {:s} - Type {:s} - Function {:s}\n'
  title = title.format(arg[1], arg[0], arg[2])

  return title

#
#
#
XLabel = {'szse': 'Structuring Element size', 'szim': 'Image size'}

#
#
#
def plotTimes(cli, df):

  xcol = df.columns[0]
  ycols = df.columns[1:]

  xmin, xmax = cli.xmin, cli.xmax
  if xmin is None:
    xmin = df[xcol].min()
  if xmax is None :
    xmax = df[xcol].max()

  if cli.xmin is None or cli.xmax is None:
    if cli.xscale == 'auto' and xmax > 10 * xmin:
      cli.xscale = 'log'
    xmin = calcLimits(xmin, cli.xscale, False)
    xmax = calcLimits(xmax, cli.xscale, True)

  ymin, ymax = cli.ymin, cli.ymax
  if ymin is None:
    for c in ycols:
      v = df[c].min()
      if ymin is None:
        ymin = v
      else:
        ymin = min(ymin, v)
    rs = True

  if ymax is None:
    for c in ycols:
      v = df[c].max()
      if ymax is None:
        ymax = v
      else:
        ymax = max(ymax, v)

  if cli.yscale == 'auto':
    if ymax > 10 * ymin:
      cli.yscale = 'log'
    else:
      cli.yscale = 'linear'

  if cli.ymin is None:
    ymin = calcLimits(ymin, cli.yscale, False)
  if cli.ymax is None:
    ymax = calcLimits(ymax, cli.yscale, True)

  if cli.verbose:
    print("X Limits : {:8.0f} {:8.0f}".format(xmin, xmax))
    print("Y Limits : {:8.3f} {:8.3f}".format(ymin, ymax))

  plt.close()
  fig, ax = plt.subplots(figsize=figsize)

  for c in ycols:
    ax.plot(df[xcol], df[c], label=c)

  ax.set_ylim([ymin, ymax])
  ax.set_yscale(cli.yscale)

  ax.set_xlim([xmin, xmax])
  ax.set_xscale(cli.xscale)

  ax.set_ylabel("Time (ms)")
  ax.set_xlabel(XLabel[xcol])
  if cli.title is None or cli.title == "":
    cli.title = mkTitle(cli)
  if not cli.title is None and cli.title != "":
    ax.set_title(cli.title)

  ax.legend()
  ax.grid(True, "both")

  if cli.save:
    fout = mkFileName(cli)
    plt.savefig(fout)
  else:
    plt.show()
  


#
#
#
def plotSpeedup(cli, df):
  xcol = df.columns[0]
  ycols = df.columns[1:]

  xmin, xmax = cli.xmin, cli.xmax
  if xmin is None:
    xmin = df[xcol].min()
  if xmax is None :
    xmax = df[xcol].max()

  if cli.xmin is None or cli.xmax is None:
    if cli.xscale == 'auto' and xmax > 10 * xmin:
      cli.xscale = 'log'
    xmin = calcLimits(xmin, cli.xscale, False)
    xmax = calcLimits(xmax, cli.xscale, True)

  speedup = df[ycols[1]] / df[ycols[0]]
  ymin, ymax = cli.ymin, cli.ymax
  if ymin is None:
    ymin = speedup.min()
  if ymax is None:
    ymax = speedup.max()

  if cli.ymin is None or cli.ymax is None:
    if cli.yscale == 'auto':
      if ymax > 10 * ymin:
        cli.yscale = 'log'
      else:
        cli.yscale = 'linear'
    ymin = calcLimits(ymin, cli.yscale, False)
    ymax = calcLimits(ymax, cli.yscale, True)

  if cli.verbose:
    print("X Limits : {:8.0f} {:8.0f}".format(xmin, xmax))
    print("Y Limits : {:8.3f} {:8.3f}".format(ymin, ymax))

  plt.close()
  fig, ax = plt.subplots(figsize=figsize)

  ax.plot(df[xcol], speedup, label="Speed Up")

  ax.set_ylim([ymin, ymax])
  ax.set_yscale(cli.yscale)

  ax.set_xlim([xmin, xmax])
  ax.set_xscale(cli.xscale)

  ax.set_ylabel("Speed Up")
  ax.set_xlabel(XLabel[xcol])
  if cli.title is None or cli.title == "":
    cli.title = mkTitle(cli)
  if not cli.title is None and cli.title != "":
    ax.set_title(cli.title)

  ax.legend()
  ax.grid(True, "both")

  if cli.save:
    fout = mkFileName(cli)
    plt.savefig(fout)
  else:
    plt.show()


#
#
#
def main(args):

  plt.figure()
  cli = getCliArgs()

  fPath = os.path.join(cli.dirin, cli.fin)
  if not os.path.isfile(fPath):
    return False

  df = pd.read_csv(fPath, sep=';')

  if cli.debug or cli.verbose:
    print()
    print(df)
    print()

  if cli.speedup:
    plotSpeedup(cli, df)
  else:
    plotTimes(cli, df)

  return 0


if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

#!/usr/bin/env python

import sys
import os
import argparse
import logging
import multiav

from bintools import splitter
from colors import colors

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the file to analyze")
    parser.add_argument("-s", "--step", type=int, help="initial step size for dsplit. (default 1Kb)")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose output")
    args = parser.parse_args()

    step = args.step or 1024
    dsplit_dir = os.getcwd() + '/offsets'
    splitter.dsplit(args.file, todir=dsplit_dir, chunksize=step, verbose=args.verbose)

    base_dir = os.path.realpath(__file__)
    multi_av = multiav.CMultiAV(base_dir + '/multiav.cfg')
    ret = multi_av.scan(dsplit_dir, multiav.AV_SPEED_MEDIUM)
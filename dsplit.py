#!/usr/bin/env python

import sys
import os
import argparse
import math
import logging

from bintools import splitter
from colors import colors

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the file to analyze")
    parser.add_argument("-s", "--step", type=int, help="step size. (default 1Kb)")
    parser.add_argument("-o", "--offset", type=int, help="offset for the file, expressed in bytes")
    parser.add_argument("-l", "--limit", type=int, help="limit the number of bytes read")
    parser.add_argument("-w", "--write", help="path to write results to")
    parser.add_argument("-f", "--fill", action="store_true", help="fill the part with zeros instead of truncating")
    args = parser.parse_args()

    step = args.step or 1024
    offset = args.offset or 0
    limit = args.limit or None
    outdir = args.write or os.getcwd()

    to_divide = limit or os.path.getsize(args.file)
    logging.info("%sdsplit: %s%d parts will be generated in %s" %
                    (colors.OKGREEN, colors.ENDC, math.ceil(to_divide / step), outdir))
    splitter.dsplit(args.file, todir=outdir, chunksize=step, offset=offset, limit=limit, fill=args.fill)

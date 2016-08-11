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
    parser.add_argument("-c", "--cover", type=int, help="byte to cover sections with (default 0x90)")
    parser.add_argument("-o", "--offset", type=int, help="initial offset to start covering bytes")
    parser.add_argument("-l", "--limit", type=int, help="limit the generated files size")
    parser.add_argument("-w", "--write", help="path to write results to")
    args = parser.parse_args()

    step = args.step or 1024
    cover = args.cover or 0x90
    offset = args.offset or 0
    limit = args.limit or None
    outdir = args.write or os.getcwd()

    to_divide = os.path.getsize(args.file)
    logging.info("%savfuck: %s%d files will be generated in %s" %
                    (colors.OKGREEN, colors.ENDC, math.ceil(to_divide / step), outdir))
    splitter.avfuck(args.file, todir=outdir, coversize=step, filling=cover, offset=offset, limit=limit)

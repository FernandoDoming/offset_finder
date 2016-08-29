#!/usr/bin/env python

import sys
import os
import argparse
import logging
import re
import multiav.core

from bintools import splitter
from colors import colors

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("file", help="the file to analyze")
  parser.add_argument("-s", "--step", type=int, help="initial step size for dsplit. (default 1Kb)")
  parser.add_argument("-p", "--precision", type=int, help="Precision for the signature location (absolute error in bytes). (default 100)")
  parser.add_argument("-v", "--verbose", action='store_true', help="Verbose output")
  args = parser.parse_args()

  if args.verbose: log_level = logging.INFO
  else:            log_level = logging.WARN

  logging.basicConfig(level=log_level,
                      format='%(levelname)s: %(message)s')

  parts_pattern = re.compile('.+part(\d+)$')

  step = args.step or 1024
  precision = args.precision or 100
  dsplit_dir = os.path.join(os.getcwd(), 'offsets')
  splitter.dsplit(args.file, todir=dsplit_dir, chunksize=step, verbose=args.verbose)

  base_dir = os.path.dirname(os.path.realpath(__file__))
  multi_av = multiav.core.CMultiAV( os.path.join(base_dir, 'multiav.cfg') )
  logging.info("Beginning scanning at %s..." % (dsplit_dir))
  scans = multi_av.scan(dsplit_dir, multiav.core.AV_SPEED_MEDIUM)

  detected_parts = []
  for engine, parts in scans.iteritems():
    logging.info("%s found %d results" % (engine, len(parts)))

    for part, result in parts.iteritems():
      if result[0] == 'FOUND':
        matched = parts_pattern.match(part)
        part_n = int(matched.group(1))
        detected_parts.append(part_n)
        logging.info("Part %d detected as %s" % (part_n, result[1]))

    min_part = min(detected_parts)
    logging.info("First detected part by %s is %d" % (engine, min_part))
    offset = min_part * step
    logging.info("Signature for %s starts at offset %d - %d" % (engine, offset, offset + step))
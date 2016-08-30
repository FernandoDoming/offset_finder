#!/usr/bin/env python

import sys
import os
import shutil
import argparse
import logging
import re
import multiav.core

from bintools import splitter
from colors import colors

################ Functions ################

def scan_parts(parts):
  detected_parts = []
  parts_pattern = re.compile('.+part(\d+)$')

  for part, result in parts.iteritems():
    if result[0] != 'FOUND': continue

    matched = parts_pattern.match(part)
    part_n = int(matched.group(1))
    detected_parts.append(part_n)
    logging.info("Part %d detected as %s" % (part_n, result[1]))

  return detected_parts

################   main   ################

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("file", help="the file to analyze")
  parser.add_argument("-s", "--step", type=int, help="initial step size for dsplit. (default 1Kb)")
  parser.add_argument("-i", "--iter", type=int, help="Maximum iterations. (default None)")
  parser.add_argument("-p", "--precision", type=int, help="Precision for the signature location " +
                                                          "(absolute error in bytes). (default 1000)")
  parser.add_argument("-v", "--verbose", action='store_true', help="Verbose output")
  parser.add_argument("-t", "--truncate", action='store_true', help="Truncate instead of filling with zeros. " +
                                                                    "Filling with zeros usually works better " +
                                                                    "but uses more space")
  args = parser.parse_args()

  if args.verbose: log_level = logging.INFO
  else:            log_level = logging.WARN

  logging.basicConfig(level=log_level,
                      format='%(levelname)s: %(message)s')

  base_dir      = os.path.dirname(os.path.realpath(__file__))
  multi_av      = multiav.core.CMultiAV( os.path.join(base_dir, 'multiav.cfg') )

  step       = args.step or 1024
  precision  = args.precision or 1000
  dsplit_dir = os.path.join(os.getcwd(), 'offsets')
  max_iter   = args.iter or float('inf')

  offset = 0; limit = None; i = 0
  while step > precision:
    logging.info("Beginning iteration %d B. Offset: %d B, step: %d B" % (i, offset, step))

    # Clean working directory
    if os.path.isdir(dsplit_dir): shutil.rmtree(dsplit_dir)
    # Generate parts
    splitter.dsplit(args.file, todir=dsplit_dir, chunksize=step,
                    offset=offset, limit=limit, fill=not args.truncate)

    logging.info("Beginning scanning at %s..." % (dsplit_dir))
    scans = multi_av.scan(dsplit_dir, multiav.core.AV_SPEED_MEDIUM)

    for engine, parts in scans.iteritems():
      logging.info("%s found %d results" % (engine, len(parts)))

      detected_parts = scan_parts(parts)
      min_part = min(detected_parts)
      if not detected_parts:
        logging.warn("No detected parts by %s. Skipping..." % (engine))
        break     # TODO: should be continue

      logging.info("First detected part by %s is %d" % (engine, min_part))
      offset = offset + min_part * step
      limit = step * 2
      logging.info("Signature for %s starts at offset %d - %d, error: %d"
                    % (engine, offset, offset + step, step))
      # TODO: Support multiple engines
      break   # Right now only one engine at a time
      # /for

    if i >= max_iter:
      logging.warn("Reached maximum iterations (%d). Breaking..." % (max_iter))
      break

    step /= 2
    i += 1
    logging.info("------------------------------------------------------")
    # /while

  logging.info("Signature start located to offset %d - %d, error: %d"
                % (offset, offset + step, step))

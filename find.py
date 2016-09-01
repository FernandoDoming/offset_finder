#!/usr/bin/env python

import sys
import os
import shutil
import argparse
import logging
import re
import multiav.core

from bintools import splitter
from bintools import tools
from colors import colors

################ Functions ################

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def scan_parts(parts):
  detected_parts = []
  parts_pattern = re.compile('.+(?:part|fuck)(\d+)$')

  for part, result in parts.iteritems():
    if result[0] != 'FOUND': continue

    matched = parts_pattern.match(part)
    part_n = int(matched.group(1))
    detected_parts.append(part_n)
    logging.info("Part %d detected as %s" % (part_n, result[1]))

  return detected_parts

def missing_elements(L, start, end):
  return sorted(set(xrange(start, end + 1)).difference(L))

def get_args():
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
  return parser.parse_args()

################   main   ################

if __name__ == "__main__":

  args = get_args()
  if args.verbose: log_level = logging.INFO
  else:            log_level = logging.WARN

  logging.basicConfig(level=log_level,
                      format='%(levelname)s: %(message)s')

  base_dir = os.path.dirname(os.path.realpath(__file__))
  multi_av = multiav.core.CMultiAV( os.path.join(base_dir, 'multiav.cfg') )

  step       = args.step or 1024
  precision  = args.precision or 1000
  dsplit_dir = os.path.join(os.getcwd(), 'offsets')
  avfuck_dir = os.path.join(os.getcwd(), 'avfuck')
  max_iter   = args.iter or float('inf')

  # Dsplit iterations to obtain signature start offset
  offset = 0; limit = None; i = 0
  while step > precision:
    logging.info("DSPLIT: Beginning iteration %d. Offset: %d B, step: %d B" % (i, offset, step))
    if args.truncate: starting_offset = offset
    else: starting_offset = 0

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
      if not detected_parts:
        logging.warn("No detected parts by %s. Skipping..." % (engine))
        break     # TODO: should be continue

      min_part = min(detected_parts)
      logging.info("First detected part by %s is %d" % (engine, min_part))
      offset = starting_offset + min_part * step
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

  print("[*] Signature start located to offset %d - %d, error: %d"
                % (offset, offset + step, step))
  # Avfuck
  logging.info("------------------------------------------------------")
  logging.info("Starting AvFucker method...")

  coversize = step / 20
  splitter.avfuck(args.file, todir=avfuck_dir, coversize=coversize, coffset=offset, limit=offset+step*2)
  scans = multi_av.scan(avfuck_dir, multiav.core.AV_SPEED_MEDIUM)

  for engine, parts in scans.iteritems():
    logging.info("%s found %d results" % (engine, len(parts)))
    detected_parts = scan_parts(parts)
    undetected_parts = missing_elements(detected_parts, start=0, end=40)
    logging.info("Undetected parts: %s" % (str(undetected_parts).strip('[]')))

    for part in undetected_parts:
      breaking_offset = offset + int(part) * coversize
      print("[*] Modifing offset %d - %d breaks the signature" % (breaking_offset, breaking_offset+coversize))

      should_dump = query_yes_no("Do you want to dump the contents at that range?", default="yes")
      if should_dump:
        tools.print_dump(tools.dump(args.file, start=breaking_offset, end=breaking_offset+coversize))
    break


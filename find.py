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

  offset, err = tools.find_start_offset(args.file, precision=precision, step=step,
                      truncate=args.truncate, dsplit_dir=dsplit_dir, max_i=max_iter)
  print("[*] Signature start located to offset %d - %d, error: %d"
        % (offset, offset + err, err))

  # Avfuck
  coversize = err / 20
  logging.info("Starting AvFucker method. Offset: %d, Coversize: %d" % (offset, coversize))
  breaking_offsets, precision = tools.find_breaking_offset(args.file, avfuck_dir=avfuck_dir, coversize=coversize,
                                                          offset=offset, step=err)

  for offset in breaking_offsets:
    print("[*] Modifing offset %d - %d breaks the signature" % (offset, offset + coversize))
    should_dump = query_yes_no("Do you want to dump the contents at that range?", default="yes")
    if should_dump:
      tools.print_dump(tools.dump(args.file, start=offset, end=offset+precision))


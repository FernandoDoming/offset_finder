import sys
import os
import shutil
import argparse
import logging
import re
import multiav.core

from bintools import splitter
from colors import colors

base_dir = os.path.join( os.path.dirname(os.path.realpath(__file__)), '..')
multi_av = multiav.core.CMultiAV( os.path.join(base_dir, 'multiav.cfg') )

def dump(filename, start, end):
  f = open(filename, 'rb')
  f.seek(start, 1)
  data = f.read(end - start)
  f.close()
  return data


def missing_elements(L, start, end):
  return sorted(set(xrange(start, end + 1)).difference(L))


def hexdump(filename, start, end):
  data = dump(filename, start, end)
  return format(ord(byte), 'x')


def print_dump(data, addr=None):
  shex = ""
  for byte in data:
    shex += format(ord(byte), 'x') + " "
  if addr: shex = str(addr) + ": " + shex
  print(shex)


def scan_parts(parts):
  detected_parts = []
  parts_pattern = re.compile('.+(?:part|fuck)(\d+)$')

  for part, result in parts.iteritems():
    matched = parts_pattern.match(part)
    part_n = int(matched.group(1))
    detected_parts.append(part_n)
    if isinstance(result, list):
      logging.info("Part %d detected as %s" % (part_n, result[1]))
    else:
      logging.info("Part %d detected as %s" % (part_n, result))

  return detected_parts


def lowest_detected_part(scans):
  for engine, parts in scans.iteritems():
    logging.info("%s found %d results" % (engine, len(parts)))

    detected_parts = scan_parts(parts)
    min_part = None
    if not detected_parts:
      logging.warn("No detected parts by %s. Skipping..." % (engine))
      break     # TODO: should be continue

    min_part = min(detected_parts)
    logging.info("First detected part by %s is %d" % (engine, min_part))
    # TODO: Support multiple engines
    break   # Right now only one engine at a time
  return min_part


def find_start_offset(file, precision, step, truncate, dsplit_dir, max_i=float('inf')):
  # Dsplit iterations to obtain signature start offset
  offset = 0; limit = None; i = 0
  while True:
    logging.info("DSPLIT: Beginning iteration %d. Offset: %d B, step: %d B" % (i, offset, step))
    if truncate: starting_offset = offset
    else: starting_offset = 0

    # Clean working directory
    if os.path.isdir(dsplit_dir): shutil.rmtree(dsplit_dir)
    # Generate parts
    splitter.dsplit(file, todir=dsplit_dir, chunksize=step,
                    offset=offset, limit=limit, fill=not truncate)

    logging.info("Beginning scanning at %s..." % (dsplit_dir))
    scans = multi_av.scan(dsplit_dir, multiav.core.AV_SPEED_MEDIUM)
    part  = lowest_detected_part(scans)
    if part is None: break
    offset = starting_offset + part * step
    #logging.info("Signature for %s starts at offset %d - %d, error: %d"
    #             % (engine, offset, offset + step, step))

    limit = step * 2
    if i >= max_i:
      logging.warn("Reached maximum iterations (%d). Breaking..." % (max_i))
      break

    if precision > step: break
    step /= 2
    i    += 1
  return offset, step


def find_breaking_offset(file, avfuck_dir, coversize, offset, step, precision):
  offsets = []
  while True:
    total_parts = splitter.avfuck(file, todir=avfuck_dir, coversize=coversize, coffset=offset, limit=offset+step*2)
    scans = multi_av.scan(avfuck_dir, multiav.core.AV_SPEED_MEDIUM)

    for engine, parts in scans.iteritems():
      logging.info("%s found %d results" % (engine, len(parts)))
      detected_parts = scan_parts(parts)
      undetected_parts = missing_elements(detected_parts, start=0, end=total_parts)
      logging.info("Undetected parts: %s" % (str(undetected_parts).strip('[]')))

      for part in undetected_parts:
        offsets.append(offset + int(part) * coversize)
      break    # TODO: Multiple engines
      # end for
    if precision >= coversize: break
    coversize /= 2
    # end while
  return offsets, coversize

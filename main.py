#!/usr/bin/env python

import sys
import os
import argparse

from bintools import splitter

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="the file to analyze")
    parser.add_argument("-s", "--step", type=int, help="step size. (default 1Kb)")
    parser.add_argument("-o", "--offset", type=int, help="offset for the file, expressed in bytes")
    parser.add_argument("-l", "--limit", type=int, help="limit the number of bytes read")
    args = parser.parse_args()

    step = int(args.step) if args.step else 1024
    splitter.dsplit(args.file, os.getcwd(), step)

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))      # Add lib to python path
from bintools import splitter

def print_usage():
    print("Usage: %s file step [offset]" % (sys.argv[0]))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    filename = sys.argv[1]
    step = int(sys.argv[2])
    offset = int(sys.argv[3]) if len(sys.argv) >= 4 else 0

    splitter.dsplit(filename, os.getcwd(), step)

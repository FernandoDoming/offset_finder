import os
import shutil
import math
import logging
from colors import colors

BUFFER = 1024

def dsplit(fromfile, todir=os.getcwd(), offset=0, limit=None, chunksize=1024, fill=False):
    """
    Splits a file using the dsplit mechanism
    """
    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts

    original_file = os.path.basename(fromfile)
    filesize = os.path.getsize(fromfile)

    if fill:
        # do not truncate headers if fill is set
        if limit is not None: limit = offset + limit;
        offset = 0

    # calculate sizes to operate with
    if limit is not None: to_divide = min(limit, filesize - offset)
    else: to_divide = filesize - offset

    logging.info("%sdsplit: %s%d parts will be generated in %s" %
        (colors.OKGREEN, colors.ENDC, math.ceil(to_divide / chunksize), todir))

    cont = True; partnum = 0; read = chunksize
    while cont:
        if read > to_divide:
            # Do the last read if conditions met
            cont = False
            read = to_divide
        tofile = os.path.join(todir, ('%s.part%d' % (original_file, partnum)))
        __read_write_block(fromfile, read, tofile, offset)
        if fill:
            cover = filesize - read
            __cover_block(tofile, size=cover, offset=read, filling=0x00)
        partnum += 1
        read    += chunksize

def avfuck(fromfile, todir=os.getcwd(), coversize=1024, filling=0x90, offset=0, limit=None, coffset=0):
    """
    Covers sections of a file using the AVfuck method

    Keyword arguments:
    fromfile -- file to cover
    todir -- output directory (default os.getcwd())
    coversize -- number of bytes to cover in each iteration (default 1024)
    filling -- byte value to cover with (default 0x90)
    offset -- begin reading fromfile at said offset (default 0)
    limit -- do not read more than these bytes from fromfile (default None)
    """

    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts

    original_file = os.path.basename(fromfile)
    filesize = os.path.getsize(fromfile)
    if coversize > limit and limit is not None: coversize = limit
    max_size = limit or filesize - offset

    cont = True; partnum = 0; read = max_size; cover_offset = coffset
    while cover_offset < max_size:
        tofile = os.path.join(todir, ('%s.fuck%d' % (original_file, partnum)))
        __read_write_block(fromfile, size=read, tofile=tofile, offset=offset)
        __cover_block(tofile, size=coversize, offset=cover_offset, filling=filling)
        cover_offset += coversize
        partnum += 1

#### Private methods

def __cover_block(fromfile, size, offset, filling=0x90):
    stream = open(fromfile, 'rb+')
    stream.seek(offset, 1)
    cover = bytearray([filling] * size)
    stream.write(cover)
    stream.close()

def __read_write_block(fromfile, size, tofile, offset=0):
    stream = open(fromfile, 'rb')
    out = open(tofile, 'wb')
    stream.seek(offset, 1)

    bytesread = 0
    while bytesread < size:
        if bytesread + BUFFER > size:
            # Read will exceed limit, limit the number of bytes to read
            n = size - bytesread
        else:
            # Read the maximum
            n = BUFFER
        chunk = stream.read(n)
        bytesread += len(chunk)
        out.write(chunk)
    stream.close()
    out.close()

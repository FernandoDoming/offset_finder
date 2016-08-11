import os
import shutil

BUFFER = 1024

def dsplit(fromfile, todir=os.getcwd(), offset=0, limit=None, chunksize=1024):
    """
    Splits a file using the dsplit mechanism
    """
    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts

    original_file = os.path.basename(fromfile)
    filesize = os.path.getsize(fromfile)
    cont = True; partnum = 0; read = chunksize
    while cont:
        if read > (filesize - offset) or (read > limit and limit is not None):
            # Do the last read if conditions met
            cont = False
            read = limit or (filesize - offset)
        tofile = os.path.join(todir, ('%s.part%d' % (original_file, partnum)))
        __read_write_block(fromfile, read, tofile, offset)
        partnum += 1
        read    += chunksize

def avfuck(fromfile, todir=os.getcwd(), coversize=1024, filling=0x90, offset=0, limit=None):
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

    cont = True; partnum = 0; read = max_size; cover_offset = 0
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

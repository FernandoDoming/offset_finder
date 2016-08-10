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

def avfuck(fromfile, todir=os.getcwd(), chunksize=1024):
    """
    Covers sections of a file using the AVfuck method
    """
    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts

    original_file = os.path.basename(fromfile)
    filesize = os.path.getsize(fromfile)
    cont = True; partnum = 0; read = chunksize; offset = 0
    while cont:
        if read > filesize - offset:
            # Do the last read if conditions met
            cont = False
            read = filesize - offset
        tofile = os.path.join(todir, ('%s.fuck%d' % (original_file, partnum)))
        shutil.copyfile(fromfile, tofile)
        __cover_block(tofile, read, offset)
        offset += read
        partnum += 1

#### Private methods

def __cover_block(fromfile, size, offset, filling=0x90):
    stream = open(fromfile, 'ab+')
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

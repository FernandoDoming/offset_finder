import os

# Splits a file using the dsplit mechanism
def dsplit(fromfile, todir = os.getcwd(), offset = 0, limit = None, chunksize = 1024):
    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts

    original_file = os.path.basename(fromfile)
    filesize = os.path.getsize(fromfile)
    cont = True; partnum = 1; read = chunksize
    while cont:
        if read > (filesize - offset) or (read > limit and limit is not None):
            # Do the last read if conditions met
            cont = False
            read = limit or (filesize - offset)
        tofile = os.path.join(todir, ('%s.part%d' % (original_file, partnum)))
        chunk  = __read_write_block(fromfile, read, tofile, offset)
        partnum += 1
        read    += chunksize

#### Private methods

def __read_write_block(fromfile, n, tofile, offset = 0):
    stream = open(fromfile, 'rb')
    stream.seek(offset, 1)
    chunk = stream.read(n)
    stream.close()
    if not chunk: return

    fileobj = open(tofile, 'wb')
    fileobj.write(chunk)
    fileobj.close()
    return fileobj

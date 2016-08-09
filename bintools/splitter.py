import os

# Splits a file using the dsplit mechanism
def dsplit(fromfile, todir, chunksize = 1024):
    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts

    original_file = os.path.basename(fromfile)
    filesize = os.path.getsize(fromfile)
    cont = True
    partnum = 0
    while cont:
        if chunksize > filesize:
            cont = False
            chunksize = filesize
        chunk = __read_write_block(fromfile, chunksize)
        if not chunk: break
        partnum  = partnum + 1
        filename = os.path.join(todir, ('%s.part%d' % (original_file, partnum)))
        fileobj  = open(filename, 'wb')
        fileobj.write(chunk)
        fileobj.close()
        chunksize *= 2

#### Private methods

def __read_write_block(f, n):
    stream = open(f, 'rb')
    chunk = stream.read(n)
    stream.close()
    return chunk

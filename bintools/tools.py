
def dump(filename, start, end):
  f = open(filename, 'rb')
  f.seek(start, 1)
  data = f.read(end - start)
  f.close()
  return data

def hexdump(filename, start, end):
  data = dump(filename, start, end)
  shex = ""
  for byte in data:
    shex += format(ord(byte), 'x') + " "
  return start + ": " + shex
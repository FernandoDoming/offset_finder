
def dump(filename, start, end):
  f = open(filename, 'rb')
  f.seek(start, 1)
  data = f.read(end - start)
  f.close()
  return data

def hexdump(filename, start, end):
  data = dump(filename, start, end)
  return format(ord(byte), 'x')

def print_dump(data, addr=None):
  shex = ""
  for byte in data:
    shex += format(ord(byte), 'x') + " "
  if addr: shex = addr + ": " + shex
  print(shex)
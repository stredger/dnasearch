import sys


def unmathtable(inf, of):
  fd = open(inf)
  lines = fd.readlines()
  fd.close()
  fd = open(of, 'w')
  for l in lines:
    if '$' == l[0]:
      parts = l.split(' & ')
      parts[0] = parts[0].strip('$')
      parts[1] = parts[1].strip('$')
      parts[2] = parts[2].strip('$')
      l = ' & '.join(parts)
    fd.write(l)




if __name__ == '__main__':
  globals()[sys.argv[1]](*sys.argv[2:])

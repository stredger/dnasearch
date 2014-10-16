

from common import *
import sagefs
import sys


def GetFullFileList():
  fs = sagefs.SageFS()
  return fs.list()
  # files = fs.list()
  # fullfiles = []
  # for loc in files.keys():
  #   fullfiles += map(lambda f: ''.join(['/', loc, '/', f]), files[loc])
  # return fullfiles


def DetermineBowtie2Results():
  """ Creates a file '/vic/bowtie2results.txt' containing all 
  the valid matches found in the result .sam files """
  fs = sagefs.SageFS()
  btrfs = filter(lambda f: '.sam' in f, GetFullFileList())
  ofd = fs.open('/vic/bowtie2results.txt', create=True)
  ctr = 0
  for f in btrfs:
    ctr += 1
    ifd = fs.open(f)
    alllines = ifd.readlines()
    goodlines = filter(lambda dat: dat[0] != '@' and '\t' in dat, alllines)
    for gl in goodlines:
      lineparts = gl.split('\t')
      if lineparts[1] != '4':
        l_log('Found Alignment - ctr %d : %s' % (ctr, lineparts[:9]))
        ofd.write('\t'.join(lineparts))
      else:
        l_log('No Alignment - ctr %d : %s' % (ctr, lineparts[:9]))
    ifd.close()
  ofd.close()


def ReadBowtie2ResultsHeaders():
  fs = sagefs.SageFS()
  fd = fs.open('/vic/bowtie2results.txt')
  heads = [l.split('\t')[:9] for l in fd.readlines()]
  fd.close()
  return heads


def ParseMatchesFromCigar(cigstr):
  specialchars = ['M', 'S', 'I', 'D', 'N', 'H', 'P', '=', 'X']
  maxmatch = 0
  totmatch = 0
  totseq = 0
  numstr = ''
  for c in cigstr:
    if c in specialchars:
      num = int(numstr)
      totseq += num
      if c == 'M':
        if num > maxmatch:
          maxmatch = num
        totmatch += num
      numstr = ''
    else:
      numstr += c
  return [maxmatch, totmatch, totseq]


def FindVirusesFromResults(heads):
  # fullheads are the headers with the virus strain appeneded to the back
  fullheads = [h + [h[0].split('|')[-2].replace('.1', '.fna')] for h in heads]
  files = GetFullFileList()
  # midheads are fullheads with the path to the virus file appeneded
  midheads = []
  for f in files:
    for h in fullheads:
      if h[-1] in f:
        midheads.append(h + [f])
  # trueheads have the match info appeneded
  trueheads = []
  for h in midheads:
    trueheads.append(h + ParseMatchesFromCigar(h[5]))
  return trueheads



def PrintResults(res):
  for r in res:
    n = r[-4].split('/')[-2:] + [r[2]] + r[-3:]
    for e in n[:-1]:
      print str(e).split('.')[0] + '\t',
    print n[-1]


def PrintMatches():
  heads = ReadBowtie2ResultsHeaders()
  res = FindVirusesFromResults(heads)
  print res
  PrintResults(res)


def PrintHeaders():
  print ReadBowtie2ResultsHeaders()


def ReadSageFile(f):
  fs = sagefs.SageFS()
  fd = fs.open(f)
  print fd.read()
  fd.close()


def GetMatchesFromSam(fd):
  alllines = fd.readlines()
  goodlines = filter(lambda dat: dat[0] != '@' and '\t' in dat, alllines)
  headers = [gl.split('\t')[:9] for gl in goodlines]
  res = FindVirusesFromResults(headers)
  print res
  PrintResults(res)


def GetMatchesFromFile(fullpath):
  fs = sagefs.SageFS()
  fd = fs.open(fullpath)
  GetMatchesFromSamFile(fd)



if __name__ == '__main__':
  globals()[sys.argv[1]](*sys.argv[2:])
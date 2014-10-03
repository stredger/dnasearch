
import requests
import sagefs
import re
import urlparse
import os
import sys
import socket

from common import *


def GetFilesystem():
  return sagefs.SageFS()


def GenerateUrl(baseurl, *resourceparts):
  if '://' not in baseurl: baseurl += '://'
  if baseurl[-1] != '/': baseurl += '/'
  return ''.join([baseurl, '/'.join(list(resourceparts))])


def RequestUrl(url):
  resp = requests.get(url)
  if not resp.ok:
    raise Exception('Failed to get: %s' % (url))
  return resp.content


def FindLinks(html, startstr='<a href="', endstr='">'):
  linkregex = re.compile(''.join([startstr, '.*', endstr]))
  return [l[len(startstr):-len(endstr)] for l in re.findall(linkregex, html)]  


@LogLevelFunction
@ExceptionCapture
def _GetSequenceFile(url, link, f, fs, rootdir, loc):
  t_log('Downloading %s' % (f))
  seq = RequestUrl(GenerateUrl(url, f))
  s_log()
  fname = ''.join(['/', loc, '/', rootdir, link, f])
  fd = fs.open(fname, inmem=True, create=True)
  fd.write(seq, sync=False)
  t_log('Writing file to: %s' % (fname))
  fd.close()
  s_log()


@LogLevelFunction
@ExceptionCapture
def GetSequenceFiles(url, link, rootdir, filterfn=lambda x: True, loc='/local/'):
  l_log('Crawling %s' % (url))
  links = FindLinks(RequestUrl(url))
  files = filter(filterfn, links)
  l_log('Found %d files to download: %s' % (len(files), files))
  fs = GetFilesystem()
  for f in files:
    _GetSequenceFile(url, link, f, fs, rootdir, loc)


def GetAllGenomes(url, filterfn, rootdir, loc):
  l_log('Starting to crawl %s' % (url))
  links = FindLinks(RequestUrl(url))
  l_log('Found %d links to traverse' % (len(links)))
  for link in links:
    GetSequenceFiles(GenerateUrl(url, link), link, rootdir, filterfn, loc)


def GetFractionOfGenomes(url, filterfn, rootdir, totalparts, part, loc):
  l_log('Starting to crawl %s' % (url))
  links = FindLinks(RequestUrl(url))
  numlinks = len(links)
  numparts = numlinks // totalparts
  startpos = numparts*(part-1)
  if part == totalparts:
    # add the extras to the last part
    numparts += numlinks - (numparts*totalparts)
  endpos = startpos + numparts
  links = links[startpos:endpos]
  l_log('Found %d links to traverse' % (len(links)))
  for link in links:
    GetSequenceFiles(GenerateUrl(url, link), link, rootdir, filterfn, loc)


def GetAllVirusGenomes(loc):
  url = GenerateUrl('http', 'ftp.ncbi.nih.gov/genomes/Viruses')
  filterfn = lambda f: os.path.splitext(f)[-1] in ['.fna', '.fa']
  GetAllGenomes(url, filterfn, 'Virus/', loc)


def GetFractionOfVirusGenomes(totalparts, part, loc):  
  url = GenerateUrl('http', 'ftp.ncbi.nih.gov/genomes/Viruses')
  filterfn = lambda f: os.path.splitext(f)[-1] in ['.fna', '.fa']
  GetFractionOfGenomes(url, filterfn, 'Virus/', totalparts, part, loc)


def GetAllHumanChromosomes(loc):
  url = GenerateUrl('http', 'ftp.ncbi.nih.gov/genomes/Homo_sapiens')
  filterfn = lambda f: 'hs_ref_GRCh' in f and '.fa.gz' in f
  GetAllGenomes(url, filterfn, 'Human/', loc)


def GetFractionOfHumanChromosomes(totalparts, part, loc):
  url = GenerateUrl('http', 'ftp.ncbi.nih.gov/genomes/Homo_sapiens')
  filterfn = lambda f: 'hs_ref_GRCh' in f and '.fa.gz' in f
  GetFractionOfGenomes(url, filterfn, 'Human/', totalparts, part, loc)



if __name__ == '__main__':
  usage = 'ERROR'
  argc = len(sys.argv)
  if argc > 2:
    if sys.argv[1] == 'all':
      loc = sys.argv[3] if argc > 3 else 'local'
      if sys.argv[2] == 'virus':
        GetAllVirusGenomes(loc)
        sys.exit()
      elif sys.argv[2] == 'human':
        GetAllHumanChromosomes(loc)
        sys.exit()
    elif sys.argv[1] == 'frac' and argc > 4:
      loc = sys.argv[5] if argc > 5 else 'local'
      if sys.argv[2] == 'virus':
        GetFractionOfVirusGenomes(int(sys.argv[3]), int(sys.argv[4]), loc)
        sys.exit()
      elif sys.argv[2] == 'human':
        GetFractionOfHumanChromosomes(int(sys.argv[3]), int(sys.argv[4]), loc)
        sys.exit()
  print usage



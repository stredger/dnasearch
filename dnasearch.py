 
import sagefs
import subprocess
import os
import sys

from common import *


def ShellCommand(args):
  t_log('Executing: " %s "' % (args))
  p = subprocess.Popen(args)
  out, _ = p.communicate()
  if p.returncode:
    raise Exception('Process " %s " returned with: %d' % (' '.join(args), p.returncode))
  s_log()
  return out


@LogLevelFunction
def SetupDirs(dirs):
  cmd = 'mkdir -p %s' % (' '.join(dirs))
  ShellCommand(cmd.split())


@LogLevelFunction
def Unzip(fname):
  path, base = os.path.split(fname)
  cmd = 'gunzip -f %s' % (fname)
  ShellCommand(cmd.split())


@LogLevelFunction
@ExceptionCapture
def AlignSequenceWithMUMmer(refseq, queryseq, outfileprefix, toolpath):
  cmd = '%s %s %s %s' % (os.path.join(toolpath, 'run-mummer3'), refseq, queryseq, outfileprefix)
  ShellCommand(cmd.split())


@LogLevelFunction
@ExceptionCapture
def AlignSequenceWithBowtie2(indexprefix, queryfile, outfile, toolpath):
  cmd = '%s -f --local -x %s -U %s -S %s' % (os.path.join(toolpath, 'bowtie2'), indexprefix, queryfile, outfile)
  ShellCommand(cmd.split())


@LogLevelFunction
@ExceptionCapture
def DownloadChromosomes():
  fs = sagefs.SageFS()
  t_log('Getting Chromosome File List')
  flist = fs.list()
  files = []
  for loc in flist.keys():
    files += map(lambda x: ''.join(['/', loc, '/', x]), filter(lambda x: 'Human/' in x, flist[loc]))
  s_log()
  fnames = []
  for f in files:
    t_log('Downloading %s' % (f))
    fd = fs.open(f)
    s_log()
    fname = 'chroms/' + f.split('_')[-1]
    t_log('Writing to disk as %s' % (fname))
    fd.todisk(fname, overwrite=True)
    s_log()
    fd.close()
    l_log('Unzipping %s' % (fname))
    Unzip(fname)
    fnames.append(fname)
  return fnames


@LogLevelFunction
@ExceptionCapture
def GetVirusList(loc):
  fs = sagefs.SageFS()
  t_log('Getting Virus File List')
  files = map(lambda x: ''.join(['/', loc, '/', x]), filter(lambda x: 'Virus/' in x, fs.list(''.join(['/', loc, '/']))))
  s_log()
  return files


@LogLevelFunction
@ExceptionCapture
def DownloadVirusGenome(f):
  fs = sagefs.SageFS()
  t_log('Downloading %s' % (f))
  fd = fs.open(f)
  s_log()
  fname = 'virus/' + '_'.join(f.split('/')[2:])
  t_log('Writing to disk as %s' % (fname))
  fd.todisk(fname, overwrite=True)
  s_log()
  fd.close()
  return fname


@LogLevelFunction
@ExceptionCapture
def UploadMUMmerOutputFiles(prefix, loc):
  fs = sagefs.SageFS()
  for suffix in ['.out']: #, '.align', '.errorsgaps', '.gaps']:
    fname = prefix + suffix
    lfd = open(fname)
    sfd = fs.open(''.join(['/', loc, '/', fname]), create=True)
    t_log('Uploading %s' % (sfd.sagename))
    sfd.write(lfd.read(), sync=False)
    lfd.close()
    sfd.close()
    s_log()


@LogLevelFunction
@ExceptionCapture
def UploadBowtie2OutputFiles(fname, loc):
  fs = sagefs.SageFS()
  lfd = open(fname)
  sfd = fs.open(''.join(['/', loc, '/', os.path.basename(fname)]), create=True)
  t_log('Uploading %s' % (sfd.sagename))
  sfd.write(lfd.read(), sync=False)
  lfd.close()
  sfd.close()
  s_log()


def SearchDnaWithMUMmer(loc, mummerloc):
  chromfiles = ['chroms/'+cf+'.fa' for cf in ['chr'+str(i) for i in xrange(1,23) ] + ['chr'+s for s in ['MT', 'Un', 'X', 'Y']]]
  l_log('Performing Alignments against: %s' % (chromfiles))
  files = GetVirusList(loc)
  for f in files:
    fname = DownloadVirusGenome(f)
    for cf in chromfiles:
      outfileprefix = os.path.join('results/', '_'.join([os.path.splitext(os.path.basename(cf))[0], 'X', os.path.splitext('_'.join(f.split('/')[-2:]))[0]]))
      AlignSequenceWithMUMmer(cf, fname, outfileprefix, mummerloc)
      UploadMUMmerOutputFiles(outfileprefix, loc)
    

def SearchDnaWithBowtie2(loc, bowtieloc):
  files = GetVirusList(loc)
  for f in files:
    fname = DownloadVirusGenome(f)
    outfile = os.path.join('results/', os.path.basename(fname).replace('.fna', '.sam'))
    AlignSequenceWithBowtie2(os.path.join(bowtieloc, 'refseq/hg19'), fname, outfile, bowtieloc)
    UploadBowtie2OutputFiles(outfile, loc)


if __name__ == '__main__':
  usage = 'ERROR'
  argc = len(sys.argv)
  if argc > 3:
    l_log('Setting Up Directories')
    SetupDirs(['virus', 'results'])
    l_log('Performing Alignments')
    if 'bowtie2' in sys.argv[1]:
      SearchDnaWithBowtie2(sys.argv[2], os.path.expanduser(sys.argv[3]))
    elif 'mummer' in sys.argv[1]:
      SearchDnaWithMUMmer(sys.argv[2], os.path.expanduser(sys.argv[3]))
    sys.exit()
  elif 'dlchroms' in sys.argv[1]:
    l_log('Setting Up Directories')
    SetupDirs(['chroms'])
    l_log('Downloading Chromosomes')
    DownloadChromosomes()
    sys.exit()
  
  print usage + ' : ' + str(sys.argv)




from fabric.api import *


hosts = {
  'pc24.utahddc.geniracks.net':'vic',
  'pc4.instageni.illinois.edu':'tor',
  'pc5.instageni.maxgigapop.net':'carl'
}

env.hosts = hosts.keys()
env.user = 'ig_111'
env.key_filename = 'keys/ig_111.pem'


def DeterminePlatform():
  plats = ['ubuntu', 'fedora']
  plat = run('python -m platform').lower()
  for p in plats:
    if p in plat:
      return p
  return None


def AptInstall(pkgs):
  sudo('apt-get install -y %s' % (pkgs))


def AptUpdate():
  with settings(warn_only=True):
    sudo('apt-get update')


def YumInstall(pkgs):
  sudo('yum install -y %s' % (pkgs))


def YumUpdate():
  with settings(warn_only=True):
    sudo('yum update')


def PkgInstall(pkgs):
  fs = {'ubuntu':AptInstall, 'fedora':YumInstall}
  fs[DeterminePlatform()](pkgs)


def WebGet(url):
  run('wget %s' % (url))


def GetRepo(url):
  run('git clone %s' % (url))


def PipInstall(pkgs):
  sudo('pip install %s' % (pkgs))


def GetPartNum():
  return 1 if hosts[env.host_string] == 'tor' else 2 if hosts[env.host_string] == 'vic' else 3


def SetupDependencies():
  PkgInstall('git python-setuptools')
  with settings(warn_only=True):
    GetRepo('https://github.com/stredger/sagefs.git')
  with cd('sagefs'):
    sudo('python setup.py install')


def SetupCrawler():
  SetupDependencies()
  run('mkdir -p bioinf')
  put('crawler.py', 'bioinf/crawler.py')
  put('common.py', 'bioinf/common.py')


def SetupSearcher():
  SetupDependencies()
  run('mkdir -p bioinf')
  put('dnasearch.py', 'bioinf/dnasearch.py')
  put('common.py', 'bioinf/common.py')



@parallel
def DownloadChromosomes():
  SetupSearcher()
  with cd('bioinf'):
    run('python dnasearch.py dlchroms')


@parallel
def GetVirusGenomes():
  SetupCrawler()
  part = GetPartNum()
  with cd('bioinf'):
    run('python crawler.py frac virus %d %d %s' % (len(hosts.keys()), part, hosts[env.host_string]))


@parallel
def GetHumanChromosomes():
  SetupCrawler()
  part = GetPartNum()
  if part == 1: return
  with cd('bioinf'):
    run('python crawler.py frac human %d %d %s' % (len(hosts.keys()), part, hosts[env.host_string]))


@parallel
def InstallMummer():
  v = '3.23'
  PkgInstall('gcc csh gcc-c++ perl make binutils')
  run('mkdir -p bioinf')
  with cd('bioinf'):
    WebGet('https://sourceforge.net/projects/mummer/files/mummer/%s/MUMmer%s.tar.gz/download -O MUMmer%s.tar.gz' % (v, v, v))
    run('tar xzf MUMmer%s.tar.gz' % (v))
    with cd('MUMmer%s' % (v)):
      run('make install')


@parallel
def InstallBowtie2():
  run('mkdir -p bioinf')
  PkgInstall('unzip')
  with cd('bioinf'):
    WebGet('http://sourceforge.net/projects/bowtie-bio/files/bowtie2/2.2.3/bowtie2-2.2.3-linux-x86_64.zip/download -O bowtie2.zip')
    run('unzip bowtie2.zip')
    with cd('bowtie2-2.2.3'):
      run('mkdir -p refseq')
      with cd('refseq'):
        WebGet('ftp://ftp.ccb.jhu.edu/pub/data/bowtie2_indexes/hg19.zip')
        run('unzip hg19.zip')


@parallel
def RunBowtie2Search():
  # SetupSearcher()
  with cd('bioinf'):
    run('python dnasearch.py bowtie2 %s %s' % (hosts[env.host_string], 'bowtie2-2.2.3'))


@parallel
def RunMummerSearch():
  SetupSearcher()
  with cd('bioinf'):
    run('python dnasearch.py mummer %s %s' % (hosts[env.host_string], 'MUMmer3.23'))


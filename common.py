loglevel = 0

def l_log(s, newline=True, ignoreLevel=False):
  s = str(s)
  if loglevel and not ignoreLevel: spaces = ' ' * 2 * loglevel
  else: spaces = ''
  if newline: print spaces + s
  else: print spaces + s,

def s_log():
  l_log('Success', ignoreLevel=True)

def t_log(s):
  l_log('%s ...' % (s), False)


def LogLevelFunction(fn):
  def Incrementer(*args, **kwargs):
    global loglevel
    loglevel += 1
    ret = fn(*args, **kwargs)
    loglevel -= 1
    return ret
  return Incrementer


def ExceptionCapture(fn):
  def Capture(*args, **kwargs):
    try:
      return fn(*args, **kwargs)
    except Exception, e:
      l_log('>> EXCEPTION <<')
      l_log(e)
      return None
  return Capture



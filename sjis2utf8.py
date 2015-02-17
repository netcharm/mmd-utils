#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# The MIT License (MIT)
#
# Copyright (c) <year> <copyright holders>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###############################################################################
# from __future__ import unicode_literals
from __future__ import division

import os
import sys

import codecs

def ShiftjisToUTF8_f(folder):
  cwd = os.path.abspath(os.getcwd())
  os.chdir(os.path.abspath(folder))
  print(folder)
  print('-' * 80)
  for item in os.listdir('.'):
    fullname = item
    try:
      if sys.version_info.major >= 3:
        f_old = str.encode(item).decode('utf8')
        f_new = str.encode(item).decode('utf8').encode('mbcs').decode('shiftjis')
      else:
        f_old = b'%s' % item
        f_new = f_old.decode('shiftjis')

      try:
        f_new.encode('gbk')
        os.rename(f_old, f_new)
      except:
        f_new = f_old
        pass
      fullname = f_new
      if sys.version_info.major >= 3:
        print('[%s] ==> [%s]' % (f_old, f_new))
      else:
        print(u'[%s] ==> [%s]' % (f_old.decode('gbk'), f_new))
    except:
      pass

    if os.path.isdir(fullname):
      ShiftjisToUTF8_f(fullname)

  print('=' * 80)
  # os.chdir('..')
  os.chdir(cwd)

def ShiftjisToUTF8_ft(folder):
  cwd = os.path.abspath(os.getcwd())
  os.chdir(os.path.abspath(folder))
  print(folder)
  print('-' * 80)
  for item in os.listdir('.'):
    fullname = item
    if sys.version_info.major >= 3:
      f_old = str.encode(item).decode('utf8')
      f_new = str.encode(item).decode('utf8').encode('mbcs').decode('shiftjis')
    else:
      f_old = b'%s' % item
      f_new = f_old.decode('shiftjis')
    os.rename(f_old, f_new)
    fullname = f_new
    if sys.version_info.major >= 3:
      print('[%s] ==> [%s]' % (f_old, f_new))
    else:
      print(u'[%s] ==> [%s]' % (f_old.decode('gbk'), f_new))

    if os.path.isdir(fullname):
      ShiftjisToUTF8_ft(fullname)
  print('=' * 80)
  # os.chdir('..')
  os.chdir(cwd)

def ShiftjisToUTF8(name):
  try:
    f_old = b'%s' % name
    f_new = f_old.decode('shiftjis')
    os.rename(f_old, f_new)
    print(u'[%s] ==> [%s]' % (f_old.decode('gbk'), f_new))
    return(f_new)
  except:
    return(f_old)
    pass

if __name__ ==  '__main__':
  ROOT = '.'
  if len(sys.argv) >= 2:
    ROOT = sys.argv[1]
  ShiftjisToUTF8_f(ROOT)

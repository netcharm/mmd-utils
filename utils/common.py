#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# The MIT License (MIT)
#
# Copyright (c) 2015 NetCharm <netcharm@gmail.com>
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
from __future__ import unicode_literals
from __future__ import division

import os
import sys

import cmath

import StringIO

import codecs

from PIL import Image, ImageFile, BmpImagePlugin


from pandac.PandaModules import *

# Shader.load(Shader.SLGLSL, './shaders/shader_v.sha', './shaders/shader_f.sha' )
Shader.load(Shader.SLGLSL, './shaders/phong.vert', './shaders/phong.frag' )


DEBUG = True
DEBUG = False

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])

JIS2GBK = dict({
  u'\uff77\uff9e': u'ギ',
  u'\u30bf\uff9e': u'ダ',
  u'\u30db\uff9e': u'ボ',
  u'\u30f3\uff9e': u'ゾ',
  u'\u30af': u'ク',
  u'\u30bf': u'タ',
  u'\u30f3': u'ン',
  u'\u30fb': u'·',
  u'\ufeff': u'',
  u'\uff11': u'1',
  u'\uff12': u'2',
  u'\uff13': u'3',
  u'\uff14': u'4',
  u'\uff29': u'I',
  u'\uff2b': u'K',
  u'\uff68': u'イ',
  u'\uff6d': u'ユ', #ュ
  u'\uff6f': u'シ',
  u'\uff70': u'-',
  u'\uff71': u'ア',
  u'\uff72': u'イ',
  u'\uff73': u'ゥ',
  u'\uff74': u'エ',
  u'\uff75': u'ォ',
  u'\uff76': u'カ',
  u'\uff77': u'キ', # ｷ
  u'\uff78': u'ク',
  u'\uff7d': u'ス',
  u'\uff80': u'タ',
  u'\uff84': u'ト',
  u'\uff88': u'ネ',
  u'\uff89': u'ノ',
  u'\uff8a': u'ハ',
  u'\uff8b': u'ヒ',
  u'\uff8c': u'フ',
  u'\uff8d': u'ヘ',
  u'\uff8e': u'ホ',
  u'\uff8f': u'マ',
  u'\uff97': u'ラ',
  u'\uff98': u'リ',
  u'\uff9d': u'ン',
  u'\uff9e': u'\uff9e',
})

def log(info, force=False):
  if DEBUG or force:
    # print(repr(info))
    for k in JIS2GBK:
      info = info.replace(k, JIS2GBK[k])
    # print(repr(info))
    # print(info)
    try:
      print(info)
    except:
      print(repr(info))

_i16, _i32 = BmpImagePlugin.i16, BmpImagePlugin.i32

class BmpAlphaImageFile(ImageFile.ImageFile):
  format = "BMP+Alpha"
  format_description = "BMP with full alpha channel"

  def _open(self):
    s = self.fp.read(14)
    if s[:2].decode('utf8') != u'BM'.decode('utf8'):
        raise SyntaxError("Not a BMP file")
    offset = _i32(s[10:])

    self._read_bitmap(offset)

  def _read_bitmap(self, offset):
    s = self.fp.read(4)
    s += ImageFile._safe_read(self.fp, _i32(s) - 4)

    if len(s) not in (40, 108, 124):
      # Only accept BMP v3, v4, and v5.
      raise IOError("Unsupported BMP header type (%d)" % len(s))

    bpp = _i16(s[14:])
    if bpp != 32:
      # Only accept BMP with alpha.
      raise IOError("Unsupported BMP pixel depth (%d)" % bpp)

    compression = _i32(s[16:])
    if compression == 3:
      # BI_BITFIELDS compression
      mask = (_i32(self.fp.read(4)), _i32(self.fp.read(4)),
              _i32(self.fp.read(4)), _i32(self.fp.read(4)))
      # XXX Handle mask.
    elif compression != 0:
      # Only accept uncompressed BMP.
      raise IOError("Unsupported BMP compression (%d)" % compression)

    self.mode, rawmode = 'RGBA', 'BGRA'

    self.size = (_i32(s[4:]), _i32(s[8:]))
    direction = -1
    if s[11] == '\xff':
      # upside-down storage
      self.size = self.size[0], 2**32 - self.size[1]
      direction = 0

    self.info["compression"] = compression

    # data descriptor
    self.tile = [("raw", (0, 0) + self.size, offset, (rawmode, 0, direction))]

  pass

def loadTexture(tex_file, model_path=None):
  texture = None #Texture('NULL')
  try:
    if model_path:
      tex_file = os.path.relpath(tex_file, CWD)
    else:
      tex_file = os.path.join(model_path, tex_file)
  except:
    pass

  if tex_file and os.path.isfile(tex_file):
    tex_ext = os.path.splitext(tex_file)[1]
    if os.altsep:
      tex_file = tex_file.replace(os.path.sep, os.path.altsep)
    if tex_ext.lower() in ['.spa', '.sph', '.bmp']:
      try:
        im = BmpAlphaImageFile(tex_file)
        buf = StringIO.StringIO()
        im.save(buf, 'PNG')

        pnm = PNMImage()
        pnm.read(StringStream(buf.getvalue()))
        buf.close()
      except:
        texFile = Filename.fromOsSpecific(tex_file)
        Filename.makeCanonical(texFile)
        pnm = PNMImage(texFile)
      texture = Texture(tex_file)
      texture.load(pnm)
    else:
      texFile = Filename.fromOsSpecific(tex_file)
      Filename.makeCanonical(texFile)
      pnm = PNMImage(texFile)
      texture = Texture(tex_file)
      texture.load(pnm)

    texture.setFilename(tex_file)

    texture.generateRamMipmapImages()
    texture.setMagfilter(Texture.FTNearestMipmapNearest)
    texture.setMinfilter(Texture.FTNearestMipmapNearest)
    # texture.setAnisotropicDegree(30)
  return(texture)
  pass

def loadJ2ETable(j2e_file):
  with codecs.open(j2e_file, 'r', encoding='utf8') as f:
    lines = f.readlines()

  J2E = dict()
  for line in lines:
    item = line.split(',')
    j = item[0].strip().decode('utf8')
    e = item[1].strip()
    # log(u'%s <-> %s' % (j, e), force=True)
    J2E[j] = e
    J2E[e] = j

  return(J2E)
  pass

cD2R = 180/cmath.pi
def V2V(vertex, euler=Vec3(1,1,1)):
  # if ZUp:
  return(Vec3(euler.x*vertex.x, euler.y*vertex.z, euler.z*vertex.y))

def R2D(rad, euler=Vec3(1,1,1)):
  return(Vec3(euler.x*rad.x*cD2R if not cmath.isnan(rad.x) else 0,
              euler.y*rad.y*cD2R if not cmath.isnan(rad.y) else 0,
              euler.z*rad.z*cD2R if not cmath.isnan(rad.z) else 0))

def R2DV(rad, euler=Vec3(1,-1,-1)):
  return(Vec3(euler.x*rad.y*cD2R if not cmath.isnan(rad.y) else 0,
              euler.z*rad.x*cD2R if not cmath.isnan(rad.x) else 0,
              euler.y*rad.z*cD2R if not cmath.isnan(rad.z) else 0))

def D2D(rad, euler=Vec3(1,1,1)):
  return(Vec3(euler.x*rad.x if not cmath.isnan(rad.x) else 0,
              euler.y*rad.y if not cmath.isnan(rad.y) else 0,
              euler.z*rad.z if not cmath.isnan(rad.z) else 0))

def vdist(v1, v2):
  return(abs(cmath.sqrt((v2.x-v1.x)**2 + (v2.y-v1.y)**2 + (v2.z-v1.z)**2 ).real))

if __name__ == '__main__':
  pmxFile = u'../models/meiko/meiko.pmx'
  pmxFile = u'../models/apimiku/Miku long hair.pmx'
  # pmxFile = u'../models/cupidmiku/Cupid Miku.pmx'

  pmxFile = u'../models/alice/alice.pmd'

  if len(sys.argv) > 1:
    if len(sys.argv[1]) > 0:
      pmxFile = sys.argv[1]

  ext = os.path.splitext(pmxFile)[1].lower()
  if ext in ['.pmd']:
    testPMD(pmxFile)
  elif ext in ['.pmx']:
    testPMX(pmxFile)

  # testPMD(pmdFile)


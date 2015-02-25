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
  u'\u30fb': u'·',
  u'\uff77\uff9e': u'ギ',
  u'\uff68': u'イ',
  u'\uff73': u'ゥ',
  u'\uff77': u'キ', # ｷ
  u'\uff78': u'ク',
  u'\uff9d': u'ン',
  u'\uff6d': u'ユ', #ュ
  u'\uff6f': u'シ',
  u'\uff98': u'リ',
  u'\uff9e': u'\uff9e',
})

def log(info, force=False):
  if DEBUG or force:
    # print(repr(info))
    for k in JIS2GBK:
      info = info.replace(k, JIS2GBK[k])
    # print(repr(info))
    print(info)

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

def loadTexture(tex_file):
  texture = None #Texture('NULL')
  tex_file = os.path.relpath(tex_file)
  if tex_file and os.path.isfile(tex_file):
    tex_ext = os.path.splitext(tex_file)[1]
    if tex_ext.lower() in ['.spa', '.sph', '.bmp']:
      try:
        im = BmpAlphaImageFile(tex_file)
        buf = StringIO.StringIO()
        im.save(buf, 'PNG')

        pnm = PNMImage()
        pnm.read(StringStream(buf.getvalue()))
        buf.close()
      except:
        # pnm = PNMImage(Filename.toOsSpecific(tex_file))
        pnm = PNMImage(tex_file)
      texture = Texture(tex_file)
      texture.load(pnm)
    else:
      # pnm = PNMImage(Filename.toOsSpecific(tex_file))
      pnm = PNMImage(tex_file)
      texture = Texture(tex_file)
      texture.load(pnm)

    texture.setFilename(tex_file)
    # texture.generateRamMipmapImages()
    # texture.setMinfilter(Texture.FTNearestMipmapNearest)
    # texture.setRenderToTexture(True)
  return(texture)
  pass

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


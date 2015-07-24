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

import math
import cmath

import unicodedata as unidata
import romkan

from jTransliterate import JapaneseTransliterator

import urllib
import json

import StringIO

import codecs

from PIL import Image, ImageFile, BmpImagePlugin


from panda3d.core import *


DEBUG = True
DEBUG = False

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])

shader_v = os.path.relpath(os.path.join(os.path.dirname(__file__), u'../shaders/phong.vert'), CWD)
shader_f = os.path.relpath(os.path.join(os.path.dirname(__file__), u'../shaders/phong.frag'), CWD)
if os.path.altsep:
  shader_v = shader_v.replace(os.path.sep, os.path.altsep)
  shader_f = shader_f.replace(os.path.sep, os.path.altsep)
Shader.load(Shader.SLGLSL, shader_v, shader_f)
print(u'Loading shader, Vertex: %s, Fragment: %s' % (shader_v, shader_f))

colorSelected = LVector4f(1, 0.95, 0, 1)
colorBone = LVector4f(0.12, 1, 0.44, 1)


JIS_KATAKANA_H2F = dict()
jis_katakana_h2f_file = os.path.join(CWD, 'utils', 'jis_katakana_h2f.json')
if os.path.isfile(jis_katakana_h2f_file):
  with open(jis_katakana_h2f_file, 'rt') as f:
    JIS_KATAKANA_H2F = json.load(f)
else:
  print(u'File is not exists : %s' % jis_katakana_h2f_file)

JIS2GBK = dict({
  u'\x8f\xe3': u'a', # ã
  # u'\x8f': u'a', # 
  u'\xab': u'《', # «
  u'\xaf': u'￣', # ¯
  u'\xb0': u'°', # º¼
  u'\xbb': u'》', # »
  u'\xbc': u'°',
  u'\xba': u'°', # º
  u'\xcc': u'I', # Ì
  # u'\xe3': u'a', # ã
  u'\u017d': u'Z', # Ž,
  u'\u02dc': u'~',
  u'\u2018': u'‘',
  u'\u201a': u',',
  u'\u201b': u'’',
  u'\u201c': u'“',
  u'\u201d': u'”',
  u'\u2030': u'‰',
  u'\u226a': u'《', # ≪
  u'\u226b': u'》', # ≫
  u'\u30bf\uff9e': u'ダ',
  u'\u30db\uff9e': u'ボ',
  u'\u30f3\uff9e': u'ゾ',
  u'\uff77\uff9e': u'ギ',
  u'\u300b': u'》',
  u'\u3095': u'か',
  u'\u3096': u'け',
  u'\u3099': u'゛',
  u'\u309b': u'ダ',
  u'\u309c': u'゜',
  u'\u309d': u'ゝ',
  u'\u309e': u'ゞ',
  u'\u309f': u'より',
  u'\u30a4': u'イ',
  u'\u30ad': u'キ',
  u'\u30af': u'ク',
  u'\u30b3': u'コ',
  u'\u30b7': u'シ',
  u'\u30b8': u'ジ',
  u'\u30b9': u'ス',
  u'\u30bb': u'セ',
  u'\u30bf': u'タ',
  u'\u30c8': u'ト',
  u'\u30cf': u'ハ',
  u'\u30d2': u'ヒ',
  u'\u30d5': u'フ',
  u'\u30d8': u'ヘ',
  u'\u30df': u'ミ',
  u'\u30c1': u'チ',
  u'\u30c8': u'ト',
  u'\u30e4': u'ヤ',
  u'\u30e6': u'ユ',
  u'\u30f3': u'ン',
  u'\u30f7': u'ぁ',
  u'\u30f8': u'ヰ゛', # ヴぃ / ヴィ
  u'\u30f9': u'ヱ゛', # ヴぇ / ヴェ
  u'\u30fa': u'ヲ゛', # ヴぉ / ヴォ
  u'\u30fb': u'·',
  u'\ufeff': u'',
  u'\uff11': u'1',
  u'\uff12': u'2',
  u'\uff13': u'3',
  u'\uff14': u'4',
  u'\uff29': u'I',
  u'\uff2b': u'K',
  u'\uff68': u'イ',
  u'\uff6a': u'エ',
  u'\uff6b': u'オ',
  u'\uff6c': u'ヤ', #ャ
  u'\uff6d': u'ユ', #ュ
  u'\uff6e': u'ヨ',
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
  u'\uff7a': u'コ',
  u'\uff7c': u'シ',
  u'\uff7d': u'ス',
  u'\uff7e': u'セ',
  u'\uff7f': u'ソ',
  u'\uff80': u'タ',
  u'\uff81': u'チ',
  u'\uff82': u'ツ',
  u'\uff83': u'テ',
  u'\uff84': u'ト',
  u'\uff85': u'ナ',
  u'\uff86': u'ニ',
  u'\uff87': u'ヌ',
  u'\uff88': u'ネ',
  u'\uff89': u'ノ',
  u'\uff8a': u'ハ',
  u'\uff8b': u'ヒ',
  u'\uff8c': u'フ',
  u'\uff8d': u'ヘ',
  u'\uff8e': u'ホ',
  u'\uff8f': u'マ',
  u'\uff90': u'ミ',
  u'\uff92': u'メ',
  u'\uff93': u'モ',
  u'\uff94': u'ヤ',
  u'\uff95': u'ユ',
  u'\uff96': u'ヨ',
  u'\uff97': u'ラ',
  u'\uff98': u'リ',
  u'\uff99': u'ル',
  u'\uff9a': u'レ',
  u'\uff9b': u'ロ',
  u'\uff9c': u'ワ',
  u'\uff9d': u'ン',
  u'\uff9e': u'゛',
  u'\uff9f': u'°',

})

def encode(url):
  url_e = url.replace(r' ', '%20')
  return(url_e)

def toGBK(text):
  gbk = ''
  for c in text:
    # gbk += JIS2GBK[c] if c in JIS2GBK else c;
    if c in JIS_KATAKANA_H2F:
      gbk += JIS_KATAKANA_H2F[c]
    elif c in JIS2GBK:
      gbk += JIS2GBK[c]
    else:
      gbk += c

  return(gbk)


def log(info, force=False):
  if DEBUG or force:
    info = toGBK(info)
    try:
      print(info.strip())
    except:
      print(repr(info.strip()))


#
# 32bits RGBA Bitmap support
#
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
    if s[11] == r'\xff':
      # upside-down storage
      self.size = self.size[0], 2**32 - self.size[1]
      direction = 0

    self.info["compression"] = compression

    # data descriptor
    self.tile = [("raw", (0, 0) + self.size, offset, (rawmode, 0, direction))]

  pass


def bmp2png(bmpfile):
  pngfile = bmpfile
  fn = os.path.splitext(bmpfile)
  name = fn[0]
  ext = fn[1]
  if ext.lower() in ['.spa', '.sph', '.bmp']:
    try:
      im = BmpAlphaImageFile(bmpfile)
    except:
      im = Image.open(bmpfile)
    pngfile = u'%s.png' % name
    im.save(pngfile, 'PNG')
    log('Converted %s to %s' % (bmpfile, pngfile))

  return(pngfile)

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
    if tex_ext.lower() in ['.dds']:
      try:
        with open(tex_file, 'rb') as f:
          buf = f.read()
          ts = StringStream(buf)       # turn into an istream
          texture = Texture()               # create texture object
          texture.readDds(ts, tex_file)     # load texture from dds ram image
      except:
        print('dds error!')
    elif tex_ext.lower() in ['.spa', '.sph', '.bmp']:
      try:
        try:
          im = BmpAlphaImageFile(tex_file)
        except:
          im = Image.open(tex_file)
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
      try:
        pnm = PNMImage(texFile)
        texture = Texture(tex_file)
        texture.load(pnm)
      except:
        im = Image.open(tex_file)
        buf = StringIO.StringIO()
        im.save(buf, 'PNG')

        pnm = PNMImage()
        pnm.read(StringStream(buf.getvalue()))
        buf.close()

        texture = Texture(tex_file)
        texture.load(pnm)

    texture.setFilename(tex_file)
    # texture.setCompression(Texture.CMOn)
    texture.compressRamImage()
    texture.setMatchFramebufferFormat(True)
  return(texture)
  pass

def hasAlpha(texture):
  return(texture.getFormat() in [Texture.FRgba, Texture.FRgbm, Texture.FRgba4, Texture.FRgba5, Texture.FRgba8, Texture.FRgba12, Texture.FRgba16, Texture.FRgba32])

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

def getHprFromTo(fromPt, toPt):
  """
  HPR to rotate *from* point to look at *to* point
  """

  # Translate points so that fromPt is origin
  pos2 = toPt - fromPt

  # Find which XY-plane quadrant toPt lies in
  #    +Y
  #    ^
  #  2 | 1
  # ---o---> +X
  #  3 | 4
  quad = 0

  if pos2.x < 0:
    if pos2.y < 0:
      quad = 3
    else:
      quad = 2
  else:
    if pos2.y < 0:
      quad = 4

  # Get heading angle
  ax   = abs( pos2.x )
  ay   = abs( pos2.y )
  head = math.degrees( math.atan2( ay, ax ) )

  # Adjust heading angle based on quadrant
  if 2 == quad:
    head = 180 - head
  elif 3 == quad:
    head = 180 + head
  elif 4 == quad:
    head = 360 - head

  # Compute roll angle
  v    = Vec3( pos2.x, pos2.y, 0 )
  vd   = abs( v.length() )
  az   = abs( pos2.z )
  roll = math.degrees( math.atan2( az, vd ) )

  # Adjust if toPt lies below XY-plane
  if pos2.z < 0:
    roll = - roll

  # Make HPR
  return Vec3( head, 0, -roll-90 )

def getHprFromToNP(fromNP, toNP):
  # Rotate Y-axis of *from* to point to *to*
  fromNP.lookAt( toNP )
  # Rotate *from* so X-axis points at *to*
  fromNP.setHpr( fromNP, Vec3( 90, 0, 0 ) )
  # Extract HPR of *from*
  return fromNP.getHpr()


if __name__ == '__main__':
  pass


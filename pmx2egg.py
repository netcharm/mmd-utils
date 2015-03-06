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

import StringIO

import codecs

from utils.common import *

from pymeshio import pmx
from pymeshio.pmx import reader as pmxReader

def pmxLoad(f_pmx):
  model = None
  if os.path.isfile(f_pmx):
    model = pmxReader.read_from_file(f_pmx)
  return(model)

def pmx2egg(pmx):
  modelname = os.path.basename(pmx.path)
  modelpath = os.path.dirname(pmx.path)

  lines = []
  #
  # make egg header
  #
  # lines.append('<CoordinateSystem> { Z-Up }')
  lines.append('<CoordinateSystem> { Y-up-left }')
  lines.append('')
  lines.append('<Comment> {')
  lines.append('  "%s"' % pmx.path)
  lines.append('}')
  lines.append('')
  #
  # load texture list
  #
  tex_mode = dict()
  for m in pmx.materials:
    tmode = ('Modulate', None)
    if m.texture_index >= 0:
      tex_mode[pmx.textures[m.texture_index]] = tmode
    if m.sphere_texture_index>=0:
      if m.sphere_mode > 0:
        if m.sphere_mode == 1:
          tmode = ('ModulateGlow', m.name+'_sphere')
        elif m.sphere_mode == 2:
          tmode = ('Add', m.name+'_sphere')
        elif m.sphere_mode == 3:
          tmode = ('Replace', m.name+'_sphere')
      tex_mode[pmx.textures[m.sphere_texture_index]] = tmode
    if m.toon_texture_index>=0:
      if m.toon_sharing_flag > 0:
        tmode = ('Glow', m.name+'_toon')
      tex_mode[pmx.textures[m.toon_texture_index]] = tmode
  #
  # load shared toon textures
  #
  idx = 0
  textures = []
  for tex in pmx.textures:
    if tex in tex_mode:
      tmode = tex_mode[tex]
    else:
      tmode = 'REPLACE'
    tex = os.path.basename(bmp2png(os.path.join(modelpath, tex)))
    lines.append('<Texture> tex_%04d {' % (idx))
    lines.append('  "%s"' % (tex))
    lines.append('  <Scalar> minfilter { NEAREST_MIPMAP_NEAREST }')
    lines.append('  <Scalar> magfilter { NEAREST_MIPMAP_NEAREST }')
    lines.append('  <Scalar> magfilteralpha { NEAREST_MIPMAP_NEAREST }')
    lines.append('  <Scalar> magfiltercolor { NEAREST_MIPMAP_NEAREST }')
    if tmode[1]:
      lines.append('  <Scalar> format { RGB }')
      lines.append('  <Scalar> wrapu { CLAMP }')
      lines.append('  <Scalar> envtype { %s }' % tmode[0])
      lines.append('  <Scalar> stage-name { %s }' % tmode[1])
      lines.append('  <Scalar> tex-gen { EYE_SPHERE_MAP}')
      lines.append('  <Scalar> alpha { ON }')
    else:
      lines.append('  <Scalar> format { RGBA }')
      lines.append('  <Scalar> envtype { ModulateGloss }')
      lines.append('  <Scalar> alpha { ON }')
    lines.append('  <Scalar> draw-order { 10000 }')
    lines.append('  <Transform> { <Scale> { 1 -1 1 } }')
    lines.append('}')
    textures.append(u'tex_%04d' % (idx))
    idx += 1
  lines.append('')
  idx = 0
  for toon in ['toon0.bmp', 'toon01.bmp', 'toon02.bmp', 'toon03.bmp', 'toon04.bmp', 'toon05.bmp', 'toon06.bmp', 'toon07.bmp', 'toon08.bmp', 'toon09.bmp', 'toon10.bmp']:
    tmode = ('Glow', 'ts_toon_%02d' % idx)
    tex = os.path.basename(bmp2png(os.path.join(modelpath, toon)))
    lines.append('<Texture> toon_%02d {' % (idx))
    lines.append('  "%s"' % (toon))
    lines.append('  <Scalar> minfilter { NEAREST_MIPMAP_NEAREST }')
    lines.append('  <Scalar> magfilter { NEAREST_MIPMAP_NEAREST }')
    lines.append('  <Scalar> magfilteralpha { NEAREST_MIPMAP_NEAREST }')
    lines.append('  <Scalar> magfiltercolor { NEAREST_MIPMAP_NEAREST }')
    lines.append('  <Scalar> format { RGB }')
    lines.append('  <Scalar> wrapu { CLAMP }')
    lines.append('  <Scalar> envtype { %s }' % tmode[0])
    lines.append('  <Scalar> stage-name { %s }' % tmode[1])
    lines.append('  <Scalar> tex-gen { EYE_SPHERE_MAP}')
    lines.append('  <Scalar> alpha { ON }')
    lines.append('  <Scalar> draw-order { 10000 }')
    lines.append('  <Transform> { <Scale> { 1 -1 1 } }')
    lines.append('}')
    textures.append(u'tex_%04d' % (idx))
    idx += 1
  lines.append('')
  #
  # load materials
  #
  idx = 0
  for m in pmx.materials:
    lines.append('<Material> "%s" {' % m.name)
    lines.append('  <Scalar> ambientr { %.8f }' % m.ambient_color.r)
    lines.append('  <Scalar> ambientg { %.8f }' % m.ambient_color.g)
    lines.append('  <Scalar> ambientb { %.8f }' % m.ambient_color.b)
    lines.append('  <Scalar> ambienta { %.8f }' % m.alpha)
    lines.append('  <Scalar> diffr { %.8f }' % m.diffuse_color.r)
    lines.append('  <Scalar> diffg { %.8f }' % m.diffuse_color.g)
    lines.append('  <Scalar> diffb { %.8f }' % m.diffuse_color.b)
    lines.append('  <Scalar> diffa { %.8f }' % m.alpha)
    lines.append('  <Scalar> emissionr { %.8f }' % m.edge_color.r)
    lines.append('  <Scalar> emissiong { %.8f }' % m.edge_color.g)
    lines.append('  <Scalar> emissionb { %.8f }' % m.edge_color.b)
    lines.append('  <Scalar> emissiona { %.8f }' % m.edge_color.a)
    lines.append('  <Scalar> specr { %.8f }' % m.specular_color.r)
    lines.append('  <Scalar> specg { %.8f }' % m.specular_color.g)
    lines.append('  <Scalar> specb { %.8f }' % m.specular_color.b)
    lines.append('  <Scalar> speca { %.8f }' % m.alpha)
    lines.append('  <Scalar> shininess { %.8f }' % m.specular_factor )
    lines.append('  <Scalar> local { 0 }')
    lines.append('}')
  lines.append('')
  #
  # load morph data
  #
  dxyz = dict()
  for morph in pmx.morphs:
    if morph.morph_type == 1:
      for idx in xrange(len(morph.offsets)):
        offset = morph.offsets[idx]
        v = pmx.vertices[offset.vertex_index].position
        o = offset.position_offset
        i = offset.vertex_index
        if i in dxyz:
          dxyz[i].append((morph.name, o))
        else:
          dxyz[i] = [(morph.name, o)]
  #
  # load vertices
  #
  idx = 0
  lines.append('<VertexPool> "%s" {' % pmx.name)
  for v in pmx.vertices:
    p = v.position
    uv = v.uv
    n = v.normal
    lines.append('  <Vertex> %d {' % idx)
    # lines.append('    %.8f %.8f %.8f' % (p.x, p.z, p.y))
    lines.append('    %.8f %.8f %.8f' % (p.x, p.y, p.z))
    lines.append('    <UV> { %.8f %.8f }' % (uv.x, uv.y))
    lines.append('    <Normal> { %.8f %.8f %.8f }' % (n.x, n.y, n.z))
    lines.append('    <RGBA> { 1 1 1 1 }')
    if idx in dxyz:
      for vm in dxyz[idx]:
        lines.append('    <Dxyz> "%s" { %.8f %.8f %.8f }' % (vm[0], vm[1].x, vm[1].y, vm[1].z))
    lines.append('  }')
    idx += 1
  lines.append('}')
  lines.append('')
  #
  # load face polygon
  #
  vIndex = 0
  lines.append('<Group> "%s" {' % pmx.name)
  lines.append('  <Dart> { 1 }')
  lines.append('  <Group> "Body" {')
  for m in pmx.materials:
    lines.append('    <Group> "%s" {' % m.name)
    for idx in xrange(vIndex, vIndex+m.vertex_count, 3):
      lines.append('      <Polygon> {')
      lines.append('        <VertexRef> { %d %d %d <Ref> { %s } }' % ( pmx.indices[idx], pmx.indices[idx+1], pmx.indices[idx+2], pmx.name))
      lines.append('        <MRef> { "%s" }' % (m.name))
      if   m.flag & 0x00000001:
        lines.append('        <BFace> { 1 }')
      if m.texture_index >= 0:
        lines.append('        <TRef> { "%s" }' % (textures[m.texture_index]))
      if m.sphere_texture_index >= 0:
        lines.append('        <TRef> { "%s" }' % (textures[m.sphere_texture_index]))
      if m.toon_sharing_flag > 0:
        if m.toon_texture_index >= 0:
          lines.append('        <TRef> { "%s" }' % (textures[m.toon_texture_index]))
      else:
        if m.toon_texture_index > 0:
          lines.append('        <TRef> { "%s" }' % (u'toon_%02d' % m.toon_texture_index))
        else:
          lines.append('        <TRef> { "%s" }' % (u'toon_00'))
      lines.append('      }')
    lines.append('    }')
    vIndex += m.vertex_count
  lines.append('  }')
  #
  # load bone data
  #
  idx = 0
  lines.append('<Joint> %s {' % 'aa')
  boneRelative = dict()
  for bone in pmx.bones:
    if bone.parent_index in boneRelative:
      boneRelative[bone.parent_index].append()
    else:
      boneRelative[bone.parent_index] = dict()
    pass

  lines.append('}')
  lines.append('')

  #
  # make animation data
  #
  idx = 0
  lines.append('<Table> expressions {')
  for morph in pmx.morphs:
    lines.append('  <Bundle> "%s" {' % pmx.name)
    lines.append('    <Table> morph {')
    lines.append('      <S$Anim> "%s" {' % morph.name)
    lines.append('        <Scalar> fps { 5 }')
    lines.append('        <V> { 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 }')
    lines.append('      }')
    lines.append('    }')
    lines.append('  }')
    idx += 1
  lines.append('}')
  lines.append('')
  #
  #
  #
  lines.append('')
  lines.append('')
  lines.append('')
  lines.append('')
  lines.append('')


  return(lines)
  return('\n'.join(lines))
  pass


if __name__ == '__main__':
  pmxfile = 'models/meiko/meiko.pmx'
  pmxmodel = pmxLoad(pmxfile)
  egg = pmx2egg(pmxmodel)

  with codecs.open('egg_test.egg', 'w') as f:
    f.writelines('\n'.join(egg))

  pass
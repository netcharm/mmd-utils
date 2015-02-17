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
from __future__ import unicode_literals
from __future__ import division

import os
import sys

import StringIO

import codecs

from PIL import Image, ImageFile, BmpImagePlugin


from pymeshio import pmm
from pymeshio.pmm import reader as pmmReader

from pymeshio import pmd
from pymeshio.pmd import reader as pmdReader

from pymeshio import pmx
from pymeshio.pmx import reader as pmxReader

from pymeshio import vmd
from pymeshio.vmd import reader as vmdReader


from pandac.PandaModules import *

DEBUG = True
DEBUG = False

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])

def log(info, force=False):
  if DEBUG or force:
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
      pnm = PNMImage(tex_file)
    texture = Texture(tex_file)
    texture.load(pnm)
  else:
    pnm = PNMImage(tex_file)
    texture = Texture(tex_file)
    texture.load(pnm)

  texture.generateRamMipmapImages()
  texture.setMinfilter(Texture.FTNearestMipmapNearest)
  # texture.setRenderToTexture(True)
  return(texture)
  pass

def pmxLoad(f_pmx):
  model = None
  if os.path.isfile(f_pmx):
    model = pmxReader.read_from_file(f_pmx)
  return(model)

def pmxInfo(model, screen=False):
  lines = []
  if isinstance(model, pmx.Model):
    lines.append(u'path         : %s' % model.path)
    lines.append(u'version      : %s' % model.version)
    lines.append(u'name(jpn)    : %s' % model.name.replace(u'\u30fb', u'·').strip())
    lines.append(u'name(eng)    : %s' % model.english_name.strip())
    lines.append(u'comment(jpn) : \n{0}\n{1}\n{0}'.format('-'*80, model.comment.replace(u'\u30fb', u'·').strip()))
    lines.append(u'comment(eng) : \n{0}\n{1}\n{0}'.format('-'*80, model.english_comment.strip()))
    lines.append(u'='*80)

    lines.append(u'textures     : Total {1}.\n{0}'.format('-'*80, len(model.textures)))
    idx = 0
    for texture in model.textures:
      lines.append('%4d : %s' % (idx, texture))
      idx += 1
    lines.append(u'='*80)

    lines.append(u'materials    : Total {1}.\n{0}'.format('-'*80, len(model.materials)))
    idx = 0
    for mat in model.materials:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn) : %s' % mat.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng) : %s' % mat.english_name.strip())
      lines.append(u'  diffuse   : (%s, %s, %s)' % (mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b))
      lines.append(u'  alpha     : %.2f' % mat.alpha)
      lines.append(u'  specular  : (%s, %s, %s), %.2f' % (mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, mat.specular_factor))
      lines.append(u'  ambient   : (%s, %s, %s)' %  (mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b))
      lines.append(u'  flag      : %s' % mat.flag)
      lines.append(u'  edge      : (%s, %s, %s, %s), %.2f' % (mat.edge_color.r, mat.edge_color.g, mat.edge_color.b, mat.edge_color.a, mat.edge_size))
      lines.append(u'  texture   : %4d' % mat.texture_index)
      lines.append(u'  sphere    : %4d, %4d' % (mat.sphere_mode, mat.sphere_texture_index))
      lines.append(u'  toon      : %4d, %4d' % (mat.toon_sharing_flag, mat.toon_texture_index))
      lines.append(u'  comment   : %s' % mat.comment.strip())
      lines.append(u'  vertexs   : %4d' % mat.vertex_count)
    lines.append(u'='*80)

    lines.append(u'bones        : Total {1}.\n{0}'.format('-'*80, len(model.bones)))
    idx = 0
    for bone in model.bones:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % bone.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)    : %s' % bone.english_name.strip())
      lines.append(u'  position     : %s' % str(bone.position.to_tuple()))
      lines.append(u'  parent_index : %4d' % bone.parent_index)
      lines.append(u'  layer        : %4d' % bone.layer)
      lines.append(u'  flag         : %4d' % bone.flag)
      lines.append(u'  tail         : %4d, %s' % (bone.tail_index, bone.tail_position.to_tuple()))
      lines.append(u'  effect       : %4d, %.4f' % (bone.effect_index, bone.effect_factor))
      lines.append(u'  fixed_axis   : %s' % str(bone.fixed_axis.to_tuple()))
      lines.append(u'  local_vector : x%s, z%s' % (bone.local_x_vector.to_tuple(), bone.local_z_vector.to_tuple()))
      lines.append(u'  external_key : %4d' % bone.external_key)
      if bone.ik:
        ik_links = map(lambda link: (link.bone_index, link.limit_angle, link.limit_max.to_tuple(), link.limit_min.to_tuple()), bone.ik.link)
        lines.append(u'  ik           : %.4f, %s, %4d, %4d' % (bone.ik.limit_radian, ik_links[:5], bone.ik.loop, bone.ik.target_index ))
      else:
        lines.append(u'  ik           : %s' % u'')
      lines.append(u'  index        : %4d' % bone.index)
    lines.append(u'='*80)

    lines.append(u'morphs       : Total {1}.\n{0}'.format('-'*80, len(model.morphs)))
    idx = 0
    for morph in model.morphs:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)  : %s' % morph.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)  : %s' % morph.english_name.strip())
      lines.append(u'  panel      : %4d' % morph.panel)
      lines.append(u'  morph_type : %4d' % morph.morph_type)
      ol = map(lambda offset: (offset.morph_index, offset.value) if isinstance(offset, pmx.GroupMorphData) else (offset.vertex_index, offset.position_offset.to_tuple()), morph.offsets)
      lines.append(u'  offsets    : %4d, %s' % (len(morph.offsets), ol[:5]))
    lines.append(u'='*80)

    lines.append(u'display_slot : Total {1}.\n{0}'.format('-'*80, len(model.display_slots)))
    idx = 0
    for slot in model.display_slots:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % slot.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)    : %s' % slot.english_name.strip())
      lines.append(u'  references   : %4d, %s' % (len(slot.references), str(slot.references)))
      lines.append(u'  special_flag : %4d' % slot.special_flag)
    lines.append(u'='*80)

    lines.append(u'rigidbodies  : Total {1}.\n{0}'.format('-'*80, len(model.rigidbodies)))
    idx = 0
    for rigidbody in model.rigidbodies:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)          : %s' % rigidbody.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)          : %s' % rigidbody.english_name.strip())
      lines.append(u'  bone_index         : %4d' % rigidbody.bone_index)
      lines.append(u'  collision_group    : %4d' % rigidbody.collision_group)
      lines.append(u'  no_collision_group : %4d' % rigidbody.no_collision_group)
      lines.append(u'  shape              : %4d, %s, %s, %s' % (rigidbody.shape_type, rigidbody.shape_size.to_tuple(), rigidbody.shape_position.to_tuple(), rigidbody.shape_rotation.to_tuple()))
      lines.append(u'  param              : %4d, %.4f, %.4f, %.4f, %.4f' % (rigidbody.param.mass, rigidbody.param.linear_damping, rigidbody.param.angular_damping, rigidbody.param.restitution, rigidbody.param.friction))
      lines.append(u'  mode               : %4d' % rigidbody.mode)
    lines.append(u'='*80)

    lines.append(u'joints       : Total {1}.\n{0}'.format('-'*80, len(model.joints)))
    idx = 0
    for joint in model.joints:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)         : %s' % joint.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)         : %s' % joint.english_name.strip())
      lines.append(u'  joint_type        : %4d' % joint.joint_type)
      lines.append(u'  rigidbody_index   : %4d, %4d' % (joint.rigidbody_index_a, joint.rigidbody_index_b))
      lines.append(u'  position          : %s' % str(joint.position.to_tuple()))
      lines.append(u'  rotation          : %s' % str(joint.rotation.to_tuple()))
      lines.append(u'  translation_limit : %s, %s' % (joint.translation_limit_min.to_tuple(), joint.translation_limit_max.to_tuple()))
      lines.append(u'  rotation_limit    : %s, %s' % (joint.rotation_limit_min.to_tuple(), joint.rotation_limit_max.to_tuple()))
      lines.append(u'  spring_constant   : %s, %s' % (joint.spring_constant_translation.to_tuple(), joint.spring_constant_rotation.to_tuple()))
    lines.append(u'='*80)

    lines.append(u'vertices     : Total {1}.\n{0}'.format('-'*80, len(model.vertices)))
    idx = 0
    for vertex in model.vertices:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  position    : %s' % str(vertex.position.to_tuple()))
      lines.append(u'  normal      : %s' % str(vertex.normal.to_tuple()))
      lines.append(u'  uv          : %s' % str(vertex.uv.to_tuple()))
      lines.append(u'  deform      : %s' % str(vertex.deform))
      lines.append(u'  edge_factor : %.4f' % vertex.edge_factor)
    lines.append(u'='*80)

    lines.append(u'indices      : Total {1}.\n{0}'.format('-'*80, len(model.indices)))
    idx = 0
    for indic in model.indices:
      lines.append(u'  %8d : %8d' % (idx, indic))
      idx += 1
    lines.append(u'='*80)

  if screen:
    for line in lines:
      print(line)
  return(lines)
  pass

def pmx2p3d(pmx_model, alpha=True):
  #
  # load textures
  #
  textures = TextureCollection()
  for tex in pmx_model.textures:
    tex_path = os.path.normpath(os.path.join(os.path.dirname(pmx_model.path), tex))
    tex_path = os.path.normcase(tex_path)
    log(u'Loading Texture : %s' % tex_path)
    texture = loadTexture(tex_path)
    if texture:
      textures.append(texture)
      log(u'Loaded Texture : %s' % tex_path, force=True)
      log(texture)
    else:
      textures.append(Texture('NULL'))
      log('Texture Error: %s' % tex_path)

  #
  # load materials
  #
  materials = MaterialCollection()
  for mat in pmx_model.materials:
    log(u'Loading Material :, %s' % mat.name.replace(u'\u30fb', u'·').strip())
    material = Material(mat.name)
    material.setAmbient(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, mat.alpha)) #Make this material blue
    material.setDiffuse(VBase4(mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b, mat.alpha))
    material.setSpecular(VBase4(mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, mat.alpha))
    material.setShininess(5.0) #Make this material shiny
    material.setLocal(True)
    if   mat.flag & 0x00000001:
      # 两面描画
      material.setTwoside(True)
    elif mat.flag & 0x00000010:
      # 地面影
      pass
    elif mat.flag & 0x00000100:
      # セルフ影マツ
      pass
    elif mat.flag & 0x00001000:
      # セルフ影
      pass
    elif mat.flag & 0x00010000:
      # 輪郭有效
      pass

    materials.addMaterial(material)
    log(u'Loaded Material :, %s' % mat.name.replace(u'\u30fb', u'·').strip(), force=True)

  #
  # load vertices(vertex list)
  #
  formatArray = GeomVertexArrayFormat()
  formatArray.addColumn(InternalName.make("drawFlag"), 1, Geom.NTUint8, Geom.COther)

  format = GeomVertexFormat(GeomVertexFormat.getV3n3cpt2())
  format.addArray(formatArray)
  GeomVertexFormat.registerFormat(format)

  vdata = GeomVertexData(pmx_model.name, format, Geom.UHStatic)

  vdata.setNumRows(4)
  vertex = GeomVertexWriter(vdata, 'vertex')
  normal = GeomVertexWriter(vdata, 'normal')
  color = GeomVertexWriter(vdata, 'color')
  texcoord = GeomVertexWriter(vdata, 'texcoord')

  for v in pmx_model.vertices:
    # vertex.addData3f(v.position.x, v.position.y, v.position.z)
    # normal.addData3f(v.normal.x, v.normal.y, v.normal.z)
    vertex.addData3f(v.position.x, v.position.z, v.position.y)
    normal.addData3f(v.normal.x, v.normal.z, v.normal.y)
    color.addData4f(.95, .95, .95, 1)
    texcoord.addData2f(v.uv.x, v.uv.y)

  #
  # load polygons face
  #
  vIndex = 0
  model = ModelNode(pmx_model.name)
  for mat in pmx_model.materials:
    prim = GeomTriangles(Geom.UHStatic)
    log(u'Loading Node :, %s' % mat.name.replace(u'\u30fb', u'·').strip())
    for idx in xrange(vIndex, vIndex+mat.vertex_count, 3):
      # flip trig-face for inverted axis-y/axis-z
      prim.addVertices(pmx_model.indices[idx+2], pmx_model.indices[idx+1], pmx_model.indices[idx+0])

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode(mat.name)
    node.addGeom(geom)
    # nodePath = render.attachNewNode(node)
    nodePath = NodePath(node)

    #
    # set polygon face material
    #
    nodePath.setMaterial(materials.findMaterial(mat.name), 1) #Apply the material to this nodePath

    #
    # set polygon face textures
    #
    if mat.texture_index >= 0 and textures[mat.texture_index]:
      textures[mat.texture_index].setBorderColor(VBase4(mat.edge_color.r, mat.edge_color.g, mat.edge_color.b, mat.alpha))
      textures[mat.texture_index].setWrapU(Texture.WM_clamp)
      # textures[mat.texture_index].setWrapV(Texture.WM_clamp)
      nodePath.setTexture(textures[mat.texture_index], 1)
      nodePath.setTexScale(TextureStage.getDefault(), 1, -1, -1)

    # if mat.sphere_mode > 0 and textures[mat.sphere_texture_index]:
    if mat.sphere_mode > 0:
      if mat.sphere_mode == 1:
        texMode = TextureStage.MModulateGloss
        # texMode = TextureStage.MModulateGlow
      elif mat.sphere_mode == 2:
        texMode = TextureStage.MAdd
      elif mat.sphere_mode == 3:
        texMode = TextureStage.MReplace
      else:
        texMode = TextureStage.MGloss

      log(u'%s: mode[%d], texop[%d], sysop[modulate(%d), modulategloss(%d), add(%d), replace(%d), gloss(%d)]' % (mat.name.replace(u'\u30fb', u'·'), mat.sphere_mode, texMode, TextureStage.MModulate, TextureStage.MModulateGlow, TextureStage.MAdd, TextureStage.MReplace, TextureStage.MGloss))
      # texMode = TextureStage.MAdd
      ts_sphere = TextureStage(mat.name+'_sphere')
      ts_sphere.setMode(texMode)
      if mat.sphere_texture_index < 0:
        tex = Texture()
        ts_sphere.setColor(VBase4(0.9, 0.9, 0.9, 0.68))
      else:
        tex = textures[mat.sphere_texture_index]
      tex.setWrapU(Texture.WM_clamp)
      tex.setWrapV(Texture.WM_clamp)
      nodePath.setTexGen(ts_sphere, TexGenAttrib.MEyeSphereMap)
      nodePath.setTexture(ts_sphere, tex, 1)
      nodePath.setTexScale(ts_sphere, 1, -1, -1)

    if mat.toon_texture_index>=0 and textures[mat.toon_texture_index] and mat.toon_sharing_flag >= 0:
      if mat.sphere_mode == 1:
        texMode = TextureStage.MModulateGlow
      elif mat.sphere_mode == 2:
        texMode = TextureStage.MAdd
      elif mat.sphere_mode == 3:
        texMode = TextureStage.MReplace
      else:
        texMode = TextureStage.MGloss

      texMode = TextureStage.MGlow

      ts_toon = TextureStage(mat.name+'_toon')
      ts_toon.setMode(texMode)
      textures[mat.toon_texture_index].setWrapU(Texture.WM_clamp)
      # textures[mat.toon_texture_index].setWrapV(Texture.WM_clamp)
      nodePath.setTexGen(ts_toon, TexGenAttrib.MEyeNormal)
      nodePath.setTexture(ts_toon, textures[mat.toon_texture_index], 1)
      nodePath.setTexScale(ts_toon, 1, -1, -1)


    nodePath.setColorOff()
    # nodePath.setShaderAuto()

    nodePath.setAntialias(AntialiasAttrib.MAuto)

    if alpha:
      #
      # Here is not really to solve the tex alpha-transparency bug, only a other bug :(
      #
      if mat.flag & 0x00000001:
        nodePath.setTransparency(True)
        # nodePath.setTransparency(TransparencyAttrib.MAlpha)
        # nodePath.setTransparency(TransparencyAttrib.MDual)
        # nodePath.setTransparency(TransparencyAttrib.MBinary)

    vIndex += mat.vertex_count
    model.addChild(node)
    log(u'Loaded Node :, %s' % mat.name.replace(u'\u30fb', u'·').strip(), force=True)

  return(NodePath(model))
  pass

def pmdLoad(f_pmd):
  model = None
  if os.path.isfile(f_pmd):
    model = pmdReader.read_from_file(f_pmd)
  return(model)

def pmdInfo(model, screen=False):
  lines = []
  if isinstance(model, pmd.Model):
    lines.append(u'path         : %s' % model.path)
    lines.append(u'version      : %s' % model.version)
    lines.append(u'name(jpn)    : %s' % model.name.replace(u'\u30fb', u'·').strip())
    lines.append(u'name(eng)    : %s' % model.english_name.strip())
    lines.append(u'comment(jpn) : \n{0}\n{1}\n{0}'.format('-'*80, model.comment.replace(u'\u30fb', u'·').strip()))
    lines.append(u'comment(eng) : \n{0}\n{1}\n{0}'.format('-'*80, model.english_comment.strip()))
    lines.append(u'='*80)

    lines.append(u'textures     : Total {1}.\n{0}'.format('-'*80, len(model.toon_textures)))
    idx = 0
    for texture in model.toon_textures:
      lines.append('%4d : %s' % (idx, texture))
      idx += 1
    lines.append(u'='*80)

    lines.append(u'materials    : Total {1}.\n{0}'.format('-'*80, len(model.materials)))
    idx = 0
    for mat in model.materials:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  diffuse   : (%s, %s, %s)' % (mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b))
      lines.append(u'  alpha     : %.2f' % mat.alpha)
      lines.append(u'  specular  : (%s, %s, %s), %.2f' % (mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, mat.specular_factor))
      lines.append(u'  ambient   : (%s, %s, %s)' %  (mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b))
      lines.append(u'  edge_flag : %s' % mat.edge_flag)
      lines.append(u'  texture   : %4d' % mat.texture_file)
      lines.append(u'  toon      : %4d' % (mat.toon_index))
      lines.append(u'  vertexs   : %4d' % mat.vertex_count)
    lines.append(u'='*80)

    lines.append(u'bones        : Total {1}.\n{0}'.format('-'*80, len(model.bones)))
    idx = 0
    for bone in model.bones:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % bone.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)    : %s' % bone.english_name.strip())
      lines.append(u'  index        : %4d' % bone.index)
      lines.append(u'  type         : %4d' % bone.type)
      lines.append(u'  pos          : %s' % str(bone.pos.to_tuple()))
      lines.append(u'  parent       : %4d, %s' % (bone.parent_index, bone.parent))
      lines.append(u'  tail         : %4d, %s' % (bone.tail_index, bone.tail))
      lines.append(u'  children     : %4d' % bone.children)
      lines.append(u'  ik_index     : %4d' % bone.ik_index)
      if bone.ik:
        ik_links = map(lambda link: (link.index, link.target, link.iterations, link.weight, link.length, link.children), bone.ik)
        lines.append(u'  ik           : %.4f, %s, %4d, %4d' % (bone.ik.limit_radian, ik_links[:5], bone.ik.loop, bone.ik.target_index ))
      else:
        lines.append(u'  ik           : %s' % u'')
    lines.append(u'='*80)

    lines.append(u'ik_list      : Total {1}.\n{0}'.format('-'*80, len(model.ik_list)))
    idx = 0
    for bone in model.bones:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % bone.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)    : %s' % bone.english_name.strip())
      lines.append(u'  position     : %s' % str(bone.position.to_tuple()))
      lines.append(u'  parent_index : %4d' % bone.parent_index)
      lines.append(u'  layer        : %4d' % bone.layer)
      lines.append(u'  flag         : %4d' % bone.flag)
      lines.append(u'  tail         : %4d, %s' % (bone.tail_index, bone.tail_position.to_tuple()))
      lines.append(u'  effect       : %4d, %.4f' % (bone.effect_index, bone.effect_factor))
      lines.append(u'  fixed_axis   : %s' % str(bone.fixed_axis.to_tuple()))
      lines.append(u'  local_vector : x%s, z%s' % (bone.local_x_vector.to_tuple(), bone.local_z_vector.to_tuple()))
      lines.append(u'  external_key : %4d' % bone.external_key)
      if bone.ik:
        ik_links = map(lambda link: (link.bone_index, link.limit_angle, link.limit_max.to_tuple(), link.limit_min.to_tuple()), bone.ik.link)
        lines.append(u'  ik           : %.4f, %s, %4d, %4d' % (bone.ik.limit_radian, ik_links[:5], bone.ik.loop, bone.ik.target_index ))
      else:
        lines.append(u'  ik           : %s' % u'')
      lines.append(u'  index        : %4d' % bone.index)
    lines.append(u'='*80)

    lines.append(u'morphs       : Total {1}.\n{0}'.format('-'*80, len(model.morphs)))
    idx = 0
    for morph in model.morphs:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % morph.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)    : %s' % morph.english_name.strip())
      lines.append(u'  type         : %4d' % morph.type)
      lines.append(u'  pos_list     : %4d' % str(morph.pos_list[:4]))
      lines.append(u'  vertex_count : %4d' % morph.vertex_count)
      ol = map(lambda offset: (offset.morph_index, offset.value) if isinstance(offset, pmx.GroupMorphData) else (offset.vertex_index, offset.position_offset.to_tuple()), morph.indices)
      lines.append(u'  indices      : %4d, %s' % (len(morph.offsets), ol[:5]))
    lines.append(u'='*80)

    lines.append(u'morph_indices: Total {1}.\n{0}'.format('-'*80, len(model.morph_indices)))
    idx = 0
    for morph in model.morph_indices:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)  : %s' % morph.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)  : %s' % morph.english_name.strip())
      lines.append(u'  panel      : %4d' % morph.panel)
      lines.append(u'  morph_type : %4d' % morph.morph_type)
      ol = map(lambda offset: (offset.morph_index, offset.value) if isinstance(offset, pmx.GroupMorphData) else (offset.vertex_index, offset.position_offset.to_tuple()), morph.offsets)
      lines.append(u'  offsets    : %4d, %s' % (len(morph.offsets), ol[:5]))
    lines.append(u'='*80)

    lines.append(u'bone_group_list : Total {1}.\n{0}'.format('-'*80, len(model.bone_group_list)))
    idx = 0
    for slot in model.bone_group_list:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % slot.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)    : %s' % slot.english_name.strip())
    lines.append(u'='*80)

    lines.append(u'bone_display_list : Total {1}.\n{0}'.format('-'*80, len(model.bone_display_list)))
    idx = 0
    for slot in model.bone_display_list:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % slot.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)    : %s' % slot.english_name.strip())
    lines.append(u'='*80)

    lines.append(u'rigidbodies  : Total {1}.\n{0}'.format('-'*80, len(model.rigidbodies)))
    idx = 0
    for rigidbody in model.rigidbodies:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)          : %s' % rigidbody.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  bone_index         : %4d' % rigidbody.bone_index)
      lines.append(u'  collision_group    : %4d' % rigidbody.collision_group)
      lines.append(u'  no_collision_group : %4d' % rigidbody.no_collision_group)
      lines.append(u'  shape              : %4d, %s, %s, %s' % (rigidbody.shape_type, rigidbody.shape_size.to_tuple(), rigidbody.shape_position.to_tuple(), rigidbody.shape_rotation.to_tuple()))
      lines.append(u'  param              : %4d, %.4f, %.4f, %.4f, %.4f' % (rigidbody.mass, rigidbody.linear_damping, rigidbody.angular_damping, rigidbody.restitution, rigidbody.friction))
      lines.append(u'  mode               : %4d' % rigidbody.mode)
    lines.append(u'='*80)

    lines.append(u'joints       : Total {1}.\n{0}'.format('-'*80, len(model.joints)))
    idx = 0
    for joint in model.joints:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)         : %s' % joint.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  rigidbody_index   : %4d, %4d' % (joint.rigidbody_index_a, joint.rigidbody_index_b))
      lines.append(u'  position          : %s' % str(joint.position.to_tuple()))
      lines.append(u'  rotation          : %s' % str(joint.rotation.to_tuple()))
      lines.append(u'  translation_limit : %s, %s' % (joint.translation_limit_min.to_tuple(), joint.translation_limit_max.to_tuple()))
      lines.append(u'  rotation_limit    : %s, %s' % (joint.rotation_limit_min.to_tuple(), joint.rotation_limit_max.to_tuple()))
      lines.append(u'  spring_constant   : %s, %s' % (joint.spring_constant_translation.to_tuple(), joint.spring_constant_rotation.to_tuple()))
    lines.append(u'='*80)

    lines.append(u'no_parent_bones : Total {1}.\n{0}'.format('-'*80, len(model.no_parent_bones)))
    idx = 0
    for slot in model.display_slots:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % slot.name.replace(u'\u30fb', u'·').strip())
      lines.append(u'  name(eng)    : %s' % slot.english_name.strip())
    lines.append(u'='*80)

    lines.append(u'vertices     : Total {1}.\n{0}'.format('-'*80, len(model.vertices)))
    idx = 0
    for vertex in model.vertices:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  position    : %s' % str(vertex.position.to_tuple()))
      lines.append(u'  normal      : %s' % str(vertex.normal.to_tuple()))
      lines.append(u'  uv          : %s' % str(vertex.uv.to_tuple()))
      lines.append(u'  deform      : %s' % str(vertex.deform))
      lines.append(u'  edge_factor : %.4f' % vertex.edge_factor)
    lines.append(u'='*80)

    lines.append(u'indices      : Total {1}.\n{0}'.format('-'*80, len(model.indices)))
    idx = 0
    for indic in model.indices:
      lines.append(u'  %8d : %8d' % (idx, indic))
      idx += 1
    lines.append(u'='*80)

  if screen:
    for line in lines:
      print(line)
  return(lines)
  pass

def pmd2p3d(pmd_model, alpha=True):

  pass


def displayPmdModelInfo(model):
  # print(dir(model))
  info = pmdInfo(model)
  print
  fn = os.path.splitext(os.path.basename(model.path))
  log(os.path.join(CWD, fn[0]+'_info'+'.txt'))
  with codecs.open(os.path.join(CWD, fn[0]+'_info'+'.txt'), 'w', encoding='utf8') as f:
    f.writelines(os.linesep.join(info))
  pass

def displayPmxModelInfo(model):
  # print(dir(model))
  info = pmxInfo(model)
  fn = os.path.splitext(os.path.basename(model.path))
  log(os.path.join(CWD, fn[0]+'_info'+'.txt'))
  with codecs.open(os.path.join(CWD, fn[0]+'_info'+'.txt'), 'w', encoding='utf8') as f:
    f.writelines(os.linesep.join(info))
  pass

def pmx2model(pmx):
  pmxModel = pmxLoad(pmx)
  import direct.directbase.DirectStart
  p3dnodes, p3dmodel = pmx2p3d(pmxModel)
  return(p3dmodel)

def testPMX(pmx):
  pmxModel = pmxLoad(pmx)
  if pmxModel:
    displayPmxModelInfo(pmxModel)

    import direct.directbase.DirectStart
    p3dnode = pmx2p3d(pmxModel)
    p3dnode.reparentTo(render)

    run()
    pass
  pass

def testPMD(pmd):
  pmdModel = pmdLoad(pmdFile)
  if pmdModel:
    print(pmdModel.path)
    displayPmdModelInfo(pmdModel)

    # import direct.directbase.DirectStart
    # p3dnodes, p3dmodel = pmd2p3d(pmdModel)

    # run()
    pass
  pass


if __name__ == '__main__':
  pmxFile = u'../models/meiko/meiko.pmx'
  pmxFile = u'../models/apimiku/Miku long hair.pmx'
  pmxFile = u'../models/cupidmiku/Cupid Miku.pmx'

  pmdFile = u'../models/alice/alice.pmd'

  if len(sys.argv) > 1:
    if len(sys.argv[1]) > 0:
      pmxFile = sys.argv[1]

  ext = os.path.splitext(pmxFile)[1].lower()
  if ext in ['.pmd']:
    testPMD(pmxFile)
  elif ext in ['.pmx']:
    testPMX(pmxFile)

  # testPMD(pmdFile)


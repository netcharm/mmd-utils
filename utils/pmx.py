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

from pandac.PandaModules import *

from common import *

from pymeshio import pmx
from pymeshio.pmx import reader as pmxReader

DEBUG = True
DEBUG = False

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])

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
    lines.append(u'name(jpn)    : %s' % model.name)
    lines.append(u'name(eng)    : %s' % model.english_name.strip())
    lines.append(u'comment(jpn) : \n{0}\n{1}\n{0}'.format('-'*80, model.comment))
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
      lines.append(u'  name(jpn) : %s' % mat.name)
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
      lines.append(u'  name(jpn)    : %s' % bone.name)
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
      lines.append(u'  name(jpn)  : %s' % morph.name)
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
      lines.append(u'  name(jpn)    : %s' % slot.name)
      lines.append(u'  name(eng)    : %s' % slot.english_name.strip())
      lines.append(u'  references   : %4d, %s' % (len(slot.references), str(slot.references)))
      lines.append(u'  special_flag : %4d' % slot.special_flag)
    lines.append(u'='*80)

    lines.append(u'rigidbodies  : Total {1}.\n{0}'.format('-'*80, len(model.rigidbodies)))
    idx = 0
    for rigidbody in model.rigidbodies:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)          : %s' % rigidbody.name)
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
      lines.append(u'  name(jpn)         : %s' % joint.name)
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
    log(u'Loading Material : %s' % mat.name)
    material = Material(mat.name)
    material.setAmbient(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, mat.alpha)) #Make this material blue
    material.setDiffuse(VBase4(mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b, mat.alpha))
    material.setSpecular(VBase4(mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, mat.alpha))
    material.setShininess(mat.specular_factor)
    material.setEmission(VBase4(mat.edge_color.r, mat.edge_color.g, mat.edge_color.b, 0.33))
    material.setLocal(False)
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
    log(u'Loaded Material : %s' % mat.name, force=True)

  #
  # load vertices(vertex list)
  #
  formatArray = GeomVertexArrayFormat()
  formatArray.addColumn(InternalName.make(str("edge_factor")), 1, Geom.NTFloat32, Geom.COther)
  formatArray.addColumn(InternalName.make(str("drawFlag")), 1, Geom.NTUint8, Geom.COther)
  formatArray.addColumn(InternalName.make(str("index")), 1, Geom.NTUint32, Geom.CIndex)
  # formatArray.addColumn(InternalName.make("morph"), 1, Geom.NTFloat32, Geom.CMorphDelta)

  format = GeomVertexFormat(GeomVertexFormat.getV3n3cpt2())
  format.addArray(formatArray)
  format = GeomVertexFormat.registerFormat(format)

  vdata = GeomVertexData(pmx_model.name, format, Geom.UHDynamic)

  vdata.setNumRows(6)
  vertex = GeomVertexWriter(vdata, 'vertex')
  normal = GeomVertexWriter(vdata, 'normal')
  color = GeomVertexWriter(vdata, 'color')
  texcoord = GeomVertexWriter(vdata, 'texcoord')
  edge = GeomVertexWriter(vdata, 'edge_factor')
  index = GeomVertexWriter(vdata, 'index')

  idx = 0
  for v in pmx_model.vertices:
    vertex.addData3f(v.position.x, v.position.z, v.position.y)
    normal.addData3f(v.normal.x, v.normal.z, v.normal.y)
    color.addData4f(.95, .95, .95, 1)
    texcoord.addData2f(v.uv.x, v.uv.y)
    edge.addData1f(v.edge_factor)
    index.addData1i(idx)
    idx += 1

  #
  # load polygons face
  #
  vIndex = 0
  model = ModelNode(pmx_model.name)
  model.setPythonTag('path', pmx_model.path)
  model.setPythonTag('version', str(pmx_model.version))
  model.setPythonTag('name', pmx_model.name)
  model.setPythonTag('english_name', pmx_model.english_name)
  model.setPythonTag('comment', pmx_model.comment)
  model.setPythonTag('english_comment', pmx_model.english_comment)

  modelBody = ModelRoot('Body')
  model.addChild(modelBody)

  matIndex = 0
  for mat in pmx_model.materials:
    prim = GeomTriangles(Geom.UHDynamic)
    log(u'Loading Node : %s' % mat.name)
    for idx in xrange(vIndex, vIndex+mat.vertex_count, 3):
      # flip trig-face for inverted axis-y/axis-z
      prim.addVertices(pmx_model.indices[idx+2], pmx_model.indices[idx+1], pmx_model.indices[idx+0])

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode(mat.name)
    node.addGeom(geom)
    nodePath = NodePath(node)
    nodePath.setPythonTag('english_name', mat.english_name)

    #
    # set polygon face material
    #
    nodePath.setMaterial(materials.findMaterial(mat.name), 1) #Apply the material to this nodePath

    nodePath.setPythonTag('edge_color', mat.edge_color)
    nodePath.setPythonTag('edge_size', mat.edge_size)
    nodePath.setPythonTag('material_index', matIndex)
    nodePath.setPythonTag('material', materials.findMaterial(mat.name))

    #
    # set polygon face textures
    #
    if mat.texture_index >= 0 and textures[mat.texture_index]:
      textures[mat.texture_index].setBorderColor(VBase4(mat.edge_color.r, mat.edge_color.g, mat.edge_color.b, mat.alpha))
      # textures[mat.texture_index].setWrapU(Texture.WM_clamp)
      # # textures[mat.texture_index].setWrapV(Texture.WM_clamp)
      nodePath.setTexture(textures[mat.texture_index], matIndex)
      nodePath.setTexScale(TextureStage.getDefault(), 1, -1, -1)
      if textures[mat.texture_index].getFormat() in [Texture.FRgba, Texture.FRgbm, Texture.FRgba4, Texture.FRgba5, Texture.FRgba8, Texture.FRgba12, Texture.FRgba16, Texture.FRgba32]: #, Texture.FSrgbAlpha]:
        nodePath.setTransparency(TransparencyAttrib.MDual, matIndex)

    # if mat.sphere_mode > 0 and textures[mat.sphere_texture_index]:
    if mat.sphere_mode > 0:
      if mat.sphere_mode == 1:
        texMode = TextureStage.MGloss
        # texMode = TextureStage.MModulateGlow
      elif mat.sphere_mode == 2:
        texMode = TextureStage.MAdd
      elif mat.sphere_mode == 3:
        texMode = TextureStage.MReplace
      else:
        texMode = TextureStage.MGlow
        # texMode = TextureStage.MReplace

      log(u'%s: mode[%d], texop[%d], sysop[modulate(%d), modulategloss(%d), add(%d), replace(%d), gloss(%d)]' % (mat.name, mat.sphere_mode, texMode, TextureStage.MModulate, TextureStage.MModulateGlow, TextureStage.MAdd, TextureStage.MReplace, TextureStage.MGloss))
      # texMode = TextureStage.MAdd
      ts_sphere = TextureStage(mat.name+'_sphere')
      ts_sphere.setColor(VBase4(1,1,1,1))
      ts_sphere.setMode(texMode)
      ts_sphere.setSort(matIndex)
      ts_sphere.setPriority(matIndex)
      if (mat.sphere_texture_index < 0) or (not textures[mat.sphere_texture_index]):
        tex = Texture('NULL')
        ts_sphere.setColor(VBase4(0.9, 0.9, 0.9, 0.68))
      else:
        tex = textures[mat.sphere_texture_index]
      tex.setWrapU(Texture.WM_clamp)
      tex.setWrapV(Texture.WM_clamp)

      # nodePath.setTexGen(ts_sphere, TexGenAttrib.MEyeCubeMap, matIndex)
      nodePath.setTexGen(ts_sphere, TexGenAttrib.MPointSprite, matIndex)
      nodePath.setTexture(ts_sphere, tex, matIndex)
      nodePath.setTexScale(ts_sphere, 1, -1, -1)
      # nodePath.setShaderAuto(matIndex)

    if mat.toon_texture_index>=0 and textures[mat.toon_texture_index] and mat.toon_sharing_flag >= 0:
      if mat.sphere_mode == 1:
        texMode = TextureStage.MModulateGlow
      elif mat.sphere_mode == 2:
        texMode = TextureStage.MAdd
      elif mat.sphere_mode == 3:
        texMode = TextureStage.MReplace
      else:
        texMode = TextureStage.MGloss

      texMode = TextureStage.MGloss

      ts_toon = TextureStage(mat.name+'_toon')
      ts_toon.setColor(VBase4(1,1,1,1))
      ts_toon.setMode(texMode)
      ts_toon.setSort(matIndex)
      ts_toon.setPriority(matIndex)
      textures[mat.toon_texture_index].setWrapU(Texture.WM_clamp)
      # nodePath.setTexGen(ts_sphere, TexGenAttrib.MEyeCubeMap, matIndex)
      # nodePath.setTexGen(ts_toon, TexGenAttrib.MEyePosition, matIndex)
      nodePath.setTexGen(ts_toon, TexGenAttrib.MPointSprite, matIndex)
      nodePath.setTexture(ts_toon, textures[mat.toon_texture_index], matIndex)
      nodePath.setTexScale(ts_toon, 1, -1, -1)


    # nodePath.setColorOff()
    # nodePath.setShaderAuto(2)
    # nodePath.setShaderAuto(BitMask32.bit(Shader.BitAutoShaderNormal) , 2)
    nodePath.setAntialias(AntialiasAttrib.MAuto)

    if alpha:
      #
      # Here is not really to solve the tex alpha-transparency bug, only a other bug :(
      #
      if mat.flag & 0x00000001:
        # nodePath.setTransparency(True, 0)
        # nodePath.setTransparency(True, 1)
        # nodePath.setTransparency(TransparencyAttrib.MAlpha, matIndex)
        # nodePath.setTransparency(TransparencyAttrib.MDual, matIndex)
        # nodePath.setTransparency(TransparencyAttrib.MBinary, 0)
        pass

    vIndex += mat.vertex_count
    modelBody.addChild(node)
    matIndex += 1
    log(u'Loaded Node : %s' % mat.name, force=True)

  modelPath = NodePath(model)
  # modelPath.setShaderAuto()
  return(modelPath)
  pass

def loadPmxBody(pmx_model):
  return(pmx2p3d(pmx_model))

def loadPmxBone(pmx_model):
  def GetParentNode(root, parent_index):
    node = None
    if parent_index == -1:
      node = root
      pass
    else:
      for child in root.getChildren():
        node = GetParentNode(child, parent_index)
        if node:
          break
        else:
          boneIndex = child.getPythonTag('boneIndex')
          if boneIndex == parent_index:
            node = child
            break
        pass
    return(node)
    pass
  #
  # Load Bone data
  #
  formatArray = GeomVertexArrayFormat()
  formatArray.addColumn(InternalName.make(str("vindex")), 1, Geom.NTUint32, Geom.CIndex)
  formatArray.addColumn(InternalName.make(str("vparent")), 3, Geom.NTUint32, Geom.CIndex)

  format = GeomVertexFormat(GeomVertexFormat.getV3c4())
  format.addArray(formatArray)
  format = GeomVertexFormat.registerFormat(format)

  boneNode = PandaNode('Bones')
  boneIndex = 0
  for bone in pmx_model.bones:
    log(u'Loading Bone : %s' % bone.name, force=True)

    #
    # load vertices(vertex list)
    #
    vdata = GeomVertexData(bone.name+'_vdata', format, Geom.UHDynamic)
    vdata.setNumRows(4)
    vertex = GeomVertexWriter(vdata, 'vertex')
    color = GeomVertexWriter(vdata, 'color')
    vindex = GeomVertexWriter(vdata, 'vindex')
    vparent = GeomVertexWriter(vdata, 'vparent')

    node = GeomNode(bone.name)

    boneData = None
    v = bone.position
    vertex.addData3f(v.x, v.z, v.y)
    color.addData4f(.95, .95, 0, 1)
    vindex.addData1i(boneIndex)
    vparent.addData1i(bone.parent_index)

    parentNode = GetParentNode(boneNode, bone.parent_index)
    if parentNode:
      if parentNode.getPythonTag('position'):
        v = parentNode.getPythonTag('position')
    vertex.addData3f(v.x, v.z, v.y)
    color.addData4f(.95, 0, 0.95, 1)
    vindex.addData1i(boneIndex)
    vparent.addData1i(bone.parent_index)

    prim = GeomLines(Geom.UHDynamic)
    prim.addVertex(1)
    prim.addVertex(0)

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node.addGeom(geom)

    node.setPythonTag('english_name', bone.english_name)
    node.setPythonTag('position', bone.position)
    node.setPythonTag('parent_index', bone.parent_index)
    node.setPythonTag('layer', bone.layer)
    node.setPythonTag('flag', bone.flag)
    node.setPythonTag('tail_index', bone.tail_index)
    node.setPythonTag('tail_position', bone.tail_position)
    node.setPythonTag('effect_index', bone.effect_index)
    node.setPythonTag('effect_factor', bone.effect_factor)
    node.setPythonTag('fixed_axis', bone.fixed_axis)
    node.setPythonTag('local_x_vector', bone.local_x_vector)
    node.setPythonTag('local_z_vector', bone.local_z_vector)
    node.setPythonTag('external_key', bone.external_key)
    node.setPythonTag('ik', bone.ik)
    node.setPythonTag('index', bone.index)
    node.setPythonTag('boneIndex', boneIndex)

    parentNode = GetParentNode(boneNode, bone.parent_index)
    if isinstance(parentNode, PandaNode):
      parentNode.addChild(node)
    elif isinstance(parentNode, GeomNode):
      parentNode.addGeom(node)
    boneIndex += 1

  np = NodePath(boneNode)
  ofs = OFileStream('bonelist.txt', 3)
  np.ls(ofs, 2)
  # with codecs.open('bonelist.txt', 'w', encoding='utf8') as f:
  #   f.write(np.ls())

  # np.hide()
  return(np)
  pass

def loadPmxMorph(pmx_model):
  #
  # Load Morph data
  #
  formatArray = GeomVertexArrayFormat()
  formatArray.addColumn(InternalName.make(str("vindex")), 1, Geom.NTUint32, Geom.CIndex)
  # formatArray.addColumn(InternalName.make(str("v.morph")), 3, Geom.NTFloat32, Geom.CMorphDelta)
  formatArray.addColumn(InternalName.make(str("vmorph")), 3, Geom.NTFloat32, Geom.COther)
  formatArray.addColumn(InternalName.make(str("transform_index")), 1, Geom.NTUint32, Geom.CIndex)
  formatArray.addColumn(InternalName.make(str("transform_weight")), 3, Geom.NTUint32, Geom.COther)
  formatArray.addColumn(InternalName.make(str("emotion.morph.strange")), 1, Geom.NTFloat32, Geom.COther)

  format = GeomVertexFormat(GeomVertexFormat.getV3())
  format.addArray(formatArray)
  format = GeomVertexFormat.registerFormat(format)

  morphNode = PandaNode('Morphs')
  morphIndex = 0
  for morph in pmx_model.morphs:
    log(u'Loading Morph : %s' % morph.name, force=True)

    #
    # load vertices(vertex list)
    #
    vdata = GeomVertexData(morph.name+'_vdata', format, Geom.UHDynamic)
    vdata.setNumRows(6)
    vertex = GeomVertexWriter(vdata, 'vertex')
    vindex = GeomVertexWriter(vdata, 'vindex')
    # vmorph = GeomVertexWriter(vdata, 'v.morph')
    vmorph = GeomVertexWriter(vdata, 'vmorph')
    transform_index = GeomVertexWriter(vdata, 'transform_index')
    transform_weight = GeomVertexWriter(vdata, 'transform_weight')
    column_morph_slider = GeomVertexWriter(vdata, 'emotion.morph.strange')

    node = GeomNode(morph.name)

    morphData = None
    # print(dir(morph))
    # print(len(morph.offsets))
    if   morph.morph_type == 0: # group morph
      morphData = []
      for idx in xrange(len(morph.offsets)):
        offset = morph.offsets[idx]
        o = offset
        morphData.append((o.morph_index, o.value))
      pass
    elif morph.morph_type == 1: # vertex morph
      prim = GeomPoints(Geom.UHDynamic)
      for idx in xrange(len(morph.offsets)):
        offset = morph.offsets[idx]
        v = pmx_model.vertices[offset.vertex_index]
        o = offset.position_offset
        i = offset.vertex_index
        vertex.addData3f(v.position.x, v.position.z, v.position.y)
        vindex.addData1i(i)
        vmorph.addData3f(o.x, o.z, o.y)
        transform_index.addData1i(i)
        transform_weight.addData3f(o.x, o.z, o.y)
        column_morph_slider.addData1f(1.0)

        prim.addVertex(idx)

      geom = Geom(vdata)
      geom.addPrimitive(prim)
      node.addGeom(geom)
      pass
    elif morph.morph_type == 2: # bone morph
      morphData = []
      pass
    elif morph.morph_type == 3: # UvMorph morph
      morphData = []
      pass
    elif morph.morph_type == 4: # UvMorph1 morph
      morphData = []
      pass
    elif morph.morph_type == 5: # UvMorph2 morph
      morphData = []
      pass
    elif morph.morph_type == 6: # UvMorph3 morph
      morphData = []
      pass
    elif morph.morph_type == 7: # UvMorph4 morph
      morphData = []
      pass
    elif morph.morph_type == 8: # material morph
      morphData = []
      for idx in xrange(len(morph.data)):
        o = morph.data[idx]
        np = NodePath(u'mat_%04d' % (idx))
        material = Material(u'%s_%04d' % (morph.name, idx))
        material.setAmbient(VBase4(o.ambient.r, o.ambient.g, o.ambient.b, 1))
        material.setDiffuse(VBase4(o.diffuse.r, o.diffuse.g, o.diffuse.b, 1))
        material.setSpecular(VBase4(o.specular.r, o.specular.g, o.specular.b, 1))
        material.setShininess(o.specular_factor)
        np.setMaterial(material)
        np.setPythonTag('materialIndex', o.material_index)
        np.setPythonTag('calcMode', o.calc_mode)
        np.setPythonTag('edge_color', o.edge_color)
        np.setPythonTag('edge_size', o.edge_size)
        np.setPythonTag('texture_factor', o.texture_factor)
        np.setPythonTag('sphere_texture_factor', o.sphere_texture_factor)
        np.setPythonTag('toon_texture_factor', o.toon_texture_factor)
        morphData.append(np)
    pass

    node.setPythonTag('english_name', morph.english_name)
    node.setPythonTag('panel', morph.panel)
    node.setPythonTag('morph_type', morph.morph_type)
    node.setPythonTag('morph_data', morphData)
    node.setPythonTag('morph_index', morphIndex)
    morphNode.addChild(node)

    morphIndex += 1

  np = NodePath(morphNode)
  np.hide()
  return(np)
  pass

def loadPmxIK(pmx_model):
  #
  # Load IK data
  #
  iknode = ModelNode('IK')
  pass

def loadPmxRigid(pmx_model):
  #
  # Load Rigid data
  #
  rigidNnode = ModelNode('Rigid')
  pass

def loadPmxSlot(pmx_model):
  #
  # Load Display Slot data
  #
  slotNnode = ModelNode('Slots')
  pass

def loadPmxJoint(pmx_model):
  #
  # Load Joints data
  #
  jointNnode = ModelNode('Joints')
  pass

def loadPmxActor(pmx_model):
  model = loadPmxModel(pmx_model)
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
  p3dmodel = pmx2p3d(pmxModel)
  return(p3dmodel)

def loadPmxModel(modelfile):
  p3dnode = None
  mmdFile = os.path.relpath(modelfile)
  if os.path.altsep:
    mmdFile = mmdFile.replace('\\', os.path.altsep)
  ext = os.path.splitext(mmdFile)[1].lower()
  if ext in ['.pmx']:
    mmdModel = pmxLoad(mmdFile)
    if mmdModel:
      p3dnode = loadPmxBody(mmdModel)
      morphs = loadPmxMorph(mmdModel)
      morphs.reparentTo(p3dnode)
      bones = loadPmxBone(mmdModel)
      bones.reparentTo(p3dnode)
  elif ext in ['', '.egg', '.pz', '.bam']:
    return(p3dnode)
  return(p3dnode)

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


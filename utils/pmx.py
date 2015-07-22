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

from panda3d.core import *
from panda3d.egg import *

from panda3d.ode import *

from panda3d.bullet import ZUp
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletSoftBodyNode
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletConeShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletConeTwistConstraint

from direct.actor.Actor import Actor

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

def pmx2p3d(pmx_model):

  return(loadPmxBody(pmx_model))

def loadPmxBody(pmx_model, alpha=True):
  modelPath = os.path.dirname(pmx_model.path)

  #
  # load textures
  #
  # textures = TextureCollection()
  texIndex = 0
  textures = []
  for tex in pmx_model.textures:
    tex_path = os.path.normpath(os.path.join(os.path.dirname(pmx_model.path), tex))
    tex_path = os.path.normcase(tex_path)
    log(u'Loading Texture %03d: %s' % (texIndex, tex), force=True)
    texture = loadTexture(tex_path, model_path=modelPath)
    textures.append(texture)
    if texture:
      log(u'Loaded Texture %03d: %s' % (texIndex, tex))
    else:
      log(u'Texture Failed %03d: %s' % (texIndex, tex), force=True)
    texIndex += 1


  modelName = pmx_model.name
  #
  # load vertices(vertex list)
  #
  formatArray = GeomVertexArrayFormat()
  # formatArray.addColumn(InternalName.make(str("vertex")),   3, Geom.NTFloat32, Geom.C_vector)
  # formatArray.addColumn(InternalName.make(str("normal")),   3, Geom.NTFloat32, Geom.C_vector)
  # formatArray.addColumn(InternalName.make(str("color")),    4, Geom.NTFloat32, Geom.C_color)
  # formatArray.addColumn(InternalName.make(str("texcoord")), 2, Geom.NTFloat32, Geom.C_texcoord)

  formatArray.addColumn(InternalName.make(str("edge_factor")), 1, Geom.NTFloat32, Geom.COther)
  formatArray.addColumn(InternalName.make(str("drawFlag")), 1, Geom.NTUint8, Geom.COther)
  formatArray.addColumn(InternalName.make(str("index")), 1, Geom.NTUint32, Geom.CIndex)
  # formatArray.addColumn(InternalName.make(str("morph")), 1, Geom.NTFloat32, Geom.CMorphDelta)
  # print(formatArray)

  format = GeomVertexFormat(GeomVertexFormat.getV3n3cpt2())
  format.addArray(formatArray)
  format = GeomVertexFormat.registerFormat(format)

  vdata = GeomVertexData(modelName, format, Geom.UHDynamic)
  vdata.setNumRows(len(pmx_model.vertices))

  vertex = GeomVertexWriter(vdata, str('vertex'))
  normal = GeomVertexWriter(vdata, 'normal')
  color = GeomVertexWriter(vdata, 'color')
  texcoord = GeomVertexWriter(vdata, 'texcoord')
  edge = GeomVertexWriter(vdata, 'edge_factor')
  index = GeomVertexWriter(vdata, 'index')

  idx = 0
  skins = dict()
  log(u'Loading Vertices : %d' % (len(pmx_model.vertices)), force=True)
  for v in pmx_model.vertices:
    vertex.addData3f(V2V(v.position))
    normal.addData3f(V2V(v.normal))
    color.addData4f(.95, .95, .95, 1)
    texcoord.addData2f(v.uv.x, v.uv.y)
    edge.addData1f(v.edge_factor)
    index.addData1i(idx)
    idx += 1

    #
    # bind vertex to bone
    #
    deform = v.deform
    if isinstance(deform, pmx.Bdef1):
      bone0 = pmx_model.bones[deform.index0]
      if not bone0.name in skins:
        skins[bone0.name] = []
      skins[bone0.name].append(v)
      pass
    elif isinstance(deform, pmx.Bdef2):
      bone0 = pmx_model.bones[deform.index0]
      bone1 = pmx_model.bones[deform.index1]
      if not bone0.name in skins:
        skins[bone0.name] = []
      skins[bone0.name].append((idx, v))
      if not bone1.name in skins:
        skins[bone1.name] = []
      skins[bone1.name].append((idx, v))
      pass
    elif isinstance(deform, pmx.Bdef4):
      bone0 = pmx_model.bones[deform.index0]
      bone1 = pmx_model.bones[deform.index1]
      bone2 = pmx_model.bones[deform.index2]
      bone3 = pmx_model.bones[deform.index3]
      if not bone0.name in skins:
        skins[bone0.name] = []
      skins[bone0.name].append((idx, v))
      if not bone1.name in skins:
        skins[bone1.name] = []
      skins[bone1.name].append((idx, v))
      if not bone2.name in skins:
        skins[bone2.name] = []
      skins[bone2.name].append((idx, v))
      if not bone3.name in skins:
        skins[bone3.name] = []
      skins[bone3.name].append((idx, v))
      pass
    elif isinstance(deform, pmx.Sdef):
      bone0 = pmx_model.bones[deform.index0]
      bone1 = pmx_model.bones[deform.index1]
      if not bone0.name in skins:
        skins[bone0.name] = []
      skins[bone0.name].append((idx, v))
      if not bone1.name in skins:
        skins[bone1.name] = []
      skins[bone1.name].append((idx, v))
      pass

  #
  # load polygons face
  #
  vIndex = 0
  model = Character(modelName)
  model.setPythonTag('path', pmx_model.path)
  model.setPythonTag('version', str(pmx_model.version))
  model.setPythonTag('name', modelName)
  model.setPythonTag('english_name', pmx_model.english_name)
  model.setPythonTag('comment', pmx_model.comment)
  model.setPythonTag('english_comment', pmx_model.english_comment)
  modelPath = NodePath(model)

  modelBody = ModelRoot('Body')
  modelBody.setPythonTag('Skins', skins)
  bodyPath = NodePath(modelBody)
  bodyPath.reparentTo(modelPath)

  materials = MaterialCollection()
  matIndex = 0
  matCount = len(pmx_model.materials)
  for mat in pmx_model.materials:
    #
    # load materials
    #
    log(u'Loading Material %03d: %s' % (matIndex, mat.name), force=True)
    material = Material(mat.name)
    material.setDiffuse(VBase4(mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b, mat.alpha))
    if mat.specular_factor > 0 or (mat.specular_color.r != 1 and mat.specular_color.g != 1 and mat.specular_color.b != 1):
      material.setSpecular(VBase4(mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, 1))
      material.setShininess(mat.specular_factor*10)
    else:
      material.setSpecular(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, 0.01))
      material.setShininess(0)

    material.setAmbient(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, 1))
    material.setEmission(VBase4(0, 0, 0, 1))

    matflag_twoside      = bool(mat.flag & 0b00000001) # 两面描画
    matflag_shadowfloor  = bool(mat.flag & 0b00000010) # 地面影
    matflag_shadowself0  = bool(mat.flag & 0b00000100) # セルフ影マツ
    matflag_shadowself1  = bool(mat.flag & 0b00001000) # セルフ影
    matflag_outline      = bool(mat.flag & 0b00010000) # 輪郭有效

    # material.setLocal(False)
    material.setLocal(True)
    if matflag_twoside:
      # 两面描画
      material.setTwoside(True)
    else:
      material.setTwoside(False)

    if matflag_shadowfloor:
      # 地面影
      pass
    if matflag_shadowself0:
      # セルフ影マツ
      pass
    if matflag_shadowself1:
      # セルフ影
      pass
    if matflag_outline:
      # 輪郭有效
      pass

    materials.addMaterial(material)
    log(u'Loaded Material %03d: %s' % (matIndex, mat.name))

    #
    # Load vertex for every material/polygon face
    #
    prim = GeomTriangles(Geom.UHDynamic)
    log(u'Loading Polygons %03d: %s' % (matIndex, mat.name), force=True)
    for idx in xrange(vIndex, vIndex+mat.vertex_count, 3):
      # flip trig-face for inverted axis-y/axis-z
      prim.addVertices(pmx_model.indices[idx+2], pmx_model.indices[idx+1], pmx_model.indices[idx+0])
    prim.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode(mat.name)
    node.addGeom(geom)

    nodePath = NodePath(node)
    nodePath.setPythonTag('english_name', mat.english_name)

    #
    # set polygon face material
    #
    # Apply the material to this nodePath
    tsid = matCount - matIndex
    tsid_main   =  tsid
    tsid_sphere =  tsid
    tsid_toon   =  tsid
    # tsid_main   = 1
    # tsid_sphere = 2
    # tsid_toon   = 3
    nodePath.setMaterial(material, tsid_main)
    nodePath.setTwoSided(material.getTwoside())

    nodePath.setPythonTag('edge_color', mat.edge_color)
    nodePath.setPythonTag('edge_size', mat.edge_size)
    nodePath.setPythonTag('material_index', matIndex)
    nodePath.setPythonTag('material', material)
    nodePath.setPythonTag('vIndex', vIndex)
    nodePath.setPythonTag('vCount', mat.vertex_count)
    nodePath.setPythonTag('pickableObjTag', 1)

    if mat.texture_index < 0 and mat.sphere_texture_index < 0 and mat.toon_texture_index < 0:
      nodePath.setTransparency(TransparencyAttrib.MDual, matIndex)
    else:
      if mat.alpha == 1:
        nodePath.setTransparency(TransparencyAttrib.MNone, matIndex)
      else:
        nodePath.setTransparency(TransparencyAttrib.MAlpha, matIndex)

    # if mat.alpha<1:
    #   nodePath.setTransparency(TransparencyAttrib.MAlpha, matIndex)

    #
    # set polygon face main textures
    #
    if mat.texture_index >= 0:
      # print('Texture %s : Main %03d' % (mat.name, mat.texture_index))
      texMain = textures[mat.texture_index]
      if  texMain and texMain.hasRamImage():
        if matflag_outline:
          # 輪郭有效
          texMain.setBorderColor(VBase4(mat.edge_color.r, mat.edge_color.g, mat.edge_color.b, mat.edge_color.a))
          pass

        # texMain.setWrapU(Texture.WMClamp)

        ts_main = TextureStage('%3d_%s_main' % (matIndex, mat.name))
        ts_main.setColor(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, 1))
        ts_main.setSort(tsid_main)
        ts_main.setPriority(tsid_main)

        if mat.sphere_texture_index < 0:
          ts_main.setMode(TextureStage.MReplace)
          # ts_main.setMode(TextureStage.MGloss)
          if matflag_shadowself0 and matflag_shadowself1 and matflag_twoside:
             # セルフ影マツ or       # セルフ影              # Twoside
            ts_main.setMode(TextureStage.MModulate)
          else:
            nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
            pass

        if hasAlpha(texMain):
          # if nodePath.getTransparency() != TransparencyAttrib.MNone:
          #   pass

          #
          # it's a stupid method for setTransparency, but now i can not found another effected method
          #
          if not matflag_outline:
            nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
          elif matflag_outline and mat.edge_color.a != 1:
            nodePath.setTransparency(TransparencyAttrib.MMultisample, tsid_main)
          elif mat.edge_color.a == 1:
            nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
          elif mat.sphere_texture_index < 0:
            nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
          else:
            # nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
            nodePath.setTransparency(TransparencyAttrib.MMultisample, tsid_main)
            # print('setting alpha except')
            pass

          #
          # it's a stupid method for setTransparency, but now i can not found another effected method
          #
          # print mat.name.lower()[:4]
          if mat.alpha == 1:
            if matflag_twoside and mat.specular_factor > 100:
              nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
            elif not matflag_twoside and mat.specular_factor > 20:
              nodePath.setTransparency(TransparencyAttrib.MNone, tsid_main)
            elif matflag_twoside and mat.specular_factor > 20:
              nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
            elif matflag_twoside and mat.specular_factor > 10:
              pass
            elif matflag_twoside and 2 < mat.specular_factor <= 10:
              nodePath.setTransparency(TransparencyAttrib.MNone, tsid_main)
              pass
            elif matflag_twoside and mat.specular_factor >= 5:
              nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
            elif matflag_twoside and mat.specular_factor > 1:
              nodePath.setTransparency(TransparencyAttrib.MNone, tsid_main)
          elif mat.alpha == 0:
            nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
          elif mat.sphere_texture_index < 0 and mat.specular_factor > 0:
            nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
          elif mat.sphere_texture_index < 0 and not matflag_twoside and mat.specular_factor > 20:
            nodePath.setTransparency(TransparencyAttrib.MNone, tsid_main)

        else:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
          # nodePath.setTransparency(TransparencyAttrib.MBinary, tsid_main)

        if mat.name.lower() in ['hairshadow', 'other', 'body']:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name.lower()[:4] in ['face']:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name.lower()[:3] in ['eye']:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name in ['肌', '顔', '髪影', 'レース']:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name in ['スカート']:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name in ['瞳']:
          nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
        elif mat.name.find('瞳') >= 0:
          # ts_main.setMode(TextureStage.MModulateGloss)
          nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
        elif mat.name in ['頬']:
          ts_main.setMode(TextureStage.MModulateGloss)
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name.find('頬') >= 0:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name in ['白目']:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name.find('ﾏｰｸ') >= 0:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name.find('ｸﾞﾚｲ') >= 0:
          nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
        elif mat.name.find('マーク') >= 0:
          nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
        elif mat.name.find('透過') >= 0 and (0 < mat.alpha < 1):
          nodePath.setTransparency(TransparencyAttrib.MMultisample, tsid_main)
        elif mat.name.find('hair') >= 0:
          nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)



          pass

        # print(nodePath.getTransparency())
        if matflag_shadowfloor:
          # 地面影
          pass

        if mat.alpha > 0:
          nodePath.setTexture(ts_main, texMain, tsid_main)
          nodePath.setTexScale(ts_main, 1, -1, -1)
      else:
        if 0 < mat.alpha < 1:
          nodePath.setTransparency(TransparencyAttrib.MAlpha, tsid_main)
    else:
      if mat.name.lower() in ['hairshadow', 'other']:
        nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
      elif mat.name.lower()[:4] in ['face']:
        nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
      elif mat.name.lower()[:3] in ['eye']:
        nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
      elif mat.name in ['肌', '顔', '髪影', 'レース']:
        nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
      elif mat.name in ['スカート', '瞳']:
        nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
      elif mat.name in ['白目']:
        nodePath.setTransparency(TransparencyAttrib.MDual, tsid_main)
      pass

    #
    # Set Sphere Texture
    #
    if mat.sphere_texture_index >= 0:
      # print('Texture %s : Sphere %03d' % (mat.name, mat.sphere_texture_index))
      if mat.sphere_mode > 0:
        texSphere = textures[mat.sphere_texture_index]
        if texSphere and texSphere.hasRamImage():
          if mat.sphere_mode == 1:
            texMode = TextureStage.MModulateGloss
          elif mat.sphere_mode == 2:
            texMode = TextureStage.MAdd
          elif mat.sphere_mode == 3:
            texMode = TextureStage.MReplace
          else:
            texMode = TextureStage.MModulate

          ts_sphere = TextureStage('%3d_%s_sphere' % (matIndex, mat.name))

          ts_sphere.setMode(texMode)
          ts_sphere.setColor(VBase4(mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, 1))
          ts_sphere.setSort(tsid_sphere)
          ts_sphere.setPriority(tsid_sphere)

          nodePath.setTexGen(ts_sphere, TexGenAttrib.MEyeSphereMap, tsid_sphere)
          nodePath.setTexture(ts_sphere, texSphere, tsid_sphere)
          nodePath.setTexScale(ts_sphere, 1, -1, -1)
          # nodePath.setShaderAuto(matIndex)

          if mat.texture_index < 0:
            if hasAlpha(texSphere):
              nodePath.setTransparency(TransparencyAttrib.MDual, tsid_sphere)
            # else:
            #   nodePath.setTransparency(TransparencyAttrib.MNone, tsid_sphere)

    #
    # Set Toon Texture
    #
    if mat.toon_texture_index>=0:
      # print('Texture %s : Toon %03d' % (mat.name, mat.toon_texture_index))

      if mat.toon_sharing_flag > 0:
        texToon = loadTexture(u'toon/toon%02d.bmp' % (mat.toon_texture_index+1))
      elif (mat.toon_texture_index < 0) or (not textures[mat.toon_texture_index]):
        texToon = Texture('NULL')
      else:
        texToon = textures[mat.toon_texture_index]

      if texToon and texToon.hasRamImage():
        # texMode = TextureStage.MDecal
        # texMode = TextureStage.MGloss
        # texMode = TextureStage.MAdd
        texMode = TextureStage.MModulate #Glow

        ts_toon = TextureStage('%3d_%s_toon' % (matIndex, mat.name))
        ts_toon.setColor(VBase4(0,0,0, .18))
        ts_toon.setMode(texMode)
        ts_toon.setSort(tsid_toon)
        ts_toon.setPriority(tsid_toon)

        nodePath.setTexGen(ts_toon, TexGenAttrib.MEyeSphereMap, tsid_toon)
        nodePath.setTexture(ts_toon, texToon, tsid_toon)
        nodePath.setTexScale(ts_toon, 1, -1, -1)
        pass

    # nodePath.setBin("unsorted", matIndex)
    nodePath.setAntialias(AntialiasAttrib.MAuto)

    # print(nodePath.getTransparency())
    vIndex += mat.vertex_count

    # modelBody.addChild(node)
    nodePath.reparentTo(bodyPath)
    log(u'Loaded Polygons %03d: %s' % (matIndex, mat.name))
    matIndex += 1

  # modelPath = NodePath(model)
  # modelPath.setShaderAuto()
  return(modelPath)
  pass

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
  # Load Bone outline for display
  #
  data = EggData()
  data.read('stages/bone.egg')
  # data.read('stages/bone_oct.egg')
  # data.read('stages/bone_cone.egg')
  dnp = NodePath(loadEggData(data))
  dnp.setColor(LVector4f(1,1,0,1))
  boneOutline = dnp.node().getChild(0)
  min_point = LPoint3f()
  max_point = LPoint3f()
  dnp.calcTightBounds(min_point, max_point)
  bone_size = LPoint3f(max_point.x-min_point.x, max_point.y-min_point.y, max_point.z-min_point.z)

  #
  # Load Bone data
  #
  formatArray = GeomVertexArrayFormat()
  formatArray.addColumn(InternalName.make(str("vindex")), 1, Geom.NTUint32, Geom.CIndex)
  formatArray.addColumn(InternalName.make(str("tindex")), 1, Geom.NTFloat32, Geom.COther)
  formatArray.addColumn(InternalName.make(str("pindex")), 1, Geom.NTFloat32, Geom.COther)

  format = GeomVertexFormat(GeomVertexFormat.getV3c4())
  format.addArray(formatArray)
  format = GeomVertexFormat.registerFormat(format)

  boneNode = PandaNode('Bones')
  boneIndex = 0
  for bone in pmx_model.bones:
    log(u'Loading Bone %03d: %s' % (boneIndex, bone.name), force=True)

    #
    # load vertices(vertex list)
    #
    vdata = GeomVertexData(bone.name+'_vdata', format, Geom.UHDynamic)
    vdata.setNumRows(3)

    vertex = GeomVertexWriter(vdata, 'vertex')
    color = GeomVertexWriter(vdata, 'color')
    vindex = GeomVertexWriter(vdata, 'vindex')
    tindex = GeomVertexWriter(vdata, 'tindex')
    pindex = GeomVertexWriter(vdata, 'pindex')

    node = GeomNode(bone.name)

    tu = LVector3f(bone.tail_position.x, bone.tail_position.y, bone.tail_position.z)
    log(tu.cross(LVector3f(bone.position.x, bone.position.y, bone.position.z)))

    if bone.tail_index >= 0:
      t = V2V(pmx_model.bones[bone.tail_index].position)
    else:
      t = V2V(bone.position+bone.tail_position)
    vertex.addData3f(t)
    color.addData4f(.95, .95, 0, 1) # Yellow
    vindex.addData1i(boneIndex)
    tindex.addData1i(bone.tail_index)
    pindex.addData1i(bone.parent_index)

    v = V2V(bone.position)
    vertex.addData3f(v)
    color.addData4f(0, .95, 0.95, 1) # Cyan
    vindex.addData1i(boneIndex)
    tindex.addData1i(bone.tail_index)
    pindex.addData1i(bone.parent_index)

    geom = Geom(vdata)

    prim = GeomLines(Geom.UHDynamic)
    prim.addVertex(0)
    prim.addVertex(1)
    geom.addPrimitive(prim)

    node.addGeom(geom)

    node.setPythonTag('english_name', bone.english_name)
    node.setPythonTag('position', V2V(bone.position))
    node.setPythonTag('parent_index', bone.parent_index)
    node.setPythonTag('layer', bone.layer)
    node.setPythonTag('flag', bone.flag)
    node.setPythonTag('tail_index', bone.tail_index)
    node.setPythonTag('tail_position', V2V(bone.tail_position))
    node.setPythonTag('effect_index', bone.effect_index)
    node.setPythonTag('effect_factor', bone.effect_factor)
    node.setPythonTag('fixed_axis', V2V(bone.fixed_axis))
    node.setPythonTag('local_x_vector', V2V(bone.local_x_vector))
    node.setPythonTag('local_z_vector', V2V(bone.local_z_vector))
    node.setPythonTag('external_key', bone.external_key)
    if bone.ik:
      iklink = map(lambda ik: {
        'bone_index':ik.bone_index,
        'limit_angle':ik.limit_angle,
        'limit_max':LVector3f(V2V(ik.limit_max)),
        'limit_min':LVector3f(V2V(ik.limit_min))
        }, bone.ik.link)

      node.setPythonTag('ik.limit_radian', bone.ik.limit_radian)
      node.setPythonTag('ik.loop', bone.ik.loop)
      node.setPythonTag('ik.target_index', bone.ik.target_index)
      node.setPythonTag('ik.link', bone.ik.link)
    else:
      node.setPythonTag('ik', None)
    node.setPythonTag('index', bone.index)
    node.setPythonTag('boneIndex', boneIndex)
    node.setPythonTag('pickableObjTag', 1)

    vd = vdist(v, t)
    scale = vd / bone_size.z
    s_x = scale if scale<.25 else .25
    s_y = scale if scale<.25 else .25
    s_z = scale #if scale<.25 else .25
    s = LVector3f(s_x, s_y, s_z)

    r = getHprFromTo(v, t)
    trans = TransformState.makePosHprScale(v, r, s)
    bo = boneOutline.makeCopy()
    bo.setName(bone.name)
    bo.setTransform(trans)
    bo.setPythonTag('pickableObjTag', 1)

    parentNode = GetParentNode(boneNode, bone.parent_index)
    if isinstance(parentNode, PandaNode):
      # print('PNode: ', parentNode)
      parentNode.addChild(node)
      parentNode.addChild(bo)
    elif isinstance(parentNode, GeomNode):
      # print('GNode: ', parentNode)
      parentNode.addGeom(node)
      # parentNode.addGeom(bo)
    boneIndex += 1

  np = NodePath(boneNode)
  np.setRenderModeWireframe()
  # np.setPythonTag('pickableObjTag', 1)
  # ofs = OFileStream('bonelist.txt', 3)
  # np.ls(ofs, 2)
  np.hide()
  return(np)

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
    log(u'Loading Morph %03d: %s' % (morphIndex, morph.name), force=True)

    #
    # load vertices(vertex list)
    #
    vdata = GeomVertexData(morph.name+'_vdata', format, Geom.UHDynamic)
    # vdata.setNumRows(6)

    vertex = GeomVertexWriter(vdata, 'vertex')
    vindex = GeomVertexWriter(vdata, 'vindex')
    # vmorph = GeomVertexWriter(vdata, 'v.morph')
    vmorph = GeomVertexWriter(vdata, 'vmorph')
    transform_index = GeomVertexWriter(vdata, 'transform_index')
    transform_weight = GeomVertexWriter(vdata, 'transform_weight')
    column_morph_slider = GeomVertexWriter(vdata, 'emotion.morph.strange')

    node = GeomNode(morph.name)

    morphData = None

    if   morph.morph_type == 0: # group morph
      morphData = []
      for idx in xrange(len(morph.offsets)):
        offset = morph.offsets[idx]
        o = offset
        morphData.append((o.morph_index, o.value))
      pass
    elif morph.morph_type == 1: # vertex morph
      morphID = encode(morph.name)
      morphEggText = []
      morphEggText.append(u'<CoordinateSystem> { Z-up }')
      morphEggText.append(u'<Group> %s_ACTOR {' % morphID)
      morphEggText.append(u'  <DART> { 1 }')
      morphEggText.append(u'  <Group> %s {' % morphID)
      morphEggText.append(u'    <VertexPool> %s {' % morphID)

      prim = GeomPoints(Geom.UHDynamic)
      vdata.setNumRows(len(morph.offsets))
      for idx in xrange(len(morph.offsets)):
        offset = morph.offsets[idx]
        v = V2V(pmx_model.vertices[offset.vertex_index].position)
        o = V2V(offset.position_offset)
        i = offset.vertex_index
        vertex.addData3f(v)
        vindex.addData1i(i)
        vmorph.addData3f(o)
        transform_index.addData1i(i)
        transform_weight.addData3f(o)
        column_morph_slider.addData1f(1.0)
        prim.addVertex(idx)

        morphEggText.append(u'      <Vertex> %d {' % idx)
        morphEggText.append(u'        %.11f %.11f %.11f' % (v.x, v.y, v.z))
        morphEggText.append(u'        <Dxyz> Wedge { %.6f %.6f %.6f }' % (o.x, o.y, o.z))
        morphEggText.append(u'      }')

      morphEggText.append(u'    }')
      morphEggText.append(u'  }')
      morphEggText.append(u'}')

      geom = Geom(vdata)
      geom.addPrimitive(prim)
      node.addGeom(geom)

      egg = EggData()
      egg.read(StringStream('\n'.join(morphEggText)))
      action = loadEggData(egg).getChild(0)
      node.addChild(action)
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
    node.setPythonTag('pickableObjTag', 1)
    morphNode.addChild(node)

    morphIndex += 1

  np = NodePath(morphNode)
  np.hide()
  return(np)
  pass

def loadPmxSlot(pmx_model):
  #
  # Load Display Slot data
  #
  slotNode = PandaNode('Slots')
  slotIndex = 0
  for slot in pmx_model.display_slots:
    log(u'Loading Slot %03d: %s' % (slotIndex, slot.name), force=True)
    node = PandaNode(slot.name)
    node.setPythonTag('english_name', slot.english_name)
    node.setPythonTag('references', slot.references)
    node.setPythonTag('special_flag', slot.special_flag)
    node.setPythonTag('slotIndex', slotIndex)
    node.setPythonTag('pickableObjTag', 1)

    slotNode.addChild(node)
    slotIndex += 1
  np = NodePath(slotNode)
  np.hide()
  return(np)

def loadPmxRigid(pmx_model):
  #
  # Load Rigid data
  #
  rigidNode = PandaNode('Rigid')
  rigidIndex = 0
  for rigid in pmx_model.rigidbodies:
    log(u'Loading Rigid %03d: %s' % (rigidIndex, rigid.name), force=True)
    node = PandaNode(rigid.name)
    node.setPythonTag('english_name', rigid.english_name)
    node.setPythonTag('bone_index', rigid.bone_index)
    node.setPythonTag('collision_group', rigid.collision_group)
    node.setPythonTag('no_collision_group', rigid.no_collision_group)
    node.setPythonTag('shape_type', rigid.shape_type)
    node.setPythonTag('shape_size', V2V(rigid.shape_size))
    node.setPythonTag('shape_position', V2V(rigid.shape_position))
    node.setPythonTag('shape_rotation', R2DV(rigid.shape_rotation))
    node.setPythonTag('param.mass', rigid.param.mass)
    node.setPythonTag('param.linear_damping', rigid.param.linear_damping)
    node.setPythonTag('param.angular_damping', rigid.param.angular_damping)
    node.setPythonTag('param.restitution', rigid.param.restitution)
    node.setPythonTag('param.friction', rigid.param.friction)
    node.setPythonTag('mode', rigid.mode)
    node.setPythonTag('rigidIndex', rigidIndex)
    node.setPythonTag('pickableObjTag', 1)

    rigidNode.addChild(node)
    rigidIndex += 1
  np = NodePath(rigidNode)
  np.hide()
  return(np)

def loadPmxJoint(pmx_model):
  #
  # Load Joints data
  #
  jointNode = PandaNode('Joints')
  jointIndex = 0
  for joint in pmx_model.joints:
    log(u'Loading Joint %03d: %s' % (jointIndex, joint.name), force=True)
    node = PandaNode(joint.name)
    node.setPythonTag('english_name', joint.english_name)
    node.setPythonTag('joint_type', joint.joint_type)
    node.setPythonTag('rigidbody_index_a', joint.rigidbody_index_a)
    node.setPythonTag('rigidbody_index_b', joint.rigidbody_index_b)
    node.setPythonTag('position', V2V(joint.position))
    node.setPythonTag('rotation', R2DV(joint.rotation))
    node.setPythonTag('translation_limit_min', V2V(joint.translation_limit_min))
    node.setPythonTag('translation_limit_max', V2V(joint.translation_limit_max))
    node.setPythonTag('rotation_limit_min', R2DV(joint.rotation_limit_min))
    node.setPythonTag('rotation_limit_max', R2DV(joint.rotation_limit_max))
    node.setPythonTag('spring_constant_translation', V2V(joint.spring_constant_translation))
    node.setPythonTag('spring_constant_rotation', R2DV(joint.spring_constant_rotation))
    node.setPythonTag('jointIndex', jointIndex)
    node.setPythonTag('pickableObjTag', 1)

    jointNode.addChild(node)
    jointIndex += 1
  np = NodePath(jointNode)
  np.hide()
  return(np)

def loadPmxActor(pmx_model):
  model = loadPmxModel(pmx_model)
  pass

def loadPmxOde(pmx_model, world):
  bodyNP = NodePath('Physics')

  if not world:
    return None

  rigidIndex = 0
  rigidList = []
  for rigid in pmx_model.rigidbodies:
    shape_size = V2V(rigid.shape_size)
    shape_pos = V2V(rigid.shape_position)
    shape_rot = R2DV(rigid.shape_rotation)

    log(u'%03d: s%s, p%s, r%s'% (len(rigidList), str(shape_size), str(shape_pos), str(shape_rot)))

    if rigid.bone_index==-1:
      bone = pmx_model.bones[0]
    else:
      bone = pmx_model.bones[rigid.bone_index]

    rigidBody = OdeBody(world)
    rigidMass = OdeMass()
    mass = rigid.param.mass
    if mass <= 0:
      mass = 0.01
    if rigid.shape_type == 0:
      rigidMass.setSphereTotal(mass, shape_size.x)
      rigidGeom = OdeSphereGeom(shape_size.x)
    elif rigid.shape_type == 1:
      rigidMass.setBoxTotal(mass, shape_size)
      rigidGeom = OdeBoxGeom(shape_size.x, shape_size.y, shape_size.z)
    elif rigid.shape_type == 2:
      rigidMass.setCapsuleTotal(mass, 1, shape_size.x, shape_size.z)
      rigidGeom = OdeCappedCylinderGeom(shape_size.x, shape_size.z)
    rigidGeom.setBody(rigidBody)
    rigidBody.setMass(rigidMass)
    rigidBody.setPosition(shape_pos)
    rigidBody.setQuaternion(Quat(1, shape_rot))

    world.applyDampening(rigid.param.linear_damping, rigidBody)

    # rigidBody.setLinearDamping(rigid.param.linear_damping)
    # rigidBody.setAngularDamping(rigid.param.angular_damping)
    # rigidBody.setRestitution(rigid.param.restitution)
    # rigidBody.setFriction(rigid.param.friction)

    rigidNode = PandaNode(rigid.name)
    rigidNode.setPythonTag('body', rigidBody)
    rigidNode.setPythonTag('geom', rigidGeom)
    rigidNode.setPythonTag('name', rigid.name)
    rigidNode.setPythonTag('index', rigidIndex)
    rigidNode.setPythonTag('mode', rigid.mode)
    rigidNode.setPythonTag('bone_index', rigid.bone_index)
    rigidNode.setPythonTag('rotation', shape_rot)
    rigidNode.setPythonTag('collision_group', rigid.collision_group)
    rigidNode.setPythonTag('no_collision_group', rigid.no_collision_group)
    rigidNode.setPythonTag('pickableObjTag', 1)

    rigidList.append(rigidNode)
    rigidIndex += 1

  csList = OdeJointCollection()
  for joint in pmx_model.joints:
    rigidIndexA = joint.rigidbody_index_a
    rigidIndexB = joint.rigidbody_index_b
    translimit_min = V2V(joint.translation_limit_min)
    translimit_max = V2V(joint.translation_limit_max)
    rotlimit_min = R2DV(joint.rotation_limit_min)
    rotlimit_max = R2DV(joint.rotation_limit_max)
    springTrans = V2V(joint.spring_constant_translation)
    springRot = R2DV(joint.spring_constant_rotation)

    rigidNodeA = rigidList[rigidIndexA]
    ragidBodyA = rigidNodeA.getPythonTag('body')
    rigidNodeB = rigidList[rigidIndexB]
    ragidBodyB = rigidNodeB.getPythonTag('body')

    cs = OdeBallJoint(world)
    cs.attach(ragidBodyA, ragidBodyB)
    # cs.setAnchor()
    # cs.setAnchor2()

    rot_limit = rotlimit_max - rotlimit_min
    twist  = rot_limit.x # degrees
    swing1 = rot_limit.y # degrees
    swing2 = rot_limit.z # degrees

    # cs.flexLimit = swing1
    # cs.twistLimit = twist

    csList.addJoint(cs)
    log(u'%03d: %s <-> %s' % (len(csList)-1, rigidNodeA.getPythonTag('name'), rigidNodeB.getPythonTag('name')))

  # geomList = []
  # for bone  in
  # bodyNP.ls()

  bodyNP.setPythonTag('Engine', 'ode')
  bodyNP.setPythonTag('Joints', csList)
  bodyNP.setPythonTag('Rigids', rigidList)
  bodyNP.setPythonTag('Bones', pmx_model.bones)

  # ofs = OFileStream('jointlist.txt', 3)
  # bodyNP.ls(ofs, 2)
  # bodyNP.ls()
  return(bodyNP)
  pass

def loadPmxBullet(pmx_model):
  bodyNP = NodePath('Physics')

  rigidIndex = 0
  rigidList = []
  for rigid in pmx_model.rigidbodies:
    shape_size = V2V(rigid.shape_size)
    shape_pos = V2V(rigid.shape_position)
    shape_rot = R2DV(rigid.shape_rotation)

    log(u'%03d: s%s, p%s, r%s'% (len(rigidList), str(shape_size), str(shape_pos), str(shape_rot)))

    if rigid.bone_index==-1:
      bone = pmx_model.bones[0]
    else:
      bone = pmx_model.bones[rigid.bone_index]

    if rigid.shape_type == 0:
      shape = BulletSphereShape(shape_size.x)
    elif rigid.shape_type == 1:
      shape = BulletBoxShape(shape_size)
    elif rigid.shape_type == 2:
      shape = BulletCapsuleShape(shape_size.x, shape_size.z)
    else:
      log('--> other shape type: %d' % rigid.shape_type)
      continue

    rigidBody = BulletRigidBodyNode(rigid.name)
    rigidBody.addShape(shape)
    # if rigid.param.mass != 1:
    if rigid.param.mass > 0:
      rigidBody.setMass(rigid.param.mass)
      rigidBody.setStatic(False)
    else:
      rigidBody.setStatic(True)
    rigidBody.setLinearDamping(rigid.param.linear_damping)
    rigidBody.setAngularDamping(rigid.param.angular_damping)
    rigidBody.setRestitution(rigid.param.restitution)
    rigidBody.setFriction(rigid.param.friction)

    rigidBody.setPythonTag('bone_index', rigid.bone_index)
    rigidBody.setPythonTag('rotation', shape_rot)
    rigidBody.setPythonTag('collision_group', rigid.collision_group)
    rigidBody.setPythonTag('no_collision_group', rigid.no_collision_group)
    rigidBody.setPythonTag('mode', rigid.mode)
    rigidBody.setPythonTag('rigidIndex', rigidIndex)
    rigidBody.setPythonTag('pickableObjTag', 1)

    if rigid.mode == 0:
      rigidBody.setKinematic(True)
      # rigidBody.setDeactivationEnabled(True)
    elif rigid.mode == 1:
      rigidBody.setKinematic(False)
      # rigidBody.setDeactivationEnabled(False)
    else:
      rigidBody.setKinematic(True)
      # rigidBody.setDeactivationEnabled(True)

    # rigidBody.setDeactivationEnabled(True)
    rigidBody.setCollisionResponse(True)
    rigidBody.setActive(True)

    rigidBodyNP = NodePath(rigidBody)
    rigidBodyNP.setPos(shape_pos)
    rigidBodyNP.setHpr(shape_rot)
    # rigidBodyNP.setHpr(NodePath(bone), shape_rot)
    rigidBodyNP.setPythonTag('pickableObjTag', 1)

    rigidBodyNP.reparentTo(bodyNP)
    rigidList.append(rigidBody)
    rigidIndex += 1

  csList = []
  for joint in pmx_model.joints:
    rigidIndexA = joint.rigidbody_index_a
    rigidIndexB = joint.rigidbody_index_b
    translimit_min = V2V(joint.translation_limit_min)
    translimit_max = V2V(joint.translation_limit_max)
    rotlimit_min = R2DV(joint.rotation_limit_min)
    rotlimit_max = R2DV(joint.rotation_limit_max)
    springTrans = V2V(joint.spring_constant_translation)
    springRot = R2DV(joint.spring_constant_rotation)

    ragidBodyA = rigidList[rigidIndexA]
    ragidBodyB = rigidList[rigidIndexB]

    # frameA = TransformState.makePosHpr(translimit_min, rotlimit_min)
    # frameB = TransformState.makePosHpr(translimit_max, rotlimit_max)
    pos = V2V(Vec3(0,0,0))
    rot = R2DV(Vec3(0,0,0))
    frameA = TransformState.makePosHpr(pos, rot)
    frameB = TransformState.makePosHpr(pos, rot)

    # swing1 = 60 # degrees
    # swing2 = 36 # degrees
    # twist = 120 # degrees
    rot_limit = rotlimit_max - rotlimit_min
    twist  = rot_limit.x # degrees
    swing1 = rot_limit.y # degrees
    swing2 = rot_limit.z # degrees

    cs = BulletConeTwistConstraint(ragidBodyA, ragidBodyB, frameA, frameB)
    cs.setLimit(swing1, swing2, twist)
    cs.setEnabled(True)
    cs.setDebugDrawSize(1.0)
    # cs.setPythonTag('pickableObjTag', 1)

    csList.append(cs)
    log(u'%03d: %s <-> %s' % (len(csList)-1, ragidBodyA.getName(), ragidBodyB.getName()))

  # bodyNP.ls()
  bodyNP.setPythonTag('Engine', 'bullet')
  bodyNP.setPythonTag('Rigids', rigidList)
  bodyNP.setPythonTag('Joints', csList)
  bodyNP.setPythonTag('Bones', pmx_model.bones)
  # ofs = OFileStream('jointlist.txt', 3)
  # bodyNP.ls(ofs, 2)
  # bodyNP.ls()
  return(bodyNP)
  pass

def loadPmxIK(pmx_model):
  #
  # Load IK data, PMX file is no IK now
  #
  ikNode = PandaNode('IK')
  ikIndex = 0
  for ik in pmx_model.iks:
    log(u'Loading IK %03d: %s' % (ikIndex, ik.name), force=True)
    node = PandaNode(slot.name)
    node.setPythonTag('english_name', ik.english_name)
    node.setPythonTag('references', ik.references)
    node.setPythonTag('special_flag', ik.special_flag)

    ikNode.addChild(node)
    ikIndex += 1
  np = NodePath(ikNode)
  np.hide()
  return(np)

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

def loadPmxModel(modelfile, world=None, engine='bullet'):
  p3dnode = None
  try:
    mmdFile = os.path.relpath(modelfile)
  except:
    mmdFile = modelfile
    pass

  ext = os.path.splitext(mmdFile)[1].lower()
  if os.path.altsep:
    mmdFile = mmdFile.replace(os.path.sep, os.path.altsep)
  if ext in ['.pmx']:
    mmdModel = pmxLoad(mmdFile)
    if mmdModel:
      p3dnode = loadPmxBody(mmdModel)
      morphs = loadPmxMorph(mmdModel)
      if morphs:
        morphs.reparentTo(p3dnode)
      bones = loadPmxBone(mmdModel)
      if bones:
        bones.reparentTo(p3dnode)
      slots = loadPmxSlot(mmdModel)
      if slots:
        slots.reparentTo(p3dnode)
      rigids = loadPmxRigid(mmdModel)
      rigids.reparentTo(p3dnode)
      joints = loadPmxJoint(mmdModel)
      joints.reparentTo(p3dnode)
      if engine.lower() == 'bullet':
        physics = loadPmxBullet(mmdModel)
      elif engine.lower() == 'ode':
        physics = loadPmxOde(mmdModel, world)
      if physics:
        physics.reparentTo(p3dnode)
        # p3dnode.setPythonTag('Physics', physics)
        pass

  elif ext in ['', '.egg', '.pz', '.bam']:
    return(p3dnode)
  return(p3dnode)

def testPMX(pmx):
  pmxModel = pmxLoad(pmx)
  if pmxModel:
    displayPmxModelInfo(pmxModel)

    from direct.showbase.ShowBase import ShowBase
    base = ShowBase()

    p3dnode = pmx2p3d(pmxModel)
    p3dnode.reparentTo(base.render)

    base.run()
    pass
  pass

if __name__ == '__main__':
  pmxFile = u'../models/meiko/meiko.pmx'
  pmxFile = u'../models/apimiku/Miku long hair.pmx'
  pmxFile = u'../models/cupidmiku/Cupid Miku.pmx'

  # pmxFile = u'../models/alice/alice.pmd'

  if len(sys.argv) > 1:
    if len(sys.argv[1]) > 0:
      pmxFile = sys.argv[1]

  ext = os.path.splitext(pmxFile)[1].lower()
  if ext in ['.pmd']:
    testPMD(pmxFile)
  elif ext in ['.pmx']:
    testPMX(pmxFile)

  # testPMD(pmdFile)


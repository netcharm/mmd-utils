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
  textures = []
  for tex in pmx_model.textures:
    tex_path = os.path.normpath(os.path.join(os.path.dirname(pmx_model.path), tex))
    tex_path = os.path.normcase(tex_path)
    log(u'Loading Texture : %s' % os.path.dirname(tex))
    texture = loadTexture(tex_path, model_path=modelPath)
    textures.append(texture)
    if texture:
      log(u'Loaded Texture : %s' % tex, force=True)
    else:
      log(u'Texture Failed : %s' % tex, force=True)

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
    # material.setEmission(VBase4(1, 1, 1, 0.67))
    # material.setEmission(VBase4(mat.edge_color.r, mat.edge_color.g, mat.edge_color.b, mat.alpha))


    material.setLocal(False)
    material.setTwoside(False)
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

  modelName = pmx_model.name
  #
  # load vertices(vertex list)
  #
  formatArray = GeomVertexArrayFormat()
  formatArray.addColumn(InternalName.make(str("edge_factor")), 1, Geom.NTFloat32, Geom.COther)
  formatArray.addColumn(InternalName.make(str("drawFlag")), 1, Geom.NTUint8, Geom.COther)
  formatArray.addColumn(InternalName.make(str("index")), 1, Geom.NTUint32, Geom.CIndex)
  # formatArray.addColumn(InternalName.make(str("morph")), 1, Geom.NTFloat32, Geom.CMorphDelta)

  format = GeomVertexFormat(GeomVertexFormat.getV3n3cpt2())
  format.addArray(formatArray)
  format = GeomVertexFormat.registerFormat(format)

  vdata = GeomVertexData(modelName, format, Geom.UHDynamic)
  vdata.setNumRows(len(pmx_model.vertices))

  vertex = GeomVertexWriter(vdata, 'vertex')
  normal = GeomVertexWriter(vdata, 'normal')
  color = GeomVertexWriter(vdata, 'color')
  texcoord = GeomVertexWriter(vdata, 'texcoord')
  edge = GeomVertexWriter(vdata, 'edge_factor')
  index = GeomVertexWriter(vdata, 'index')

  idx = 0
  for v in pmx_model.vertices:
    vertex.addData3f(V2V(v.position))
    normal.addData3f(V2V(v.normal))
    color.addData4f(.95, .95, .95, 1)
    texcoord.addData2f(v.uv.x, v.uv.y)
    edge.addData1f(v.edge_factor)
    index.addData1i(idx)
    idx += 1

  #
  # load polygons face
  #
  vIndex = 0
  model = Character(modelName)
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
    nodePath.setMaterial(materials.findMaterial(mat.name), 1) #Apply the material to this nodePath

    nodePath.setPythonTag('edge_color', mat.edge_color)
    nodePath.setPythonTag('edge_size', mat.edge_size)
    nodePath.setPythonTag('material_index', matIndex)
    nodePath.setPythonTag('material', materials.findMaterial(mat.name))
    nodePath.setPythonTag('pickableObjTag', 1)

    #
    # set polygon face main textures
    #
    if mat.texture_index >= 0 and textures[mat.texture_index]:
      textures[mat.texture_index].setBorderColor(VBase4(mat.edge_color.r, mat.edge_color.g, mat.edge_color.b, mat.alpha))
      # if setWrapU then some model may be error, such as not mirror symmetry texture.
      # textures[mat.texture_index].setWrapU(Texture.WM_clamp)
      # # textures[mat.texture_index].setWrapV(Texture.WM_clamp)
      nodePath.setTexture(textures[mat.texture_index], matIndex)
      nodePath.setTexScale(TextureStage.getDefault(), 1, -1, -1)
      if textures[mat.texture_index].getFormat() in [Texture.FRgba, Texture.FRgbm, Texture.FRgba4, Texture.FRgba5, Texture.FRgba8, Texture.FRgba12, Texture.FRgba16, Texture.FRgba32]: #, Texture.FSrgbAlpha]:
        nodePath.setTransparency(TransparencyAttrib.MDual, matIndex)
        # nodePath.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd,
        #                    ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne))

    #
    # Set Sphere Texture
    #
    if mat.sphere_texture_index >=0 and textures[mat.sphere_texture_index]:
      if mat.sphere_mode > 0:
        if mat.sphere_mode == 1:
          texMode = TextureStage.MModulateGlow
        elif mat.sphere_mode == 2:
          texMode = TextureStage.MAdd
        elif mat.sphere_mode == 3:
          texMode = TextureStage.MReplace
        else:
          texMode = TextureStage.MGloss

        tex = textures[mat.sphere_texture_index]
        tex.setWrapU(Texture.WM_clamp)
        # tex.setWrapV(Texture.WM_clamp)

        ts_sphere = TextureStage(mat.name+'_sphere')
        ts_sphere.setMode(texMode)

        ts_sphere.setSort(matIndex)
        ts_sphere.setPriority(matIndex)

        nodePath.setTexGen(ts_sphere, TexGenAttrib.MEyeSphereMap, matIndex)
        nodePath.setTexture(ts_sphere, tex, matIndex)
        nodePath.setTexScale(ts_sphere, 1, -1, -1)
        # nodePath.setShaderAuto(matIndex)

    #
    # Set Toon Texture
    #
    if mat.toon_texture_index>=0:
      # texMode = TextureStage.MModulateGloss
      texMode = TextureStage.MGlow

      ts_toon = TextureStage(mat.name+'_toon')
      ts_toon.setColor(VBase4(1,1,1,.33))
      ts_toon.setMode(texMode)
      ts_toon.setSort(matIndex)
      ts_toon.setPriority(matIndex)

      if mat.toon_sharing_flag > 0:
        tex = loadTexture(u'toon/toon%02d.bmp' % (mat.toon_texture_index+1))
      elif (mat.toon_texture_index < 0) or (not textures[mat.toon_texture_index]):
        tex = loadTexture(u'toon/toon0.bmp')
      else:
        tex = textures[mat.toon_texture_index]
      tex.setWrapU(Texture.WM_clamp)
      #tex.setWrapV(Texture.WM_clamp)

      nodePath.setTexGen(ts_toon, TexGenAttrib.MEyeSphereMap, matIndex)
      nodePath.setTexture(ts_toon, tex, matIndex)
      nodePath.setTexScale(ts_toon, 1, -1, -1)

    nodePath.setAntialias(AntialiasAttrib.MAuto)

    vIndex += mat.vertex_count
    modelBody.addChild(node)
    matIndex += 1
    log(u'Loaded Node : %s' % mat.name, force=True)

  modelPath = NodePath(model)
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
    log(u'Loading Bone : %s' % bone.name, force=True)

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
    log(u'Loading Morph : %s' % morph.name, force=True)

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
    log(u'Loading Slot : %s' % slot.name, force=True)
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
    log(u'Loading RigidBodies : %s' % rigid.name, force=True)
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
    log(u'Loading RigidBodies : %s' % joint.name, force=True)
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

def loadPmxBullet(pmx_model):
  # body = BulletRigidBodyNode('Bullet')
  bodyNP = NodePath('Bullet')

  # boxBody = BulletRigidBodyNode('Box')
  # height = 1.75
  # radius = 0.4
  # shape = BulletCapsuleShape(radius, height - 2*radius, ZUp)
  # boxBody.addShape(shape)
  # boxBodyNP = NodePath(boxBody)
  # boxBodyNP.setPos(0, 0, 1.0001)
  # boxBodyNP.reparentTo(bodyNP)

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
    if rigid.param.mass != 1:
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
    twist = rot_limit.x # degrees
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
    log(u'Loading IK : %s' % ik.name, force=True)
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

def loadPmxModel(modelfile):
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
      # rigids = loadPmxRigid(mmdModel)
      # rigids.reparentTo(p3dnode)
      # joints = loadPmxJoint(mmdModel)
      # joints.reparentTo(p3dnode)
      bullet = loadPmxBullet(mmdModel)
      if bullet:
        bullet.reparentTo(p3dnode)
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


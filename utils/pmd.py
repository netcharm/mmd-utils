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

from common import *

from pymeshio import pmd
from pymeshio.pmd import reader as pmdReader


DEBUG = True
DEBUG = False

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])


def pmd2model(pmd):
  pmdModel = pmdLoad(pmd)
  p3dmodel = pmd2p3d(pmdModel)
  return(p3dmodel)

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
    lines.append(u'name(jpn)    : %s' % model.name.decode('shift_jis', errors='replace'))
    lines.append(u'name(eng)    : %s' % model.english_name.decode('shift_jis', errors='replace').strip())
    lines.append(u'comment(jpn) : \n{0}\n{1}\n{0}'.format('-'*80, model.comment.decode('shift_jis', errors='replace')))
    lines.append(u'comment(eng) : \n{0}\n{1}\n{0}'.format('-'*80, model.english_comment.decode('shift_jis', errors='replace')))
    lines.append(u'='*80)

    lines.append(u'toon_textures: Total {1}.\n{0}'.format('-'*80, len(model.toon_textures)))
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
      lines.append(u'  texture   : %s' % mat.texture_file)
      lines.append(u'  toon      : %4d' % (mat.toon_index))
      lines.append(u'  vertexs   : %4d' % mat.vertex_count)
    lines.append(u'='*80)

    lines.append(u'bones        : Total {1}.\n{0}'.format('-'*80, len(model.bones)))
    idx = 0
    for bone in model.bones:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % bone.name.decode('shift_jis', errors='replace'))
      lines.append(u'  name(eng)    : %s' % bone.english_name.decode('shift_jis', errors='replace'))
      lines.append(u'  index        : %4d' % bone.index)
      lines.append(u'  type         : %4d' % bone.type)
      lines.append(u'  pos          : %s' % str(bone.pos.to_tuple()))

      lines.append(u'  parent       : %4d, %s' % (bone.parent_index, (bone.parent.name.decode('shift_jis', errors='replace') if bone.parent else u'NULL')))
      lines.append(u'  tail         : %4d, %s' % (bone.tail_index, bone.tail))
      lines.append(u'  children     : %s' % bone.children[:5])
      lines.append(u'  ik_index     : %4d' % bone.ik_index)
    lines.append(u'='*80)

    lines.append(u'ik_list      : Total {1}.\n{0}'.format('-'*80, len(model.ik_list)))
    idx = 0
    for ik in model.ik_list:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  index      : %4d' % ik.index)
      lines.append(u'  target     : %s' % ik.target)
      lines.append(u'  weight     : %4d' % ik.weight)
      lines.append(u'  length     : %4d' % ik.length)
      lines.append(u'  children   : %s' % str(ik.children[:5]))
      lines.append(u'  iterations : %4d' % ik.iterations)
    lines.append(u'='*80)

    lines.append(u'morphs       : Total {1}.\n{0}'.format('-'*80, len(model.morphs)))
    idx = 0
    for morph in model.morphs:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % morph.name.decode('shift_jis', errors='replace'))
      lines.append(u'  name(eng)    : %s' % morph.english_name.decode('shift_jis', errors='replace'))
      lines.append(u'  type         : %4d' % morph.type)
      lines.append(u'  pos_list     : %s' % str(morph.pos_list[:4]))
      lines.append(u'  vertex_count : %4d' % morph.vertex_count)
      lines.append(u'  indices      : %4d, %s' % (len(morph.indices), morph.indices[:5]))
    lines.append(u'='*80)

    lines.append(u'morph_indices: Total {1}.\n{0}'.format('-'*80, len(model.morph_indices)))
    idx = 0
    for indices in model.morph_indices:
      if idx != 0: lines.append('')
      lines.append(u'  %8d : %8d' % (idx, indices))
      idx += 1
    lines.append(u'='*80)

    lines.append(u'bone_group_list : Total {1}.\n{0}'.format('-'*80, len(model.bone_group_list)))
    idx = 0
    for slot in model.bone_group_list:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % slot.name.decode('shift_jis', errors='replace'))
      lines.append(u'  name(eng)    : %s' % slot.english_name.decode('shift_jis', errors='replace'))
    lines.append(u'='*80)

    lines.append(u'bone_display_list : Total {1}.\n{0}'.format('-'*80, len(model.bone_display_list)))
    idx = 0
    for slot in model.bone_display_list:
      if idx != 0: lines.append('')
      lines.append(u'  %8d : %s' % (idx, slot))
      idx += 1
    lines.append(u'='*80)

    lines.append(u'rigidbodies  : Total {1}.\n{0}'.format('-'*80, len(model.rigidbodies)))
    idx = 0
    for rigidbody in model.rigidbodies:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)          : %s' % rigidbody.name.decode('shift_jis', errors='replace'))
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
      lines.append(u'  name(jpn)         : %s' % joint.name.decode('shift_jis', errors='replace'))
      lines.append(u'  rigidbody_index   : %4d, %4d' % (joint.rigidbody_index_a, joint.rigidbody_index_b))
      lines.append(u'  position          : %s' % str(joint.position.to_tuple()))
      lines.append(u'  rotation          : %s' % str(joint.rotation.to_tuple()))
      lines.append(u'  translation_limit : %s, %s' % (joint.translation_limit_min.to_tuple(), joint.translation_limit_max.to_tuple()))
      lines.append(u'  rotation_limit    : %s, %s' % (joint.rotation_limit_min.to_tuple(), joint.rotation_limit_max.to_tuple()))
      lines.append(u'  spring_constant   : %s, %s' % (joint.spring_constant_translation.to_tuple(), joint.spring_constant_rotation.to_tuple()))
    lines.append(u'='*80)

    lines.append(u'no_parent_bones : Total {1}.\n{0}'.format('-'*80, len(model.no_parent_bones)))
    idx = 0
    for bone in model.no_parent_bones:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  name(jpn)    : %s' % bone.name.decode('shift_jis', errors='replace'))
      lines.append(u'  name(eng)    : %s' % bone.english_name.decode('shift_jis', errors='replace'))
    lines.append(u'='*80)

    lines.append(u'vertices     : Total {1}.\n{0}'.format('-'*80, len(model.vertices)))
    idx = 0
    for vertex in model.vertices:
      if idx != 0: lines.append('')
      idx += 1
      lines.append(u'  pos       : %s' % str(vertex.pos.to_tuple()))
      lines.append(u'  normal    : %s' % str(vertex.normal.to_tuple()))
      lines.append(u'  uv        : %s' % str(vertex.uv.to_tuple()))
      lines.append(u'  bone0     : %s' % str(vertex.bone0))
      lines.append(u'  bone1     : %s' % str(vertex.bone1))
      lines.append(u'  weight0   : %s' % str(vertex.weight0))
      lines.append(u'  edge_flag : %4d' % vertex.edge_flag)
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

def pmd2p3d(pmd_model):
  return(loadPmdBody(pmd_model))

def loadPmdBody(pmd_model, alpha=True):
  modelPath = os.path.dirname(pmd_model.path)

  #
  # load textures
  #
  textures = TextureCollection()
  for tex in pmd_model.toon_textures:
    tex_path = os.path.join(modelPath, tex)
    if tex.lower() in ['toon01.bmp', 'toon02.bmp', 'toon03.bmp', 'toon04.bmp', 'toon05.bmp',
                       'toon06.bmp', 'toon07.bmp', 'toon08.bmp', 'toon09.bmp', 'toon10.bmp']:
      tex_path = u'toon/%s' % tex
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
  matIndex = 0
  for mat in pmd_model.materials:
    matName = u'mat_%04d' % matIndex
    log(u'Loading Material : %s' % matName)
    material = Material(matName)
    material.setDiffuse(VBase4(mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b, mat.alpha))

    # material.setSpecular(VBase4(mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, 1))
    if mat.specular_factor > 0 or (mat.specular_color.r != 1 and mat.specular_color.g != 1 and mat.specular_color.b != 1):
      material.setSpecular(VBase4(mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, 1))
      material.setShininess(mat.specular_factor*10)
    else:
      material.setSpecular(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, 0.01))
      material.setShininess(0)

    material.setAmbient(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, 1))

    material.setLocal(False)
    # material.setTwoside(True)
    materials.addMaterial(material)
    matIndex += 1
    log(u'Loaded Material : %s' % (matName), force=True)

  modelName = pmd_model.name.decode('shift_jis', errors='replace')
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
  vdata.setNumRows(len(pmd_model.vertices))

  vertex = GeomVertexWriter(vdata, 'vertex')
  normal = GeomVertexWriter(vdata, 'normal')
  color = GeomVertexWriter(vdata, 'color')
  texcoord = GeomVertexWriter(vdata, 'texcoord')
  edge = GeomVertexWriter(vdata, 'edge_factor')
  index = GeomVertexWriter(vdata, 'index')

  idx = 0
  for v in pmd_model.vertices:
    vertex.addData3f(V2V(v.pos))
    normal.addData3f(V2V(v.normal))
    color.addData4f(.95, .95, .95, 1)
    texcoord.addData2f(v.uv.x, v.uv.y)
    edge.addData1f(1.0)
    index.addData1i(idx)
    idx += 1


  #
  # load polygons face
  #
  vIndex = 0
  model = Character(modelName)
  model.setPythonTag('path', pmd_model.path)
  model.setPythonTag('version', str(pmd_model.version))
  model.setPythonTag('name', modelName)
  model.setPythonTag('english_name', pmd_model.english_name)
  model.setPythonTag('comment', pmd_model.comment)
  model.setPythonTag('english_comment', pmd_model.english_comment)

  modelBody = ModelRoot('Body')
  model.addChild(modelBody)

  matIndex = 0
  texList = dict()
  for mat in pmd_model.materials:
    matName = u'mat_%04d' % matIndex
    prim = GeomTriangles(Geom.UHStatic)
    log(u'Loading Node : %s' % matName)
    for idx in xrange(vIndex, vIndex+mat.vertex_count, 3):
      # flip trig-face for inverted axis-y/axis-z
      prim.addVertices(pmd_model.indices[idx+2], pmd_model.indices[idx+1], pmd_model.indices[idx+0])

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode(matName)
    node.addGeom(geom)
    nodePath = NodePath(node)

    #
    # set polygon face material
    #
    nodePath.setMaterial(materials[matIndex], 1) #Apply the material to this nodePath
    nodePath.setTwoSided(materials[matIndex].getTwoside())

    nodePath.setPythonTag('material', materials[matIndex])
    nodePath.setPythonTag('pickableObjTag', 1)

    #
    # set polygon face textures
    #
    texFileMain = None
    texFileSphere = None

    if (not mat.texture_file) and mat.toon_index < 0:
      nodePath.setTransparency(TransparencyAttrib.MDual, matIndex)

    if mat.alpha<1:
      nodePath.setTransparency(TransparencyAttrib.MAlpha, matIndex)

    if mat.texture_file and len(mat.texture_file) >= 0:
      texName = mat.texture_file.decode('shift_jis', errors='replace')
      tex_list = texName.split('*')
      if len(tex_list)==1:
        tex_list = texName.split('/')
      if len(tex_list)==2:
        texFileMain = tex_list[0].strip()
        texFileSphere = tex_list[1].strip()
      else:
        ext = os.path.splitext(texName)[1]
        if ext.lower() in ['.spa', '.sph']:
          texFileMain = None
          texFileSphere = texName
        else:
          texFileMain = texName
          texFileSphere = None

      if texFileMain:
        if not texFileMain in texList:
          texList[texFileMain] = loadTexture(os.path.join(modelPath, texFileMain))
          if texList[texFileMain]:
            log(u'Loaded Texture : %s' % texFileMain, force=True)
            # texList[texFileMain].setWrapU(Texture.WM_clamp)

        texMain = texList[texFileMain]
        if texMain and texMain.hasRamImage():
          if mat.edge_flag:
            # 輪郭有效
            texMain.setBorderColor(VBase4(mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b, 1))
          pass

          ts_main = TextureStage('%s_%3d_main' % (matName, matIndex))
          ts_main.setColor(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, 1))
          ts_main.setSort(matIndex)
          ts_main.setPriority(matIndex)

          if not texFileSphere:
            ts_main.setMode(TextureStage.MReplace)

          if isAlpha(texMain):
            nodePath.setTransparency(TransparencyAttrib.MDual, matIndex)

          nodePath.setTexture(ts_main, texMain)
          nodePath.setTexScale(ts_main, 1, -1, -1)

      if texFileSphere:
        texMode = TextureStage.MReplace
        ext = os.path.splitext(texFileSphere)[1]
        if ext.lower() in ['.spa']:
          texMode = TextureStage.MAdd
        elif ext.lower() in ['.sph']:
          # texMode = TextureStage.MGlow
          texMode = TextureStage.MModulateGlow
          # texMode = TextureStage.MBlend

        # texMode = TextureStage.MBlend
        if not texFileSphere in texList:
          texList[texFileSphere] = loadTexture(os.path.join(modelPath, texFileSphere))

        texSphere = texList[texFileSphere]
        if texSphere and texSphere.hasRamImage():
          log(u'Loaded Texture : %s' % texFileSphere, force=True)
          # texSphere.setWrapU(Texture.WM_clamp)
          # texSphere.setWrapV(Texture.WM_clamp)

          ts_sphere = TextureStage('%s_%03d_sphere' % (matName, matIndex))
          ts_sphere.setMode(texMode)
          ts_sphere.setSort(matIndex)
          ts_sphere.setPriority(matIndex)

          nodePath.setTexGen(ts_sphere, TexGenAttrib.MEyeSphereMap, 2)
          nodePath.setTexture(ts_sphere, texSphere, 1)
          nodePath.setTexScale(ts_sphere, 1, -1, -1)

          if not texFileMain:
            if isAlpha(texSphere):
              nodePath.setTransparency(TransparencyAttrib.MDual, matIndex)


    if mat.toon_index>=0 and textures[mat.toon_index] and textures[mat.toon_index].hasRamImage():
      texMode = TextureStage.MModulateGlow
      # texMode = TextureStage.MModulateGloss
      # texMode = TextureStage.MBlend
      texToon = textures[mat.toon_index]
      # texToon.setMagfilter(Texture.FTNearestMipmapNearest)
      # texToon.setMinfilter(Texture.FTNearestMipmapNearest)
      # texToon.setAnisotropicDegree(30)
      # texToon.setWrapU(Texture.WM_clamp)

      ts_toon = TextureStage('%s_%03d_toon' % (matName, matIndex))
      # ts_toon.setColor(VBase4(1,1,1,.67))
      ts_toon.setMode(texMode)
      ts_toon.setSort(matIndex)
      ts_toon.setPriority(matIndex)

      nodePath.setTexGen(ts_toon, TexGenAttrib.MEyeSphereMap, 2)
      nodePath.setTexture(ts_toon, texToon, 1)
      nodePath.setTexScale(ts_toon, 1, -1, -1)


    nodePath.setAntialias(AntialiasAttrib.MAuto)
    if nodePath.getTransparency() == TransparencyAttrib.MNone:
      nodePath.setTwoSided(True)

    vIndex += mat.vertex_count
    modelBody.addChild(node)
    matIndex += 1
    log(u'Loaded Node : %s' % matName, force=True)

  modelPath = NodePath(model)
  # modelPath.setShaderAuto()
  return(modelPath)
  pass

def loadPmdBone(pmd_model):
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
  for bone in pmd_model.bones:
    boneName = bone.name.decode('shift_jis', errors='replace')
    log(u'Loading Bone : %s' % boneName, force=True)

    #
    # load vertices(vertex list)
    #
    vdata = GeomVertexData(boneName+'_vdata', format, Geom.UHDynamic)
    vdata.setNumRows(3)

    vertex = GeomVertexWriter(vdata, 'vertex')
    color = GeomVertexWriter(vdata, 'color')
    vindex = GeomVertexWriter(vdata, 'vindex')
    tindex = GeomVertexWriter(vdata, 'tindex')
    pindex = GeomVertexWriter(vdata, 'pindex')

    node = GeomNode(boneName)

    tu = LVector3f(bone.tail.x, bone.tail.y, bone.tail.z)
    log(tu.cross(LVector3f(bone.pos.x, bone.pos.y, bone.pos.z)))

    if bone.tail_index >= 0:
      t = V2V(pmd_model.bones[bone.tail_index].pos)
    else:
      t = V2V(bone.pos+bone.tail)
    vertex.addData3f(t)
    color.addData4f(.95, .95, 0, 1) # Yellow
    vindex.addData1i(boneIndex)
    tindex.addData1i(bone.tail_index)
    pindex.addData1i(bone.parent_index)

    v = V2V(bone.pos)
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
    node.setPythonTag('position', V2V(bone.pos))
    node.setPythonTag('parent_index', bone.parent_index)
    node.setPythonTag('tail_index', bone.tail_index)
    node.setPythonTag('tail_position', V2V(bone.tail))
    # if bone.ik:
    #   iklink = map(lambda ik: {
    #     'bone_index':ik.bone_index,
    #     'limit_angle':ik.limit_angle,
    #     'limit_max':LVector3f(V2V(ik.limit_max)),
    #     'limit_min':LVector3f(V2V(ik.limit_min))
    #     }, bone.ik.link)

    #   node.setPythonTag('ik.limit_radian', bone.ik.limit_radian)
    #   node.setPythonTag('ik.loop', bone.ik.loop)
    #   node.setPythonTag('ik.target_index', bone.ik.target_index)
    #   node.setPythonTag('ik.link', bone.ik.link)
    # else:
    #   node.setPythonTag('ik', None)

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
    bo.setName(boneName)
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

def loadPmdMorph(pmd_model):
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
  morphBase = None
  for morph in pmd_model.morphs:
    morphName = morph.name.decode('shift_jis', errors='replace')
    log(u'Loading Morph : %s' % morphName, force=True)

    if morphIndex==0 and morphName == 'base':
      morphBase = morph
      morphIndex += 1
      continue

    #
    # load vertices(vertex list)
    #
    vdata = GeomVertexData(morphName+'_vdata', format, Geom.UHDynamic)
    # vdata.setNumRows(6)

    vertex = GeomVertexWriter(vdata, 'vertex')
    vindex = GeomVertexWriter(vdata, 'vindex')
    # vmorph = GeomVertexWriter(vdata, 'v.morph')
    vmorph = GeomVertexWriter(vdata, 'vmorph')
    transform_index = GeomVertexWriter(vdata, 'transform_index')
    transform_weight = GeomVertexWriter(vdata, 'transform_weight')
    column_morph_slider = GeomVertexWriter(vdata, 'emotion.morph.strange')

    node = GeomNode(morphName)

    morphData = None
    morphID = encode(morphName)
    morphEggText = []
    morphEggText.append('<CoordinateSystem> { Z-up }')
    morphEggText.append('<Group> %s_ACTOR {' % morphID)
    morphEggText.append('  <DART> { 1 }')
    morphEggText.append('  <Group> %s {' % morphID)
    morphEggText.append('    <VertexPool> %s {' % morphID)

    prim = GeomPoints(Geom.UHDynamic)
    vdata.setNumRows(len(morph.pos_list))
    for idx in xrange(len(morph.pos_list)):
      i = morphBase.indices[morph.indices[idx]]
      v = V2V(pmd_model.vertices[i].pos)
      o = V2V(morph.pos_list[idx])

      vertex.addData3f(v)
      vindex.addData1i(i)
      vmorph.addData3f(o)
      transform_index.addData1i(i)
      transform_weight.addData3f(o)
      column_morph_slider.addData1f(1.0)
      prim.addVertex(idx)

      morphEggText.append('      <Vertex> %d {' % idx)
      morphEggText.append('        %.11f %.11f %.11f' % (v.x, v.y, v.z))
      morphEggText.append('        <Dxyz> Wedge { %.6f %.6f %.6f }' % (o.x, o.y, o.z))
      morphEggText.append('      }')

    morphEggText.append('    }')
    morphEggText.append('  }')
    morphEggText.append('}')

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node.addGeom(geom)

    egg = EggData()
    egg.read(StringStream('\n'.join(morphEggText)))
    action = loadEggData(egg).getChild(0)
    node.addChild(action)

    node.setPythonTag('english_name', morph.english_name)
    node.setPythonTag('morph_type', 1)
    node.setPythonTag('morph_data', morphData)
    node.setPythonTag('morph_index', morphIndex)
    node.setPythonTag('pickableObjTag', 1)
    morphNode.addChild(node)

    morphIndex += 1

  np = NodePath(morphNode)
  np.hide()
  return(np)
  pass

def loadPmdSlot(pmd_model):
  #
  # Load Display Slot data
  #
  slotNode = PandaNode('Slots')
  slotIndex = 0
  for slot in pmd_model.display_slots:
    slotName = slot.name.decode('shift_jis', errors='replace')
    log(u'Loading Slot : %s' % slotName, force=True)
    node = PandaNode(slotName)
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

def loadPmdRigid(pmd_model):
  #
  # Load Rigid data
  #
  rigidNode = PandaNode('Rigid')
  rigidIndex = 0
  for rigid in pmd_model.rigidbodies:
    rigidName = rigid.name.decode('shift_jis', errors='replace')
    log(u'Loading RigidBodies : %s' % rigidName, force=True)
    node = PandaNode(rigidName)
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

def loadPmdJoint(pmd_model):
  #
  # Load Joints data
  #
  jointNode = PandaNode('Joints')
  jointIndex = 0
  for joint in pmd_model.joints:
    jointName = joint.name.decode('shift_jis', errors='replace')
    log(u'Loading RigidBodies : %s' % jointName, force=True)
    node = PandaNode(jointName)
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

def displayPmdModelInfo(model):
  # print(dir(model))
  info = pmdInfo(model)
  fn = os.path.splitext(os.path.basename(model.path))
  log(os.path.join(CWD, fn[0]+'_info'+'.txt'))
  with codecs.open(os.path.join(CWD, fn[0]+'_info'+'.txt'), 'w', encoding='utf8') as f:
    f.writelines(os.linesep.join(info))
  pass

def testPMD(pmd):
  pmdModel = pmdLoad(pmd)
  if pmdModel:
    print(pmdModel.path)
    displayPmdModelInfo(pmdModel)

    from direct.showbase.ShowBase import ShowBase
    base = ShowBase()

    p3dnode = pmd2p3d(pmdModel)
    p3dnode.reparentTo(base.render)

    base.run()
    pass
  pass

def loadPmdModel(modelfile):
  p3dnode = None
  try:
    mmdFile = os.path.relpath(modelfile)
  except:
    mmdFile = modelfile
    pass

  if os.path.altsep:
    mmdFile = mmdFile.replace('\\', os.path.altsep)
  ext = os.path.splitext(mmdFile)[1].lower()
  if ext in ['.pmd']:
    mmdModel = pmdLoad(mmdFile)
    if mmdModel:
      p3dnode = loadPmdBody(mmdModel)
      morphs = loadPmdMorph(mmdModel)
      if morphs:
        morphs.reparentTo(p3dnode)
      bones = loadPmdBone(mmdModel)
      if bones:
        bones.reparentTo(p3dnode)
      # slots = loadPmdSlot(mmdModel)
      # if slots:
      #   slots.reparentTo(p3dnode)
  elif ext in ['.pmx']:
    mmdModel = pmxLoad(mmdFile)
    if mmdModel:
      p3dnode = pmx2p3d(mmdModel)
      morphs = loadPmxMorph(mmdModel)
      morphs.reparentTo(p3dnode)
  elif ext in ['', '.egg', '.pz', '.bam']:
    return(p3dnode)
  return(p3dnode)

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


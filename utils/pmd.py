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

from common import *

from pymeshio import pmd
from pymeshio.pmd import reader as pmdReader

from pandac.PandaModules import *

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
    lines.append(u'name(jpn)    : %s' % model.name.decode('shift_jis'))
    lines.append(u'name(eng)    : %s' % model.english_name.decode('shift_jis').strip())
    lines.append(u'comment(jpn) : \n{0}\n{1}\n{0}'.format('-'*80, model.comment.decode('shift_jis')))
    lines.append(u'comment(eng) : \n{0}\n{1}\n{0}'.format('-'*80, model.english_comment.decode('shift_jis')))
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
      lines.append(u'  name(jpn)    : %s' % bone.name.decode('shift_jis'))
      lines.append(u'  name(eng)    : %s' % bone.english_name.decode('shift_jis'))
      lines.append(u'  index        : %4d' % bone.index)
      lines.append(u'  type         : %4d' % bone.type)
      lines.append(u'  pos          : %s' % str(bone.pos.to_tuple()))

      lines.append(u'  parent       : %4d, %s' % (bone.parent_index, (bone.parent.name.decode('shift_jis') if bone.parent else u'NULL')))
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
      lines.append(u'  name(jpn)    : %s' % morph.name.decode('shift_jis'))
      lines.append(u'  name(eng)    : %s' % morph.english_name.decode('shift_jis'))
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
      lines.append(u'  name(jpn)    : %s' % slot.name.decode('shift_jis'))
      lines.append(u'  name(eng)    : %s' % slot.english_name.decode('shift_jis'))
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
      lines.append(u'  name(jpn)          : %s' % rigidbody.name.decode('shift_jis'))
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
      lines.append(u'  name(jpn)         : %s' % joint.name.decode('shift_jis'))
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
      lines.append(u'  name(jpn)    : %s' % bone.name.decode('shift_jis'))
      lines.append(u'  name(eng)    : %s' % bone.english_name.decode('shift_jis'))
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

def pmd2p3d(pmd_model, alpha=True):
  modelPath = os.path.normpath(os.path.dirname(pmd_model.path))
  modelPath = os.path.normcase(modelPath)
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
    material.setAmbient(VBase4(mat.ambient_color.r, mat.ambient_color.g, mat.ambient_color.b, mat.alpha)) #Make this material blue
    material.setDiffuse(VBase4(mat.diffuse_color.r, mat.diffuse_color.g, mat.diffuse_color.b, mat.alpha))
    material.setSpecular(VBase4(mat.specular_color.r, mat.specular_color.g, mat.specular_color.b, mat.alpha))
    material.setShininess(mat.specular_factor)
    material.setLocal(False)
    material.setTwoside(False)
    materials.addMaterial(material)
    matIndex += 1
    log(u'Loaded Material : %s' % matName, force=True)

  #
  # load vertices(vertex list)
  #
  formatArray = GeomVertexArrayFormat()
  formatArray.addColumn(InternalName.make(str("drawFlag")), 1, Geom.NTUint8, Geom.COther)

  format = GeomVertexFormat(GeomVertexFormat.getV3n3cpt2())
  format.addArray(formatArray)
  GeomVertexFormat.registerFormat(format)

  vdata = GeomVertexData(pmd_model.name.decode('shift_jis'), format, Geom.UHStatic)

  vdata.setNumRows(4)
  vertex = GeomVertexWriter(vdata, 'vertex')
  normal = GeomVertexWriter(vdata, 'normal')
  color = GeomVertexWriter(vdata, 'color')
  texcoord = GeomVertexWriter(vdata, 'texcoord')

  for v in pmd_model.vertices:
    vertex.addData3f(v.pos.x, v.pos.z, v.pos.y)
    normal.addData3f(v.normal.x, v.normal.z, v.normal.y)
    color.addData4f(.95, .95, .95, 1)
    texcoord.addData2f(v.uv.x, v.uv.y)

  #
  # load polygons face
  #
  vIndex = 0
  modelName = pmd_model.name.decode('shift_jis')
  model = ModelNode(modelName)
  model.setPythonTag('path', pmd_model.path)
  model.setPythonTag('version', str(pmd_model.version))
  model.setPythonTag('name', modelName)
  model.setPythonTag('english_name', pmd_model.english_name)
  model.setPythonTag('comment', pmd_model.comment)
  model.setPythonTag('english_comment', pmd_model.english_comment)

  matIndex = 0
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
    nodePath.setMaterial(materials.findMaterial(matName), 1) #Apply the material to this nodePath

    #
    # set polygon face textures
    #
    if mat.texture_file and len(mat.texture_file) >= 0:
      texName = mat.texture_file.decode('shift_jis')
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

      texture = None
      if texFileMain:
        texture = loadTexture(os.path.join(modelPath, texFileMain))
      if texture:
        # texture.setWrapU(Texture.WM_clamp)
        nodePath.setTexture(texture, matIndex)
        nodePath.setTexScale(TextureStage.getDefault(), 1, -1, -1)

      if texFileSphere:
        texMode = TextureStage.MModulateGloss
        ext = os.path.splitext(texFileSphere)[1]
        if ext.lower() in ['.spa']:
          texMode = TextureStage.MAdd
        elif ext.lower() in ['.sph']:
          texMode = TextureStage.MModulateGlow

        texSphere = loadTexture(os.path.join(modelPath, texFileSphere))
        if texSphere:
          texSphere.setWrapU(Texture.WM_clamp)
          # tex.setWrapV(Texture.WM_clamp)

          ts_sphere = TextureStage(matName+'_sphere')
          ts_sphere.setMode(texMode)
          ts_sphere.setSort(2)
          ts_sphere.setPriority(0)
          nodePath.setTexGen(ts_sphere, TexGenAttrib.MEyeSphereMap, 2)
          nodePath.setTexture(ts_sphere, texSphere, 1)
          nodePath.setTexScale(ts_sphere, 1, -1, -1)

    if mat.toon_index>=0 and textures[mat.toon_index]:
      texMode = TextureStage.MModulateGlow
      tex = textures[mat.toon_index]
      tex.setMagfilter(Texture.FTNearestMipmapNearest)
      tex.setMinfilter(Texture.FTNearestMipmapNearest)
      tex.setAnisotropicDegree(30)
      tex.setWrapU(Texture.WM_clamp)

      ts_toon = TextureStage(matName+'_toon')
      ts_toon.setMode(texMode)
      nodePath.setTexGen(ts_toon, TexGenAttrib.MEyeSphereMap)
      nodePath.setTexture(ts_toon, tex, 1)
      nodePath.setTexScale(ts_toon, 1, -1, -1)


    nodePath.setColorOff()
    # nodePath.setShaderAuto(2)
    # nodePath.setShaderAuto(BitMask32.bit(Shader.BitAutoShaderNormal) , 2)
    nodePath.setAntialias(AntialiasAttrib.MAuto)

    if alpha:
      #
      # Here is not really to solve the tex alpha-transparency bug, only a other bug :(
      #
      # nodePath.setTransparency(True, 0)
      # nodePath.setTransparency(True, 1)
      # nodePath.setTransparency(TransparencyAttrib.MAlpha, 1)
      nodePath.setTransparency(TransparencyAttrib.MDual, 1)
      pass

    vIndex += mat.vertex_count
    model.addChild(node)
    matIndex += 1
    log(u'Loaded Node : %s' % matName, force=True)

  return(NodePath(model))
  pass

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

    import direct.directbase.DirectStart
    p3dnode = pmd2p3d(pmdModel)
    p3dnode.reparentTo(render)

    run()
    pass
  pass

def loadPmdModel(modelfile):
  p3dnode = None
  mmdFile = os.path.relpath(modelfile)
  if os.path.altsep:
    mmdFile = mmdFile.replace('\\', os.path.altsep)
  ext = os.path.splitext(mmdFile)[1].lower()
  if ext in ['.pmd']:
    mmdModel = pmdLoad(mmdFile)
    if mmdModel:
      p3dnode = pmd2p3d(mmdModel)
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


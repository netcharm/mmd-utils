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

import time
import random

import StringIO

import locale

rcdomain = 'wxViewMMD'
localedir = os.path.realpath('i18n')
os.environ['LANG'] = locale.getdefaultlocale()[0]

import gettext
_ = gettext.gettext

import wx
import wx.aui
import wx.lib.platebtn as platebtn

# if wx.GetApp().GetComCtl32Version() >= 600 and wx.DisplayDepth() >= 32:
#   # Use the 32-bit images
#   wx.SystemOptions.SetOption("msw.remap", 2)

WIN_SIZE = (800, 800)

from pandac.PandaModules import *
# need to be before the Direct Start Import
loadPrcFileData('startup', 'window-type none')
loadPrcFileData("", "window-title MMD PMX/PMX Model Viewer")
loadPrcFileData("", "icon-filename mmdviewer.png")
loadPrcFileData("", "win-size %d %d" % WIN_SIZE)
loadPrcFileData("", "window-type none")
loadPrcFileData('', 'text-encoding utf8')
loadPrcFileData('', 'textures-power-2 none')
loadPrcFileData('', 'geom-cache-size 10')

# loadPrcFileData('', 'notify-level warning')
# loadPrcFileData('', 'default-directnotify-level warning')
# loadPrcFileData('', 'want-pstats 1')

from panda3d.core import ConfigVariableString
from panda3d.core import Shader
from panda3d.core import Filename
from panda3d.core import Material
from panda3d.core import VBase4

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBase import WindowControls
from direct.showbase.DirectObject import DirectObject
# from direct.directtools.DirectGrid import DirectGrid
# from direct.directtools.DirectGlobals import *

from direct.gui.DirectGui import *

from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from direct.interval.IntervalGlobal import *
from direct.task import Task

from direct.wxwidgets.ViewPort import *

from utils.DrawPlane import *
from utils.pmx import *

from main_ui import *

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])

SHOW_LIGHT_POS = True
SHOW_LIGHT_POS = False

SHOW_SHADOW = True
SHOW_SHADOW = False

SHOW_AXIS = True
# SHOW_AXIS = False

lastModel = None

ID_GRIDPLANE  = 20000
ID_EXPRESSION = 30000


class TestFrame(wx.Frame):
  def __init__(self, *args, **kwargs):
    wx.Frame.__init__(self, *args, **kwargs)

    self.auiManager = wx.aui.AuiManager(self)

    # self.panda = Viewport.makeFront(self)
    # self.panda = Viewport.makePerspective(self)
    self.panda = Viewport.make(self, vpType=CREATENEW)

    pandaInfo = wx.aui.AuiPaneInfo().Name("panda3d")
    pandaInfo.Center().CloseButton(False).MaximizeButton(True).CaptionVisible(False)
    self.auiManager.AddPane(self.panda, pandaInfo)

    self.auiManager.Update()

  def onQuit(self, evt):
    self.auiManager.UnInit()
    self.Close()

  pass


class Frame(MainForm):
  def __init__(self, *args, **kwargs):
    MainForm.__init__(self, *args, **kwargs)

    self.auiManager = wx.aui.AuiManager(self)

    # self.panda = Viewport.makeFront(self)
    # self.panda = Viewport.makePerspective(self)
    self.panda = Viewport('panda3dviewport', self)

    pandaInfo = wx.aui.AuiPaneInfo().Name("panda3d")
    pandaInfo.Center().CloseButton(False).MaximizeButton(True).CaptionVisible(False)
    self.auiManager.AddPane(self.panda, pandaInfo)

    self.auiManager.Update()

  def onQuit(self, evt):
    self.auiManager.UnInit()
    self.Close()

  pass


class Stage(object):
  lights = None
  @staticmethod
  def setAxis(render, update=False):
    def CreateAxis(axisStage):
      grid = ThreeAxisGrid(gridstep=20, subdiv=20, xy=True, yz=False, xz=False, z=False)
      gridnodepath = grid.create()
      grid.showPlane(XY=True)
      grid.showAxis(Z=False)
      gridnodepath.writeBamFile(axisStage)
      return(gridnodepath)

    axisStage = u'./stages/default_axis.bam'
    if not update:
      try:
        gridnodepath = loader.loadModel(axisStage)
        gridnodepath = gridnodepath.getChild(0)
      except:
        gridnodepath = CreateAxis()
    else:
      gridnodepath = CreateAxis()

    gridnodepath.reparentTo(render)
    pass

  @staticmethod
  def setStudioLight(render):
    lightsStage = u'./stages/default_lights.bam'
    try:
      lights = loader.loadModel(lightsStage)
      lights = lights.getChild(0)
    except:
      lights = NodePath(PandaNode('StageLights'))

      alight = AmbientLight('alight')
      alight.setColor(VBase4(0.67, 0.67, 0.67, .8))
      # alight.setColor(VBase4(0.33, 0.33, 0.33, 0.67))
      alnp = render.attachNewNode(alight)
      alnp.reparentTo(lights)

      dlight_top = PointLight('top dlight')
      dlnp_top = render.attachNewNode(dlight_top)
      dlnp_top.setX(-5)
      dlnp_top.setZ(45)
      dlnp_top.setY(0)
      # dlnp_top.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
      dlnp_top.node().setAttenuation( Vec3( 0.005, 0.005, 0.005 ) )
      dlnp_top.setHpr(0, -180, 0)
      if SHOW_LIGHT_POS:
        dlnp_top.node().showFrustum()
      dlnp_top.reparentTo(lights)

      dlight_back = PointLight('back dlight')
      dlnp_back = render.attachNewNode(dlight_back)
      dlnp_back.setX(0)
      dlnp_back.setZ(25)
      dlnp_back.setY(+55)
      # dlnp_back.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
      dlnp_back.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
      dlnp_back.setHpr(0, -168, 0)
      if SHOW_LIGHT_POS:
        dlnp_back.node().showFrustum()
      dlnp_back.reparentTo(lights)

      dlight_front = PointLight('front dlight')
      dlnp_front = render.attachNewNode(dlight_front)
      dlnp_front.setX(0)
      dlnp_front.setY(-36)
      dlnp_front.setZ(15)
      dlens = dlnp_front.node().getLens()
      dlens.setFilmSize(41, 21)
      # dlens.setNearFar(50, 75)
      dlnp_front.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
      # dlnp_front.node().setAttenuation( Vec3( 0.005, 0.005, 0.005 ) )
      dlnp_front.setHpr(0, -10, 0)
      if SHOW_LIGHT_POS:
        dlnp_front.node().showFrustum()
      dlnp_front.reparentTo(lights)

      dlight_left = Spotlight('left dlight')
      dlnp_left = render.attachNewNode(dlight_left)
      dlnp_left.setX(-46)
      dlnp_left.setY(+36)
      dlnp_left.setZ(27)
      dlens = dlnp_left.node().getLens()
      dlens.setFilmSize(41, 21)
      # dlens.setNearFar(50, 75)
      dlnp_left.node().setAttenuation( Vec3( 0.001, 0.002, 0.001 ) )
      # dlnp_left.node().setAttenuation( Vec3( 0.011, 0.011, 0.011 ) )
      dlnp_left.setHpr(-130, -15, 0)
      if SHOW_LIGHT_POS:
        dlnp_left.node().showFrustum()
      dlnp_left.reparentTo(lights)

      dlight_right = Spotlight('right dlight')
      dlnp_right = render.attachNewNode(dlight_right)
      dlnp_right.setX(+50)
      dlnp_right.setY(+40)
      dlnp_right.setZ(30)
      dlens = dlnp_right.node().getLens()
      dlens.setFilmSize(41, 21)
      # dlens.setNearFar(50, 75)
      dlnp_right.node().setAttenuation( Vec3( 0.001, 0.002, 0.001 ) )
      # dlnp_right.node().setAttenuation( Vec3( 0.011, 0.011, 0.011 ) )
      dlnp_right.setHpr(130, -15, 0)
      if SHOW_LIGHT_POS:
        dlnp_right.node().showFrustum()
      dlnp_right.reparentTo(lights)

      if SHOW_SHADOW:
        lights.setShaderAuto()
        lights.setShadowCaster(True, 512, 512)

      lights.writeBamFile(lightsStage)

    # lights.reparentTo(render)
    Stage.lights = lights
    return(lights)
    pass

  @staticmethod
  def lightAtNode(node, lights=None):
    if not lights:
        return
    if isinstance(node, NodePathCollection):
      for np in node:
        for light in lights.getChildren():
          np.setLight(light)
    elif isinstance(node, NodePath):
      for light in lights.getChildren():
        try:
          node.setLight(light)
        except:
          continue
    pass

  @staticmethod
  def setCamera(x=0, y=0, z=0, h=0, p=0, r=0, oobe=False):
    base.camLens.setNearFar(0.1, 550.0)
    base.camLens.setFov(45.0)
    base.camLens.setFocalLength(50)

    # base.trackball.node().setPos(0, 20, -20)
    base.trackball.node().setHpr(h, p, r)
    base.trackball.node().setPos(x, y, -z)

    # base.useDrive()
    if oobe:
      # base.oobe()
      base.oobeCull()
    pass

  @staticmethod
  def resetCamera(model=None):
    WIN_SIZE = (500, 500)
    if model:
      lens = base.camLens

      fov_old = render.getPythonTag('lensFov')
      fov_new = lens.getFov()
      aspect = lens.getAspectRatio()
      scale_x = fov_new.getX() / fov_old.getX()
      scale_y = fov_new.getY() / fov_old.getY()
      # print('Scale : x=%.4f, y=%.4f' % (scale_x, scale_y))

      min_point = LPoint3f()
      max_point = LPoint3f()
      model.calcTightBounds(min_point, max_point)
      node_size = LPoint3f(max_point.x-min_point.x, max_point.y-min_point.y, max_point.z-min_point.z)
      # print(node_size)

      camPosX = 0
      camPosY = 1.6*node_size.z/scale_y
      camPosZ = 0.5*node_size.z #/scale_y

    else:
      camPosX = 0
      camPosY = 100
      camPosZ = 20
    Stage.setCamera(x=camPosX, y=camPosY, z=camPosZ, p=10, oobe=False)
    pass

  pass


class Utils(object):
  @staticmethod
  def processVertexData(vdata_src, vdata_dst, morphOn=True, strength=1.0):
    vertex_src = GeomVertexWriter(vdata_src, 'vertex')
    vertex_dst = GeomVertexReader(vdata_dst, 'vertex')
    vindex_dst = GeomVertexReader(vdata_dst, 'vindex')
    # vmorph_dst = GeomVertexReader(vdata_dst, 'v.morph')
    vmorph_dst = GeomVertexReader(vdata_dst, 'vmorph')

    # vertex_src.setColumn('vertex')
    while not vertex_dst.isAtEnd():
      i_dst = vindex_dst.getData1i()
      v_dst = vertex_dst.getData3f()
      m_dst = vmorph_dst.getData3f()
      vertex_src.setRow(i_dst)
      if morphOn:
        vertex_src.setData3f(v_dst.getX()+m_dst.getX()*strength, v_dst.getY()+m_dst.getY()*strength, v_dst.getZ()+m_dst.getZ()*strength)
      else:
        vertex_src.setData3f(v_dst.getX(), v_dst.getY(), v_dst.getZ())
      # print(vertex_src.getWriteRow())
    del vertex_src, vertex_dst, vindex_dst, vmorph_dst

  @staticmethod
  def processGeomNode(geomNode, morphNode, morphOn=True, strength=1.0):
    geom = geomNode.modifyGeom(0)
    morphgeom = morphNode.getGeom(0)
    vdata_src = geom.modifyVertexData()
    vdata_dst = morphgeom.getVertexData()
    result = Utils.processVertexData(vdata_src, vdata_dst, morphOn, strength)
    del vdata_src, vdata_dst, geom, morphgeom
    return(result)

  @staticmethod
  def morphVertex(nodepath, morphnodepath, morphOn=True, strength=1.0):
    morphNode = morphnodepath.node()
    geomNodeCollection = nodepath.findAllMatches('**/Body/+GeomNode')
    idx = 0
    for nodePath in geomNodeCollection:
      log(u'%s' % nodePath.getName().replace(u'\u30fb', u'.'))
      geomNode = nodePath.node()
      Utils.processGeomNode(geomNode, morphNode, morphOn, strength)
      # idx += 1
      del geomNode
    del morphNode, geomNodeCollection
    pass

  @staticmethod
  def morphMaterial(nodepath, morphData, morphOn=True, strength=1.0):
    idx = 0
    print(u'-> Morph Material Count : %d' % len(morphData))
    for data in morphData:
      material_index        = data.getPythonTag('materialIndex')
      calc_mode             = data.getPythonTag('calcMode')
      edge_color            = data.getPythonTag('edge_color')
      edge_size             = data.getPythonTag('edge_size')
      texture_factor        = data.getPythonTag('texture_factor')
      sphere_texture_factor = data.getPythonTag('sphere_texture_factor')
      toon_texture_factor   = data.getPythonTag('toon_texture_factor')

      mat = data.getMaterial()
      print(u'--> Target Material Count : %d' % len(morphData))
      print(u'--> Target Material Index : %d' % material_index)

      nps = nodepath.findAllMatches('**/Body/*')
      for np in nps:
        log(u'---> %s, %d, %s' % (np.getName(), np.getPythonTag('material_index'), str(morphOn)), force=True)
        matIndex = np.getPythonTag('material_index')
        if material_index < 0:
          pass
        elif matIndex != material_index:
          continue

        tex_name = u'%s_morph_%04d' % (np.getName(), idx)
        ts_morph = TextureStage(tex_name)

        tsSphereName = u'%s_sphere' % np.getName()
        tsSphere = np.findTextureStage(tsSphereName)
        tsToonName = u'%s_toon' % np.getName()
        tsToon = np.findTextureStage(tsToonName)
        if morphOn:
          np.setMaterial(mat, 1)
          if   calc_mode == 0: # *
            np.setColorScale(texture_factor.r, texture_factor.g, texture_factor.b, texture_factor.a, matIndex)
          elif calc_mode == 1: # +
            np.setColorScale(texture_factor.r, texture_factor.g, texture_factor.b, texture_factor.a, matIndex)
        else:
          np.setColorScaleOff(matIndex)
          np.clearMaterial()
          np.setMaterial(np.getPythonTag('material'), 1)

        if tsSphere:
          if morphOn:
            np.setPythonTag('sphere_combine_mode', (
              tsSphere.getCombineRgbMode(),
              tsSphere.getCombineRgbSource0(),
              tsSphere.getCombineRgbOperand0(),
              tsSphere.getCombineRgbSource1(),
              tsSphere.getCombineRgbOperand1(),
              tsSphere.getCombineRgbSource2(),
              tsSphere.getCombineRgbOperand2(),
              tsSphere.getCombineAlphaMode(),
              tsSphere.getCombineAlphaSource0(),
              tsSphere.getCombineAlphaOperand0(),
              tsSphere.getCombineAlphaSource1(),
              tsSphere.getCombineAlphaOperand1(),
              tsSphere.getCombineAlphaSource2(),
              tsSphere.getCombineAlphaOperand2(),
              tsSphere.getMode()
              ))
            if calc_mode == 0: # *
              color = VBase4(sphere_texture_factor.r*strength/10, sphere_texture_factor.g*strength/10, sphere_texture_factor.b*strength/10, sphere_texture_factor.a*strength/10)
              tsSphere.setColor(color)
              tsSphere.setCombineRgb(TextureStage.CMModulate, TextureStage.CSPrevious, TextureStage.COSrcColor, TextureStage.CSTexture, TextureStage.COSrcColor)
              tsSphere.setCombineAlpha(TextureStage.CMModulate, TextureStage.CSPrevious, TextureStage.COSrcAlpha, TextureStage.CSTexture, TextureStage.COSrcAlpha)
            elif calc_mode == 1: # +
              color = VBase4(-sphere_texture_factor.r*strength, -sphere_texture_factor.g*strength, -sphere_texture_factor.b*strength, -sphere_texture_factor.a*strength)
              tsSphere.setColor(color)
              tsSphere.setCombineRgb(TextureStage.CMSubtract, TextureStage.CSTexture, TextureStage.COSrcColor, TextureStage.CSConstant, TextureStage.COSrcColor)
              tsSphere.setCombineAlpha(TextureStage.CMSubtract, TextureStage.CSTexture, TextureStage.COSrcAlpha, TextureStage.CSConstant, TextureStage.COSrcAlpha)
          else:
            cMode = np.getPythonTag('sphere_combine_mode')
            # tsSphere.setCombineRgb(cMode[0], cMode[1], cMode[2], cMode[3], cMode[4], cMode[5], cMode[6])
            # tsSphere.setCombineAlpha(cMode[7], cMode[8], cMode[9], cMode[10], cMode[11], cMode[12], cMode[13])
            tsSphere.setMode(cMode[14])
          pass
        pass

        if tsToon:
          if morphOn:
            np.setPythonTag('toon_combine_mode', (
              tsToon.getCombineRgbMode(),
              tsToon.getCombineRgbSource0(),
              tsToon.getCombineRgbOperand0(),
              tsToon.getCombineRgbSource1(),
              tsToon.getCombineRgbOperand1(),
              tsToon.getCombineRgbSource2(),
              tsToon.getCombineRgbOperand2(),
              tsToon.getCombineAlphaMode(),
              tsToon.getCombineAlphaSource0(),
              tsToon.getCombineAlphaOperand0(),
              tsToon.getCombineAlphaSource1(),
              tsToon.getCombineAlphaOperand1(),
              tsToon.getCombineAlphaSource2(),
              tsToon.getCombineAlphaOperand2(),
              tsToon.getMode()
              ))
            if calc_mode == 0: # *
              color = VBase4(toon_texture_factor.r*strength/5, toon_texture_factor.g*strength/5, toon_texture_factor.b*strength/5, toon_texture_factor.a*strength/5)
              tsToon.setColor(color)
              tsToon.setCombineRgb(TextureStage.CMModulate, TextureStage.CSTexture, TextureStage.COSrcColor, TextureStage.CSPrevious, TextureStage.COSrcColor)
              tsToon.setCombineAlpha(TextureStage.CMModulate, TextureStage.CSTexture, TextureStage.COSrcAlpha, TextureStage.CSPrevious, TextureStage.COSrcAlpha)
            elif calc_mode == 1: # +
              color = VBase4(toon_texture_factor.r*strength/5, toon_texture_factor.g*strength/5, toon_texture_factor.b*strength/5, toon_texture_factor.a*strength/5)
              tsToon.setColor(color)
              print(color)
              tsToon.setCombineRgb(TextureStage.CMSubtract, TextureStage.CSPrevious, TextureStage.COSrcColor, TextureStage.CSConstant, TextureStage.COSrcColor)
              tsToon.setCombineAlpha(TextureStage.CMSubtract, TextureStage.CSPrevious, TextureStage.COSrcAlpha, TextureStage.CSConstant, TextureStage.COSrcAlpha)
          else:
            cMode = np.getPythonTag('toon_combine_mode')
            print(cMode)
            # tsToon.setCombineRgb(cMode[0], cMode[1], cMode[2], cMode[3], cMode[4], cMode[5], cMode[6])
            # tsToon.setCombineAlpha(cMode[7], cMode[8], cMode[9], cMode[10], cMode[11], cMode[12], cMode[13])
            tsToon.setMode(cMode[14])
          pass
        pass

      idx += 1
    pass

  @staticmethod
  def setExpression(model, expression, morphOn=True, strength=1.0, default=True):
    if strength < 0: strength = 0.0;
    if strength > 1: strength = 1.0;
    strength = 0.95
    morph = model.find('**/Morphs*')
    if len(expression)==0 or expression.lower()=='default':
      for item in morph.getChildren():
        if item.getPythonTag('show'):
          Utils.morphVertex(model, item, morphOn=False, strength=strength)
          item.setPythonTag('show', False)
    else:
      for item in morph.getChildren():
        if len(expression)==0 or expression.lower()=='default':
          Utils.morphVertex(model, item, morphOn=False, strength=strength)
          item.setPythonTag('show', False)
          continue
        if item.getName() == expression:
          log(u'===================\n%s\n===================' % expression, force=True)
          lastExpression = model.getPythonTag('lastExpression')

          morphType = item.getPythonTag('morph_type')
          morphPanel = item.getPythonTag('panel')
          print('Morph Type  : ', morphType)
          # print('Morph Panel : ', morphPanel)
          if morphType == 1:
            if lastExpression and default:
              Utils.morphVertex(model, lastExpression, morphOn=False, strength=strength)
              lastExpression.setPythonTag('show', False)

            state = False if item.getPythonTag('show') else True
            Utils.morphVertex(model, item, morphOn=state, strength=strength)
            item.setPythonTag('show', state)

            model.setPythonTag('lastExpression', item)
            # print(expression, morphOn)
          elif morphType == 8:
            state = False if item.getPythonTag('show') else True
            morphData = item.getPythonTag('morph_data')
            # Utils.morphMaterial(model, morphData, morphOn=state, strength=strength)
            # item.setPythonTag('show', state)
            item.setPythonTag('show', False)
          else:
            log('not vertex/material expression', force=True)
          break
        pass
      pass
    pass

  @staticmethod
  def getExpressionList(model):
    expressions = []
    if model:
      morph = model.find('**/Morphs*')
      if morph:
        for item in morph.getChildren():
          expression_name = item.getName()
          if item.getPythonTag('show'):
            expression_state = True
          else:
            expression_state = False
          expressions.append({'name':expression_name, 'state':expression_state})

    return(expressions)


class MyFileDropTarget(wx.FileDropTarget):
  def __init__(self, window):
    wx.FileDropTarget.__init__(self)
    self.window = window

  def OnDropFiles(self, x, y, filenames):
    info = "%d file(s) dropped at (%d,%d):\n" % (len(filenames), x, y)
    print(info)
    for file in filenames:
      mmdFile = file
      break

    p3dnode = loadMMDModel(mmdFile)
    p3dnode.reparentTo(render)
    Stage.lightAtNode(p3dnode, Stage.lights)
    Stage.resetCamera(model=p3dnode)
    render.setPythonTag('lastModel', p3dnode)

  pass


class MmdViewerApp(ShowBase):
  wp = None
  modelidx = 0

  def __init__(self):
    self.base = ShowBase.__init__(self, fStartDirect=False, windowType=None)
    self.startWx()
    self.wxApp.Bind(wx.EVT_CLOSE, self.quit)
    self.wxApp.Bind(wx.EVT_SIZE, self.resize)

    # self.frame = TestFrame(None)
    self.frame = Frame(None)
    outx, outy = self.frame.GetSize() - self.frame.GetClientSize()
    diffx, diffy = self.frame.GetClientSize() - wx.Size(500, 500)
    self.frame.SetSize(self.frame.GetSize() - wx.Size(diffx, diffy))

    self.wp = WindowProperties()
    self.wp.setOrigin(0,0)
    self.wp.setSize(self.frame.panda.GetSize()[0], self.frame.panda.GetSize()[1])
    self.wp.setParentWindow(self.frame.panda.GetHandle())
    base.openMainWindow(type='onscreen', props=self.wp)

    self.setupUI(self.frame)

    self.setupGL(render)

    # icon = wx.Icon('viewpmx.ico', wx.BITMAP_TYPE_ICO)
    icon = wx.Icon('mmdviewer.png', wx.BITMAP_TYPE_ANY)
    self.frame.SetIcon(icon)
    # self.frame.SetTopWindow(self.frame)
    self.frame.Show(True)
    pass

  def resize(self, event=None):
    if self.wp:
      w, h = self.frame.panda.GetSize()
      self.wp.setSize(w, h)
      base.win.requestProperties(self.wp)
      base.messenger.send(base.win.getWindowEvent(), [base.win])
      pass

  def quit(self, event=None):
    self.onDestroy(event)
    try:
      base
    except NameError:
      sys.exit()
    base.userExit()
    pass

  def loadModel(self, modelname=None):
    p3dnode = None
    if modelname == None:
      modelname = 'panda'

    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      node = lastModel.find('**/+ModelRoot')
      if node:
        loader.unloadModel(node)
      else:
        loader.unloadModel(lastModel)
      lastModel.removeNode()
      render.setPythonTag('lastModel', None)

    ext = os.path.splitext(modelname)[1].lower()
    if ext in ['.pmx', '.pmd']:
      p3dnode = loadMMDModel(modelname)
    else:
      p3dnode = loader.loadModel(Filename.fromOsSpecific(modelname))

    if p3dnode:
      p3dnode.reparentTo(render)
      Stage.lightAtNode(p3dnode, lights=Stage.lights)
      Stage.resetCamera(model=p3dnode)
      render.setPythonTag('lastModel', p3dnode)

      self.addExpressionMenu(Utils.getExpressionList(p3dnode))

    return(p3dnode)
    pass

  def addExpressionMenu(self, expressionList):
    if self.menuExpression:
      for item in self.menuExpression.GetMenuItems():
        # self.menuExpression.Destroy(item.GetId())
        item.Destroy()
      del self.menuExpression

      self.menuExpression = wx.Menu()
      idx = 0
      for item in expressionList:
        mItem = self.menuExpression.AppendCheckItem(ID_EXPRESSION+idx, item['name'], '')
        mItem.Check(item['state'])
        self.frame.Bind(wx.EVT_MENU, self.OnExpressionSeleced, id=mItem.GetId())
        idx += 1

      self.frame.toolbar.SetDropdownMenu(ID_EXPRESSION, self.menuExpression)
      self.frame.toolbar.Realize()
    pass

  def setupUI(self, win):
    self.dt = MyFileDropTarget(win)
    win.SetDropTarget(self.dt)

    self.menuPlane = wx.Menu()
    for idx in xrange(self.frame.menuView.GetMenuItemCount()):
      item = self.frame.menuView.FindItemByPosition(idx)
      text = item.GetText()
      help = item.GetHelp()
      if text=='':
        self.menuPlane.AppendSeparator()
      else:
        mItem = self.menuPlane.AppendCheckItem(ID_GRIDPLANE+idx, text, help)
        if item.IsCheckable():
          mItem.Check(item.IsChecked())
        win.Bind(wx.EVT_MENU, self.OnPlanePopupItemSelected, id=mItem.GetId())
        win.Bind(wx.EVT_MENU, self.OnPlanePopupItemSelected, id=item.GetId())

    self.btnPlane = self.frame.toolbar.AddLabelTool( ID_GRIDPLANE, _(u"Plane"), wx.Bitmap( u"icons/gridplane.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_DROPDOWN, _('Axis Plane Grid'), wx.EmptyString, None )
    self.frame.toolbar.SetDropdownMenu(ID_GRIDPLANE, self.menuPlane)

    self.frame.toolbar.AddSeparator()

    self.menuExpression = wx.Menu()
    self.btnExpression = self.frame.toolbar.AddLabelTool(ID_EXPRESSION, _(u"Expression"), wx.Bitmap( u"icons/expression.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_DROPDOWN, _('Expression List'), wx.EmptyString, None )

    self.frame.toolbar.Realize()

    win.Bind(wx.EVT_MENU_OPEN, self.OnMenuPopup)

    win.Bind(wx.EVT_TOOL, self.OnResetCamera, id=ID_CAMERARESET)
    win.Bind(wx.EVT_MENU, self.OnResetCamera, id=win.menuResetCamera.GetId())

    win.Bind(wx.EVT_TOOL, self.OnOpenFile, id=ID_OPEN)
    win.Bind(wx.EVT_MENU, self.OnOpenFile, id=win.menuOpen.GetId())
    win.Bind(wx.EVT_TOOL, self.OnSnapshot, id=ID_SNAPSHOT)
    win.Bind(wx.EVT_MENU, self.OnSnapshot, id=win.menuSnapshot.GetId())


    pass

  def setupGL(self, render):
    base.camLens.setNearFar(0.1, 550.0)
    base.camLens.setFov(45.0)
    base.camLens.setFocalLength(50)

    Stage.setAxis(render)

    self.lights = Stage.setStudioLight(render)

    Stage.resetCamera()

    render.setAntialias(AntialiasAttrib.MAuto)

    fov = base.camLens.getFov()
    render.setPythonTag('lensFov', LVecBase2f(fov.getX(), fov.getY()))

    pass

  def OnOpenFile(self, event):
    # p3dnode = self.loadModel('models/meiko/meiko.pmx')
    modellist = [u'./models/meiko/meiko.pmx', u'panda', u'./models/apimiku/Miku long hair.pmx']
    # p3dnode = self.loadModel(modellist[self.modelidx % 3])
    p3dnode = self.loadModel(modellist[2])
    self.modelidx += 1

    # p3dnode = self.loadModel('panda')

    # print(type(p3dnode))
    # print(p3dnode.ls())

    pass

  def OnResetCamera(self, event):
    model = render.getPythonTag('lastModel')
    Stage.resetCamera(model=model)
    print(model)

  def OnSnapshot(self, event):
    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      path = lastModel.node().getTag('path')
      if path:
        fn = os.path.splitext(os.path.basename(path))
        folder = os.path.dirname(path)
        snapfile = os.path.join(folder, u'snap_%s.png' % (fn[0]))
      else:
        snapfile = os.path.join(CWD, 'snap_%s.png' % lastModel.getName())
    else:
      snapfile = os.path.join(CWD, 'snap.png')
    snapfile = Filename.fromOsSpecific(snapfile)
    # print(Filename.makeTrueCase(snapfile))
    Filename.makeCanonical(snapfile)
    axis = render.find('**/threeaxisgrid*')
    axis.hide()
    base.graphicsEngine.renderFrame()
    source = base.camera.getChild(0).node().getDisplayRegion(0)
    result = base.screenshot(namePrefix=snapfile, defaultFilename=0, source=None, imageComment='')
    axis.show()
    base.graphicsEngine.renderFrame()
    pass

  def GetAxisById(self, id):
    axis = None
    if   id in [20000, -31991]:
      axis = render.find('**/AXISLINE/X*')
    elif id in [20001, -31990]:
      axis = render.find('**/AXISLINE/Y*')
    elif id in [20002, -31989]:
      axis = render.find('**/AXISLINE/Z*')
    elif id in [20004, -31988]:
      axis = render.find('**/PLANEGRID/XY*')
    elif id in [20005, -31987]:
      axis = render.find('**/PLANEGRID/YZ*')
    elif id in [20006, -31986]:
      axis = render.find('**/PLANEGRID/XZ*')
    elif id in [20008, -31985]:
      axis = render.findAllMatches('**/**/PLANEGRID/*/SUBDIV')
      # axis = render.find('**/**/PLANEGRID/*/SUBDIV')
    return(axis)

  def RefreshMenuState(self, menu):
    idlist_plane = [20000, 20001, 20002, 20003, 20004, 20005, 20006, 20007, 20008, -31991, -31990, -31989, -31988, -31987, -31986, -31985]
    for mId in idlist_plane:
      axis = self.GetAxisById(mId)
      if axis:
        for item in menu.GetMenuItems():
          if item.GetId() == mId and item.IsCheckable():
            if isinstance(axis, NodePathCollection):
              checked  = item.IsChecked()
              for ax in axis:
                checked = not ax.isHidden()
                break
              item.Check(checked)
            else:
              item.Check(not axis.isHidden())
            break

    idlist_expression = [30000, 31000]
    model = render.getPythonTag('lastModel')
    if model:
      expressionList = Utils.getExpressionList(model)
      for item in menu.GetMenuItems():
        text = item.GetText()
        for expression in expressionList:
          if text == expression['name']:
            item.Check(expression['state'])
            break
        pass
    pass

  def OnMenuPopup(self, event):
    menu = event.GetEventObject()
    self.RefreshMenuState(menu)

  def OnPlanePopupItemSelected(self, event):
    arg = event.GetId()
    axis = self.GetAxisById(arg)
    if axis:
      menu = event.GetEventObject()
      if isinstance(axis, NodePathCollection):
        if menu.IsChecked(arg):
          for ax in axis:
            ax.show()
        else:
          for ax in axis:
            ax.hide()
      else:
        if axis.isHidden():
          axis.show()
        else:
          axis.hide()

      self.RefreshMenuState(menu)
    else:
      pass
    pass


  def OnExpressionSeleced(self, event):
    menu = event.GetEventObject()
    for item in menu.GetMenuItems():
      print(item.GetText())
      print(item.GetId() , event.GetId())
      if item.GetId() == event.GetId():
        Utils.setExpression(render.getPythonTag('lastModel'), item.GetText(), default=False)
        break
    pass

  pass

if __name__ == '__main__':
  app = MmdViewerApp()
  app.run()

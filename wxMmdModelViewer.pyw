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
loadPrcFileData("", "icon-filename viewpmx.ico")
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

class STAGE(object):
  lights = None
  @staticmethod
  def setAxis(render):
    axisStage = u'./stages/default_axis.bam'
    try:
      gridnodepath = loader.loadModel(axisStage)
      gridnodepath = gridnodepath.getChild(0)
    except:
      grid = ThreeAxisGrid(xy=True, yz=False, xz=False, z=False)
      gridnodepath = grid.create()
      grid.showPlane(XY=True)
      grid.showAxis(Z=False)
      gridnodepath.writeBamFile(axisStage)
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
    STAGE.lights = lights
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
    if model:
      x = base.win.getXSize()
      y = base.win.getYSize()
      minsize = min(x, y)
      print(x, y)

      lens = base.camLens
      print(lens)
      aspect = lens.getAspectRatio()
      print(aspect)
      # base.camLens.setFov(LVecBase2f(x, y))

      min_point = LPoint3f()
      max_point = LPoint3f()
      model.calcTightBounds(min_point, max_point)
      node_size = LPoint3f(max_point.x-min_point.x, max_point.y-min_point.y, max_point.z-min_point.z)

      scale = 1.60

      camPosX = 0
      camPosY = 2.67*node_size.z
      camPosZ = 0.53*node_size.z
    else:
      camPosX = 0
      camPosY = 100
      camPosZ = 20
    STAGE.setCamera(x=camPosX, y=camPosY, z=camPosZ, p=10, oobe=False)
    pass

  pass


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
    STAGE.lightAtNode(p3dnode, STAGE.lights)
    STAGE.resetCamera(model=p3dnode)
    render.setPythonTag('lastModel', p3dnode)

  pass


class MmdViewerApp(ShowBase):
  wp = None

  def __init__(self):
    self.base = ShowBase.__init__(self, fStartDirect=False, windowType=None)
    self.startWx()
    self.wxApp.Bind(wx.EVT_CLOSE, self.quit)
    self.wxApp.Bind(wx.EVT_SIZE, self.resize)

    self.frame = Frame(None)
    # self.frame = TestFrame(None)

    self.wp = WindowProperties()
    self.wp.setOrigin(0,0)
    self.wp.setSize(self.frame.panda.GetSize()[0], self.frame.panda.GetSize()[1])
    self.wp.setParentWindow(self.frame.panda.GetHandle())
    base.openMainWindow(type='onscreen', props=self.wp)

    self.setupUI(self.frame)

    self.setupGL(render)

    icon = wx.Icon('viewpmx.ico', wx.BITMAP_TYPE_ICO)
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

  def setupUI(self, win):
    self.dt = MyFileDropTarget(win)
    win.SetDropTarget(self.dt)

    menu = wx.Menu()
    for id in xrange(self.frame.menuView.GetMenuItemCount()):
      item = self.frame.menuView.FindItemByPosition(id)
      text = item.GetText()
      help = item.GetHelp()
      if text=='':
        menu.AppendSeparator()
      else:
        mItem = menu.AppendCheckItem(wx.NewId(), text, help)
        if item.IsCheckable():
          mItem.Check(item.IsChecked())
        win.Bind(wx.EVT_MENU, self.OnPlanePopup, id=mItem.GetId())
        win.Bind(wx.EVT_MENU, self.OnPlanePopup, id=item.GetId())

    btn = self.frame.toolbar.FindById(ID_GRIDPLANE)
    self.frame.toolbar.SetDropdownMenu(ID_GRIDPLANE, menu)

    # droparrow = platebtn.PB_STYLE_DROPARROW + platebtn.PB_STYLE_SQUARE + platebtn.PB_STYLE_NOBG
    # icon = wx.Bitmap( u"icons/layers.png", wx.BITMAP_TYPE_ANY )
    # self.btnPlane = platebtn.PlateButton(self.frame.toolbar, wx.ID_ANY, "", icon, style=droparrow)
    # self.frame.toolbar.AddControl(self.btnPlane, _(u'Plane'))
    # self.frame.toolbar.Realize()


    # # make a menu
    # menu = wx.Menu()
    # # Show how to put an icon in the menu
    # item = wx.MenuItem(menu, self.popupID1,"One")
    # bmp = images.Smiles.GetBitmap()
    # item.SetBitmap(bmp)
    # menu.AppendItem(item)
    # # add some other items
    # menu.Append(self.popupID2, "Two")
    # menu.Append(self.popupID3, "Three")
    # menu.Append(self.popupID4, "Four")
    # menu.Append(self.popupID5, "Five")
    # menu.Append(self.popupID6, "Six")

    win.Bind(wx.EVT_TOOL, self.OnOpen, id=ID_OPEN)
    win.Bind(wx.EVT_MENU, self.OnOpen, id=win.menuOpen.GetId())
    win.Bind(wx.EVT_TOOL, self.OnSnapshot, id=ID_SNAPSHOT)
    win.Bind(wx.EVT_MENU, self.OnSnapshot, id=win.menuSnapshot.GetId())

    win.Bind(wx.EVT_MENU, self.OnPlanePopup, id=ID_GRIDPLANE)

    pass

  def setupGL(self, render):
    base.camLens.setNearFar(0.1, 550.0)
    base.camLens.setFov(45.0)
    base.camLens.setFocalLength(50)

    STAGE.setAxis(render)

    self.lights = STAGE.setStudioLight(render)

    STAGE.resetCamera()

    render.setAntialias(AntialiasAttrib.MAuto)
    pass

  def OnOpen(self, event):
    p3dnode = loader.loadModel('panda')
    p3dnode.reparentTo(render)
    STAGE.lightAtNode(p3dnode, lights=STAGE.lights)
    STAGE.resetCamera(model=p3dnode)
    pass

  def OnSnapshot(self, event):
    snapfile = os.path.join(CWD, 'snap02.png')
    snapfile = Filename.fromOsSpecific(snapfile)
    base.graphicsEngine.renderFrame()
    source = base.camera.getChild(0).node().getDisplayRegion(0)
    result = base.screenshot(namePrefix=snapfile, defaultFilename=0, source=None, imageComment='')
    print(result)
    pass

  def OnPlanePopup(self, event):
    # btn = self.frame.toolbar.GetToolClientData(ID_GRIDPLANE)
    print(event)
    # pop =
    # self.frame.PopupMenu(self.frame.menuView)
  pass

if __name__ == '__main__':
  app = MmdViewerApp()
  app.run()

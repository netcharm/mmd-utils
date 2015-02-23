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

import wx
import wx.aui

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
from direct.directtools.DirectGrid import DirectGrid
from direct.directtools.DirectGlobals import *

from direct.gui.DirectGui import *

from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from direct.interval.IntervalGlobal import *
from direct.task import Task
# from direct.wxwidgets import WxAppShell
from direct.wxwidgets.ViewPort import *
from direct.wxwidgets.WxPandaWindow import *

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

    self.panda = Viewport.makeFront(self)

    pandaInfo = wx.aui.AuiPaneInfo().Name("panda3d")
    pandaInfo.Center().CloseButton(False).MaximizeButton(True).CaptionVisible(False)
    self.auiManager.AddPane(self.panda, pandaInfo)

    self.auiManager.Update()

  def onQuit(self, evt):
    self.auiManager.UnInit()
    self.Close()

class Frame(MainForm):
  def __init__(self, *args, **kwargs):
    MainForm.__init__(self, *args, **kwargs)

    self.auiManager = wx.aui.AuiManager(self)

    self.panda = Viewport.makeFront(self)
    # self.panda.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize )
    # self.panda.SetSize(self.glvp.GetSize())
    # self.panda.AutoLayout = True

    # self.auiManager = wx.aui.AuiManager(self.glvp)

    pandaInfo = wx.aui.AuiPaneInfo().Name("panda3d")
    pandaInfo.Center().CloseButton(False).MaximizeButton(True).CaptionVisible(False)
    self.auiManager.AddPane(self.panda, pandaInfo)

    self.auiManager.Update()

  def onQuit(self, evt):
    self.auiManager.UnInit()
    self.Close()

class MmdViewerApp(ShowBase):
  wp = None

  def __init__(self):
    ShowBase.__init__(self, fStartDirect=False, windowType=None)
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


    # loader.loadModel('panda')

    self.setupUI(self.frame)

    icon = wx.Icon('viewpmx.ico', wx.BITMAP_TYPE_ICO)
    self.frame.SetIcon(icon)
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
    win.Bind(wx.EVT_TOOL, self.OnOpen, id=ID_OPEN)
    win.Bind(wx.EVT_TOOL, self.OnSnapshot, id=ID_SNAPSHOT)
    win.Bind(wx.EVT_MENU, self.OnSnapshot, id=win.menuSnapshot.GetId())

    pass

  def OnOpen(self, event):
    loader.loadModel('panda').reparentTo(render)
    pass

  def OnSnapshot(self, event):

    snapfile = os.path.join(CWD, 'snap02.png')
    snapfile = Filename.fromOsSpecific(snapfile)
    base.graphicsEngine.renderFrame()
    source = base.camera.getChild(0).node().getDisplayRegion(0)
    result = base.screenshot(namePrefix=snapfile, defaultFilename=0, source=None, imageComment='')
    print(result)
    pass

  pass

if __name__ == '__main__':
  app = MmdViewerApp()
  app.run()

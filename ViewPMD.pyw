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

from pandac.PandaModules import *

# need to be before the Direct Start Import
loadPrcFileData("", "window-title MMD PMX/PMX Model Viewer")
loadPrcFileData("", "icon-filename viewpmx.ico")
loadPrcFileData("", "win-size 800 800")
loadPrcFileData("", "window-type none")
loadPrcFileData('', 'text-encoding utf8')
loadPrcFileData('', 'textures-power-2 none')

from panda3d.core import ConfigVariableString
from panda3d.core import Shader
from panda3d.core import Filename
from panda3d.core import Material
from panda3d.core import VBase4


from direct.filter.CommonFilters import CommonFilters

import direct.directbase.DirectStart

from direct.gui.DirectGui import *

from utils.DrawPlane import *
from utils.pmx import *

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])

SHOW_LIGHT_POS = True
SHOW_LIGHT_POS = False

SHOW_SHADOW = True
SHOW_SHADOW = False

SHOW_AXIS = True
# SHOW_AXIS = False

lastModel = None

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

def resetCamera():
  if lastModel:
    min_point = LPoint3f()
    max_point = LPoint3f()
    lastModel.calcTightBounds(min_point, max_point)

    node_size = LPoint3f(max_point.x-min_point.x, max_point.y-min_point.y, max_point.z-min_point.z)
    setCamera(x=0, y=1.6*node_size.z, z=0.5*node_size.z, p=10, oobe=False)
  pass

def setStudioLight(render):
  lights = []

  alight = AmbientLight('alight')
  # alight.setColor(VBase4(0.6, 0.6, 0.6, 1))
  alight.setColor(VBase4(0.33, 0.33, 0.33, 0.33))
  alnp = render.attachNewNode(alight)
  lights.append(alnp)

  dlight_topback = Spotlight('backtop dlight')
  dlnp_topback = render.attachNewNode(dlight_topback)
  dlnp_topback.setX(0)
  dlnp_topback.setZ(25)
  dlnp_topback.setY(+55)
  dlnp_topback.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
  # dlnp_topback.node().setAttenuation( Vec3( 0.005, 0.005, 0.005 ) )
  dlnp_topback.setHpr(0, -168, 0)
  if SHOW_LIGHT_POS:
    dlnp_topback.node().showFrustum()
  lights.append(dlnp_topback)

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
  lights.append(dlnp_front)

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
  lights.append(dlnp_left)

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
  lights.append(dlnp_right)

  if SHOW_SHADOW:
    for light in lights:
      try:
        light.node().setShadowCaster(True, 512, 512)
      except:
        continue

  return(lights)
  pass

def lightAtNode(node, lights=None):
  if not lights:
      return
  if isinstance(node, NodePathCollection):
    for np in node:
      for light in lights:
        np.setLight(light)
  elif isinstance(node, NodePath):
    for light in lights:
      node.setLight(light)
  pass


def setAxis(render):
  grid = ThreeAxisGrid(xy=True, yz=False, xz=False, z=False)
  gridnodepath = grid.create()
  gridnodepath.reparentTo(render)
  gridnodepath.setShaderAuto()
  pass

def setUI():
  UI = []

  btnReset = DirectButton(pos=(480,480), text=u'RESET', text_pos=(10,10), frameSize=(460, 460, 80, 80))
  pass

def setAppInfo(title, icon):
  # 'DtoolClassDict', 'DtoolGetSupperBase',
  # 'MAbsolute', 'MRelative', 'M_absolute', 'M_relative',
  # 'ZBottom', 'ZNormal', 'ZTop', 'Z_bottom', 'Z_normal', 'Z_top',
  # 'addProperties', 'add_properties',
  # 'assign', 'clear',
  # 'clearCursorFilename', 'clearCursorHidden', 'clearDefault', 'clearFixedSize',
  # 'clearForeground', 'clearFullscreen',
  #  'clearIconFilename', 'clearMinimized', 'clearMouseMode',
  #  'clearOpen', 'clearOrigin', 'clearParentWindow', 'clearRawMice', 'clearSize',
  #  'clearTitle', 'clearUndecorated',
  #  'clearZOrder', 'clear_cursor_filename', 'clear_cursor_hidden',
  #  'clear_default', 'clear_fixed_size', 'clear_foreground', 'clear_fullscreen', 'clear_icon_filename',
  #  'clear_minimized', 'clear_mouse_mode', 'clear_open', 'clear_origin', 'clear_parent_window', 'clear_raw_mice', 'clear_size',
  #  'clear_title', 'clear_undecorated', 'clear_z_order',
  #  'getConfigProperties', 'getCursorFilename', 'getCursorHidden', 'getDefault', 'getFixedSize', 'getForeground', 'getFullscreen',
  #  'getIconFilename', 'getMinimized', 'getMouseMode', 'getOpen', 'getParentWindow', 'getRawMice', 'getTitle', 'getUndecorated',
  #  'getXOrigin', 'getXSize', 'getYOrigin', 'getYSize', 'getZOrder',
  #  'get_config_properties', 'get_cursor_filename', 'get_cursor_hidden', 'get_default', 'get_fixed_size',
  #  'get_foreground', 'get_fullscreen', 'get_icon_filename', 'get_minimized', 'get_mouse_mode', 'get_open',
  #  'get_parent_window', 'get_raw_mice', 'get_title', 'get_undecorated',
  #  'get_x_origin', 'get_x_size', 'get_y_origin', 'get_y_size', 'get_z_order',
  #  'hasCursorFilename', 'hasCursorHidden', 'hasFixedSize', 'hasForeground', 'hasFullscreen', 'hasIconFilename', 'hasMinimized',
  #  'hasMouseMode', 'hasOpen', 'hasOrigin', 'hasParentWindow', 'hasRawMice', 'hasSize', 'hasTitle', 'hasUndecorated', 'hasZOrder',
  #  'has_cursor_filename', 'has_cursor_hidden', 'has_fixed_size', 'has_foreground', 'has_fullscreen', 'has_icon_filename',
  #  'has_minimized', 'has_mouse_mode', 'has_open', 'has_origin', 'has_parent_window', 'has_raw_mice', 'has_size', 'has_title',
  #  'has_undecorated', 'has_z_order', 'isAnySpecified', 'is_any_specified',
  #  'output',
  #  'setCursorFilename', 'setCursorHidden', 'setDefault', 'setFixedSize', 'setForeground', 'setFullscreen', 'setIconFilename',
  #  'setMinimized', 'setMouseMode', 'setOpen', 'setOrigin', 'setParentWindow', 'setRawMice', 'setSize', 'setTitle', 'setUndecorated',
  #  'setZOrder', 'set_cursor_filename', 'set_cursor_hidden', 'set_default', 'set_fixed_size', 'set_foreground', 'set_fullscreen',
  #  'set_icon_filename', 'set_minimized', 'set_mouse_mode', 'set_open', 'set_origin', 'set_parent_window', 'set_raw_mice', 'set_size',
  #  'set_title', 'set_undecorated', 'set_z_order', 'size', this', 'this_metatype'

  props = WindowProperties()
  props.setTitle(title)
  props.setIconFilename(Filename.fromOsSpecific(os.path.join(CWD, icon)))
  base.win.requestProperties(props)
  pass

def snapshot(snapfile='snap_00.png'):
  # n = base.win.ModelPool[0].getName()
  if lastModel:
    path = lastModel.node().getTag('path')
    fn = os.path.splitext(os.path.basename(path))
    folder = os.path.dirname(path)
    snapfile = os.path.join(folder, u'snap_%s.png' % (fn[0]))
    # snapfile = u'snap_%s.png' % lastModel.getName()
  return(base.win.saveScreenshot(filename=snapfile))
  pass

if __name__ == '__main__':
  # title = 'PMX/PMX file Viewer'
  # icon = 'viewpmx.ico'
  # setAppInfo(title, icon)

  base.openMainWindow(type = 'onscreen')

  pmxFile = u'./models/apimiku/Miku long hair.pmx'
  pmxFile = u'./models/cupidmiku/Cupid Miku.pmx'
  pmxFile = u'./models/meiko/meiko.pmx'

  if len(sys.argv) > 1:
    if len(sys.argv[1]) > 0:
      pmxFile = sys.argv[1]

  pmxModel = pmxLoad(pmxFile)
  if pmxModel:
    if SHOW_AXIS:
      setAxis(render)

    p3dnode = pmx2p3d(pmxModel)
    p3dnode.reparentTo(render)
    lastModel = p3dnode

    lights = setStudioLight(render)
    lightAtNode(p3dnode, lights=lights)

    resetCamera()
    # base.screenshot(namePrefix='snap_', defaultFilename=p3dnode.getName())

    # btnReset = DirectButton(pos=(480,480), text=u'RESET', text_pos=(10,10), frameSize=(460, 460, 80, 80))
    btnSnapshot = DirectButton(text=u'截屏', scale=.05, pos=(-0.935, -10, 0.938), command=snapshot)
    btnSnapshot = DirectButton(text=u'复位', scale=.05, pos=(-0.935, -10, 0.852), command=resetCamera)

    # btnSnapshot = DirectButton(text=u'SNAP', text_pos=(10,10), frameSize=(460, 460, 80, 80), scale=5.05, command=snapshot)



  # pmodel = loader.loadModel('panda')
  # print(type(pmodel))

  # render.setAntialias(AntialiasAttrib.MMultisample, 8)
  # render.setAntialias(AntialiasAttrib.MAuto)
  # render.setShaderAuto()

  mydir = os.path.abspath(sys.path[0])

  # Convert that to panda's unix-style notation.
  # 转换为 panda 使用的 unix 风格。
  mydir = Filename.fromOsSpecific(mydir).getFullpath()
  # print(mydir)

  run()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
# Three Axis Coordinate Plane Grid Class (ThreeAxisGrid)
# Mathew Lloyd AKA 'Forklift', August 2008
# 'matthewadamlloyd@gmail.com'
#
#   The grid can be created with any number of axis planes in mind.
#   Simply set size values for the planes you wish to use. Sizes of
#   zero will be ignored. By default, you can create single and three
#   plane setups. Use plane visibility to disable any planes you don't
#   need to acheive a 2 plane setup.
#
#   To create a grid, first create an instance of this class. Then call
#   its 'create' method to create the grid based on the class member
#   variables. 'create' will return a NodePath instance that must be
#   parented to 'render' in order to acheive visibility. Once the grid
#   is created, its settings cannot be changed as the 'create' method
#   generates the geometry procedurally using Panda's LineSeg class.
#    If another grid or a different grid is needed, create a new
#   instance of the ThreeAxisGrid class and setup as described above.
#
#   A 'refresh' method is planned for a future version. This method
#   would allow you to change a ThreeAxisGrid instance's settings,
#   then recreate the geometry without changing the
#   parentNodePath of the instance.
#
# ThreeAxisGrid class member variables are as follows:
#   'xsize' is the x axis length in units of the grid
#   'ysize' is the y axis length in units of the grid
#   'zsize' is the z axis lenght in units of the grid
#   'gridstep' is the spacing in units at which primary grid lines
#      will be drawn
#   'subdiv' is the number used to subdivide the main (gridstep based)
#      grid lines for drawing secondary grid lines example: if the
#      primary grid lines are drawn every 10 units, and subdivision
#      is set at 4, then secondary grid lines will be drawn
#      every 2.5 units
#   'XYPlaneShow' and so forth: used to disable a plane with the
#      creation of 2 plane grids in mind. 1 is on, 0 is off.
#   'endCapLinesShow' is used to turn grid border edges on or off.
#      1 is on, 0 is off.
#   'xaxiscolor' and so forth: axis colors are defaulted to the
#      Maya standard axis colors
#   'gridcolor' is the RGB color of the primary grid lines,
#      defaulted to black
#   'subdivcolor' is the RGB color of the secondary grid lines,
#      defaulted to dark gray
#   'axisThickness' and so forth: sets the thickness of the
#      respective component's lines
#   'parentNode' and 'parentNodePath' are used to contain
#      the three LineSeg instance nodes and paths
#######################################################################
#
# Modified by netcharm, 2015
#
#######################################################################

import sys
import os

from panda3d.core import *


DEBUG = True
DEBUG = False

class ThreeAxisGrid:
   def __init__(self,
      xsize = 50, ysize = 50, zsize = 50,
      gridstep = 10, subdiv = 10,
      xy=True, xz=True, yz=True,
      x=True, y=True, z=True,
      board=True):

      #Init passed variables
      self.XSize = xsize
      self.YSize = ysize
      self.ZSize = zsize
      self.gridStep = gridstep
      self.subdiv = subdiv

      #Init default variables

      #Plane and end cap line visibility (1 is show, 0 is hide)
      if xy:
         self.XYPlaneShow = 1
      else:
         self.XYPlaneShow = 1

      if xz:
         self.XZPlaneShow = 1
      else:
         self.XZPlaneShow = 1

      if yz:
         self.YZPlaneShow = 1
      else:
         self.YZPlaneShow = 1

      if x:
         self.XAxisShow = 1
      else:
         self.XAxisShow = 1

      if y:
         self.YAxisShow = 1
      else:
         self.YAxisShow = 1

      if z:
         self.ZAxisShow = 1
      else:
         self.ZAxisShow = 1

      if board:
         self.endCapLinesShow = 1
      else:
         self.endCapLinesShow = 0

      #Alpha variables for each plane
      #self.XYPlaneAlpha = 1
      #self.XZPlaneAlpha = 1
      #self.YZPlaneAlpha = 1

      #Colors (RGBA passed as a VBase4 object)
      self.XAxisColor = VBase4(1, 0, 0, 1)
      self.YAxisColor = VBase4(0, 1, 0, 1)
      self.ZAxisColor = VBase4(0, 0, 1, 1)
      self.gridColor = VBase4(0, 0, 0, 1)
      self.subdivColor = VBase4(.35, .35, .35, 1)

      #Line thicknesses (in pixels)
      self.axisThickness = 1
      self.gridThickness = 1
      self.subdivThickness = 1

      #Axis, grid, and subdiv lines must be seperate LineSeg
      #objects in order to allow different thicknesses.
      #The parentNode groups them together for convenience.
      #All may be accessed individually if necessary.
      self.parentNode = None
      self.parentNodePath = None
      self.axisLinesNode = None
      self.axisLinesNodePath = None
      self.gridLinesNode = None
      self.gridLinesNodePath = None
      self.subdivLinesNode = None
      self.subdivLinesNodePath = None

      #Create line objects
      self.axisLinesX = LineSegs('X')
      self.axisLinesY = LineSegs('Y')
      self.axisLinesZ = LineSegs('Z')

      self.gridLinesXY = LineSegs('XY')
      self.gridLinesYZ = LineSegs('YZ')
      self.gridLinesXZ = LineSegs('XZ')

      self.subdivLinesXY = LineSegs('SUBDIV')
      self.subdivLinesYZ = LineSegs('SUBDIV')
      self.subdivLinesXZ = LineSegs('SUBDIV')

   def create(self):

      #Set line thicknesses
      self.axisLinesX.setThickness(self.axisThickness)
      self.axisLinesY.setThickness(self.axisThickness)
      self.axisLinesZ.setThickness(self.axisThickness)

      self.subdivLinesXY.setThickness(self.subdivThickness)
      self.subdivLinesYZ.setThickness(self.subdivThickness)
      self.subdivLinesXZ.setThickness(self.subdivThickness)

      if(self.XSize != 0):
         #Draw X axis line
         self.axisLinesX.setColor(self.XAxisColor)
         self.axisLinesX.moveTo(-(self.XSize), 0, 0)
         self.axisLinesX.drawTo(self.XSize, 0, 0)

      if(self.YSize != 0):
         #Draw Y axis line
         self.axisLinesY.setColor(self.YAxisColor)
         self.axisLinesY.moveTo(0, -(self.YSize), 0)
         self.axisLinesY.drawTo(0, self.YSize, 0)

      if(self.ZSize != 0):
         #Draw Z axis line
         self.axisLinesZ.setColor(self.ZAxisColor)
         self.axisLinesZ.moveTo(0, 0, -(self.ZSize))
         self.axisLinesZ.drawTo(0, 0, self.ZSize)

      #Check to see if primary grid lines should be drawn at all
      if(self.gridStep != 0):

         #Draw primary grid lines
         self.gridLinesXY.setColor(self.gridColor)
         self.gridLinesYZ.setColor(self.gridColor)
         self.gridLinesXZ.setColor(self.gridColor)

         #Draw primary grid lines metering x axis if any x-length
         if(self.XSize != 0):

            if((self.YSize != 0) and (self.XYPlaneShow != 0)):
            #Draw y lines across x axis starting from center moving out
            #XY Plane
               for x in self.myfrange(0, self.XSize, self.gridStep):
                  self.gridLinesXY.moveTo(x, -(self.YSize), 0)
                  self.gridLinesXY.drawTo(x, self.YSize, 0)
                  self.gridLinesXY.moveTo(-x, -(self.YSize), 0)
                  self.gridLinesXY.drawTo(-x, self.YSize, 0)

               if(self.endCapLinesShow != 0):
                  #Draw endcap lines
                  self.gridLinesXY.moveTo(self.XSize, -(self.YSize), 0)
                  self.gridLinesXY.drawTo(self.XSize, self.YSize, 0)
                  self.gridLinesXY.moveTo(-(self.XSize), -(self.YSize), 0)
                  self.gridLinesXY.drawTo(-(self.XSize), self.YSize, 0)

            if((self.ZSize != 0) and (self.XZPlaneShow != 0)):
            #Draw z lines across x axis starting from center moving out
            #XZ Plane
               for x in self.myfrange(0, self.XSize, self.gridStep):
                  self.gridLinesXZ.moveTo(x, 0, -(self.ZSize))
                  self.gridLinesXZ.drawTo(x, 0, self.ZSize)
                  self.gridLinesXZ.moveTo(-x, 0, -(self.ZSize))
                  self.gridLinesXZ.drawTo(-x, 0, self.ZSize)

               if(self.endCapLinesShow != 0):
                  #Draw endcap lines
                  self.gridLinesXZ.moveTo(self.XSize, 0, -(self.ZSize))
                  self.gridLinesXZ.drawTo(self.XSize, 0, self.ZSize)
                  self.gridLinesXZ.moveTo(-(self.XSize), 0, -(self.ZSize))
                  self.gridLinesXZ.drawTo(-(self.XSize), 0, self.ZSize)

         #Draw primary grid lines metering y axis if any y-length
         if(self.YSize != 0):

            if((self.YSize != 0) and (self.XYPlaneShow != 0)):
            #Draw x lines across y axis
            #XY Plane
               for y in self.myfrange(0, self.YSize, self.gridStep):
                  self.gridLinesXY.moveTo(-(self.XSize), y, 0)
                  self.gridLinesXY.drawTo(self.XSize, y, 0)
                  self.gridLinesXY.moveTo(-(self.XSize), -y, 0)
                  self.gridLinesXY.drawTo(self.XSize, -y, 0)

               if(self.endCapLinesShow != 0):
                  #Draw endcap lines
                  self.gridLinesXY.moveTo(-(self.XSize), self.YSize, 0)
                  self.gridLinesXY.drawTo(self.XSize, self.YSize, 0)
                  self.gridLinesXY.moveTo(-(self.XSize), -(self.YSize), 0)
                  self.gridLinesXY.drawTo(self.XSize, -(self.YSize), 0)

            if((self.ZSize != 0) and (self.YZPlaneShow != 0)):
            #Draw z lines across y axis
            #YZ Plane
               for y in self.myfrange(0, self.YSize, self.gridStep):
                  self.gridLinesYZ.moveTo(0, y, -(self.ZSize))
                  self.gridLinesYZ.drawTo(0, y, self.ZSize)
                  self.gridLinesYZ.moveTo(0, -y, -(self.ZSize))
                  self.gridLinesYZ.drawTo(0, -y, self.ZSize)

               if(self.endCapLinesShow != 0):
                  #Draw endcap lines
                  self.gridLinesYZ.moveTo(0, self.YSize, -(self.ZSize))
                  self.gridLinesYZ.drawTo(0, self.YSize, self.ZSize)
                  self.gridLinesYZ.moveTo(0, -(self.YSize), -(self.ZSize))
                  self.gridLinesYZ.drawTo(0, -(self.YSize), self.ZSize)

         #Draw primary grid lines metering z axis if any z-length
         if(self.ZSize != 0):

            if((self.XSize != 0) and (self.XZPlaneShow != 0)):
            #Draw x lines across z axis
            #XZ Plane
               for z in self.myfrange(0, self.ZSize, self.gridStep):
                  self.gridLinesXZ.moveTo(-(self.XSize), 0, z)
                  self.gridLinesXZ.drawTo(self.XSize, 0, z)
                  self.gridLinesXZ.moveTo(-(self.XSize), 0, -z)
                  self.gridLinesXZ.drawTo(self.XSize, 0, -z)

               if(self.endCapLinesShow != 0):
                  #Draw endcap lines
                  self.gridLinesXZ.moveTo(-(self.XSize), 0, self.ZSize)
                  self.gridLinesXZ.drawTo(self.XSize, 0, self.ZSize)
                  self.gridLinesXZ.moveTo(-(self.XSize), 0, -(self.ZSize))
                  self.gridLinesXZ.drawTo(self.XSize, 0, -(self.ZSize))

            if((self.YSize != 0) and (self.YZPlaneShow != 0)):
            #Draw y lines across z axis
            #YZ Plane
               for z in self.myfrange(0, self.ZSize, self.gridStep):
                  self.gridLinesYZ.moveTo(0, -(self.YSize), z)
                  self.gridLinesYZ.drawTo(0, self.YSize, z)
                  self.gridLinesYZ.moveTo(0, -(self.YSize), -z)
                  self.gridLinesYZ.drawTo(0, self.YSize, -z)

               if(self.endCapLinesShow != 0):
                  #Draw endcap lines
                  self.gridLinesYZ.moveTo(0, -(self.YSize), self.ZSize)
                  self.gridLinesYZ.drawTo(0, self.YSize, self.ZSize)
                  self.gridLinesYZ.moveTo(0, -(self.YSize), -(self.ZSize))
                  self.gridLinesYZ.drawTo(0, self.YSize, -(self.ZSize))

      #Check to see if secondary grid lines should be drawn
      if(self.subdiv != 0):

         #Draw secondary grid lines
         self.subdivLinesXY.setColor(self.subdivColor)
         self.subdivLinesYZ.setColor(self.subdivColor)
         self.subdivLinesXZ.setColor(self.subdivColor)

         if(self.XSize != 0):
            adjustedstep = self.gridStep / self.subdiv
            if DEBUG:
               print(self.gridStep)
               print(self.subdiv)
               print(adjustedstep)
               print(self.gridStep/self.subdiv)

            if((self.YSize != 0) and (self.XYPlaneShow != 0)):
            #Draw y lines across x axis starting from center moving out
            #XY
               for x in self.myfrange(0, self.XSize, adjustedstep):
                  self.subdivLinesXY.moveTo(x, -(self.YSize), 0)
                  self.subdivLinesXY.drawTo(x, self.YSize, 0)
                  self.subdivLinesXY.moveTo(-x, -(self.YSize), 0)
                  self.subdivLinesXY.drawTo(-x, self.YSize, 0)

            if((self.ZSize != 0) and (self.XZPlaneShow != 0)):
            #Draw z lines across x axis starting from center moving out
            #XZ
               for x in self.myfrange(0, self.XSize, adjustedstep):
                  self.subdivLinesXZ.moveTo(x, 0, -(self.ZSize))
                  self.subdivLinesXZ.drawTo(x, 0, self.ZSize)
                  self.subdivLinesXZ.moveTo(-x, 0, -(self.ZSize))
                  self.subdivLinesXZ.drawTo(-x, 0, self.ZSize)

         if(self.YSize != 0):

            if((self.YSize != 0) and (self.XYPlaneShow != 0)):
            #Draw x lines across y axis
            #XY
               for y in self.myfrange(0, self.YSize, adjustedstep):
                  self.subdivLinesXY.moveTo(-(self.XSize), y, 0)
                  self.subdivLinesXY.drawTo(self.XSize, y, 0)
                  self.subdivLinesXY.moveTo(-(self.XSize), -y, 0)
                  self.subdivLinesXY.drawTo(self.XSize, -y, 0)

            if((self.ZSize != 0) and (self.YZPlaneShow != 0)):
            #Draw z lines across y axis
            #YZ
               for y in self.myfrange(0, self.YSize, adjustedstep):
                  self.subdivLinesYZ.moveTo(0, y, -(self.ZSize))
                  self.subdivLinesYZ.drawTo(0, y, self.ZSize)
                  self.subdivLinesYZ.moveTo(0, -y, -(self.ZSize))
                  self.subdivLinesYZ.drawTo(0, -y, self.ZSize)

         if(self.ZSize != 0):

            if((self.XSize != 0) and (self.XZPlaneShow != 0)):
            #Draw x lines across z axis
            #XZ
               for z in self.myfrange(0, self.ZSize, adjustedstep):
                  self.subdivLinesXZ.moveTo(-(self.XSize), 0, z)
                  self.subdivLinesXZ.drawTo(self.XSize, 0, z)
                  self.subdivLinesXZ.moveTo(-(self.XSize), 0, -z)
                  self.subdivLinesXZ.drawTo(self.XSize, 0, -z)

            if((self.YSize != 0) and (self.YZPlaneShow != 0)):
            #Draw y lines across z axis
            #YZ
               for z in self.myfrange(0, self.ZSize, adjustedstep):
                  self.subdivLinesYZ.moveTo(0, -(self.YSize), z)
                  self.subdivLinesYZ.drawTo(0, self.YSize, z)
                  self.subdivLinesYZ.moveTo(0, -(self.YSize), -z)
                  self.subdivLinesYZ.drawTo(0, self.YSize, -z)

      #Create ThreeAxisGrid nodes and nodepaths
      #Create parent node and path
      self.parentNode = PandaNode('threeaxisgrid-parentnode')
      self.parentNodePath = NodePath(self.parentNode)

      #Create axis lines node and path, then reparent
      self.axisLinesNode = PandaNode('AXISLINE')
      self.axisLinesNodePath = NodePath(self.axisLinesNode)
      self.axisLinesNodePath.reparentTo(self.parentNodePath)

      self.axisLinesNodeX = self.axisLinesX.create()
      self.axisLinesNodePathX = NodePath(self.axisLinesNodeX)
      self.axisLinesNodePathX.reparentTo(self.axisLinesNodePath)

      self.axisLinesNodeY = self.axisLinesY.create()
      self.axisLinesNodePathY = NodePath(self.axisLinesNodeY)
      self.axisLinesNodePathY.reparentTo(self.axisLinesNodePath)

      self.axisLinesNodeZ = self.axisLinesZ.create()
      self.axisLinesNodePathZ = NodePath(self.axisLinesNodeZ)
      self.axisLinesNodePathZ.reparentTo(self.axisLinesNodePath)

      #Create grid lines node and path, then reparent
      self.gridLinesNode     = PandaNode('PLANEGRID')
      self.gridLinesNodePath = NodePath(self.gridLinesNode)
      self.gridLinesNodePath.reparentTo(self.parentNodePath)

      self.gridLinesNodeXY     = self.gridLinesXY.create()
      self.gridLinesNodePathXY = NodePath(self.gridLinesNodeXY)
      self.gridLinesNodePathXY.reparentTo(self.gridLinesNodePath)

      self.gridLinesNodeYZ     = self.gridLinesYZ.create()
      self.gridLinesNodePathYZ = NodePath(self.gridLinesNodeYZ)
      self.gridLinesNodePathYZ.reparentTo(self.gridLinesNodePath)

      self.gridLinesNodeXZ     = self.gridLinesXZ.create()
      self.gridLinesNodePathXZ = NodePath(self.gridLinesNodeXZ)
      self.gridLinesNodePathXZ.reparentTo(self.gridLinesNodePath)

      self.subdivLinesNodeXY     = self.subdivLinesXY.create()
      self.subdivLinesNodePathXY = NodePath(self.subdivLinesNodeXY)
      self.subdivLinesNodePathXY.reparentTo(self.gridLinesNodePathXY)

      self.subdivLinesNodeYZ     = self.subdivLinesYZ.create()
      self.subdivLinesNodePathYZ = NodePath(self.subdivLinesNodeYZ)
      self.subdivLinesNodePathYZ.reparentTo(self.gridLinesNodePathYZ)

      self.subdivLinesNodeXZ     = self.subdivLinesXZ.create()
      self.subdivLinesNodePathXZ = NodePath(self.subdivLinesNodeXZ)
      self.subdivLinesNodePathXZ.reparentTo(self.gridLinesNodePathXZ)

      self.parentNodePath.setShaderAuto(1)

      return self.parentNodePath

   #Thanks to Edvard Majakari for this float-accepting range method
   def myfrange(self, start, stop=None, step=None):
      if stop is None:
         stop = float(start)
         start = 0.0
      if step is None:
         step = 1.0
      cur = float(start)
      while cur < stop:
         yield cur
         cur += step

   def planeXY(self, show=True, subdiv=True):
      if show:
         # self.XYPlaneshow = 1
         self.gridLinesNodePathXY.show()
         if subdiv:
            self.subdivLinesNodePathXY.show()
         else:
            self.subdivLinesNodePathXY.hide()
      else:
         # self.XYPlaneShow = 0
         self.gridLinesNodePathXY.hide()
         # self.subdivLinesNodePathXY.hide()
      pass

   def planeYZ(self, show=True, subdiv=True):
      if show:
         # self.YZPlaneshow = 1
         self.gridLinesNodePathYZ.show()
         if subdiv:
            self.subdivLinesNodePathYZ.show()
         else:
            self.subdivLinesNodePathYZ.hide()
      else:
         # self.YZPlaneShow = 0
         self.gridLinesNodePathYZ.hide()
         # self.subdivLinesNodePathYZ.hide()
      pass

   def planeXZ(self, show=True, subdiv=True):
      if show:
         # self.XZPlaneshow = 1
         self.gridLinesNodePathXZ.show()
         if subdiv:
            self.subdivLinesNodePathXZ.show()
         else:
            self.subdivLinesNodePathXZ.hide()
      else:
         # self.XZPlaneShow = 0
         self.gridLinesNodePathXZ.hide()
         # self.subdivLinesNodePathXZ.hide()
      pass

   def showPlane(self, XY=False, YZ=False, XZ=False, SUBDIV=True):
      self.planeXY(show=XY, subdiv=SUBDIV)
      self.planeYZ(show=YZ, subdiv=SUBDIV)
      self.planeXZ(show=XZ, subdiv=SUBDIV)
      pass

   def axisX(self, show=True):
      if show:
         self.axisLinesNodePathX.show()
      else:
         self.axisLinesNodePathX.hide()

   def axisY(self, show=True):
      if show:
         self.axisLinesNodePathY.show()
      else:
         self.axisLinesNodePathY.hide()

   def axisZ(self, show=True):
      if show:
         self.axisLinesNodePathZ.show()
      else:
         self.axisLinesNodePathZ.hide()

   def showAxis(self, X=True, Y=True, Z=True):
      self.axisX(show=X)
      self.axisY(show=Y)
      self.axisZ(show=Z)
      pass

   def gridBoard(self, show=True):
      if show:
         self.endCapLinesShow = 1
      else:
         self.endCapLinesShow = 0
      pass


if __name__ == '__main__':
   from direct.showbase.ShowBase import ShowBase
   base = ShowBase()

   grid = ThreeAxisGrid()
   gridnodepath = grid.create()
   gridnodepath.reparentTo(base.render)

   base.run()

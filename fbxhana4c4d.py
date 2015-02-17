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

import re

import codecs

from FbxCommon import *

def checkFormat(fbx):
  with open(fbx, 'rb') as f:
    line = f.read(20)
  if line.startswith(r'Kaydara FBX Binary'):
    return('binary')
  else:
    return('ascii')
  pass

def hana2unicode(text):
  str_univalue = re.sub(r"u'(.*?)'", '\\1', repr(text).replace('\\\\', '\\'))
  return(str_univalue)

def DisplayMetaData(pScene):
  sceneInfo = pScene.GetSceneInfo()
  if sceneInfo:
    print("\n--------------------\nMeta-Data\n--------------------\n")
    print("    Title    : %s" % sceneInfo.mTitle.Buffer())
    print("    Subject  : %s" % sceneInfo.mSubject.Buffer())
    print("    Author   : %s" % sceneInfo.mAuthor.Buffer())
    print("    Keywords : %s" % sceneInfo.mKeywords.Buffer())
    print("    Revision : %s" % sceneInfo.mRevision.Buffer())
    print("    Comment  : %s" % sceneInfo.mComment.Buffer())

  pass

def shape2unicode(pGeometry):
  lBlendShapeCount = pGeometry.GetDeformerCount(FbxDeformer.eBlendShape)

  for lBlendShapeIndex in range(lBlendShapeCount):
    lBlendShape = pGeometry.GetDeformer(lBlendShapeIndex, FbxDeformer.eBlendShape)
    name_old = lBlendShape.GetName()
    name_new = hana2unicode(name_old)
    lBlendShape.SetName(name_new)
    # DisplayString(u"    BlendShape ", name_old, name_new)

    lBlendShapeChannelCount = lBlendShape.GetBlendShapeChannelCount()
    for lBlendShapeChannelIndex in range(lBlendShapeChannelCount):
      lBlendShapeChannel = lBlendShape.GetBlendShapeChannel(lBlendShapeChannelIndex)
      name_old = lBlendShapeChannel.GetName()
      name_new = hana2unicode(name_old)
      lBlendShapeChannel.SetName(name_new)

      lTargetShapeCount = lBlendShapeChannel.GetTargetShapeCount()
      for lTargetShapeIndex in range(lTargetShapeCount):
        lShape = lBlendShapeChannel.GetTargetShape(lTargetShapeIndex)
        name_old = lShape.GetName()
        name_new = hana2unicode(name_old)
        lShape.SetName(name_new)
  pass

def marker2unicode(pNode):
  lMarker = pNode.GetNodeAttribute()

  name_old = pNode.GetName()
  name_new = hana2unicode(name_old)
  # pNode.SetName(name_new)

  pass

def skeleton2unicode(pNode):
  lSkeleton = pNode.GetNodeAttribute()

  name_old = pNode.GetName()
  name_new = hana2unicode(name_old)
  # pNode.SetName(name_new)

  pass

def mesh2unicode(pNode):
  lMesh = pNode.GetNodeAttribute ()

  name_old = pNode.GetName()
  name_new = hana2unicode(name_old)
  pNode.SetName(name_new)

  shape2unicode(lMesh)

  pass

def scene2unicode(pScene):
  lNode = pScene.GetRootNode()

  if lNode:
    for i in range(lNode.GetChildCount()):
      node2unicode(lNode.GetChild(i))

  pass

def node2unicode(pNode):
  if pNode.GetNodeAttribute() == None:
    print("NULL Node Attribute\n")
  else:
    lAttributeType = (pNode.GetNodeAttribute().GetAttributeType())
    if lAttributeType == FbxNodeAttribute.eMarker:
      marker2unicode(pNode)
    elif lAttributeType == FbxNodeAttribute.eSkeleton:
      skeleton2unicode(pNode)
    elif lAttributeType == FbxNodeAttribute.eMesh:
      mesh2unicode(pNode)
    # elif lAttributeType == FbxNodeAttribute.eNurbs:
    #   DisplayNurb(pNode)
    # elif lAttributeType == FbxNodeAttribute.ePatch:
    #   DisplayPatch(pNode)
    # elif lAttributeType == FbxNodeAttribute.eCamera:
    #   DisplayCamera(pNode)
    # elif lAttributeType == FbxNodeAttribute.eLight:
    #   DisplayLight(pNode)

    # DisplayUserProperties(pNode)
    # DisplayTarget(pNode)
    # DisplayPivotsAndLimits(pNode)
    # DisplayTransformPropagation(pNode)
    # DisplayGeometricTransform(pNode)

    nodeName_old = pNode.GetName()
    nodeName_new = hana2unicode(nodeName_old)
    # pNode.SetName(nodeName_new)

  for i in range(pNode.GetChildCount()):
      node2unicode(pNode.GetChild(i))


def sdkLoadFBX(fbx, formatFollowSource=True, format=0):
  # Checing source file binary/ascii
  if formatFollowSource:
    if checkFormat(fbx).lower() == 'binary':
      format = 0
    else:
      format = 1

  # Prepare the FBX SDK.
  lSdkManager, lScene = InitializeSdkObjects()

  # Load the scene.
  lResult = LoadScene(lSdkManager, lScene, fbx)

  if not lResult:
    print("\n\nAn error occurred while loading the scene...")
  else :
    DisplayMetaData(lScene)

    scene2unicode(lScene)

    fs = os.path.splitext(fbx)
    SaveScene(lSdkManager, lScene, u'%s_unicode%s' % (fs[0], fs[1]), pFileFormat=format)

  # Destroy all objects created by the FBX SDK.
  lSdkManager.Destroy()
  pass

def main():
  # Prepare the FBX SDK.
  lSdkManager, lScene = InitializeSdkObjects()
  # Load the scene.

  ff = lSdkManager.GetIOPluginRegistry().GetWriterFormatCount()
  print(ff)

  lFormatCount = lSdkManager.GetIOPluginRegistry().GetWriterFormatCount()
  for lFormatIndex in range(lFormatCount):
    if lSdkManager.GetIOPluginRegistry().WriterIsFBX(lFormatIndex):
      lDesc = lSdkManager.GetIOPluginRegistry().GetWriterFormatDescription(lFormatIndex)
      print(lDesc)
      if "ascii" in lDesc:
        pFileFormat = lFormatIndex
        print(pFileFormat)
        break

  # Destroy all objects created by the FBX SDK.
  lSdkManager.Destroy()
  pass


if __name__=='__main__':
  if len(sys.argv)>1:
    fbx = sys.argv[1]
    if os.path.isfile(fbx):
      sdkLoadFBX(fbx)
  else:
    main()

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

import sys
import os

import codecs

import chardet

from PyQt4 import QtGui, QtCore, uic


SCRIPTNAME = ''
try:
    SCRIPTNAME = __file__
except:
    SCRIPTNAME = sys.argv[0]

if sys.platform == 'win32':
    enc = 'mbcs'
else:
    enc = 'utf8'
CWD = unicode(os.path.abspath(os.path.dirname(SCRIPTNAME)), enc)

def ShiftjisToUTF8_ft(folder):
  item = folder.decode('utf8').encode('mbcs')

  if os.altsep:
    sep = os.altsep
  else:
    sep = os.sep
  segs = item.split(sep)

  folder_new = []
  for seg in segs:
    seg_new = seg
    try:
      seg_new = seg.decode('shift_jis')
    except:
      seg_new = seg.decode('mbcs')
    pass
    folder_new.append(seg_new)

  result = sep.join(folder_new)
  try:
    result.encode('gbk')
    return(result)
  except:
    return(folder)
  pass

def ShiftjisToUTF8_f(folder):
  folder_old = folder
  folder_new = ShiftjisToUTF8_ft(folder_old)
  try:
    if folder_old != folder_new:
      os.rename(folder_old, folder_new)
  except:
    folder_new = folder
    pass
  cwd = os.path.abspath(os.getcwd())
  os.chdir(os.path.abspath(folder_new))
  try:
    print(u'%s' % folder_new)
  except:
    print(u'%s' % repr(folder_new))
    pass
  print('-' * 80)
  for item in os.listdir('.'):
    fullname = item
    if os.path.isfile(fullname):
      try:
        if sys.version_info.major >= 3:
          f_old = str.encode(item).decode('utf8')
          f_new = str.encode(item).decode('utf8').encode('mbcs').decode('shiftjis')
        else:
          f_old = item.decode('utf8').encode('mbcs')
          try:
            f_new = f_old.decode('shift_jis')
          except:
            f_new = f_old.decode('mbcs')
            continue

        os.rename(f_old, f_new)
        fullname = f_new
        if sys.version_info.major >= 3:
          print('[%s] ==> [%s]' % (f_old, f_new))
        else:
          print(u'[%s] ==> [%s]' % (f_old.decode('gbk'), f_new))
      except:
        continue
        pass
    elif os.path.isdir(fullname):
      ShiftjisToUTF8_f(fullname)

  print('=' * 80)
  # os.chdir('..')
  os.chdir(cwd)


class ConvertApp(QtGui.QMainWindow):
  ftext = ''
  overwrite = False
  title = ''

  def __init__(self):
    # QtGui.QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
    QtGui.QMainWindow.__init__(self)
    self.setAcceptDrops(True)

    self.ui = uic.loadUi(os.path.join(CWD, 'shiftjis2utf8_text.ui'))

    self.ui.statusbar.showMessage(self.tr('Ready'))

    # self.ui.setWindowFlags(QtCore.Qt.Window)
    self.ui.setWindowFlags(self.ui.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowContextHelpButtonHint)
    # self.ui.setWindowFlags(self.ui.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    # self.ui.setModal(True)
    self.ui.show()

    self.title = self.ui.windowTitle()

    self.ui.setAcceptDrops(True)
    self.ui.dragEnterEvent = self.dragEnterEvent
    self.ui.dragMoveEvent = self.dragEnterEvent
    self.ui.dropEvent = self.dropEvent

    self.ui.buttonBox.accepted.connect(self.btnConvert)
    self.ui.buttonBox.clicked.connect(self.btnClick)

    self.ui.chkOverwrite.toggled.connect(self.chkOverwrite)

    self.ui.lstItems.currentItemChanged.connect(self.currentItemChanged)
    self.ui.lstItems.currentItemChanged.connect(self.updateStatusbar)

    self.ui.chkOverwrite.setChecked(True)
    if self.ui.chkOverwrite.isChecked():
      self.overwrite = True
    else:
      self.overwrite = False;
    pass

  def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
      event.accept()
    else:
      event.ignore()

    pass

  def dragMoveEvent(self, event):
    if event.mimeData().hasUrls():
      event.accept()
    else:
      event.ignore()

    pass

  def dropEvent(self, event):
    idx = self.ui.lstItems.count()

    for url in event.mimeData().urls():
      path = url.toLocalFile().toLocal8Bit().data()
      item = QtGui.QListWidgetItem()
      item.setText(path.decode('mbcs'))
      item.setBackgroundColor(QtGui.QColor(0, 200, 0, 32))
      self.ui.lstItems.addItem(item)

    for idx in xrange(idx, self.ui.lstItems.count()):
      item = self.ui.lstItems.item(idx)
      path = unicode(item.text())
      if os.path.isfile(path):
        print(path)
        self.ftext = path
        try:
          result = self.convertFile(path)
          item.setToolTip(result[1])
          item.setWhatsThis(result[1])
          item.setStatusTip(result[1])
          if result[0]:
            item.setBackgroundColor(QtGui.QColor(0, 250, 0, 64))
          else:
            item.setBackgroundColor(QtGui.QColor(200, 0, 0, 64))
        except:
          continue
      elif os.path.isdir(path):
        ShiftjisToUTF8_f(path)

      # self.ui.lstItems.setCurrentRow(0)

    pass

  def currentItemChanged(self, currentItem, prevItem):
    if currentItem:
      path = unicode(currentItem.text())
      self.loadFile(path)
      self.ui.setWindowTitle(u'%s - %s' % (self.title, path))
      self.ui.statusbar.setToolTip(path)

    pass

  def loadFile(self, ftext, autodetect=False):
    with codecs.open(ftext, 'r') as f:
      lines = f.read()

    tip = self.tr(u'FAIL')
    result = False
    ftype = chardet.detect(lines)
    # print(ftext, ftype)
    if ftype and ('encoding' in ftype):
      if (ftype['confidence'] < 0.8) or (not ftype['encoding']):
        ftype['encoding'] = 'shift_jis'

      self.ui.edUTF8.setPlainText(lines.decode(ftype['encoding']))

      if ftype['encoding'].lower() == 'shift_jis':
        tip = self.tr(u'GOOD')
        result = True
      info = unicode(self.tr(u'%s, File Encoding : %s, Confidence : %2.0f%%')) % (tip, ftype['encoding'], ftype['confidence']*100)
    else:
      info = unicode(self.tr(u'%s, File Encoding : %s')) % (tip, u'UNKNOWN')

    return(result, info)

  def saveFile(self, ftext):
    if os.path.isfile(ftext):
      fn = os.path.splitext(ftext)
      # ftext = fn[0].decode('mbcs') + '_utf8' + fn[1]
      if not self.overwrite:
        ftext = fn[0] + '_utf8' + fn[1]
      with codecs.open(ftext, 'w') as f:
        f.write(codecs.BOM_UTF8)
        f.write(self.ui.edUTF8.toPlainText())
    pass

  def convertFile(self, src):
    tip = self.tr(u'FAIL')
    result = False
    ftype = None
    lines = []
    dst = src
    if os.path.isfile(src):
      with codecs.open(src, 'r') as f:
        lines = f.read()

      ftype = chardet.detect(lines)
      if ftype and ('encoding' in ftype):
        if (ftype['confidence'] < 0.8) or (not ftype['encoding']):
          ftype['encoding'] = 'shift_jis'

        lines = lines.decode(ftype['encoding'])

        if ftype['encoding'].lower() == 'shift_jis':
          tip = self.tr(u'GOOD')
          result = True
        info = unicode(self.tr(u'%s, File Encoding : %s, Confidence : %2.0f%%')) % (tip, ftype['encoding'], ftype['confidence']*100)
      else:
        info = unicode(self.tr(u'%s, File Encoding : %s')) % (tip, u'UNKNOWN')

      fn = os.path.splitext(src)
      if not self.overwrite:
        dst = fn[0] + '_utf8' + fn[1]
      with codecs.open(dst, 'w') as f:
        f.write(codecs.BOM_UTF8)
        f.write(lines.encode('utf8'))

    return(result, info)

  def btnConvert(self):
    item = self.ui.lstItems.currentItem()
    if item:
      path = unicode(item.text())
      if os.path.isfile(path):
        self.ftext = path
        self.saveFile(self.ftext)
    pass

  def btnConvertAll(self):
    for idx in xrange(0, self.ui.lstItems.count()):
      item = self.ui.lstItems.item(idx)
      path = unicode(item.text())
      if os.path.isfile(path):
        self.ftext = path
        try:
          result = self.convertFile(path)
          item.setToolTip(result[1])
          item.setWhatsThis(result[1])
          item.setStatusTip(result[1])
          if result[0]:
            item.setBackgroundColor(QtGui.QColor(0, 250, 0, 64))
          else:
            item.setBackgroundColor(QtGui.QColor(200, 0, 0, 64))
        except:
          continue
    pass

  def btnClick(self, button):
    btnID = self.ui.buttonBox.standardButton(button)
    # print(hex(btnID))
    if   btnID == 0x00000400:  ## OK
      pass
    elif btnID == 0x00000800:  ## Save
      self.btnConvert()
      pass
    elif btnID == 0x00001000:  ## Save All
      self.btnConvertAll()
      pass
    elif btnID == 0x00200000:  ## Close
      pass
    elif btnID == 0x00800000:  ## Discard
      self.ui.lstItems.clear()
      pass
    elif btnID == 0x02000000:  ## Apply
      pass
    elif btnID == 0x04000000:  ## Reset
      self.ui.lstItems.clear()
      self.ui.edUTF8.clear()
      pass
    else:
      pass

    pass

  def chkOverwrite(self, checked):
    self.overwrite = checked
    pass

  def updateStatusbar(self, msg):
    if msg:
      txt = msg.statusTip()
      if txt:
        self.ui.statusbar.showMessage(txt)
    pass

if __name__ == "__main__":
  # Create Application
  app = QtGui.QApplication(sys.argv)

  # set app icon
  app_icon = QtGui.QIcon()
  app_icon.addFile('hana.png', QtCore.QSize(16,16))
  app_icon.addFile('hana.png', QtCore.QSize(24,24))
  app_icon.addFile('hana.png', QtCore.QSize(32,32))
  app_icon.addFile('hana.png', QtCore.QSize(48,48))
  app_icon.addFile('hana.png', QtCore.QSize(256,256))
  app.setWindowIcon(app_icon)

  # load zh_CN locale
  locale = QtCore.QLocale.system()

  translator_qt = QtCore.QTranslator()
  folder_qt = unicode(os.path.dirname(QtCore.__file__), enc)
  translator_qt.load(locale, 'qt', prefix='_', directory = os.path.join(folder_qt, 'translations'), suffix='.qm')
  app.installTranslator(translator_qt)

  filename_app = os.path.splitext(os.path.basename(SCRIPTNAME))[0]
  folder_app = os.path.join(CWD, 'i18n')
  translator_app = QtCore.QTranslator()
  translator_app.load(locale, filename_app, prefix='_', directory = folder_app, suffix='.qm')
  app.installTranslator(translator_app)

  # Create Application Window
  win = ConvertApp()

  # Run Application
  sys.exit(app.exec_())

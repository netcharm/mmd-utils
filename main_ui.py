# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

ID_OPEN = 1000
ID_SAVE = 1001
ID_GRIDPLANE = 1002
ID_SNAPSHOT = 1003

###########################################################################
## Class MainForm
###########################################################################

class MainForm ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"MMD Model Viewer"), pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.menuMain = wx.MenuBar( 0 )
		self.menuFile = wx.Menu()
		self.menuOpen = wx.MenuItem( self.menuFile, wx.ID_ANY, _(u"Open"), wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuOpen )
		
		self.menuFile.AppendSeparator()
		
		self.menuExit = wx.MenuItem( self.menuFile, wx.ID_ANY, _(u"Exit"), wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.AppendItem( self.menuExit )
		
		self.menuMain.Append( self.menuFile, _(u"File") ) 
		
		self.menuTool = wx.Menu()
		self.menuSnapshot = wx.MenuItem( self.menuTool, wx.ID_ANY, _(u"Snapshot"), wx.EmptyString, wx.ITEM_NORMAL )
		self.menuTool.AppendItem( self.menuSnapshot )
		
		self.menuResetCamera = wx.MenuItem( self.menuTool, wx.ID_ANY, _(u"Reset Camera"), wx.EmptyString, wx.ITEM_NORMAL )
		self.menuTool.AppendItem( self.menuResetCamera )
		
		self.menuTool.AppendSeparator()
		
		self.menuOptions = wx.MenuItem( self.menuTool, wx.ID_ANY, _(u"Options"), wx.EmptyString, wx.ITEM_NORMAL )
		self.menuTool.AppendItem( self.menuOptions )
		
		self.menuMain.Append( self.menuTool, _(u"Tools") ) 
		
		self.menuAbout = wx.Menu()
		self.menuMain.Append( self.menuAbout, _(u"About") ) 
		
		self.SetMenuBar( self.menuMain )
		
		self.toolbar = self.CreateToolBar( wx.TB_FLAT|wx.TB_HORIZONTAL, wx.ID_ANY )
		self.toolbar.SetToolBitmapSize( wx.Size( 24,24 ) )
		self.btnOpen = self.toolbar.AddLabelTool( ID_OPEN, _(u"Open"), wx.Bitmap( u"icons/import_mesh.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.btnSave = self.toolbar.AddLabelTool( ID_SAVE, _(u"Save"), wx.Bitmap( u"icons/save.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.toolbar.AddSeparator()
		
		self.btnResetCamera = self.toolbar.AddLabelTool( ID_GRIDPLANE, _(u"Reset Camera"), wx.Bitmap( u"icons/layers.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.btnSnapshot = self.toolbar.AddLabelTool( ID_SNAPSHOT, _(u"Snapshot"), wx.Bitmap( u"icons/snapshot.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, _(u"Screen Snapshot"), wx.EmptyString, None ) 
		
		self.toolbar.Realize() 
		
		self.statusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

###########################################################################
## Class MyFrame5
###########################################################################

class MyFrame5 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	


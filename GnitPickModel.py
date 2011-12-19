import java.awt
import java.awt.GridLayout as GridLayout
import java.awt.BorderLayout as BorderLayout

import javax.swing
import javax.swing.JFrame as JFrame
import javax.swing.JTabbedPane as JTabbedPane
import javax.swing.JLabel as JLabel
import javax.swing.JPanel as JPanel
import javax.swing.JButton as JButton
import javax.swing.JMenu as JMenu
import javax.swing.JMenuItem as JMenuItem
import javax.swing.JMenuBar as JMenuBar
import javax.swing.JFileChooser as JFileChooser
import javax.swing.JScrollPane as JScrollPane
import javax.swing.JList as JList
import javax.swing.DefaultListModel as DefaultListModel
import javax.swing.SwingConstants as SwingConstants
import java.awt.event.ActionListener as ActionListener
import java.io.File as File
import java.lang.String
import java.lang.Object
import sys
import re

from nu.xom import *
import nux.xom.xquery.XQuery as XQuery
import nux.xom.xquery.XQueryUtil as XQueryUtil
import org.w3c.dom.Document 

from GnitPickMenuBar import GnitPickMenuBar

class structure:   # a dummy class to act like a C struct
    pass

class ModelItemState(java.lang.Object):
    def __init__(self,hasunsaved=0,thefile=None,thesummary=None,thecontent=None):
        self.hasUnsavedChanges = hasunsaved
        self.file = thefile
        self.content = thecontent
        self.summary = thesummary
    def getFile(self):
        return self.file
    def toString(self):
        return java.lang.String(self.summary);

class ModelProjectState:
    def __init__(self,hasopenitems=0,thedir=None):
        self.hasOpenItems=hasopenitems
        self.directory = thedir
        self.items = {}   # hash of ModelItemState objects, by file name
        self.openItems = {} # hash of Files, by file name
    def getItems(self):
        return self.items
    def getOpenItems(self):
        return self.openItems.values()
    def addItem(self, theitem, thesummary, thecontent):
        self.items[theitem.getName()] =  ModelItemState(0,theitem,thesummary,thecontent)
    def setItemContent(self,theitem,thecontent):
        self.items[theitem.getName()].content = thecontent
    def openItem(self,theitem):
        self.openItems[theitem.getName()] = theitem
    def closeItem(self,theitem):
        del self.openItems[theitem.getName()]
        
class GnitModel:
    """GnitModel
       manage information for the GnitPick application
    """
    def __init__(self, controller):
        self.currentProject = None
        self.currentItem = None
        self.projects = {}   # ModelItemStates indexed by directory path
        self.controller = controller
        
    def openProject(self,hasopenitems=0, thedir=None):
        self.projects[ thedir.getPath() ] =  ModelProjectState( hasopenitems, thedir )
        self.currentProject = thedir
        
    def addItemToProject(self, theitem, thesummary, thecontent):
        self.projects[ self.currentProject.getPath() ].addItem( theitem, thesummary, thecontent)
        
    def getItemsOfProject(self, thedir):
        return self.projects[ thedir.getPath() ].getItems()
        
    def getOpenItemsOfProject(self,thedir):
        return self.projects[ thedir.getPath() ].getOpenItems()
        
    def closeProject(self, thedir):
        del self.projects[ thedir.getPath() ]
        self.currentProject = None
        self.currentItem = None
        
    def getItemContent( self, theproject, thefile ):
        return self.projects[ theproject.getPath() ].items[ thefile.name ].content
        
    def setItemContent( self, theproject, thefile, thecontent):
        self.projects[ theproject.getPath() ].items[ thefile.getName() ].content = thecontent
 
    def getCurrentProject( self ):
        return self.currentProject
        
    def getCurrentItem( self ):
        return self.currentItem
        
    def openItem(self,theproject,thefile):
        self.projects[ theproject.getPath() ].openItem(thefile)
        self.currentItem = thefile
        print "Debug: openItem(): "+thefile.getName()
        
    def closeItem(self,theproject,thefile):
        self.projects[ theproject.getPath() ].closeItem(thefile)
        self.currentItem = None
        print "Debug: closeItem(): " + thefile.getName()
        
    def isOpenItem( self, theproject, thefile):
        return self.projects[ theproject.getPath() ].openItems.has_key( thefile.name )
   # Stand-alone Unit Execution
if __name__ == "__main__":
    pass
    # gtf = GnitPick(File(sys.argv[0]))
    # gtf = GnitPick(File("/eclipse/workspace/Grazer/src/samples/stories"))
    
    
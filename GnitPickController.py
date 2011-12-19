import java.io.File as File
import java.io.FileReader as FileReader
import java.io.FileOutputStream as FileOutputStream
import java.io.OutputStreamWriter as OutputStreamWriter
import java.io.FileNotFoundException as FileNotFoundException
import java.io.IOException as IOException
import javax.swing.undo.CannotRedoException as CannotRedoException

import sys
import re
import os

from nu.xom import *
import nux.xom.xquery.XQuery as XQuery
import nux.xom.xquery.XQueryUtil as XQueryUtil
import org.w3c.dom.Document 

from GnitPickMenuBar import GnitPickMenuBar
from GnitPickView import GnitView
from GnitPickModel import GnitModel

from ndebug import ndebug
ndebug.debug=1

class GnitController:
    """GnitController
       direct tasks for the GnitPick application
    """
    def __init__(self,mdl=None,vw=None):
        self.model = ((mdl == None) and [GnitModel(self)] or [mdl])[0]
        self.view = ((vw == None) and [GnitView(self)] or [vw])[0]
        self.itempattern = ".*\.story$"
        
    def filefilter(self, thefile):
        return re.search(self.itempattern, thefile.getName())

       # Open a project from a directory
    def openProject(self, projectdir):   # File projectdir
            # Check to see that no other project is open at the moment
            # It would be interesting to allow multiple projects but this would complicate the view        
        if self.model.getCurrentProject() != None:
            self.view.status("Cannot but open one project at a time, bucko!")
            return None
        
        if projectdir == None: 
            return None
            
        self.view.status( "Processing directory "+projectdir.getName() )
        self.model.openProject( 0, projectdir)
           # Jython doesn't have listdir; use Java instead
        # for item in filter( lambda x: re.search(".*\.story",x), listdir( projectdir.getPath() ) ):
        myitems = filter( self.filefilter, projectdir.listFiles() )
        if len(myitems) > 0:
            for fileitem in myitems:
                inputfile=open(fileitem.getPath(),"r")
                unparsedcontent=inputfile.read()
                inputfile.close()
                try:
                    self.view.status("Examining file "+fileitem.getName() )
                    doc = Builder().build( fileitem )
                    summary = XQueryUtil.xquery(doc, "/story/@title").get(0).getValue()
                    content = doc.toXML()
                    self.model.addItemToProject( fileitem, summary, content )
                except XMLException, e:
                    ndebug(unparsedcontent)
                    self.view.status("Can't find an XML parser: "+e.toString() )
                    ndebug("Can't find an XML parser: "+e.toString() )
                    self.model.addItemToProject( fileitem, fileitem.getName() + " (Warning: not well-formed: ``"+e.toString()+"'')" , unparsedcontent )
                except ParsingException, e:
# Yawn! Jython can't seem to call FileReader successfully. It always returns empty content.
# Maybe something to do with wrapping the arguments. 
#                    myunparsedcontent=""
#                    filereader=FileReader( fileitem )
#                    filereader.read(myunparsedcontent)                    
                    ndebug(unparsedcontent)
                    self.view.status("The XML Parser reports errors on the file " + fileitem.getName() + ": "+e.toString() )
                    ndebug("The XML Parser reports errors on the file " + fileitem.getName() + ": "+e.toString() )
                    self.model.addItemToProject( fileitem, fileitem.getName() + " (Warning: parser errors: ``"+e.toString()+"'')" , unparsedcontent )
                    
#                   ndebug("My Junk:" + myjunk)
                    
                except IOException, e:
                    self.view.status("The file "+fileitem.getName()+" could not be opened: "+e.toString() )
                    ndebug("The file "+fileitem.getName()+" could not be opened: "+e.toString() )
                    self.model.addItemToProject( fileitem, fileitem.getName() + " (Error: file may be truncated ``"+e.toString()+"'')" , unparsedcontent )

        self.view.openProjectTab( projectdir, self.model.getItemsOfProject(projectdir) )
        self.view.status( "Opened project ''"+projectdir.getName()+"''" )
        self.view.gnitPickMenuBar.setMenuOff( "File_OpenProject" )
        self.view.gnitPickMenuBar.setMenuOn( "File_OpenItem" )
        self.view.gnitPickMenuBar.setMenuOff( "File_SaveItem" )
        self.view.gnitPickMenuBar.setMenuOff( "Tools_QueryDomain_All" )
        self.view.gnitPickMenuBar.setMenuOff( "Tools_QueryDomain_Current" )
        self.view.gnitPickMenuBar.setMenuOff( "Tools_Query" )        

    def closeProject(self):   # Always the project associated with the current tab 
        if self.model.getCurrentProject != None:
            self.view.closeProject( self.model.getCurrentProject() )
            self.model.closeProject( self.model.getCurrentProject() )
            self.view.gnitPickMenuBar.setMenuOn( "File_OpenProject" )
            self.view.gnitPickMenuBar.setMenuOff( "File_OpenItem" )
            self.view.gnitPickMenuBar.setMenuOff( "File_SaveItem" )
            self.view.gnitPickMenuBar.setMenuOff( "Tools_QueryDomain_All" )
            self.view.gnitPickMenuBar.setMenuOff( "Tools_QueryDomain_Current" )
            self.view.gnitPickMenuBar.setMenuOff( "Tools_Query" )            

            self.view.status("Closed Project")
        else:
            self.view.status("Ye canna close a project thah isn' open, lit'l one!")
   
       # Need a current project            
    def openSelectedItem(self):
        projectdir= self.model.getCurrentProject() 
        if projectdir == None:
            self.view.status("First open a project. Then select an item in the project tab and use File->Open->Item again.")
            return
        else:   # we have a current project... ask the view to open the current selection
            itemfile = self.view.getSelectedProjectItem()
            self.openItem(itemfile)
            
       # Need a current project            
    def openItem(self,itemfile):
        projectdir= self.model.getCurrentProject() 
        if projectdir == None:
            self.view.status("First open a project. Then select an item in the project tab and use File->Open->Item again.")
            return
        else:   # we have a current project... ask the view to open the current selection
            if self.model.isOpenItem( projectdir, itemfile ):
                self.view.status("Ummm.... you've already got that item opened!")
            else:
                itemcontent = self.model.getItemContent( projectdir, itemfile )
                self.view.openItemTab( projectdir, itemfile, itemcontent)
                self.model.openItem( projectdir, itemfile )
                # self.view.gnitPickMenuBar.setMenuOn( "File_SaveItem" )
                self.view.status("Opened item " + itemfile.name )
                
    def isAnOpenItem(self,itemfile):
        return self.view.tabbedPane.tabs.has_key(itemfile.getName())
        
    def notifyCurrentItem(self, itemfile):
        if itemfile == self.model.currentProject:
            ndebug("Current file now project " + itemfile.getName())
            self.view.gnitPickMenuBar.setMenuOff( "File_CloseItem" )
            self.view.gnitPickMenuBar.setMenuOff( "File_SaveItem" )
            self.view.gnitPickMenuBar.setMenuOff( "Edit_Undo" )
            self.view.gnitPickMenuBar.setMenuOff( "Edit_Redo" )    
            self.view.gnitPickMenuBar.setMenuOff( "Tools_QueryDomain_All" )
            self.view.gnitPickMenuBar.setMenuOff( "Tools_QueryDomain_Current" )
            self.view.gnitPickMenuBar.setMenuOff( "Tools_Query" )            
            self.model.currentItem = None
        elif itemfile != None:
            ndebug("Current file not project, not None " + itemfile.getName())
            self.view.gnitPickMenuBar.setMenuOn( "File_CloseItem" )
            self.view.gnitPickMenuBar.setMenuOn( "File_SaveItem" )
            self.view.gnitPickMenuBar.setMenuOn( "File_CloseProject" )
            self.view.gnitPickMenuBar.setMenuOn( "Tools_QueryDomain_All" )
            self.view.gnitPickMenuBar.setMenuOn( "Tools_QueryDomain_Current" )
            self.view.gnitPickMenuBar.setMenuOn( "Tools_Query" )            
            self.model.currentItem = itemfile
            
            if self.view.checkUndoable():
                self.view.gnitPickMenuBar.setMenuOn( "Edit_Undo" )                    
            else:
                self.view.gnitPickMenuBar.setMenuOff( "Edit_Undo" )
                                    
            if self.view.checkRedoable():
                self.view.gnitPickMenuBar.setMenuOn( "Edit_Redo" )                    
            else:
                self.view.gnitPickMenuBar.setMenuOff( "Edit_Redo" )      
        else:
            ndebug("Current file not project, must be None " + itemfile.getName())
            self.view.gnitPickMenuBar.setMenuOff( "File_SaveItem" )
            self.view.gnitPickMenuBar.setMenuOff( "File_CloseItem" )
            self.view.gnitPickMenuBar.setMenuOff( "File_CloseProject" )
            self.view.gnitPickMenuBar.setMenuOff( "Edit_Undo" )
            self.view.gnitPickMenuBar.setMenuOff( "Edit_Redo" )
            self.view.gnitPickMenuBar.setMenuOff( "Tools_QueryDomain_All" )
            self.view.gnitPickMenuBar.setMenuOff( "Tools_QueryDomain_Current" )
            self.view.gnitPickMenuBar.setMenuOff( "Tools_Query" )            
                
                        
        if self.view.tabbedPane.getTabCount() < 2:
           self.view.gnitPickMenuBar.setMenuOff( "View_NextTab")
           self.view.gnitPickMenuBar.setMenuOff( "View_PriorTab")
        else:
           self.view.gnitPickMenuBar.setMenuOn( "View_NextTab")
           self.view.gnitPickMenuBar.setMenuOn( "View_PriorTab") 
           
              
        
    def closeItem(self):
        projectdir = self.model.getCurrentProject()
        if projectdir == None: 
            self.view.status("No project is open. How is it you still have an open item???")
        else:
            itemfile = self.model.getCurrentItem()
            if itemfile == None:
                self.view.status("Close which item?")
            else:
                nm=itemfile.getName()
                self.view.closeItemTab(itemfile)
                self.model.closeItem( projectdir, itemfile )
                # Try to coerce Swing into invoking the change listener again... by flipping between whatever tabs are left.
                BAR = self.view.tabbedPane.getSelectedIndex()
                self.view.tabbedPane.setSelectedIndex( 0 )   # this is real monkey business
                self.view.tabbedPane.setSelectedIndex( BAR )
                self.view.status("Closed "+nm)
                
    def saveItem(self, projectdir, itemfile):
        content = self.model.getItemContent(projectdir,itemfile)
        storagepath = itemfile.getPath()
        print storagepath
        try:
            fos = FileOutputStream(storagepath)
            osw = OutputStreamWriter( fos )
            osw.write( content, 0, len(content) )
            osw.close()
            self.view.status(storagepath +" Saved")
        except FileNotFoundException, e:
            self.view.status(storagepath +" could not be opened for writing")
      
    def saveCurrentItem(self):
        projectdir = self.model.getCurrentProject()
        if projectdir == None: 
            self.view.status("How is it you want to save an item when you don't even have an open project?")
        else:
            itemfile = self.model.getCurrentItem()
            if itemfile == None:
                self.view.status("Save which item?")
            else:
                self.saveItem(projectdir, itemfile)
                
    def updateModelItem(self, itemfile, itemcontent):
        projectdir = self.model.getCurrentProject()
        if projectdir == None:
            self.view.status("Something is dreadfully wrong. My internal model is screwed up.")
            return
        self.model.setItemContent( projectdir, itemfile, itemcontent)
        print "Model stored for " + itemfile.getName()
        
    def saveProject(self):
       projectdir = self.model.getCurrentProject()
#       if projectdir == None:
#            self.view.status("How is it you want to save the project when you don't even have an open project?")
#            return
       for itemfile in self.model.getOpenItemsOfProject(projectdir):
           self.saveItem(projectdir, itemfile)
           
    def openNewProject(self, projectdir):
        try:
            os.mkdir(projectdir.getPath())
        except:
            pass
        self.openProject(projectdir)
        
    def openNewItem(self,itempath):
        itempath=self.normalizeItemFileName(itempath)
        # Construct a sane default instance of an item
        defaultcontent = self.defaultItemContent
        # Add the item to the current model
        # ... use xom to create a new document model object with default content
        # then open the new item from the model
        fileitem = File(itempath)
        unparsedcontent=defaultcontent
        
        try:
            self.view.status("Examining file "+fileitem.name )
            doc = Builder().build( unparsedcontent, "" )
            summary = XQueryUtil.xquery(doc, "/story/@title").get(0).getValue()
            content = doc.toXML()
            self.model.addItemToProject( fileitem, summary, content )
        except XMLException, e:
            ndebug(unparsedcontent)
            self.view.status("Can't find an XML parser: "+e.toString() )
            ndebug("Can't find an XML parser: "+e.toString() )
            self.model.addItemToProject( fileitem, fileitem.getName() + " (Warning: not well-formed: ``"+e.toString()+"'')" , unparsedcontent )
        except ParsingException, e:                   
            ndebug(unparsedcontent)
            self.view.status("The XML Parser reports errors on the file " + fileitem.getName() + ": "+e.toString() )
            ndebug("The XML Parser reports errors on the file " + fileitem.getName() + ": "+e.toString() )
            self.model.addItemToProject( fileitem, fileitem.getName() + " (Warning: parser errors: ``"+e.toString()+"'')" , unparsedcontent )
        
        self.openItem(fileitem)
        
        self.view.updateProjectTab(  self.model.getCurrentProject(), self.model.getItemsOfProject( self.model.getCurrentProject()) )
        self.view.status( "Opened project ''"+ self.model.getCurrentProject().getName()+"''" )

        
        # In order to undo or redo, the request needs to be associated with a tab (or other widget) that
        # implements its own undo management. Fortunately, this is always the current item tab (if set)
    def undo(self):
        projectdir = self.model.getCurrentProject()
        if projectdir == None: 
            self.view.status("What edit do you want to undo? No project item is currently opened.")
        else:
            itemfile = self.model.getCurrentItem()
            if itemfile == None:
                self.view.status("Undo what? No item is selected.")
            else:
                self.view.undo()
        
    def redo(self):
        projectdir = self.model.getCurrentProject()
        if projectdir == None: 
            self.view.status("What edit do you want to redo? No project item is currently opened.")
        else:
            itemfile = self.model.getCurrentItem()
            if itemfile == None:
                self.view.status("Redo what? No item is selected.")
            else:
                self.view.redo()
        
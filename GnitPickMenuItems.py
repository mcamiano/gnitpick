import re
import string

import java.lang.System
from javax.swing import *
from java.awt import *
import java.io.File as File

from nu.xom import *
import nux.xom.xquery.XQuery as XQuery
import nux.xom.xquery.XQueryUtil as XQueryUtil

from ndebug import ndebug
ndebug.debug=1

# GnitPickMenuItems
"""GnitPickMenuItems
   used for defining menu handlers
   meant to be inherited by GnitMenuBar
   each method takes a signature (ae) where ae is an java.awt.event.ActionEvent
   additional methods can be provided to maintain state and add behaviors
   
   Prior to execution, GnitPick attaches an attribute named "controller" to the module,
   so all menu functions can access the Gnit application's model, view, and controller
   like this:
       controller.view.status("Hello, I'm fine!")
       controller.model.getCurrentProject()
       controller.openProject(projectdir)
       
   Gnit also attaches a property "element" to each function, containing the XOM element
   corresponding to the menu item's <item> element, if any, in GnitPickMenu.xml; access 
   it like this:
       def File_Open():
          ...
          print File_Open.element.getAttribute("name")
   
   A Side Note on Accessing Function Properties
   When setting properties through the parser, as in
      File_Open.element = some_xom_elem
   You can refer to the property from within the function without qualification, as in
      def File_Open():
          ...
          print element.getAttribute("name")   
   That hasn't held true when setattr() is used. GnitPickMenuBar.py uses setattr() to
   set the "element" property on each of the GnitPickMenuItem.py functions. The two
   methods of setting a property result in different bindings, and require different
   syntax as a result. Sloppy, but true.
   
   The controller is also responsible for instantiating new items. 
   The default xml text for new items is set in this module by creating a function
   named defaultItemContent() that returns the new item content upon construction;
   it takes the file system path and an optional title as the first two arguments.
"""

        # File:Save
def File_SaveItem(ae):
   projectdir = controller.model.getCurrentProject()
   if projectdir == None:
        controller.view.status("How is it you want to save an item when you don't even have an open project?")
        return
   controller.saveCurrentItem()

def File_New_Project(ae):
    projectdir= controller.model.getCurrentProject()
    if projectdir != None:
        controller.view.status("Do me a favor and close the current project before creating a new one.")
        return None
    dirtocreate = controller.view.directoryDialog(File("."), {})
    controller.openNewProject(dirtocreate)
        
def File_New_Item(ae):
    if controller.model.getCurrentProject() == None:
        controller.view.status("Sorry: New items go in projects, but you don't have a project opened.")
        return
    filetocreate = controller.view.fileDialog( controller.model.getCurrentProject(), {"story": "User Stories"})
    controller.openNewItem(filetocreate)
    
def File_OpenProject(ae):
          # Set up one tab
    dirtoopen = controller.view.directoryDialog(File("."),{})   # Returns a File object which is a directory
    controller.openProject(dirtoopen)

def File_OpenItem(ae):
    controller.openSelectedItem()
    
def File_SaveProject_SaveAll(ae):
    projectdir = controller.model.getCurrentProject()
    if projectdir == None:
        controller.view.status("How is it you want to save an item when you don't even have an open project?")
        return
    controller.saveProject()
        
def File_CloseProject_CloseAll(ae):
    controller.closeProject()
        
def File_CloseItem(ae):
    controller.closeItem()

def File_Exit(ae):
    print "Application exiting!"
    java.lang.System.exit(0)

def Edit_Undo(ae):
    controller.undo()
    
def Edit_Redo(ae):
    controller.redo()
            
def Edit_Cut(ae):
    controller.view.cut(ae)
    
def Edit_Copy(ae):
    controller.view.copy(ae)
        
def Edit_Paste(ae):
    controller.view.paste(ae)

def View_Source(ae):
    controller.view.status( "Source View doesn't do anything yet." )
    
def View_Tags(ae):
    controller.view.status( "Tags View doesn't do anything yet." )
    

def View_NextTab(ae):
    controller.view.tabbedPane.setNextTab()       
    
def View_PriorTab(ae):
    controller.view.tabbedPane.setPriorTab()

def Help_Contents(ae):
    if Help_Contents.help == None:
        htmldoc = Help_Contents.element.getChildElements()
        ndebug( htmldoc.get(0).toXML() )
        Help_Contents.help = JFrame(title="GnitPick Help Contents")
        viewSize = controller.view.getSize()
        Help_Contents.help.setSize( java.lang.Float(viewSize.width*0.80).intValue(), java.lang.Float(viewSize.height*0.90).intValue() )
        Help_Contents.help.setLayout( BorderLayout() )
        textpane=JEditorPane( "text/html", htmldoc.get(0).toXML() )
        textpane.setEditable(0)
        scrollpane=JScrollPane(textpane)
        Help_Contents.help.getContentPane().add( scrollpane, BorderLayout.CENTER ) 
        Help_Contents.help.defaultCloseOperation=JFrame.HIDE_ON_CLOSE
        Help_Contents.help.setLocationRelativeTo(controller.view)
    Help_Contents.help.setVisible(1)

   # Set up the property so the != doesn't complain that the attribute doesn't exist
Help_Contents.help = None
    
from random import randint

def Help_Unhelpful(ae):
        # Load unhelpful messages once from the xml fragment 
    if Help_Unhelpful.messages == None:
        Help_Unhelpful.messages=[]
        unhelpful_elements = Help_Unhelpful.element.getChildElements()
    
        if unhelpful_elements == None:
            print "No unhelpful messages defined!"
        else:
            i=0
            while i < unhelpful_elements.size():
                elem=unhelpful_elements.get(i)
                print i
                Help_Unhelpful.messages.append( elem.getValue() )
                i=i+1
    
    r=randint(0,len(Help_Unhelpful.messages)-1)
    controller.view.status( Help_Unhelpful.messages[r] )
    
    # Set the property; Jython will throw an exception if you try to read it before it is assigned at runtime
    # I really like JavaScript's name resolution much better than Python's. JavaScript simply tells you the 
    # property is not defined and keeps on running. Sometimes Python just barfs when you try to check.
    # In general, Python's name resolution seems to have more inconsistency to it than JavaScript's. 
Help_Unhelpful.messages = None

def Help_About(ae):
    controller.view.status( "This is Gnit Pick" )
    textcontent = Help_About.element.getChildElements().get(0).getValue()
    title = Help_About.element.getChildElements().get(1).getValue()
    
    JOptionPane.showMessageDialog(None, textcontent, title, JOptionPane.INFORMATION_MESSAGE, ImageIcon("icon.gif") )
    

def Tools_Colorize(ae):
#    ndebug( controller.view.tabbedPane.tabs[controller.view.tabbedPane.getCurrentTab()].panel.textcomponent )
    try:
        txtarea = controller.view.tabbedPane.tabs[ controller.view.tabbedPane.getCurrentTab() ].panel.textcomponent
        c = (txtarea.doColorize == 0 and [1] or [0] )[0]
        txtarea.doColorize = c
        txtarea.colorize()
    except:  #  ignore exception... just skip the part that failed 
        pass
            
def Tools_Query(ae):
    if Tools_Query.queryarea == None:
        Tools_Query.queryarea = controller.view.addQueryArea()
    controller.view.hideQueryArea()
    
Tools_Query.queryarea = None


def Tools_QueryDomain_All(ae):
    ndebug("Invoked QueryDomain_All")
    controller.view.queryall=1
    
def Tools_QueryDomain_Current(ae):
    ndebug("Invoked QueryDomain_Current")
    controller.view.queryall=0

    
from javax.swing import *
from javax.swing.text import *
import re
    
class myJButton(JButton):
    def __init__(self,lbltext):
        JButton.__init__(self,lbltext)
        self.actionPerformed=self.clickhandler
        self.view = controller.view
    def clickhandler(self,ae):
        self.view.status("Element start tag selected!")
    
def Tools_Entag(ae):
    try:
            # Get the text pane's document
        textpane = controller.view.tabbedPane.tabs[controller.view.tabbedPane.currenttabid].panel.textcomponent
        
        doc = textpane.getDocument()
        caret = textpane.getCaret()
        caretposition = caret.getDot()
        
            # The component must first be wrapped in a style
        style = doc.addStyle("StyleName", None)
        StyleConstants.setFontFamily(style,"Century Gothic")
        elementbutton = myJButton("«story»")

        StyleConstants.setComponent(style, elementbutton)
        StyleConstants.setFontSize(style, 6);
        
        matches = re.match( r"^<([a-zA-Z][a-zA-Z0-9._-]*).*", doc.getText(caretposition,doc.getLength()-caretposition) )
        if matches != None:
            elementbutton.setText( "«"+ matches.group(1)+"»" )
                # Insert the component to the left of the text
            doc.insertString( caretposition, "text (ignored)", style )
         
    except BadLocationException, e:
        pass


# Attached to controller to let it compute default content for new items
# I don't understand why Python's binding doesn't pass a "self" object when this
# is invoked as a method of the controller, but it doesn't.
def defaultItemContent( itempath, itemname=None):
    print "Getting default content for "+itempath
    fn =string.split(itempath,".",1)[0]
    if itemname == None:
        defaultItemContent.numnewitems = defaultItemContent.numnewitems + 1
        itemtitle = "%s%d" % (fn, defaultItemContent.numnewitems )
        itemid="%s%d" % (fn, defaultItemContent.numnewitems )
    c= """<?xml version="1.0" ?>
<story id="%s" title="%s" >
   <text>Description-Of-Story</text>

   <history timestamp="MM-DD-YYYY HH:MM EST">Authored by (Initials)</history>

   <task>Do something.</task>
   <task>Do something else.</task>
</story>
    """ % ( itemid, itemtitle )
   
    return c
defaultItemContent.numnewitems = 0;

# Attached to controller to let it compute file name suffix
def normalizeItemFileName( str ):
   if not re.match(r"^.*\.story$", str):
      if str == "":
          str = "unnamed"
      str=str+".story"
   return str


    
   # Stand-alone Unit Execution
if __name__ == "__main__":
#    def testit(x):
#        return not re.search("__.*__",x) 
#        
#    mylist=dir()
    print filter( lambda x: not re.search("__.*__|^re$",x), dir() )
               

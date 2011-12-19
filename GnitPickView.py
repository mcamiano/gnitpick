from java.awt import *
from javax.swing import *

#import java.awt
#import java.awt.GridLayout as GridLayout
#import java.awt.BorderLayout as BorderLayout
#import java.awt.Dimension as Dimension
#import java.awt.event.FocusAdapter as FocusAdapter
#import java.awt.event.MouseAdapter as MouseAdapter
#import java.awt.event.ActionListener as ActionListener
#import java.awt.Toolkit as Toolkit
#import java.awt.Color as Color
#
#import javax.swing.*
#import javax.swing.Action as Action
#import javax.swing.JFrame as JFrame
#import javax.swing.JTabbedPane as JTabbedPane
#import javax.swing.JTextPane as JTextPane
#import javax.swing.JLabel as JLabel
#import javax.swing.JPanel as JPanel
#import javax.swing.JButton as JButton
#import javax.swing.JMenu as JMenu
#import javax.swing.JMenuItem as JMenuItem
#import javax.swing.JMenuBar as JMenuBar
#import javax.swing.JFileChooser as JFileChooser
#import javax.swing.JScrollPane as JScrollPane
#import javax.swing.JList as JList
#import javax.swing.ImageIcon as ImageIcon
#import javax.swing.BorderFactory as BorderFactory
#import javax.swing.DefaultListModel as DefaultListModel
#import javax.swing.SwingConstants as SwingConstants
#import javax.swing.text.StyleContext as StyleContext
#import javax.swing.text.StyleConstants as StyleConstants
#import javax.swing.event.ChangeListener as ChangeListener
#import javax.swing.AbstractAction as AbstractAction
#import javax.swing.SwingUtilities as SwingUtilities
#import javax.swing.filechooser.FileFilter as FileFilter
#import javax.swing.undo.CannotRedoException as CannotRedoException
#import javax.swing.undo.CannotUndoException as CannotUndoException

from java.awt.event import *
from javax.swing.undo import *
from javax.swing.event import *
from javax.swing.text import *
from javax.swing.filechooser import *

import java.io.File as File
import java.io.FileInputStream as FileInputStream
import java.lang.Float
import java.lang.Integer

import sys
import re
from math import floor

from nu.xom import *
import nux.xom.xquery.XQuery as XQuery
import nux.xom.xquery.XQueryUtil as XQueryUtil
import org.w3c.dom.Document 

from GnitPickMenuBar import GnitPickMenuBar
from GnitPickModel import structure

import LineHighlightPainter  

from ndebug import ndebug
ndebug.debug=1

# GnitFileFilter is used to pick from one or more types of files
class GnitFileFilter(FileFilter):
    def __init__(self,filterext,filterdesc):
        FileFilter.__init__(self)
        self.ext = filterext
        self.desc = filterdesc
    def accept(self,f):   # File f
        if re.match( ".*\."+self.ext+"$", f.getName() ) != None:
            return 1
        return f.isDirectory()
    def getDescription(self):
        return self.desc

# GnitJScrollPane is used to articulate an immutable identifier and useful file info that the tabbed component can't manage directly
# If another type of container is needed for the tab, it should use the same interface
class GnitJScrollPane(JScrollPane):
    def __init__(self,obj,tabid,projitemfile):
        JScrollPane.__init__(self,obj)
        self.tabid=tabid
        self.file=projitemfile
#    def setTabid(self,tabid):
#        self.tabid = tabid
#    def setFile(self,myfile):
#        self.file = myfile
    def getFile(self):
        return self.file
    def getTabid(self):
        return self.tabid
        
class GnitJList(JList):
    def __init__(self):
        JList.__init__(self)
    def setTabid(self,tabid):
        self.tabid = tabid
    def setFile(self,myfile):
        self.file = myfile
    def getFile(self):
        return self.file
    def getTabid(self):
        return self.tabid
class GnitJTextPane(JTextPane,DocumentListener,java.lang.Runnable):
    def __init__(self,tabid,itemfile,focuslistener,itemcontent):
        JTextPane.__init__(self)
        self.getDocument().addDocumentListener(self)
        self.doColorize=0
        
            # Some app-specific stuff
        self.tabid = tabid
        self.file = itemfile
        
            # Set up the focus listener; we use this to force the GUI to be context-sensitive
        self.addFocusListener(focuslistener)
        
            # Set up highlight appearance
        self.setCaret( LineHighlightPainter.LHCaret() )

            # Set up style and content
        textpanedoc=self.getStyledDocument()
        styledef = StyleContext.getDefaultStyleContext().getStyle(StyleContext.DEFAULT_STYLE)
           # A default style
        regularstyle = textpanedoc.addStyle("regularstyle", styledef)
        StyleConstants.setFontFamily(regularstyle, "Serif")
           # A style to use for start-tags, attributes, marked sections, entity references, and end-tags
        markupstyle = textpanedoc.addStyle("markupstyle", styledef)
        StyleConstants.setFontFamily(markupstyle, "CenturyGothic")
        StyleConstants.setBold(markupstyle,1)
        StyleConstants.setFontSize(markupstyle,  StyleConstants.getFontSize(regularstyle) + 2 )
        StyleConstants.setForeground(markupstyle, Color.blue )

        badmarkupstyle = textpanedoc.addStyle("badmarkupstyle", markupstyle)
        StyleConstants.setItalic(badmarkupstyle,1)
        StyleConstants.setForeground(badmarkupstyle, Color.red )
        
        textpanedoc.insertString( textpanedoc.getLength(),  itemcontent , textpanedoc.getStyle("regularstyle") )
        
        self.run()

            # Set up Undo/Redo management
        self.undomanager = UndoManager()
        self.undomanager.setLimit(500)
        textpanedoc.addUndoableEditListener( GnitUndoableEditListener(self.undomanager) )
        
        actionmap = {}    # convert array to hash for easier lookup
        actionsArray = self.getActions()
        i=0
        while i < len(actionsArray):
            a = actionsArray[i]
            actionmap[a.getValue(Action.NAME)]= a
            i=i+1
           # Set up text styles
                   
        self.cutaction = actionmap[DefaultEditorKit.cutAction]
        self.copyaction = actionmap[DefaultEditorKit.copyAction]
        self.pasteaction = actionmap[DefaultEditorKit.pasteAction]

#    def setTabid(self,tabid):
#        self.tabid = tabid
#    def setFile(self,myfile):
#        self.file = myfile
    def changedUpdate(self,docevent):
        pass
    def insertUpdate(self,docevent):
        SwingUtilities.invokeLater(self)
    def removeUpdate(self,docevent):
        SwingUtilities.invokeLater(self)
    def run(self):
        self.colorize()
        
    def colorize(self):
        
        textpanedoc=self.getStyledDocument()

        textcontent = textpanedoc.getText( 0, textpanedoc.getLength() )
        textpanedoc.setCharacterAttributes(0, textpanedoc.getLength(), textpanedoc.getStyle("regularstyle"), 1)

        if self.doColorize == 1:
            loc=0
            context=[]
            goodstyle=textpanedoc.getStyle("markupstyle")
            badstyle=textpanedoc.getStyle("badmarkupstyle")
            nextstyle=goodstyle
            while loc < len(textcontent):
                ch = textcontent[loc]
                if ch == '<':
                    if len(context) == 0:
                        context.append(loc)
                        nextstyle=goodstyle
                    else:
                        nextstyle=badstyle
                if ch == '>':
                    if len(context) > 0:
                        lastloc = context.pop()
                        textpanedoc.setCharacterAttributes(lastloc, loc-lastloc+1, nextstyle, 1)
                        if len(context) == 0:
                            nextstyle=goodstyle
                    else:
                        nextstyle=badstyle
                loc=loc+1

    def replaceSelection(self,content):
        self.setCharacterAttributes( self.getStyledDocument().getStyle("regularstyle"), 1 )
        JTextPane.replaceSelection(self,content)
        
        
    def getFile(self):
        return self.file
    def getTabid(self):
        return self.tabid
#    def setTextEffects(self):
#        self.texteffects = GnitTextEffects( self ) 
    def undoaction(self):
        self.undomanager.undo()
    def redoaction(self):
        self.undomanager.redo()  
              
class GnitQueryPane(JTextPane):
    def __init__(self):
        JTextPane.__init__(self)
                
            # Set up highlight appearance
        self.setCaret( LineHighlightPainter.LHCaret() )

            # Set up style and content
        textpanedoc=self.getStyledDocument()
        styledef = StyleContext.getDefaultStyleContext().getStyle(StyleContext.DEFAULT_STYLE)
        regular = textpanedoc.addStyle("regular", styledef)
        StyleConstants.setFontFamily(styledef, "SansSerif")
        
            # Set up Undo/Redo management
        self.undomanager = UndoManager()
        self.undomanager.setLimit(500)
        textpanedoc.addUndoableEditListener( GnitUndoableEditListener(self.undomanager) )
        textpanedoc.insertString( textpanedoc.getLength(),  "" , textpanedoc.getStyle("regular") )

        actionmap = {}    # convert array to hash for easier lookup
        actionsArray = self.getActions()
        i=0
        while i < len(actionsArray):
            a = actionsArray[i]
            actionmap[a.getValue(Action.NAME)]= a
            i=i+1
                   
        self.cutaction = actionmap[DefaultEditorKit.cutAction]
        self.copyaction = actionmap[DefaultEditorKit.copyAction]
        self.pasteaction = actionmap[DefaultEditorKit.pasteAction]
    def undoaction(self):
        self.undomanager.undo()
    def redoaction(self):
        self.undomanager.redo()
        
class GnitListMouseListener(MouseAdapter):
    def __init__(self,gnitview):
        MouseAdapter.__init__(self)
        self.view = gnitview
    def mouseClicked(self,e):   # MouseEvent e
       self.view.status("  ")    # Clear the status on every click
       index = self.view.projectJList.locationToIndex(e.getPoint())
       tabid = self.view.getSelectedProjectItem().getName()
       if e.getClickCount() == 2:           
           ndebug("Double clicked on Item " +  java.lang.Integer(index).toString() + ":"+ tabid )
           if self.view.controller.isAnOpenItem(self.view.getSelectedProjectItem()):
               self.view.tabbedPane.setCurrentTab( tabid )
               self.view.status(tabid + " Active")
           else:
               self.view.controller.openSelectedItem()
       else:
           ndebug("Selected Item " + java.lang.Integer(index).toString() + ":"+ tabid )
           ndebug( tabid
              + " is " 
              + ( self.view.controller.isAnOpenItem( self.view.getSelectedProjectItem() ) and "opened" or "unopened"))
       
         
   # The purpose of this listener is to track the tabs and let us get to the file corresponding to the tab
   # It doesn't work straightforwardly: the keyboard focus is not given to a tab, only to some focussable component which 
   # happens to reside under the container passed to tabbedPane.add(). 
   # Also, the component is NOT given the focus just because its tab is selected.
   # Further, the component for which focusGained is invoked is not always the component for which focusLost() is subsequently 
   # called.
   # Here is the focus triggering sequene in the projects/items tabs setup:
       # app starts: focusListener.__init__ is called at construction
       # project opened through script: focus is NOT triggered even after requestFocus() (or its ilk); changeListener invoked on tabbedPane
       # mouse clicks on a project item: 
       #   focusGained() invoked w/ Opposite=GnitJScrolledPane tab (the container added as the project tab), 
       #      and Component=JList (the component added *inside of* the GnitJScrolledPane used as the tab)
       #   no focusLost() is invoked
       # mouse double clicks the item: 
       #   focusListener.__init__ called for new tab
       #   changeListener invoked on tabbedPane
       #   focusLost() invoked w/ Opposite=tabbedPane, Component=JList
       #   focusGained() invoked w/ Opposite=tabbedPane, Component=JTextPane (the component added *inside of* the item's GnitJScrolledPane)
       #   changeListener invoked on tabbedPane (again)
       # mouse clicks on the project tab (defocussing the item):
       #   focusList() opposite=tabbedPane, component=JTextPane
       #   focusGained() opposite=tabbedPane, component=JList
   # Based on that, it appears that even when a listener is placed on a JList or JTextPane 
   # the "opposite" is always set to be the higher level tabbed pane rather than the scrollpane or JList/JTextPane component.
   # In order to transfer the tabid, we have to attach a property to the JList or JTextPane
   # The way to do that is to subclass - that's the reason for the GnitJList and GnitJTextPane classes
class GnitTabFocusListener(FocusAdapter):
    def __init__(self,gnitview):
        FocusAdapter.__init__(self)
        self.view=gnitview
        ndebug("Debug: FocusListener.__init__()")
    def focusGained(self,e):
        ndebug("Debug: FocusLister.focusGained()")
        # The listener is apparently called BEFORE the focus is gained, not after.
        # so the following return can return nulls at various times
        o = e.getOppositeComponent()
        if ( o != None ):
           ndebug( "FocusGained: Opposite="+ o.toString() )
        c = e.getOppositeComponent()
        if ( c != None ):
           ndebug( "FocusGained: Component="+ c.toString()  )

    def focusLost(self,e):
        ndebug("Debug: FocusListener.focusLost()")
        # The listener is called AFTER the focus is lost, not before. 
        # Apparently, both of these return nulls at various times...
        # ndebug( "Opposite="+ e.getOppositeComponent().toString() )
        # ndebug( "Component="+ e.getComponent().getTabid() )
        o = e.getOppositeComponent()
        try:
           ndebug( "FocusLost: Opposite Component="+ o.toString()  )
        except:
           pass
        c = e.getComponent()
        try:
            ndebug( "FocusLost: Component="+ o.toString() )
        except:
            pass
           
   # This is like the other tab focus listener, but tells the controller to save the item content to the model
class GnitItemTabFocusListener(FocusAdapter):
    def __init__(self,gnitview):
        FocusAdapter.__init__(self)
        self.view=gnitview
        ndebug("Debug: FocusListener.__init__()")
        
    def focusGained(self,e):
        pass   # We don't care too much about losing focus. Huh? 
        
    def focusLost(self,e):
        textpane=e.getComponent()
        if (textpane != None):
            if e.getOppositeComponent() != None:
                ndebug( "Opposite="+ e.getOppositeComponent().toString() )
            else:
                ndebug( "Opposite Component is null" )
            if e.getComponent() != None:
                ndebug( "Component="+ e.getComponent().toString() )
            else:
                ndebug( "Component is null" )
            doc=textpane.getDocument()
            if (doc != None):
                self.view.controller.updateModelItem(textpane.getFile(), doc.getText(0, doc.getLength())  )
    
   # Stupid Swing fires the events at ill-defined points. 
   # One would think that you could capture the event both before and after a change, but Swing apparently fires it only once prior to a change.
   # So there is no way using this idiom to figure out what tab is capturing the focus after the change. 
   # Use a focusListener instead, and attach properties to the components that get the actual focus
class GnitTabChangeListener(ChangeListener):
    def __init__(self,gnitview):
        self.view = gnitview
        ndebug("Debug: ChangeListener.__init")
    def stateChanged(self,e):
        self.view.status("  ")  # Clear the status when tabs switch
        tabcomponent = self.view.tabbedPane.getSelectedComponent()
        if tabcomponent == None:
            return
        if tabcomponent.tabid != None:
            ndebug("Debug: ChangeListener.stateChanged("+e.toString()+")")
            ndebug("Tab selected: " + java.lang.Integer(self.view.tabbedPane.getSelectedIndex()).toString() )
            ndebug("Structure: "+ self.view.tabbedPane.tabs[ tabcomponent.getTabid()  ].label)
            self.view.tabbedPane.currenttabid = tabcomponent.getTabid()
            self.view.controller.notifyCurrentItem( tabcomponent.getFile() )
            
class GnitUndoableEditListener( UndoableEditListener ):
    def __init__(self,umgr):
        self.undomanager = umgr
#        self.undoAction =  UndoAction(self.undomanager)
#        self.redoAction =  RedoAction(self.undomanager)
#        self.undoAction.setRedoAction(self.redoAction)
#        self.redoAction.setUndoAction(self.undoAction)
    def undoableEditHappened(self,e):   # UndoableEditEvent  e
        self.undomanager.addEdit(e.getEdit())
#        self.undoAction.updateUndoState()
#        self.redoAction.updateRedoState()
        
        
class GnitTabbedPaneWithContext(JTabbedPane):
    """GnitTabbedPaneWithContext
       Manage tabbed interface tabs with tab identities independant of the tab sequence number
       The standard Swing JTabbedPane assigns the index number to each tab based on it's coincidental position 
       within some kind of array like structure: the index for a tab can change at any time when a tab is inserted or deleted. 
       JTabbedPane doesn't directly provide a method of incorporating an immutable id, so it isn't directly suitable for 
       editing objects referenced elsewhere in the application.
       This first cut may be rough, but IMHO the use of an index number is just plain stupid.
       The solution is in two parts. First, the GnitTabbedPaneWithContext class adds an tabid to the JTabbedPane.
       Second, each component to be added to the tabbed pane is extended using a subclass that adds a tabid attribute.
       When a listener is invoked, it can query the component for the tabid, and look up additional properties in the tabbed pane.
    """
    def __init__(self):
        JTabbedPane.__init__(self)
           # Rather than identify tabs by an index number (which changes), we use the file name (for items) or path (for projects)
        self.tabs={}   # dictionary of tab objects keyed by tab id
        self.currenttabid=None   # no tab is active at the start
        
    def setCurrentTab( self, tabid ): # make a tab the "current" tab
        if self.tabs.has_key(tabid):
            self.currenttabid = tabid
               # alter the current tab
            self.setSelectedIndex( self.getTabIndex(tabid) )
               # but wait... not enough... change the focus too
               # For some reason this doesn't work uniformly; the initial project pane, when opened, doesn't fire the focus listener
            self.tabs[tabid].panel.requestFocus()
   
    def getCurrentTab( self ):
        return self.currenttabid
        
    def setNextTab( self ):   # make the "next" tab the "current" tab
       countoftabs = self.getTabCount()
       nexttabidx = self.getSelectedIndex() + 1
       if nexttabidx >= countoftabs:
           nexttabidx = 0
       tabcomponent = self.getComponentAt(nexttabidx)
       self.setCurrentTab(tabcomponent.tabid)

    def setPriorTab( self ):   # make the "previous" tab the "current" tab
       countoftabs = self.getTabCount()
       priortabidx = self.getSelectedIndex() - 1
       if priortabidx < 0:
           priortabidx = countoftabs - 1
       tabcomponent = self.getComponentAt(priortabidx)
       self.setCurrentTab(tabcomponent.tabid)
       
    def reset(self):
        self.tabs={}
        self.currenttabid=None
        self.removeAll()
        
    def closeTab( self, tabid ): # Remove a tab
        if self.tabs.has_key(tabid):
            self.removeTabAt( self.getTabIndex( tabid )   )
            del self.tabs[tabid]

    def openTab( self, tabid, tablabel, tabtip, thefile, tabcomponent ):  # add a tab
        if self.tabs.has_key(tabid):
            print >>sys.stderr, "Error: attempted to add tab with duplicate id"
            return None
        else:
            self.tabs[tabid] = structure()
            self.tabs[tabid].label = tablabel
            if tabcomponent == None:
               tabcomponent = JPanel()
            
            self.tabs[tabid].panel = tabcomponent

#            self.tabs[tabid].file = thefile   # File for project path or item name
            self.addTab( tablabel, None, self.tabs[tabid].panel, tabtip )   # No icon
            self.setCurrentTab(tabid)
            ndebug("Debug: Tabid="+tabid + ", #="  +  java.lang.Integer(self.getTabIndex( tabid )).toString())

            return self.tabs[tabid].panel
            
    def getTabIndex(self, tabid):
        # return self.indexOfTab( tabid )
        return self.indexOfComponent( self.tabs[tabid].panel )

    def getTabFile(self,tabid):
        # return self.tabs[tabid].file
        return self.getSelectedComponent().getFile()
        
    def undo(self):
        self.tabs[self.currenttabid].panel.textcomponent.undoaction()
##        print dir(self.getSelectedComponent().getComponent(0))

    def redo(self):
        self.tabs[self.currenttabid].panel.textcomponent.redoaction()
        
class GnitView(JFrame):
    """GnitView
       Organize GUI resources for the GnitPick application
    """
    def __init__(self,controller,iconimg="icon.gif"):
        JFrame.__init__(self,"GnitPick")  # Invoke superclass constructor1
        icon = ImageIcon( iconimg )
        self.setIconImage( icon.getImage() )
        self.queryisvisible=0
        self.queryall=0
        self.openitems={}
        
        self.note="GnitPick Punchlist Editor"               
        self.controller = controller
        
           # Set up the menu bar
        self.gnitPickMenuBar = GnitPickMenuBar(self.controller)  # Reads the layout from xml, command definitions in GnitPickMenuItems.py
        self.setJMenuBar(self.gnitPickMenuBar)   # tell JFrame to put a menu bar up
        
        
        self.getContentPane().setLayout( BorderLayout() )   # a simple layout manager for the tabs and status bar


           # Set up the tabbed interface
        self.tabbedPane = GnitTabbedPaneWithContext();   # Handle details of tabs
        self.tabbedPane.setTabPlacement(JTabbedPane.LEFT)
           # much less interesting than a focus listener, since there is no state local to individual tabs
        self.tabbedPane.addChangeListener( GnitTabChangeListener(self) )


            # Split the pane
        self.splitpane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
        self.splitpane.setOneTouchExpandable(1)
        self.splitpane.setContinuousLayout(1)

        self.splitpane.setLeftComponent(self.tabbedPane)

        self.getContentPane().add( self.splitpane, BorderLayout.CENTER )   # put the tabs in the middle

        self.statusbar = JLabel(" ")             # put up a status bar too
        self.getContentPane().add( self.statusbar, BorderLayout.SOUTH )  # put the status bar on the bottom

            # Setting the size of the window relative to the screen metrics
        screenSize = Toolkit.getDefaultToolkit().getScreenSize()
        self.setSize( java.lang.Float(screenSize.width*0.45).intValue(), java.lang.Float(screenSize.height*0.75).intValue() )
        self.validate()   # Tell container to make sure size is adequate

           # Make it all visible
        # fself.setSize( 600, 800 )
        self.setLocationRelativeTo(None)
        self.setDefaultCloseOperation( JFrame.EXIT_ON_CLOSE )
        self.setVisible( 1 )
        
    def addQueryArea(self):
        self.queryPane = GnitQueryPane() 
        frameSize=self.getSize()
        self.queryPane.setSize(  java.lang.Float(frameSize.width*.30).intValue(),  java.lang.Float(frameSize.height*0.4).intValue() )

        label = JButton(" XQuery: ", actionPerformed=self.doRunQuery)
        self.querypanel = JPanel( BorderLayout())
        self.querypanel.add( label, BorderLayout.WEST )
        self.querypanel.add( JScrollPane(self.queryPane), BorderLayout.CENTER )

        self.getContentPane().add( self.querypanel, BorderLayout.NORTH )   # put the query area on the left


        self.outputPane = GnitQueryPane() 
        frameSize=self.getSize()
        outlabel = JLabel(" XQuery Output ")

        self.outpanel = JPanel( BorderLayout())
        self.outpanel.add( outlabel, BorderLayout.PAGE_START )
        self.outpanel.add( JScrollPane(self.outputPane), BorderLayout.CENTER )

        self.outpanel.setPreferredSize(  Dimension(java.lang.Float(frameSize.width*.3).intValue(),  java.lang.Float(frameSize.height*1.0).intValue()) )

#        self.getContentPane().add( self.outpanel, BorderLayout.EAST )   # put the query area on the left
        self.splitpane.setRightComponent(self.outpanel)
               
        self.validate()
        return self.queryPane
        
    def doRunQuery(self,e):
        qdoc = self.queryPane.getStyledDocument()        
        query = qdoc.getText( 0, qdoc.getLength() )
        ndebug(query)
        if self.queryall == 0:            
            itemcontent = self.getSelectedTabContent()
            queryresult = self.apply_XQuery(query,itemcontent)
            odoc = self.outputPane.getStyledDocument()
            odoc.insertString( odoc.getLength(),  queryresult , odoc.getStyle("regularstyle") )
        else: # iterate over all the item tabs
            odoc = self.outputPane.getStyledDocument()
            for tabid in self.openitems.keys():
                itemdoc = self.openitems[tabid].getDocument()
                itemcontent =itemdoc.getText(0,itemdoc.getLength())
                ndebug(itemcontent)
                queryresult = self.apply_XQuery(query,itemcontent)
                odoc.insertString( odoc.getLength(),  queryresult , odoc.getStyle("regularstyle") )
            
    def apply_XQuery(self,qry,content,validate=0):
        try:
           parser = Builder( validate )
           self.doc = parser.build(content,"./")
        except ValidityException, ex:
           print >>sys.stderr, "Validity Exception - non-conforming structure"
           self.doc = ex.getDocument()
           i=ex.getErrorCount()
           j=1
           while j < i:
              print getValidityError(j)
              j=j+1
        except ParsingException, ex:
           return "<!-- Parsing Exception - malformed markup -->"
        except IOException, ex:
           return "<!-- IO Exception - Couldn't get input -->"
        except ex:
           return "<!-- Other Exception during query: " + ex.toString() + " -->"
        i=0
        resultset = XQueryUtil.xquery(self.doc,qry)
        if resultset == None:
            return "<!-- No matches found! -->"
        i=0
        myresultxml=[]
        while i < resultset.size():
            elem=resultset.get(i)
            myresultxml.append( elem.toXML() )
            i=i+1
        return "\n".join(myresultxml)
        
    def hideQueryArea(self):
        if self.queryisvisible==0:
            self.queryisvisible = 1
        else:
            self.queryisvisible = 0
            
        self.querypanel.setVisible(self.queryisvisible)
        self.outpanel.setVisible(self.queryisvisible)
        self.validate()
        
    def status(self,msg):
        self.statusbar.setText(" "+msg)

    def fileDialog(self,currdir=File("."),exts={"story": "User Stories"}):
        self.chooser = JFileChooser()
        
        self.chooser.setCurrentDirectory(currdir)
        
        for filterext in exts.keys():
            newfilter = GnitFileFilter(filterext,exts[filterext])
            self.chooser.setFileFilter(newfilter)
            
        self.option = self.chooser.showOpenDialog(self)
          
        if (self.option == JFileChooser.APPROVE_OPTION):
          self.statusbar.setText("Selected file '" + self.chooser.getSelectedFile().getName() + "'")
          return self.chooser.getSelectedFile().getName()
        else:
          self.status("The file selection was cancelled.")
          return None
    
    def directoryDialog(self,currdir=File("."),exts={}):
        self.chooser = JFileChooser()

        self.chooser.setCurrentDirectory(currdir)
                
        for filterext in exts.keys():
            newfilter = GnitFileFilter(filterext,exts[filterext])
            self.chooser.addFileFilter(newfilter)
            
        self.chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)
        self.option = self.chooser.showOpenDialog(self)
          
        if (self.option == JFileChooser.APPROVE_OPTION):
          self.statusbar.setText("Selected file '" + self.chooser.getSelectedFile().getName() + "'")
          return self.chooser.getSelectedFile()
        else:
          self.status("The selection dialog was cancelled.")
          return None
        
    def openProjectTab(self, projectdir, projectItems ):   # ModelItemState projectItems{}, key=filename
        tabid=projectdir.getPath()

        projectlist = DefaultListModel()
        self.projectJList=GnitJList()
        self.projectJList.setFile(projectdir)
        self.projectJList.setTabid(tabid)
        self.myprojectscrollpane = GnitJScrollPane(self.projectJList,tabid,projectdir)
        for filename in projectItems.keys():
            projectlist.addElement( projectItems[filename] )
        self.projectJList.setModel(projectlist)
        
        self.projectJList.addMouseListener( GnitListMouseListener(self) )

        self.projectJList.addFocusListener( GnitTabFocusListener(self) )
        
        self.tabbedPane.openTab( tabid, projectdir.getName()+"/", projectdir.getName(), projectdir, self.myprojectscrollpane )

       # Update the list model only
    def updateProjectTab(self, projectdir, projectItems ):   # ModelItemState projectItems{}, key=filename
        tabid=projectdir.getPath()

        projectlist = DefaultListModel()
        
        for filename in projectItems.keys():
            projectlist.addElement( projectItems[filename] )
            print "Added " + filename + " to project pane. with title=" + projectItems[filename].summary
            
        self.projectJList.setModel(projectlist)
           
    def getSelectedProjectItem(self):   # For a tab containing a project JList
        return self.projectJList.getSelectedValue().getFile() 
    
    def getSelectedTabFile(self): # for a tab containing an item textPane
        return self.tabbedPane.getSelectedComponent().getFile()

    def getSelectedTabContent(self): # for a tab containing an item textPane
        doc = self.tabbedPane.tabs[ self.tabbedPane.getCurrentTab() ].panel.textcomponent.getDocument()
        return doc.getText(0,doc.getLength())
         
    def closeProjectTab(self,projectdir):
        tabid = projectdir.getPath()
        self.tabbedPane.closeTab( tabid )

    def closeProject(self, projectdir):
        self.tabbedPane.reset()
        self.openitems = {}
        
    def openItemTab(self, projectdir, itemfile, itemcontent ):
        tabid=itemfile.getName()

        try:
            dot = tabid.rindex(".")
            tablabel=tabid[0:dot]
        except:
            tablabel=tabid
        
        myTextPane = GnitJTextPane(tabid,itemfile, GnitItemTabFocusListener(self), itemcontent )   # Create a text pane

        myoutputarea=GnitJScrollPane(myTextPane,tabid,itemfile)
        myoutputarea.textcomponent = myTextPane   # bypass Swing, which can be painful to find contained components 
        mysize=self.getSize()
        mysize.height=java.lang.Float(mysize.height*.8).intValue()
        mysize.width=java.lang.Float(mysize.width*.9).intValue()
        myoutputarea.setPreferredSize( mysize )
        myoutputarea.setMinimumSize( Dimension(10, 10) )

        mytabpanel = self.tabbedPane.openTab( tabid, tablabel, itemfile.getName(), itemfile, myoutputarea )
   
        if mytabpanel != None:
            self.openitems[tabid] = myoutputarea.textcomponent
                 
#        mytabpanel.setBorder( BorderFactory.createCompoundBorder( BorderFactory.createTitledBorder( "Story" ), BorderFactory.createEmptyBorder(5,5,5,5)) )
#        mytabpanel.add( myoutputarea, BorderLayout.CENTER )

    def closeItemTab(self, itemfile ):
        tabid = itemfile.getName()
        self.tabbedPane.closeTab(tabid) 
        del self.openitems[tabid]
        
    def undo(self):
        try:
            self.tabbedPane.undo()
        except CannotUndoException, e:
            self.status("Can't undo anymore" )
    
    def redo(self):
        try:
            self.tabbedPane.redo()
        except CannotRedoException, e:
            self.status("Can't redo anymore.")
    
    def checkUndoable(self):
        print "undo="+self.tabbedPane.currenttabid
        # For some odd reason, undomananger.canUndo() returns false even when a legitimate undo can be done
        return self.tabbedPane.tabs[self.tabbedPane.currenttabid].panel.textcomponent.undomanager.canUndo() \
           or  self.tabbedPane.tabs[self.tabbedPane.currenttabid].panel.textcomponent.undomanager.isInProgress()
        
    def checkRedoable(self):
        print "can redo="+self.tabbedPane.currenttabid
        # For some odd reason, undomananger.canRedo() returns false even when a legitimate redo can be done
        return self.tabbedPane.tabs[self.tabbedPane.currenttabid].panel.textcomponent.undomanager.canRedo() \
           or  self.tabbedPane.tabs[self.tabbedPane.currenttabid].panel.textcomponent.undomanager.isInProgress()
           
    def cut(self,e):
        return self.tabbedPane.tabs[self.tabbedPane.currenttabid].panel.textcomponent.cutaction.actionPerformed(e)
    def copy(self,e):
        return self.tabbedPane.tabs[self.tabbedPane.currenttabid].panel.textcomponent.copyaction.actionPerformed(e)
    def paste(self,e):
        return self.tabbedPane.tabs[self.tabbedPane.currenttabid].panel.textcomponent.pasteaction.actionPerformed(e)

            
   # Stand-alone Unit Execution
if __name__ == "__main__":
    pass

import org.w3c.dom.Document 
import java.io.File as File
import java.io.IOException as IOException
import java.lang.Object

import javax.swing.JMenu as JMenu
import javax.swing.JMenuItem as JMenuItem
import javax.swing.JMenuBar as JMenuBar
import javax.swing.KeyStroke as KeyStroke
import javax.swing.PopupFactory as PopupFactory
import javax.swing.ButtonGroup as ButtonGroup
import javax.swing.JRadioButtonMenuItem as JRadioButtonMenuItem
import java.awt.Toolkit as Toolkit
import re
import sys
import imp
from nu.xom import *
import nux.xom.xquery.XQuery as XQuery
import nux.xom.xquery.XQueryUtil as XQueryUtil

from Audiences import Audiences

from ndebug import ndebug
ndebug.debug=1

class GnitPickMenuBar(JMenuBar):
    """GnitPickMenuBar
       Class to implement GnitPick menu bar.
       Reads MenuLayout.xml, instantiates menus, submenus, and items, and maps hierarchical names to actionPerformed methods
       Menu handlers are defined in MenuItemFunctions.py and inherited into this class
    """
    def __init__(self,controllerobj, menulayouturi="MenuLayout.xml"):       
        JMenuBar.__init__(self)
        # self.menuhandlers = GnitPickMenuItems
        self.controller = controllerobj
        self.url = menulayouturi
        self.doc=None
        self.charencoding="ISO-8859-1"   # UTF-8, UTF-16
        self.namespace=None
        self.nsprefix=None
        self.root=None
        self.validate=0 # don't validate by default
        
   
        # parse the xml definition of the menu
        try:
           parser = Builder(self.validate)
           self.doc = parser.build(self.url)
        except ValidityException, ex:
           print >>sys.stderr, "Validity Exception - GnitPickMenu.xml has non-conforming structure"
           self.doc = ex.getDocument()
           i=ex.getErrorCount()
           j=1
           while j < i:
              print getValidityError(j)
              j=j+1
        except ParsingException, ex:
           print >>sys.stderr, "Parsing Exception - menu layout xml has malformed markup"
        except IOException, ex:
           print >>sys.stderr, "IO Exception - Couldn't open menu layout xml "+menulayouturi
        except ex:
           print >>sys.stderr, "Other Exception during menu construction: " + ex.toString() 
#        print "GnitMenuBar.__init__(): read elements"         
        # read the root element and iterate over children; Create a top level menu, depth first

        # Load the menu handlers
        menuhandlersnode = XQueryUtil.xquery(self.doc,"/menubar/@handlers")
        if menuhandlersnode == None:
           print >>stderr, "No menu functions defined!"
        handlerstring = menuhandlersnode.get(0).getValue()
        
        ndebug("Loading menu functions from "+handlerstring )
        
        # ACK! LEFTOFF! ?HACK!!!
        fp, pathname, description = imp.find_module(handlerstring,"./")
        try:
            self.menuhandlers = imp.load_module(handlerstring, fp, pathname, description)
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()
            
        
        self.menuitems={}   # Indexed by heirarchical name; call setEnabled(boolean) to disable or enable the items
        self.menufunctionnames = filter( lambda x: re.search("[A-Z].*",x), dir(self.menuhandlers) )
        self.menufunctions = {}
        for name in self.menufunctionnames:
            ndebug( "Setting " + name )
            self.menufunctions[ name ] =  getattr(self.menuhandlers, name)

        setattr( self.menuhandlers, "controller", controllerobj)
# LEFTOFF. NEEDTO: change source of default item content
        self.audiences = Audiences()
        setattr( controllerobj, "defaultItemContent", self.audiences.defaultContent)
       #LEFTOFF setattr( controllerobj, "normalizeItemFileName", menuhandlers.normalizeItemFileName)

        i=0
        menusections = XQueryUtil.xquery(self.doc,"/menubar/menu")
#        print "   menu count=" + menusections.size().toString()
        if menusections == None:
            print >>stderr, "No menu items defined!"
        i=0
        while i < menusections.size():
            elem=menusections.get(i)
#            print "Adding "+elem.getAttribute("name").getValue()
            self.processMenuElement(elem,self,None)   # attach to menu bar; no parent element name
            i=i+1
            


    def setMenuOn(self,menuname):
        self.menuitems[menuname].setEnabled(1)

    def setMenuOff(self,menuname):
        self.menuitems[menuname].setEnabled(0)
        
    def processMenuElement(self,elem,parentmenu,parentname):
        
           # finish up immediately if we are processing a separator
        if elem.getLocalName() == "item" and elem.getAttribute("name") == None:
             parentmenu.addSeparator()
             return
             
           # Create the menu or item, recurse for children that are menus
           # create a unique key for the flattened menuitems dictionary 
        enm= ( parentname == None and [""] or [parentname+"_"])[0] + elem.getAttribute("name").getValue()
#        print "addMenu(" + elem.getAttribute("name").getValue() + ", parentmenu, " + enm + ")"
        
           # use a label if it is provided, name otherwise
        elbl=elem.getAttribute("label")
        if elbl == None:   # default label to name
            elbl=elem.getAttribute("name").getValue()
        else:
            elbl=elbl.getValue()
            
           # menus have items and possibly other menus as children, but no actionPerformed
        if elem.getLocalName() == "menu":
            self.menuitems[enm] = JMenu( elbl )

            accelerator = elem.getAttribute("shortcutkey")
            if accelerator != None:
                self.menuitems[enm].setMnemonic( ord(accelerator.getValue()[0] ) )

               # connect it to the parent menu
            parentmenu.add( self.menuitems[enm] )
               # recurse to add any child menus or items
            mymenusections = XQueryUtil.xquery(elem,"./menu|./item")
            # mymenusections = xquery.execute(doc)
            i=0
            while i < mymenusections.size():
                myelem=mymenusections.get(i)
                self.processMenuElement(myelem,self.menuitems[enm],enm)   # attach to lower menu section; parent is this element's menu
                i=i+1

        else:   # items normally have no children; if there is content, it is attached as a property to actionPerformed 
                # we have to find a GnitPickMenuItem() method for actionPerformed
  
            if ( elem.getChildElements("radio").size() > 0 ):
                self.menuitems[enm] = ButtonGroup()
                myradiobuttons = XQueryUtil.xquery(elem,"./radio")
                i=0
                while i < myradiobuttons.size():
                    myradio=myradiobuttons.get(i)
                    myradioenm=enm+"_"+ myradio.getAttribute("name").getValue()
                    myradiolblattr=myradio.getAttribute("label")
                    if myradiolblattr == None:
                        myradiolbl = myradio.getAttribute("name").getValue()
                    else:
                        myradiolbl = myradiolblattr.getValue()
                    sel=0
                    if ( myradio.getAttribute("selected") != None ):
                        if ( myradio.getAttribute("selected").getValue() == "selected" ):
                            sel=1 
                    self.menuitems[ myradioenm ] = JRadioButtonMenuItem( myradiolbl, sel )
                    self.menuitems[ myradioenm ].actionPerformed = getattr(self.menuhandlers, myradioenm)
                    self.menuitems[enm].add( self.menuitems[ myradioenm ] )
                    parentmenu.add( self.menuitems[ myradioenm ] )
                    i=i+1
            else:
                self.menuitems[enm] = JMenuItem( elbl )
                accelerator = elem.getAttribute("shortcutkey")
                if accelerator != None:
                    self.menuitems[enm].setAccelerator( KeyStroke.getKeyStroke( ord(accelerator.getValue()[0]), Toolkit.getDefaultToolkit().getMenuShortcutKeyMask(), 0) )
                    
                   # attach the element to the menu item handler, so it can query for content itself
    #            setattr( self.menufunctions[enm], "element", elem )
                self.menufunctions[enm].element = elem
                ndebug( "Setting " + enm  )
    
                mnemonic = elem.getAttribute("mnemonic")
                if mnemonic != None:
                    self.menuitems[enm].setMnemonic( ord(mnemonic.getValue()[0])  )
                   # refer to method by the same logical menu/menu/item name
                   # e.g. File:Open is defined using the name self.File_Open()
    #            print dir(self.menuhandlers)
                self.menuitems[enm].actionPerformed = getattr(self.menuhandlers, enm)
                
                   # connect it to the parent menu
                parentmenu.add( self.menuitems[enm] )
    
    #    # Menu item definitions are placed into the separate module GnitPickMenuItems.py
    #            contentaction = elem.getAttribute("contentaction")
    #            if contentaction != None:
    #                
    #                if contentaction.getValue() == "popup":
    #                   xmlcontent=""
    #                   i=0
    #                   children = elem.getChildElements()
    #                   while i < children.size():
    #                       xmlcontent = xmlcontent + children.get(i).toXML()
    #                   pf = PopupFactory.getSharedInstance()
    #                   ht = JTextPane()
    #                   doc = ht.getStyledDocument()
    #                   styledef = StyleContext.getDefaultStyleContext().getStyle(StyleContext.DEFAULT_STYLE)
    #                   regular = doc.addStyle("regular", styledef)
    ##                    StyleConstants.setFontFamily(styledef, "SansSerif")
    #                   doc.insertString( doc.getLength(),  xmlcontent , doc.getStyle("regular") )
    #                   sp = JScrollPane(ht)
    #                   
    #                   self.controller.view.popup = pf.getPopup( self.controller.view, sp, 100, 100)
    #                   

   # Stand-alone Unit Execution
if __name__ == "__main__":
   print filter( lambda x: re.search("[A-Z].*",x), dir(GnitPickMenuItems) )

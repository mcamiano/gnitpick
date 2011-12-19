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


from ndebug import ndebug
ndebug.debug=1

class Audiences:
    """Audiences
       Class to implement audience-driven capabilities.
       Reads audiences xml, instantiates doc types, uri methods, role-based facets
    """
    def __init__(self, audiencesuri="audiences.xml"):       
        self.url = audiencesuri
        self.doc=None
        self.charencoding="ISO-8859-1"   # UTF-8, UTF-16
        self.namespace=None
        self.nsprefix=None
        self.root=None
        self.validate=0 # don't validate by default
        
   
        # parse the xml definition of the audience capabilities
        try:
           parser = Builder(self.validate)
           self.doc = parser.build(self.url)
        except ValidityException, ex:
           print >>sys.stderr, "Validity Exception - "+audiencesuri+" has non-conforming structure"
           self.doc = ex.getDocument()
           i=ex.getErrorCount()
           j=1
           while j < i:
              print getValidityError(j)
              j=j+1
        except ParsingException, ex:
           print >>sys.stderr, "Parsing Exception - audiences xml has malformed markup"
        except IOException, ex:
           print >>sys.stderr, "IO Exception - Couldn't open audiences xml "+audiencesuri
        except ex:
           print >>sys.stderr, "Other Exception during audiences provisioning: " + ex.toString()

        # prepare for querying the structures
        audiences = self.doc.getRootElement()
        
        doctypes = XQueryUtil.xquery(self.doc,"//type")
        if doctypes == None:
           print >>stderr, "No document types defined!"
           
        appdomains = audiences.getChildElements("application-domain")
        if appdomains == None:
           print >>stderr, "No document types defined!"
       
        # LEFTOFF this is a hack to keep it working while I flesh out the rest of the code
       
        storynode = XQueryUtil.xquery(self.doc,"//type[@name='story']/new-instance-template")
        if storynode == None:
           print >>stderr, "Storynode hack couldn't find story type!"
        self.defaultContent = storynode.get(0).getValue()
       

   # Stand-alone Unit Execution
if __name__ == "__main__":
   foo = Audiences()
   print foo.defaultContent
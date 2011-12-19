import   com.thaiopensource.relaxng.translate.util.InvalidParamsException as InvalidParamsException
import   com.thaiopensource.relaxng.edit.SchemaCollection as SchemaCollection
import   com.thaiopensource.relaxng.input.InputFailedException as InputFailedException
import   com.thaiopensource.relaxng.input.InputFormat as InputFormat
import   com.thaiopensource.relaxng.input.MultiInputFormat as MultiInputFormat
import   com.thaiopensource.relaxng.input.xml.XmlInputFormat as XmlInputFormat
import   com.thaiopensource.relaxng.input.dtd.DtdInputFormat as DtdInputFormat
import   com.thaiopensource.relaxng.input.parse.compact.CompactParseInputFormat as CompactParseInputFormat
import   com.thaiopensource.relaxng.input.parse.sax.SAXParseInputFormat as SAXParseInputFormat
import   com.thaiopensource.relaxng.output.LocalOutputDirectory as LocalOutputDirectory
import   com.thaiopensource.relaxng.output.OutputDirectory as OutputDirectory
import   com.thaiopensource.relaxng.output.OutputFailedException as OutputFailedException
import   com.thaiopensource.relaxng.output.OutputFormat as OutputFormat
import   com.thaiopensource.relaxng.output.dtd.DtdOutputFormat as DtdOutputFormat
import   com.thaiopensource.relaxng.output.rnc.RncOutputFormat as RncOutputFormat
import   com.thaiopensource.relaxng.output.rng.RngOutputFormat as RngOutputFormat
import   com.thaiopensource.relaxng.output.xsd.XsdOutputFormat as XsdOutputFormat
import   com.thaiopensource.xml.sax.ErrorHandlerImpl as ErrorHandlerImpl
import   com.thaiopensource.util.Localizer as Localizer
import   com.thaiopensource.util.OptionParser as OptionParser
import   com.thaiopensource.util.UriOrFile as UriOrFile
import   com.thaiopensource.util.Version as Version
import   org.xml.sax.SAXException as SAXException

import java.io.File as File
import java.io.IOException as IOException
import org.xml.sax.SAXException as SAXException
import java.lang.String as String
import java.lang.Integer as Integer
import java.util.Iterator as Iterator

import array
import sys

def suffix(s):
   dot = s.rfind(".")
   if (dot < 0):
      return ""
   return s[dot+1:(len(s))]
      
      
class filetypeError(Exception):
   def __init__(self, msg):
       self.message = msg
   def __str__(self):
       return repr(self.message)    

def inputTypeHandler(suffix):
    handlers = { 
       'rng': SAXParseInputFormat,
       'dtd': DtdInputFormat,
       'rnc': CompactParseInputFormat,
       'xml': XmlInputFormat
       }
    if ( not( handlers.__contains__(suffix) ) ):
       raise( filetypeError( "unrecognized input type '" + suffix + "'" ) )
    return handlers[suffix]()

def outputTypeHandler(suffix):
    handlers = {
        'dtd': DtdOutputFormat,
        'rng': RngOutputFormat,
        'rnc': RncOutputFormat,
        'xsd': XsdOutputFormat
    }
    if ( not( handlers.__contains__(suffix) ) ):
        raise( filetypeError( "unrecognized output type '" + suffix + "'" ) )
    return handlers[suffix]()


class schemaxlator:
   """ Adapted from James Clark's Trang tool, specifically Driver.java
       Convert a schema in RNG, RNC, or DTD format, or an XML sample instance, 
       into  RNG, RNC, DTD, or WXS format, using the Jing api. 
   """
   
   OUTPUT_ENCODING = "UTF-8"
   LINE_LENGTH = 72
   INDENT = 2

   
   def __init__(self,inuri, outuri):
      self.errorhandler = ErrorHandlerImpl()
      try: 
        inputType = suffix(inuri).lower()
        inFormat = inputTypeHandler( inputType )

        outputType = suffix(outuri).lower()
        outFormat = outputTypeHandler( outputType )

        inputParamArray = array.array(String, [] )

        self.schemacollection = inFormat.load( UriOrFile.toUri(inuri), inputParamArray, outputType, self.errorhandler)

        outputdir = LocalOutputDirectory( self.schemacollection.getMainUri(),
           File( outuri ),
           outputType,
           self.OUTPUT_ENCODING,
           self.LINE_LENGTH,
           self.INDENT)
           
        outputParamArray = array.array(String, [] )
        
        outFormat.output( self.schemacollection, outputdir, outputParamArray, inputType.lower(), self.errorhandler)
      
      except IOException, e:
         self.errorhandler.printException(e)
      except SAXException, e:
         self.errorhandler.printException(e)
    
      
   # Stand-alone Unit Execution
if __name__ == "__main__":
    if ( len(sys.argv) == 1 ): # Convert RelaxNG XML syntax into compact syntax
    
       foo = schemaxlator( "menulayout.xml", "foo.rng" )
       bar = schemaxlator( "foo.rng", "bar.rnc" )
       foobar = schemaxlator( "bar.rnc", "foobar.rng" )        
       # foobar.rng and foo.rng should be equivalent
       
       print dir( bar.schemacollection.getSchemaDocumentMap() )
       
       iter = bar.schemacollection.getSchemaDocumentMap().entrySet().iterator()
       while iter.hasNext():
          entry = iter.next()
          print "Key=" + entry.getKey() + ", value="
          vectr = entry.getValue().getPattern()  # .getFollowingElementAnnotations()
          print vectr.class
          print vectr.getComponents().size()
          # navigate to the component patterns of the schema
          i = 0
          len = vectr.getComponents().size()
          while i < len:
             c = vectr.getComponents().get(i)
             print "Name: " + c.getName()
             print "Body: " + c.getBody().toString()
             print dir(c.attributeAnnotations)
             i=i+1
             
    elif ( len(sys.argv) == 3):   # convert fromfile into tofile, inferring the format from the file extension
       jv = schemaxlator( sys.argv[1], sys.argv[2] ) 
    else:
       print "Wrong number of arguments ( " + Integer( len( sys.argv ) ).toString() + ") "

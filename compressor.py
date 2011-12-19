import jarray
from java.util.zip import *
from java.lang import *

def decompress(data):
	print "Decompressing " + str(len(data)) + " bytes of data."
	inputString = String(data)
	ainput = inputString.getBytes()
	
	print "ainput " , ainput
	
	decompresser = Inflater()
	decompresser.setInput(ainput, 0, len(data))
	
	result = jarray.zeros(1024*8, 'b')
	
	resultLength = decompresser.inflate(result)
	print "len.0:", resultLength
	
	outputString = ""
	while resultLength > 0:
		print "len:", resultLength
		print "str:", String(result, 0, resultLength).toString()
		outputString = outputString + String(result, 0, resultLength).toString()
		print "buffer:" , outputString
		resultLength = decompresser.inflate(result)
	
	decompresser.end()
	return outputString

def compress(data):
	
	inputString = String(data)
	ainput = inputString.getBytes()
	
	compresser = Deflater()
	compresser.setInput(ainput)
	compresser.finish()
	
	result = jarray.zeros(1024*8, 'b')
	
	resultLength = compresser.deflate(result)
	outputString = ""
	while resultLength > 0:
		outputString = outputString + String(result, 0, resultLength).toString()
		resultLength = compresser.deflate(result)
	
	return outputString
	

   # Stand-alone Unit Execution
if __name__ == "__main__":
   original = "FFFFFFFFFFFFFFFF"
   zipped = compress(original)
   unzipped = decompress( zipped )
   print "Original = '" + original + "', unzipped='"+unzippped+"'"
   print 
	
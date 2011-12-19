@echo off
setlocal

SET CLASSPATH=lib/nux.jar;lib/xom.jar;lib/saxon8-xom.jar;lib/saxon8.jar;lib/jaxen-1.1-min.jar;lib/xalan.jar;lib/xercesImpl.jar;lib/xmlParserAPIs.jar;lib/jython.jar;gnitpick.jar

java com.agilemarkup.grazer.gnitpick.GnitPick

pause

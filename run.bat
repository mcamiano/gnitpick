@echo off
setlocal

rem set PATH=C:\jython-2.1;%PATH%

SET CLASSPATH=lib/nux.jar;lib/xom.jar;lib/saxon8-xom.jar;lib/saxon8.jar;lib/jaxen-1.1-min.jar;lib/xalan.jar;lib/xercesImpl.jar;lib/xmlParserAPIs.jar;/jython-2.1/jython.jar;gnitpick.jar;lib/jython.jar

java com.agilemarkup.grazer.gnitpick.GnitPick



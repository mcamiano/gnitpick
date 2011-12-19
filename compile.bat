@echo off
setlocal

set PATH=C:\jython-2.1;%PATH%

SET CLASSPATH=lib/nux.jar;lib/xom.jar;lib/saxon8-xom.jar;lib/saxon8.jar;lib/jaxen-1.1-min.jar;lib/xalan.jar;lib/xercesImpl.jar;lib/xmlParserAPIs.jar

rem throws warnings about assert and enum being keywords as of Java 1.4
jythonc --compiler C:\opt\jdk1.5.0_01\bin\javac.exe --compileropts "-source 1.3" --package com.agilemarkup.grazer.gnitpick --workdir builds --jar gnitpick.jar GnitPick.py               GnitPickController.py     GnitPickFileChooser.py GnitPickMenuBar.py        GnitPickModel.py GnitPickView.py           LineHighlightPainter.py   ndebug.py


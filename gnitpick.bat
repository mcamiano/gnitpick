@ECHO OFF

SET jython=C:\jython-2.1

SET CLASSPATH=c:/opt/nux-1.3/lib/nux.jar;C:/opt/nux-1.3/lib/xom.jar;C:/opt/nux-1.3/lib/saxon8-xom.jar;C:/opt/nux-1.3/lib/saxon8.jar;C:/opt/jython/j2_2_a1/jython.jar
rem C:/jython-2.1/jython.jar

%jython%\jython.bat GnitPick.py

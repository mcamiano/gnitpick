@echo off

mkdir dist\lib
copy lib dist\lib
mkdir dist\lib\licenses 
copy lib\licenses dist\lib\licenses
copy \jython-2.1\jython.jar dist\lib
copy gnitpick.jar dist\lib
copy rungnit.bat dist
copy GnitPickMenu.xml dist
mkdir dist\stories
copy stories dist\stories

copy COPYING dist

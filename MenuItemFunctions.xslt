<?xml version="1.0" encoding="UTF-8"?>
<!-- This stylesheet transforms a simple menu implementation document 
       which contains Jython code implementations of menu item handlers,
       into a Jython source file. 
   
      The motivation consists of three reasons:
      First, using a transformed XML format, the GnitPick collections editor 
      can utilize the NUX/XOM api to initially configure and selectively update
      its menus. The menu layout was already expressed as XML, and having 
      the implementations of the handler functions within an XML skeletal structure
      makes it easier to bind the code at run-time within a controlled environment.
   
      Second, as a consequence of the first reason, migrating from scripted code
      to declarative properties, where it is appropriate, is facilitated by having the 
      transformation process in place. 

      Third, having an XML format makes it feasible to use a robust XML editor 
      such as oXygen as a semi-integrated development environment for GnitPick 
      customization.   It is trivial to locate and modify functions using the tree sidebar;
      or to execute an XPath selection to locate a particular ancillary class; or to 
      generate technical reference documentation using alternative transforms.
-->
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
   
   <xsl:variable name="functionsignature" select="/*/@parameters" />

   <xsl:output method="text"  indent="no" />

   <xsl:template match="/">
      <xsl:apply-templates/>
   </xsl:template>

   <xsl:template match="menuhandlers">
         <xsl:apply-templates/>
      
         <xsl:text>menuhandlers = {&#xA;</xsl:text>
         <xsl:apply-templates mode="summary"/>
         <xsl:text>&#xA;}&#xA;</xsl:text>
   </xsl:template>

   <xsl:template match="eventhandler" mode="summary">
      
   </xsl:template>
   
   <xsl:template match="commoncode">
      <xsl:value-of select="." />
   </xsl:template>

   <xsl:template match="class">

      <xsl:text>def </xsl:text>
      <xsl:value-of select="@name" />
      <xsl:text>(</xsl:text>
      <xsl:value-of select="@extends"/>
      <xsl:text>):&#xA;</xsl:text>
      <xsl:apply-templates/>
   </xsl:template>

   <xsl:template match="class/method">
      <xsl:param name="indent" select="'   '" />
      
      <xsl:variable name="content" >
      <xsl:text>def </xsl:text>
      <xsl:value-of select="@name" />
      <xsl:text>(</xsl:text>
      <xsl:value-of select="@parameters"/>
      <xsl:text>):&#xA;</xsl:text>
      <xsl:apply-templates/>
      </xsl:variable>
    
       <xsl:call-template name="py-indent">
       <xsl:with-param name="content" select="$content" />
       </xsl:call-template>
   </xsl:template>

   <xsl:template match="eventhandler">
      <xsl:variable name="content" >
      <xsl:text>def </xsl:text>
      <xsl:value-of select="translate( @menu, '/', '_')" />
      <xsl:text>(</xsl:text>
      <xsl:value-of select="$functionsignature"/>
      <xsl:text>):&#xA;</xsl:text>
      <xsl:apply-templates select="text()" />
      </xsl:variable>
    
       <xsl:call-template name="py-indent">
          <xsl:with-param name="content" select="$content" />
       </xsl:call-template>
      <xsl:apply-templates select="property"/>
   </xsl:template>

   <xsl:template match="eventhandler/property">
      <xsl:value-of select="translate( parent::*/@menu, '/', '_')" />
      <xsl:text>.</xsl:text>
      <xsl:value-of select="@name" />
      <xsl:text> = </xsl:text>
      <xsl:apply-templates/>
      <xsl:text>&#xA;&#xA;</xsl:text>
   </xsl:template>

   <!-- Turn any top-level text into document comments -->
   <xsl:template match="/*/text()" >
      <xsl:if test="replace(string(.), '\n|\r|\s', '') != '' ">
         <xsl:text>""" </xsl:text>
         <xsl:value-of select="."/>
         <xsl:text>"""&#xA;&#xA;</xsl:text>
      </xsl:if>
   </xsl:template>

   <xsl:template name="py-indent" >
      <xsl:param name="first-line-indent" select="0" />
      <xsl:param name="indent" select="2" />
      <xsl:param name="content" />

      <xsl:variable name="content-tokens" select="tokenize($content,'\n')"/>
      
      <xsl:value-of select="concat(substring('                                                                                                    ', 1,  $first-line-indent), $content-tokens[1] )"/>
 
      <xsl:for-each select="$content-tokens[position() != 1]" >
         <xsl:value-of select="concat(substring('                                                                                                    ', 1, $indent), ., '&#xA;')"/>
      </xsl:for-each>
      
   </xsl:template>

</xsl:transform>
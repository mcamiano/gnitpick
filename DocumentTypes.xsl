<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">

   <xsl:output method="text" encoding="UTF-8"/>
   
   <xsl:template match="/">
      <xsl:apply-templates/>
   </xsl:template>


   <xsl:template match="audiences">      
         <xsl:apply-templates/>
   </xsl:template>


   <xsl:template match="doctypes">      
         <xsl:apply-templates/>
   </xsl:template>

   <xsl:template match="type">

      <type name="{@name}" label="{@label}" collectionlabel="{@collection-label}">

         <xsl:apply-templates/>

      </type>

   </xsl:template>
         
   <xsl:template match="type/uri">
def normalizeuri_<xsl:value-of select="@protocol"/>_<xsl:value-of select="@suffix"/>(str):
   if not re.match(r"^.*\.<xsl:value-of select="@suffix"/>$", str):
      if str == "":
          str = "unnamed"
      str=str+".<xsl:value-of select="@suffix"/>"
   return str
</xsl:template>
         
   <xsl:template match="text()"/>
   
</xsl:transform>
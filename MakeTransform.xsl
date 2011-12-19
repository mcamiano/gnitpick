<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    xmlns:xt="http://www.w3.org/1999/XSL/TransformAlias"
    >
    <xsl:key match="*" name="elementnames" use="name()" />
    
    <xsl:namespace-alias stylesheet-prefix="xt" result-prefix="xsl"/>
    
    <xsl:template match="/">
        <xt:transform>
            
          <xt:output method="xml" encoding="UTF-8" version="2.0" />
            
          <xt:template match="/" >
              <xt:apply-templates/>
          </xt:template>
            
          <xsl:text>&#xA;&#xA;</xsl:text>
            
          <xsl:apply-templates select="*"/>
          <xt:template match="text()"/>
        </xt:transform>
        
    </xsl:template>
    
    <xsl:template match="*">
        <xsl:variable name="thisnode" select="." />
        <xsl:text>&#xA;&#xA;</xsl:text>

        <xt:template>
            <xsl:attribute name="match" >
                <xsl:for-each select="(parent::*|.)[generate-id(.) = generate-id($thisnode) or generate-id(.) != generate-id(/*)]">
                    <xsl:value-of select="name()" />
                    <xsl:if test="position() != last()"><xsl:text>/</xsl:text></xsl:if>
                </xsl:for-each>
            </xsl:attribute>
            
            <xsl:text>&#xA;&#xA;</xsl:text>
            
            <xsl:element name="{name()}">
                <xsl:for-each select="@*">
                    <xsl:attribute name="{name()}">{@<xsl:value-of select="name()"/>}</xsl:attribute>
                </xsl:for-each>

            <xsl:text>&#xA;&#xA;</xsl:text>
            
            <xt:apply-templates />
            
            <xsl:text>&#xA;&#xA;</xsl:text>
                
            </xsl:element>

            <xsl:text>&#xA;&#xA;</xsl:text>
            
        </xt:template>

        <xsl:for-each-group select="*" group-by="name()">
            <xsl:apply-templates select="current-group()[1]"/>
        </xsl:for-each-group>

    </xsl:template>
    
    <xsl:template match="text()"/>
    
</xsl:stylesheet>

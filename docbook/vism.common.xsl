<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <!--
    number chapters with arabic numbers
    http://www.sagehill.net/docbookxsl/SectionNumbering.html
  -->
  <xsl:param name="chapter.autolabel" select="'I'"/>
  <!--
    highlight hyperlinks, plain HTML style
    https://pages.lip6.fr/Jean-Francois.Perrot/XML-Int/Session6/Cookbook.html
  -->
  <xsl:attribute-set name="xref.properties">
    <xsl:attribute name="color">blue</xsl:attribute>
    <xsl:attribute name="text-decoration">underline</xsl:attribute>
  </xsl:attribute-set>
</xsl:stylesheet>

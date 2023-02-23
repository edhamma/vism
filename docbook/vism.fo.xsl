<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:import href="/usr/share/xml/docbook/stylesheet/docbook-xsl-ns/fo/docbook.xsl"/>
  <xsl:import href="vism.common.xsl"/>
  <xsl:param name="body.font.family">TeX Gyre Pagella</xsl:param>
  <xsl:param name="title.font.family">TeX Gyre Pagella</xsl:param>
  <xsl:param name="paper.type" select="'A4'"/>
  <!--
    indent lists (currently only used inside biblioentry)
    https://lists.oasis-open.org/archives/docbook-apps/201309/msg00067.html
  -->
  <xsl:attribute-set name="list.block.properties">
    <xsl:attribute name="margin-left">2em</xsl:attribute>
  </xsl:attribute-set>
</xsl:stylesheet>


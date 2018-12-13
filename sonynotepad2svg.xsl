<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/2000/svg"
  >
<xsl:output method="xml" indent="no"/>

<xsl:template match="/">
  <!--
       give it the correct header elements to make it a stand-alone self-contained svg document.
  -->
  <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE svg PUBLIC "-//W3C/DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"&gt;</xsl:text>
    <xsl:copy>
      <!-- drop 3 elements embracing the svg element: notepad, drawing, page -->
      <xsl:apply-templates select="*[local-name()='notepad']/*[local-name()='drawing']/*[local-name()='page']/*" />
    </xsl:copy>
</xsl:template>

<xsl:template match="*[local-name()='svg']">
  <xsl:element name="{local-name()}">
    <!-- copy the attributes of the old svg element to the new one, but drop the namespace --> 
    <xsl:for-each select="@*">
      <xsl:attribute name="{local-name()}">
        <xsl:value-of select="."/>
      </xsl:attribute>
    </xsl:for-each>
    <!-- move width and height attributes from drawing to svg element -->
    <xsl:attribute name="width">
      <xsl:value-of select="/*[local-name()='notepad'][1]/*[local-name()='drawing'][1]/@width" />
    </xsl:attribute>
    <xsl:attribute name="height">
      <xsl:value-of select="/*[local-name()='notepad'][1]/*[local-name()='drawing'][1]/@height" />
    </xsl:attribute>
    
    <xsl:apply-templates select="./node()"/>
  </xsl:element>
</xsl:template>


<xsl:template match="comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<xsl:template match="*">
  <xsl:element name="{local-name()}">
    <xsl:apply-templates select="@*|node()"/>
  </xsl:element>
</xsl:template>

<xsl:template match="@*">
    <xsl:attribute name="{local-name()}">
      <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>
</xsl:stylesheet>

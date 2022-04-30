<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
   <xsl:template match="/">
    <html>
       <head><link rel="stylesheet" type="text/css" href="http://172.17.0.1/poemdb.css" /> >
       </head>	   
       <body>
		<h1>Poems</h1>
		  <table border="1">
			<tr>
				<th>poemID</th> <th>poem</th> <th>email</th>
			</tr>
			<xsl:for-each select="poemdb/Poem">
				<xsl:sort select="poemID"/>	
				<tr>
					<td><xsl:value-of select="poemID"/></td>
					<td><xsl:value-of select="poem"/></td>	
					<td><xsl:value-of select="email"/></td>	
				</tr>
			</xsl:for-each>
		  </table>
		</body>
    </html>
   </xsl:template>
 </xsl:stylesheet> 

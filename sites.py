#! /usr/bin/python
"""
This will return all sites within a specified distance
"""
import MySQLdb as mdb
import cgi

#Insert real values
mysql_server = ""
mysql_database = ""
mysql_user = ""
mysql_password = ""
con = mdb.connect(mysql_server, mysql_database, mysql_user, mysql_password)

def sql(command):
  with con:
    cur = con.cursor()
    cur.execute(command)
    return cur.fetchall()
	
def getSites():
  form = cgi.FieldStorage()
  geo['lat'] = form.getvalue("lat")
  geo['lon'] = form.getvalue("lon")
  geo['rad'] = str(float(form.getvalue("distance"))/69)
  #geo['lat'] = 40
  #geo['lon'] = -86
  #geo['rad'] = 1

  sqlQuery = "SET @center = GeomFromText('POINT(%(lon)s %(lat)s)')" %(geo)
  sql(sqlQuery)
  sqlQuery = "SET @radius = %(rad)s" %(geo)
  sql(sqlQuery)
  sqlQuery = """
SET @bbox = CONCAT('POLYGON((', 
X(@center) - @radius, ' ', Y(@center) - @radius, ',', 
X(@center) + @radius, ' ', Y(@center) - @radius, ',', 
X(@center) + @radius, ' ', Y(@center) + @radius, ',', 
X(@center) - @radius, ' ', Y(@center) + @radius, ',', 
X(@center) - @radius, ' ', Y(@center) - @radius, '))' 
); 
"""
  sql(sqlQuery)
  sites = sql("SELECT name,longname, SQRT(POW( ABS( X(location) - X(@center)), 2) + POW( ABS(Y(location) - Y(@center)), 2 )) AS distance, X(location) as lon, Y(location) AS lat FROM local WHERE Intersects(location, GeomFromText(@bbox)) AND SQRT(POW( ABS( X(location) - X(@center)), 2) + POW( ABS(Y(location) - Y(@center)), 2 )) < @radius  ORDER BY distance")
  return sites
  
def direction(lat,lon):
  if lat >= float(geo['lat']):
    dir = "N"
  else:
    dir = "S"
  if lon >= float(geo['lon']):
    dir = dir + "E"
  else:
    dir = dir + "W"
  return dir

def formatSites(sites):
  html = "<a id='toggle' href='javascript:toggleSites()'>show all %s sites</a><div style='display:none;' id='site-list'>" %(len(sites))
  for site in sites:
    dir = direction(site[4],site[3])
    html = html + "<input checked id='site-%s' type='checkbox' name='site-%s' value='%s' /><label for='site-%s'> %s</label> <a href='https://maps.google.com/maps?saddr=%s,%s&daddr=%s,+%s'>%smi %s</a><br />" %(site[0],site[0],site[0],site[0],site[1],geo['lat'],geo['lon'],site[4],site[3],int(float(site[2])*69), dir)
  html = html + "</div>"
  print html

geo = {}
formatSites(getSites())

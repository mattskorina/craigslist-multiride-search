#! /usr/bin/python
"""
This file is used to setup the mysql database holding the craigslist sites. Ideally you should run this file and it would do everything for you, but I just created the database by hand.

name varchar(255)
location Point
longname varchar(255)

"""

from lxml import etree
import MySQLdb as mdb
import urllib2
import lxml.html

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

"""
with open("CraigsMap.kml", "r") as f:
  kml = f.read()

tree = etree.fromstring(kml)

datas =  tree.findall(".//{http://www.opengis.net/kml/2.2}Placemark")

for data in datas:
  url = data.find(".//{http://www.opengis.net/kml/2.2}value").text
  name = url.split(".")[0].split("/")[-1]
  lat = data.find(".//{http://www.opengis.net/kml/2.2}latitude").text
  lon = data.find(".//{http://www.opengis.net/kml/2.2}longitude").text
  insert = "INSERT INTO local (name,location) VALUES ('%s', GeomFromText('POINT(%s %s)'))" %(name, lon, lat)
  print insert
  print sql(insert)

"""
def getName(site):
  url = "http://%s.craigslist.org" %(site)
  content = urllib2.urlopen(url)
  tree = lxml.html.fromstring(content.read())
  title = tree.xpath("//title")[0].text
  return title.split(" classifieds")[0].split("craigslist: ")[1]
  
sites = sql("SELECT name from local")

for site in sites:
  name = getName(site[0])
  insert = "UPDATE local SET longname='%s' WHERE name='%s'" %(name.replace("'",""), site[0])
  print insert
  print sql(insert)




#! /usr/bin/python
from operator import itemgetter
import lxml.html
import time
import datetime
import urllib2
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

def loadOptions():
  results = sql("SELECT address,name FROM sites")
  form = ""
  for site in results:
    result = {}
    result['address'] = site[0]
    result['name'] = site[1]
    form = form + "<input checked id='%(address)s' type='checkbox' name='site' value='%(address)s' /><label for='%(address)s'>%(name)s</label><br />" %result
  return form

def printHTML():
  result = getForm()
  if len(result[0]) < 10:
    name = sql("SELECT longname FROM local WHERE name='%s'" %(result[1]))
    print "<div class='ride' id='date-0'>No results from <a href='http://%s.craigslist.org'><em>%s</em></a>.</div>" %(result[1],name[0][0])
  else:
    print result[0]

def getForm():
  form = cgi.FieldStorage()
  search = form.getvalue("search")
  site = form.getvalue("site")
  days = int(form.getvalue("days"))
  #search = "los angles"
  #days = int("7")
  #site="indianapolis"
  search = search.replace(" ","%20")
  
  results = []
  
  results = craigslistSearch(site,search,results)
  results = sorted(results,key=itemgetter(0),reverse=True)
  html = loadResults(results,days)
  return(html, site)

def loadResults(results,days):
  lastWeek = int((datetime.date.today()-datetime.timedelta(days=days)).strftime("%m%d"))
  today = int(datetime.date.today().strftime("%m%d"))
  html = ""
  for ride in results:
    daysOld = today - ride[0]
    if ride[0] > lastWeek:
      name = sql("SELECT longname FROM local WHERE name='%s'" %(ride[1]))
      html = html + "<div class='days-%s ride' id='date-%s'>%s <a href='%s'>%s</a> - %s - <em>%s</em></div>" %(daysOld, ride[0], ride[2], ride[5], ride[3], ride[4],name[0][0]) 
  return html

def craigslistSearch(site, search, results):
  url = "http://%s.craigslist.org/search/rid?query=%s" %(site,search)
  content = urllib2.urlopen(url)
  tree = lxml.html.fromstring(content.read())
  dates = tree.xpath("//p[@class='row']//span[@class='date']")
  a = tree.xpath("//p[@class='row']//a")
  titles = []
  links = []
  for i in range(len(dates)):
    titles.append(a[2*i+1])
    links.append("http://" + site + ".craigslist.org" + a[2*i+1].attrib['href'])
  locations = tree.xpath("//p[@class='row']//span[@class='l2']")
  formatDates = []
  for date in dates:
    formatDates.append(convertTime(date.text))
  for i in range(len(dates)):
    try:
      location = locations[i].xpath(".//small")[0].text
    except:
      location = ""
	
    if len(links[i].split("http://")) == 2:
		results.append([formatDates[i],site,dates[i].text,titles[i].text,location,links[i]])
  return results

def convertTime(date):
  formatDate = time.strptime(date,"%b %d")
  month = str(formatDate.tm_mon)
  day = formatDate.tm_mday
  if day < 10:
    day = "0" + str(day)
  else:
    day = str(day)
  dateInt = month + day
  return int(dateInt)

printHTML()

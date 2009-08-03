import urllib2
import re, string
import urlparse
import os.path
import sys
from os import system
import MySQLdb

conn = MySQLdb.connect("localhost", "root", "", "Data")
sql = conn.cursor(MySQLdb.cursors.DictCursor)
save_to_folder = "/mnt/x/Internet/Downloading/Downer"

class Action:
	# Using an URL, find the right name, path, etc.
	def processUrl(self, url):
		url_parts = urlparse.urlparse(url)
		name = os.path.basename(url_parts.path)
		if(name == ""): name = "index.html"
		path = save_to_folder + '/' + name
		special = ''
				
		if(url_parts.hostname == "www.youtube.com"):
			special = 'youtube'
			name = self.getYoutubeTitle(url)
			path = save_to_folder + '/' + name + ".flv"
		
		return [name, path, special]
	
	# If its a YouTube page, get the Title.
	def getYoutubeTitle(self, url):
		html = urllib2.urlopen(url).read()
		
		match = re.search(r'<title>([^<]+)</title>', html)
		if(match): return match.group(1)
		else:
			match = re.search(r'v=([^\&]+)',url)
			if(match): return match.group(1)
		return "youtube.html"
	
	def download(self, url, path, special):
		# If needed info is not there in the DB.
		if(path == ""):
			data = info.processUrl(url)
			path = data[1]
			
		if(special == 'youtube'):
			system("python youtube-dl.py -o '%s' '%s'" % (path, url))
		
		else:
			system("wget -o '%s' '%s'" % (path, url))

action = Action()
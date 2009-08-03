import urllib2
import re, string
import urlparse
import os.path
import sys
import subprocess
import MySQLdb

conn = MySQLdb.connect("localhost", "root", "", "Data")
sql = conn.cursor(MySQLdb.cursors.DictCursor)
save_to_folder = "/mnt/x/Internet/Downloading/Downer"

class Action:
	# Using an URL, find the right name, path, etc.
	def processUrl(self, url, return_soon=False):
		url_parts = urlparse.urlparse(url)
		name = os.path.basename(url_parts.path)
		if(name == ""): name = "index.html"
		path = save_to_folder + '/' + name
		special = ''
				
		if(url_parts.hostname == "www.youtube.com"):
			special = 'youtube'
			name = self.getYoutubeTitle(url, return_soon)
			path = save_to_folder + '/' + name + ".flv"
		
		return [name, path, special]
	
	# If its a YouTube page, get the Title.
	def getYoutubeTitle(self, url, return_soon=False):
		html = ''
		if(not return_soon): html = urllib2.urlopen(url).read()
		
		match = re.search(r'<title>([^<]+)</title>', html)
		if(match): return match.group(1)
		else:
			match = re.search(r'v=([^\&]+)',url)
			if(match): return match.group(1)
		return "youtube.html"
	
	# This functions checks for all the necessary info and downloads the file.
	def download(self, url, path="", special=""):
		# If needed info is not there in the DB.
		if(path == ""):
			data = self.processUrl(url)
			path = data[1]
			special = data[2]
			
		# Download it!
		if(special == 'youtube'):
			self.execute("youtube-dl -o '%s' '%s'" % (path, url))
		else:
			self.execute("wget -o '%s' '%s'" % (path, url))
	
	
	def execute(self, command):
		try:
			retcode = subprocess.call(command, shell=True)
			if retcode < 0:
				print >>sys.stderr, "Child was terminated by signal", -retcode
			else:
				print >>sys.stderr, "Child returned", retcode
		except OSError, e:
			print >>sys.stderr, "Execution failed:", e


action = Action()
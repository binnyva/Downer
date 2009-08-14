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
	currently_downloading = 0
	
	# Using an URL, find the right name, path, etc.
	def processUrl(self, url, return_soon=False):
		url_parts = urlparse.urlparse(url)
		name = os.path.basename(url_parts.path)
		if(name == ""): name = "index.html"
		path = self.makePath(name)
		special = ''
		
		if(url_parts.hostname == "www.youtube.com"):
			special = 'youtube'
			name = self.getYoutubeTitle(url, return_soon)
			path = self.makePath(name + ".flv")
		
		return [name, path, special]
	
	# Create a path to where the downloads should go to and return it.
	def makePath(self, name):
		return save_to_folder + '/' + name
	
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
	def download(self, url, path="", special="", download_id=0):
		global sql
		
		# Make extra sure that the file has not been downloaded - importent if your are running multiple instance of the app together.
		if(download_id):
			sql.execute("SELECT downloaded FROM Downer WHERE id='%d'" % download_id)
			result_set = sql.fetchone ()
			if(result_set['downloaded'] != '0'): return
			
			self.currently_downloading = download_id
			
		# Make sure we are not overwriteing an exsiting file.
		if(os.access(path, os.F_OK)):
			print "The file '"+path+"' exists. Overwrite (Y/N)?"
			overwrite = raw_input()
			
			#If the user says overwrite, delet the file and continue with the download. If no, skip to the next download.
			if(overwrite == 'y' or overwrite == 'Y'): os.remove(path)
			else: return
		
		# If needed info is not there in the DB.
		if(path == ""):
			data = self.processUrl(url)
			path = data[1]
			special = data[2]
		
		# Download it!
		if(special == 'youtube'):
			self.execute("youtube-dl -o '%s' '%s'" % (path, url), download_id, path)
		else:
			self.execute("wget -O '%s' '%s'" % (path, url), download_id, path)
		
		# Once the download is done, unset the currently_downloading flag.
		self.currently_downloading = 0
	
	# Execute the given command.
	def execute(self, command, download_id=0, path=''):
		try:
			global sql
			if(download_id > 0):
				sql.execute("UPDATE Downer SET downloaded='-1' WHERE id=%d" % download_id)

			retcode = subprocess.call(command, shell=True)
			if retcode < 0:
				print >>sys.stderr, "Child was terminated by signal", -retcode
			else:
				# THe thing that was being downloaded was from the database. So, mark it as downloaded when done.
				if(download_id > 0):
					size = int(os.path.getsize(path))
					mb_size = (size / 1024) / 1024 # getsize() returns size in bytes - so convent to KB and the MB.
					sql.execute("UPDATE Downer SET downloaded='1', downloaded_on=NOW(), file_size='%f' WHERE id=%d" % (mb_size, download_id))
					
		except OSError, e:
			print >>sys.stderr, "Execution failed:", e

action = Action()

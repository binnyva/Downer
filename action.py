import urlparse,urllib,urllib2
import re, string
import os.path,sys,subprocess,commands
import MySQLdb

conn = MySQLdb.connect("localhost", "root", "", "Data")
sql = conn.cursor(MySQLdb.cursors.DictCursor)
save_to_folder = "/mnt/x/Internet/Downloading/Downer"

class Action:
	currently_downloading = 0
	verbose = False
	yes_to_all = False
	
	def info(self, message):
		if(self.verbose): print message
	
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
			
		elif(url_parts.hostname == "www.megavideo.com"):
			special = 'megavideo'
			name = self.getMegaVideoTitle(url, return_soon)
			path = self.makePath(name + ".flv")
			
		elif(url_parts.hostname == "v.youku.com"):
			special = 'youku'
			name = self.getYoukuTitle(url)
			path = self.makePath(name + ".flv")
		
		elif(url_parts.hostname == "rapidshare.com"):
			special = 'rapidshare'
			# RapidShare's name and path is already covered in the defualt method.
		
		elif(url_parts.hostname == "www.megaupload.com"):
			special = 'megaupload'
			
		return [name, path, special]
	
	# Create a path to where the downloads should go to and return it.
	def makePath(self, name):
		return save_to_folder + '/' + name
	
	# Get info on a MegaVideo page.
	def getMegaVideoTitle(self, url, return_soon=False):
		html = ''
		if(not return_soon): 
			html = urllib2.urlopen(url).read()
			match = re.search(r'flashvars.title = "([^"]+)"', html)
			if(match): return match.group(1)
		else:
			match = re.search(r'v=([^\&]+)',url)
			if(match): return match.group(1)
		
		return "megavideo.html"
	
	# Get info on a Youku page.
	def getYoukuTitle(self, url):
		# No point reading the title - usually its in japanese/chinese.
		match = re.search(r'id_([^\&=]+)',url)
		if(match): return match.group(1)
		
		return "youku.html"
	
	# If its a YouTube page, get the Title.
	def getYoutubeTitle(self, url, return_soon=False):
		html = ''
		if(not return_soon): 
			html = urllib2.urlopen(url).read()
			match = re.search(r'<title>([^<]+)</title>', html)
			if(match): return match.group(1)
		else:
			match = re.search(r'v=([^\&]+)',url)
			if(match): return match.group(1)
			
		return "youtube.html"
	
	# For some sites, there might be a bit of work involved in getting the download URL
	def getDownloadUrl(self, url, special):
		if(special == "megavideo"):
			print "Getting download link for MegaVideo("+url+") .",
			html = urllib2.urlopen(url).read()
			print ".",
			if(html):
				match = re.search(r'flashvars.un\s*=\s*"([^"]+)"', html)
				if(not match):
					print "Video page not found. URL = " + url
					exit
				hash1 = re.search(r'flashvars.un\s*=\s*"([^"]+)"', html).group(1)
				hash2 = re.search(r'flashvars.k1\s*=\s*"([^"]+)"', html).group(1)
				hash3 = re.search(r'flashvars.k2\s*=\s*"([^"]+)"', html).group(1)
				hash4 = re.search(r'flashvars.s\s*=\s*"([^"]+)"', html).group(1)
				
				clipnabber_page = urllib2.urlopen("http://clipnabber.com/").read()
				print ".",
				sid = "725637460546913145704"
				if(clipnabber_page): sid = re.search(r'<div id="Math">(\d+)</div>', clipnabber_page).group(1)
				
				clipnabber_url = "http://clipnabber.com/gethint.php?mode=1&url=" + string.replace(urllib.quote(url), "/", "%2F") + "&mv="+hash1+","+hash2+","+hash3+","+hash4+"&sid="+sid
				contents = commands.getoutput("curl -s '"+clipnabber_url+"'")
				print ". Done"
				
				# For some wierd reason, this  following never work - always gives a premission error - so had to use curl command.
				# request = urllib2.Request(clipnabber_url)
				# request.add_header('User-agent', 'Mozilla/5.0')
				# contents = urllib2.urlopen(clipnabber_url).read()
				if(contents):
					match = re.search(r"href='(http[^']+)'", contents)
					if(match): return match.group(1)
					
		elif(special == 'youku'):
			print "Getting download link for Youku("+url+") .",
			clipnabber_page = urllib2.urlopen("http://clipnabber.com/").read()
			print ".",
			sid = "725637460546913145704"
			if(clipnabber_page): sid = re.search(r'<div id="Math">(\d+)</div>', clipnabber_page).group(1)
			
			clipnabber_url = "http://clipnabber.com/gethint.php?mode=1&url="+string.replace(urllib.quote(url), "/", "%2F")+"&sid="+sid
			contents = commands.getoutput("curl -s '"+clipnabber_url+"'") # See megavideo code to know why I did this.
			print ". Done"
			if(contents):
				match = re.findall(r"href=(http[^'>]+)", contents)
				if(match): return match
		
		return url
	
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
			overwrite = 'y'
			if(self.yes_to_all == False):
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
		
		elif(special == 'rapidshare'):
			self.execute("rapidshare '%s' '%s'" % (url, path), download_id, path)
		
		elif(special == 'megaupload'):
			self.execute("megaupload '%s' '%s'" % (url, path), download_id, path)

		else:
			url = self.getDownloadUrl(url, special)
			
			# Multipart downloads - like Youku downloads.
			if(isinstance(url, list)):
				size = 0
				part_count = 1
				for individual_url in url:
					path = re.sub(r'\.([^\.]+)$', '_'+str(part_count)+r'.\1', path)
					self.execute("wget -c -O '%s' '%s'" % (path, individual_url), download_id, '')
					size += int(os.path.getsize(path))
					part_count += 1
					
				mb_size = (size / 1024) / 1024
				sql.execute("UPDATE Downer SET downloaded='1', downloaded_on=NOW(), file_size='%f' WHERE id=%d" % (mb_size, download_id))
			else:
				self.execute("wget -c -O '%s' '%s'" % (path, url), download_id, path)
		
		# Once the download is done, unset the currently_downloading flag.
		self.currently_downloading = 0
	
	# Execute the given command.
	def execute(self, command, download_id=0, path=''):
		try:
			global sql
			if(download_id > 0): sql.execute("UPDATE Downer SET downloaded='-1' WHERE id=%d" % download_id)

			retcode = subprocess.call(command, shell=True)
			
			# Error!
			if retcode != 0:
				print >>sys.stderr, "Child was terminated by signal", -retcode
				if(download_id > 0): sql.execute("UPDATE Downer SET downloaded='0' WHERE id=%d" % download_id)
				
			else:
				# The thing that was being downloaded was from the database. So, mark it as downloaded when done.
				if(download_id > 0 and path != ''):
					size = int(os.path.getsize(path))
					mb_size = (size / 1024) / 1024 # getsize() returns size in bytes - so convent to KB and the MB.
					sql.execute("UPDATE Downer SET downloaded='1', downloaded_on=NOW(), file_size='%f' WHERE id=%d" % (mb_size, download_id))
					
		except OSError, e:
			print >>sys.stderr, "Execution failed:", e
			if(download_id > 0): sql.execute("UPDATE Downer SET downloaded='0' WHERE id=%d" % download_id)

action = Action()

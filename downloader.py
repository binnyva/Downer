#!/usr/bin/python
 
from action import *
import sys

if __name__ == '__main__':
	try:
		argc = len(sys.argv) - 1
		
		# We have arguments - download it.
		if argc:
			action.download(argv[1])
		else:
			sql.execute("SELECT name, url, file_path, special FROM Download WHERE downloaded='0' ORDER BY added_on ASC")
			result_set = sql.fetchall ()
			for row in result_set:
				action.download(url = row['url'], row['file_path'], special = row['special'])
				
	except KeyboardInterrupt:
		sys.exit(u'\nCtrl+C invoked. Exiting...')
	
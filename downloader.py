#!/usr/bin/python
 
from action import *
import sys

if __name__ == '__main__':
	try:
		argc = len(sys.argv) - 1
		
		# We have arguments - download it.
		if argc:
			action.download(sys.argv[1])
			
		else:
			sql.execute("SELECT id, name, url, file_path, special FROM Downer WHERE downloaded='0' ORDER BY added_on ASC, id")
			result_set = sql.fetchall ()
			for row in result_set:
				action.download(row['url'], row['file_path'], row['special'], int(row['id']))
				
	except KeyboardInterrupt:
		print "\nResetting status for Download #" + str(action.currently_downloading)
		sql.execute("UPDATE Downer SET downloaded='0' WHERE id=%d" % action.currently_downloading)
		sys.exit(u'Ctrl+C invoked. Exiting...')
	
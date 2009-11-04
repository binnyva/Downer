#!/usr/bin/python

import getopt,sys
from action import *

def usage():
	print """Usage: downer [OPTIONS] [URL [OUTPUT FILE]]
	-v		Verbose output
	-y		Yes to all Y/N questions(overwrite existing file, etc.)
	-h,--help	Help - shows this screen
	-l,--limit=N	Limit Download to N items only.
	"""


def main():
	# Get command line arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hl:yv", ["help", "limit="])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	
	limit = 0
	for o, a in opts:
		if o == "-v":
			action.verbose = True
		elif o == "-y":
			action.yes_to_all = True
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-l", "--limit"):
			limit = a
		else:
			print "Option ", o, " not recognized"
	
	
	argc = len(args)
	if(argc):
		# A URL is given...
		path = ""
		if(argc > 1): path = args[1]
		
		action.info("Going to download " + args[0])
		action.download(args[0], path)
	else:
		sql_limit = ""
		if(limit): sql_limit = "LIMIT 0,"+str(limit)
		sql.execute("SELECT id, name, url, file_path, special FROM Downer WHERE downloaded='0' ORDER BY download_order, added_on ASC, id " + sql_limit)
		result_set = sql.fetchall ()
		for row in result_set:
			action.download(row['url'], row['file_path'], row['special'], int(row['id']))

if __name__ == '__main__':
	try:
		main()
				
	except KeyboardInterrupt:
		print "\nResetting status for Download #" + str(action.currently_downloading)
		sql.execute("UPDATE Downer SET downloaded='0' WHERE id=%d" % action.currently_downloading)
		sys.exit(u'Ctrl+C invoked. Exiting...')
	
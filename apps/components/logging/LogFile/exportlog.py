import sys
import csv

# Read a file
if (len(sys.argv) > 2) or (len(sys.argv) <= 1):
	print "To export a log file you need to..."
else:
	# Variables
	in_file = open(sys.argv[1], "r") 						# Open Log File
	array = []
	
	# Go through log file and save each line to an array.
	for line in in_file:
		array.append(line)
	in_file.close() 										# Close Log File
	
	for line in array:
		number = "200\n"
		if line.endswith(number):
			print "yes"
		else:
			array.remove(line)
	
	for line in array:
		print line
	
	# Create csv file
	# writeToFile = csv.writer(open('test.csv', 'wb'))
	# writeToFile.writerow(['Page'] + ['Visits'] + ['Total Time'] + ['Average Time'])
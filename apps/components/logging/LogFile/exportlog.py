import sys
import csv
import datetime as dt

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
			pass
		else:
			array.remove(line)
	
	# Get start and end time of log
	getStartTime = array[0].split()
	getEndTime = array[len(array) - 1].split()
	startTime = getStartTime[1] + "_" + getStartTime[2].replace(":", "-")
	endTime = getEndTime[1] + "_" + getEndTime[2].replace(":", "-")
	
	# Get name
	getName = array[0].split()
	name = getName[3]
	
	# Create csv file
	x = 0
	writeToFile = csv.writer(open(name+'-'+startTime+'_'+endTime+'.csv', 'wb'))
	writeToFile.writerow(['Page'] + ['Visits'] + ['Total Time'] + ['Average Time'])
	while x < len(array):
		line = array[x].split()
		startTime = dt.datetime.strptime(line[2], '%H:%M:%S')
		getEndTime = array[x+1].split()
		endTime = dt.datetime.strptime(getEndTime[2], '%H:%M:%S')
		diff = (endTime - startTime) 
		diff.seconds/60 
		diff = str(diff)
		writeToFile.writerow([line[4]] + ['Visits'] + [diff] + ['Average Time'])
		x = x + 1	
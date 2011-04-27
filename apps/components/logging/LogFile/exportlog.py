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
	in_file.close() 	                                    # Close Log File
	
	for line in array:
		number = "200\n"
		if line.endswith(number):
			pass
		else:
			array.remove(line)
	
	# Get start and end time of log
	getStartTimeOfLog = array[0].split()
	getEndTimeOfLog = array[len(array) - 1].split()
	startTimeOfLog = getStartTimeOfLog[1] + "_" + getStartTimeOfLog[2].replace(":", "-")
	endTimeOfLog = getEndTimeOfLog[1] + "_" + getEndTimeOfLog[2].replace(":", "-")
	
	# Get name
	getName = array[0].split()
	name = getName[3]
	
	# Create csv file
	x = 0
	openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'wb')
	writeToFile = csv.writer(openFile)
	writeToFile.writerow(['Page'] + ['Visits'] + ['Total Time'] + ['Average Time'])
	openFile.close()
	while x < len(array):
		line = array[x].split()
		startTime = dt.datetime.strptime(line[2], '%H:%M:%S')
		try:
			getEndTime = array[x+1].split()
			endTime = dt.datetime.strptime(getEndTime[2], '%H:%M:%S')
			diff = (endTime - startTime) 
			diff.seconds/60 
			diff = str(diff)
		except IndexError:
			endTime = dt.datetime.strptime("00:00:00", '%H:%M:%S')
			diff = (startTime - endTime)
		openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'ab')
		writeToFile = csv.writer(openFile)
		writeToFile.writerow([line[4]] + ['Visits'] + [diff] + ['Average Time'])
		openFile.close()
		x = x + 1	
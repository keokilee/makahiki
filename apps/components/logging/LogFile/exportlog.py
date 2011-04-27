import sys
import csv
import datetime as dt

# Global Variables
array = []
startTimeOfLog = ""
endTimeOfLog = ""
name = ""
startTime = ""
endTime = ""

def readFile():
	global array
    # Variables
    # Open log file
	in_file = open(sys.argv[1], "r")
	
	# Go through log file and save each line to an array.
	for line in in_file:
		array.append(line)
    #Close log file
	in_file.close()
	return
    
def test():
	print array
	return

def removeNotNeededLogs():
	global array
	for line in array:
		number = "200\n"
		if line.endswith(number):
			pass
		else:
			array.remove(line)

def getLogTime():
	global startTimeOfLog
	global endTimeOfLog
	global array
	# Get start and end time of log
	getStartTimeOfLog = array[0].split()
	getEndTimeOfLog = array[len(array) - 1].split()
	startTimeOfLog = getStartTimeOfLog[1] + "_" + getStartTimeOfLog[2].replace(":", "-")
	endTimeOfLog = getEndTimeOfLog[1] + "_" + getEndTimeOfLog[2].replace(":", "-")

def getName():
	global name
	findName = array[0].split()
	name = findName[3]

def createCSVFile():
	x = 0
	while x < len(array):
		findName = array[x].split()
		name = findName[3]
		openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'wb')
		writeToFile = csv.writer(openFile)
		writeToFile.writerow(['Page'] + ['Visits'] + ['Total Time'] + ['Average Time'])
		openFile.close()
		x = x + 1
	
# Read a file
if (len(sys.argv) > 2) or (len(sys.argv) <= 1):
	print "To export a log file you need to..."
else:
	readFile()
	removeNotNeededLogs()
	getLogTime()
	
	# Create csv file
	createCSVFile()
	

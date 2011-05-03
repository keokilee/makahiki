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
copyArray = []
contents = []

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
	x = 0
	while x < len(copyArray):
		print copyArray[x]
		x = x + 1

def removeNotNeededLogs():
	global array
	openFile = open('errorLog.csv', 'wb')
	writeToFile = csv.writer(openFile)
	writeToFile.writerow(['Date'] + ['Time'] + ['User'] + ['Page'] + ['Status Code'])
	for line in array:
		number = "200\n"
		values = line.split()
		date = values[1]
		time = values[2]
		username = values[3]
		page = values[4]
		statusCode = values[5]
		if line.endswith(number):
			pass
		else:
			writeToFile.writerow([date] + [time] + [username] + [page] + [statusCode])
			array.remove(line)
	openFile.close()

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
		# writeToFile.writerow(['Page'] + ['Visits'] + ['Total Time'] + ['Average Time'])
		openFile.close()
		x = x + 1

def writeToCSVFiles():
	x = 0
	while x < len(array):
		findName = array[x].split()
		name = findName[3]
		findPage = array[x].split()
		page = findPage[4]
		findDate = array[x].split()
		date = findDate[1]
		findTime = array[x].split()
		time = findTime[2]
		openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'ab')
		writeToFile = csv.writer(openFile)
		writeToFile.writerow([page] + [date] + [time])
		openFile.close()
		x = x + 1	
		
def getIndividualFiles():
	global copyArray
	match = "false"
	x = 0
	while x < len(array):
		findName = array[x].split()
		name = findName[3]
		if (len(copyArray) == 0):
			copyArray.append(array[x])
			match = "true"
		else:
			y = 0
			while y < len(copyArray):
				findN = copyArray[y].split()
				n = findN[3]
				if (name == n):
					match = "true"
				y = y + 1
		if (match == "false"):
			copyArray.append(array[x])
		match = "false"
		x = x + 1

def printArray():
	global name
	x = 0
	while x < len(copyArray):
		findName = copyArray[x].split()
		name = findName[3]
		openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'rb')
		accessFile(openFile)
		openFile.close()
		x = x + 1

def accessFile(openFile):
	global contents
	global name
	addContents = []
	page = ""
	match = "false"
	
	# print "Opening file " + name
	writeToFile = csv.reader(openFile)
	for row in writeToFile:
		line = ' '.join(row)
		contents.append(line)
	open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'w')
	x = 0
	while x < len(contents):
		try:
			findPage = contents[x].split()
			page = findPage[0]
			if len(addContents) == 0:
				addContents.append(page + " 1")
			else:
				y = 0
				while y < len(addContents):
					findP = addContents[y].split()
					p = findP[0]
					# print "comparing " + p + " with " + page
					if p == page:
						visit = int(findP[1]) + 1
						findP[1] = str(visit)
						addContents[y] = p + " " + findP[1]
						match = "true"
					y = y + 1
				if match == "false":
					addContents.append(page + " 1")
				match = "false"
		except IndexError:
			findPage = contents[x].split()
			page = findPage[0]
			if len(addContents) == 0:
				addContents.append(page + " 1")
			else:
				y = 0
				while y < len(addContents):
					findP = addContents[y].split()
					p = findP[0]
					# print "comparing " + p + " with " + page
					if p == page:
						visit = int(findP[1]) + 1
						findP[1] = str(visit)
						addContents[y] = p + " " + findP[1]
						match = "true"
					y = y + 1
				if match == "false":
					addContents.append(page + " 1")
				match = "false"
		x = x + 1
	openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'ab')
	writeToFile = csv.writer(openFile)
	writeToFile.writerow(['Page'] + ['Visits'] + ['Total Time'] + ['Average Time'])
	x = 0
	while x < len(addContents):
		find = addContents[x].split()
		page = find[0]
		visits = find[1]
		writeToFile.writerow([page] + [visits])
		x = x + 1
	
	contents = []
		
# Read a file
if (len(sys.argv) > 2) or (len(sys.argv) <= 1):
	print "To export a log file you need to..."
else:
	readFile()
	removeNotNeededLogs()
	getLogTime()
	
	# Create csv file
	createCSVFile()
	
	writeToCSVFiles()
	
	getIndividualFiles()
	printArray()